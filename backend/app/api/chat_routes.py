from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.orchestration.chat_graph import ChatGraph

router = APIRouter(prefix="/agent", tags=["Agent Chat"])

chat_graph = ChatGraph()


class ChatRequest(BaseModel):
    query: str
    tenant_id: str = "default_tenant"
    uploaded_by: str = "anonymous"
    correlation_id: str | None = None
    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    user_context: dict = Field(default_factory=dict)
    metadata_context: dict = Field(default_factory=dict)
    response_style: str = "ARCHITECT_LEVEL"


class ChatResponse(BaseModel):
    answer: str = ""
    correlation_id: str

    refined_query: str | None = None
    intent: str | None = None
    domain: str | None = None

    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)

    retrieval_required: bool = True
    retrieval_strategy: str = "HYBRID"

    selected_source: str | None = None
    selected_sources: list[str] = Field(default_factory=list)

    metadata_filters: dict = Field(default_factory=dict)

    needs_clarification: bool = False
    clarification_question: str | None = None

    information_sufficient: bool = False

    retrieved_context: list[dict] = Field(default_factory=list)
    integrated_context: str = ""

    citations: list[dict] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    response_style: str = "ARCHITECT_LEVEL"
    confidence_score: float | None = None
    analyzer_source: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    correlation_id = request.correlation_id or str(uuid4())

    # Architectural Purpose: create one stable state contract for LangGraph.
    initial_state = {
        "query": request.query,
        "tenant_id": request.tenant_id,
        "uploaded_by": request.uploaded_by,
        "correlation_id": correlation_id,
        "conversation_history": request.conversation_history,
        "user_context": request.user_context,
        "metadata_context": request.metadata_context,
        "response_style": request.response_style,
        "errors": [],
    }

    result = chat_graph.invoke(initial_state)

    return ChatResponse(
        answer=result.get("answer") or result.get("final_answer") or "",
        correlation_id=result.get("correlation_id") or correlation_id,

        refined_query=result.get("refined_query"),
        intent=result.get("intent"),
        domain=result.get("domain"),

        keywords=result.get("keywords", []),
        entities=result.get("entities", []),

        retrieval_required=result.get("retrieval_required", True),
        retrieval_strategy=result.get("retrieval_strategy", "HYBRID"),

        selected_source=result.get("selected_source"),
        selected_sources=result.get("selected_sources", []),

        metadata_filters=result.get("metadata_filters", {}),

        needs_clarification=result.get("needs_clarification", False),
        clarification_question=result.get("clarification_question"),

        information_sufficient=result.get("information_sufficient", False),

        retrieved_context=result.get("retrieved_context", []),
        integrated_context=result.get("integrated_context", ""),

        citations=result.get("citations", []),
        errors=result.get("errors", []),

        response_style=result.get("response_style", request.response_style),
        confidence_score=result.get("confidence_score"),
        analyzer_source=result.get("analyzer_source"),
    )