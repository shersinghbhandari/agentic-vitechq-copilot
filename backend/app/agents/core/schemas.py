# backend/app/agents/core/schemas.py

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    External API request contract for agent chat.

    Architectural Purpose
    ---------------------
    Defines the stable inbound request schema
    entering the orchestration layer.

    Design Principles
    -----------------
    1. API stability
       - External clients depend on this contract.

    2. Context extensibility
       - Supports future memory and personalization.

    3. Multi-tenant ready
       - Tenant and user tracing included.
    """

    query: str

    tenant_id: str = "default_tenant"
    uploaded_by: str = "anonymous"

    # Generated if not supplied by caller.
    correlation_id: str | None = None

    # Conversational memory input.
    conversation_history: list[dict[str, str]] = Field(
        default_factory=list
    )

    # User personalization context.
    user_context: dict[str, Any] = Field(
        default_factory=dict
    )

    # Request-scoped metadata context.
    metadata_context: dict[str, Any] = Field(
        default_factory=dict
    )


class ChatResponse(BaseModel):
    """
    External API response contract for agent chat.

    Architectural Purpose
    ---------------------
    Exposes orchestration output and lightweight
    observability metadata back to clients.

    Design Principles
    -----------------
    1. Debuggable AI workflows
       - Trace and validation visibility included.

    2. Retrieval transparency
       - Source selection and retrieval indicators exposed.

    3. Future extensible
       - Supports citations, evaluation,
         confidence scoring, and tool traces.
    """

    answer: str | None

    correlation_id: str

    # Query analysis output.
    refined_query: str | None = None
    intent: str | None = None
    domain: str | None = None

    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)

    # Retrieval routing metadata.
    selected_source: str | None = None

    retrieval_required: bool = True
    retrieval_strategy: str = "HYBRID"

    # Lightweight retrieval observability.
    retrieved_context_count: int = 0

    # Validation result metadata.
    validation_status: str = "NOT_VALIDATED"

    validation_errors: list[str] = Field(
        default_factory=list
    )

    # Agent-level token usage tracking.
    token_usage: dict[str, dict[str, int]] = Field(
        default_factory=dict
    )

    # Context engineering observability.
    context_engineering_metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    # Lightweight orchestration execution trace.
    trace: list[str] = Field(default_factory=list)