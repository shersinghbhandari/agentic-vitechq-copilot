# backend/app/api/chat_routes.py

from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session

from app.agents.core.agent_context import AgentContext

from app.agents.core.schemas import (
    ChatRequest,
    ChatResponse,
)

from app.agents.orchestration.chat_graph import (
    ChatGraph,
)

router = APIRouter(
    prefix="/agent",
    tags=["Agent Chat"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def agent_chat(
    request: ChatRequest,
    db: Session = Depends(get_db_session),
):
    correlation_id = (
        request.correlation_id
        or str(uuid4())
    )

    context = AgentContext(
        query=request.query,
        tenant_id=request.tenant_id,
        uploaded_by=request.uploaded_by,
        correlation_id=correlation_id,
        conversation_history=request.conversation_history,
        user_context=request.user_context,
        metadata_context=request.metadata_context,
    )

    graph = ChatGraph(db)

    result = graph.run(context)

    return ChatResponse(
        answer=result.answer,

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
            result.retrieved_context
        ),

        validation_status=result.validation_status,

        validation_errors=result.validation_errors,

        trace=result.trace,
    )