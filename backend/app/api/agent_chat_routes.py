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

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


def get_db():
    """
    Request-scoped database session provider.

    Design Principle
    ----------------
    Keeps database lifecycle isolated
    per HTTP request.
    """

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
    """
    Serves lightweight local chat UI.

    Future Direction
    ----------------
    Replace with React/Next.js frontend
    or static asset hosting.
    """

    html_path = (
        PROJECT_ROOT
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
    """
    Lightweight runtime log inspection endpoint.

    Architectural Purpose
    ---------------------
    Simplifies local debugging and
    orchestration trace visibility.
    """

    possible_log_paths = [
        PROJECT_ROOT / "logs" / "vitechq-rag-trace.log",
        PROJECT_ROOT / "backend" / "logs" / "vitechq-rag-trace.log",
        PROJECT_ROOT / "vitechq-rag-trace.log",
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
    """
    Agent chat API entrypoint.

    Architectural Purpose
    ---------------------
    Bridges external HTTP requests into
    the LangGraph-based orchestration workflow.

    Flow
    ----
    Request
        -> AgentContext
        -> ChatGraph
        -> Agent Orchestration
        -> ChatResponse

    Design Principles
    -----------------
    1. Thin API layer
       - Request validation and response mapping only.

    2. Trace-first execution
       - Every request gets correlation tracking.

    3. Multi-tenant ready
       - Tenant/user metadata propagated throughout workflow.

    4. Safe error boundary
       - Internal failures hidden behind correlation ID.
    """

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

        # Canonical orchestration state object.
        context = AgentContext(
            query=request.query.strip(),
            tenant_id=request.tenant_id,
            uploaded_by=request.uploaded_by,
            correlation_id=correlation_id,
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
                f"retrieved_context_count="
                f"{len(retrieved_context)}, "
                f"validation_status="
                f"{result.validation_status}"
            ),
        )

        return ChatResponse(
            answer=result.answer or "",
            correlation_id=result.correlation_id,
            refined_query=result.refined_query,
            intent=result.intent,
            domain=result.domain,
            keywords=result.keywords,
            entities=result.entities,
            selected_source=result.selected_source,
            retrieval_required=result.retrieval_required,
            retrieval_strategy=result.retrieval_strategy,
            retrieved_context_count=len(
                retrieved_context
            ),
            retrieved_context=retrieved_context,
            grounded_context=result.grounded_context,
            validation_status=result.validation_status,
            validation_errors=result.validation_errors,
            token_usage=result.token_usage,
            context_engineering_metadata=(
                result.context_engineering_metadata
            ),

            # Lightweight conversational memory snapshot.
            memory_snapshot=MemorySnapshot(
                conversation_history=(
                    request.conversation_history
                ),
                user_context=request.user_context,
                metadata_context=(
                    request.metadata_context
                ),
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