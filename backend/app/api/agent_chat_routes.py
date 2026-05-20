# backend/app/api/agent_chat_routes.py

from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.agents.core.agent_context import AgentContext
from app.agents.core.schemas import (
    ChatRequest,
    ChatResponse,
    MemorySnapshot,
)
from app.agents.orchestration.chat_graph import ChatGraph
from app.core.database import SessionLocal
from app.core.trace_logger import (
    TraceContext,
    TraceLogger,
)

router = APIRouter(
    prefix="/agent",
    tags=["Agent Chat"],
)


def get_project_root() -> Path:
    cwd = Path.cwd()

    if cwd.name == "backend":
        return cwd.parent

    return cwd


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/chat-ui",
    response_class=HTMLResponse,
)
def chat_ui():
    project_root = get_project_root()

    html_path = (
        project_root
        / "gui"
        / "agent-chat.html"
    )

    if not html_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {html_path}",
        )

    return html_path.read_text(
        encoding="utf-8",
    )


@router.get("/logs")
def get_logs(
    lines: int = 200,
):
    project_root = get_project_root()

    possible_log_paths = [
        project_root / "logs" / "vitechq-rag-trace.log",
        project_root / "backend" / "logs" / "vitechq-rag-trace.log",
        project_root / "vitechq-rag-trace.log",
    ]

    log_path = next(
        (
            path
            for path in possible_log_paths
            if path.exists()
        ),
        None,
    )

    if not log_path:
        return {
            "log_file": None,
            "lines": [],
            "message": "No log file found.",
        }

    content = log_path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    return {
        "log_file": str(log_path),
        "lines": content[-lines:],
    }


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="query is required",
        )

    correlation_id = (
        request.correlation_id
        or str(uuid.uuid4())
    )

    trace_ctx = TraceContext(
        correlation_id=correlation_id,
        uploaded_by=request.uploaded_by or "-",
        tenant_id=request.tenant_id,
        request_name="AGENT_CHAT",
    )

    try:
        TraceLogger.info(
            trace_ctx,
            (
                "Agent chat request received. "
                f"query={request.query}"
            ),
        )

        context = AgentContext(
            query=request.query.strip(),
            tenant_id=request.tenant_id,
            uploaded_by=request.uploaded_by,
            correlation_id=correlation_id,
            role=request.role,
            conversation_history=request.conversation_history,
            user_context=request.user_context,
            metadata_context=request.metadata_context,
        )

        graph = ChatGraph(db)

        result = graph.run(context)

        retrieved_context = (
            result.retrieved_context or []
        )

        TraceLogger.info(
            trace_ctx,
            (
                "Agent chat completed. "
                f"source={result.selected_source}, "
                f"answer_mode={result.answer_mode}, "
                f"resolved_role={result.resolved_role}, "
                f"retrieved_context_count="
                f"{len(retrieved_context)}, "
                f"validation_status="
                f"{result.validation_status}"
            ),
        )

        return ChatResponse(
            answer=result.answer or "",
            correlation_id=result.correlation_id,
            role=result.role,
            resolved_role=result.resolved_role,
            refined_query=result.refined_query,
            intent=result.intent,
            domain=result.domain,
            keywords=result.keywords,
            entities=result.entities,
            selected_source=result.selected_source,
            answer_mode=result.answer_mode,
            source_explanation=result.source_explanation,
            retrieval_required=result.retrieval_required,
            retrieval_strategy=result.retrieval_strategy,
            retrieved_context_count=len(retrieved_context),
            retrieved_context=retrieved_context,
            grounded_context=result.grounded_context,
            validation_status=result.validation_status,
            validation_errors=result.validation_errors,
            token_usage=result.token_usage,
            context_engineering_metadata=(
                result.context_engineering_metadata
            ),
            memory_snapshot=MemorySnapshot(
                conversation_history=request.conversation_history,
                user_context=request.user_context,
                metadata_context=request.metadata_context,
            ),
            trace=result.trace,
        )

    except HTTPException:
        raise

    except Exception as ex:
        TraceLogger.error(
            trace_ctx,
            f"Agent chat failed. error={str(ex)}",
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Agent chat failed. "
                f"correlation_id={correlation_id}"
            ),
        ) from ex