from pathlib import Path
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.agents.core.agent_context import AgentContext
from app.agents.core.schemas import (
    ChatRequest,
    ChatResponse,
)
from app.agents.orchestration.chat_orchestrator import (
    ChatOrchestrator,
)
from app.core.database import SessionLocal
from app.core.trace_logger import (
    TraceContext,
    TraceLogger,
)

router = APIRouter(
    prefix="/agent",
    tags=["Agent Chat"],
)


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

    project_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    html_path = (
        project_root
        / "gui"
        / "agent-chat.html"
    )

    if not html_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                f"File not found: {html_path}"
            ),
        )

    return html_path.read_text(
        encoding="utf-8",
    )


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

    correlation_id = str(uuid.uuid4())

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
        )

        orchestrator = ChatOrchestrator(db)

        result = orchestrator.run(context)

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
            query=result.query,
            refined_query=result.refined_query,
            answer=result.answer or "",
            selected_source=result.selected_source,
            citations=result.citations or [],
            retrieved_context_count=(
                len(retrieved_context)
            ),
            validation_status=(
                result.validation_status
            ),
            validation_message=(
                result.validation_message
            ),
            correlation_id=(
                result.correlation_id
            ),
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
                f"correlation_id="
                f"{correlation_id}"
            ),
        ) from ex