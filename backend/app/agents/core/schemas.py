# backend/app/agents/core/schemas.py

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    External API request contract for agent chat.

    Architectural Purpose
    ---------------------
    Defines the stable inbound request schema
    entering the orchestration workflow.

    Design Principles
    -----------------
    1. API contract stability
       - External clients depend on this schema.

    2. Context extensibility
       - Supports memory, personalization,
         and future agent coordination.

    3. Multi-tenant ready
       - Tenant-aware orchestration support.
    """

    query: str

    tenant_id: str = "default_tenant"
    uploaded_by: str = "anonymous"

    # Generated if caller does not provide one.
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


class MemorySnapshot(BaseModel):
    """
    Lightweight conversational memory snapshot.

    Architectural Purpose
    ---------------------
    Captures memory-related orchestration state
    returned to clients for debugging, replay,
    and future persistent memory systems.

    Future Direction
    ----------------
    Can evolve into:
        - episodic memory
        - semantic memory
        - session persistence
        - vector memory integration
    """

    conversation_history: list[dict[str, str]] = Field(
        default_factory=list
    )

    user_context: dict[str, Any] = Field(
        default_factory=dict
    )

    metadata_context: dict[str, Any] = Field(
        default_factory=dict
    )


class ChatResponse(BaseModel):
    """
    External API response contract for agent chat.

    Architectural Purpose
    ---------------------
    Exposes:
        - generated response
        - orchestration metadata
        - retrieval visibility
        - validation output
        - lightweight observability

    Design Principles
    -----------------
    1. Debuggable AI workflows
       - Trace and token visibility included.

    2. Retrieval transparency
       - Retrieval decisions and grounding exposed.

    3. Future extensible
       - Supports citations, confidence scoring,
         memory systems, and evaluation metadata.
    """

    # Final generated response.
    answer: str | None

    # Distributed tracing identifier.
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

    # Retrieval observability.
    retrieved_context_count: int = 0

    # Raw retrieval chunks.
    retrieved_context: list[str] = Field(
        default_factory=list
    )

    # Final engineered prompt context.
    grounded_context: str | None = None

    # Validation state.
    validation_status: str = "NOT_VALIDATED"

    validation_errors: list[str] = Field(
        default_factory=list
    )

    # Agent-level LLM usage tracking.
    token_usage: dict[str, dict[str, int]] = Field(
        default_factory=dict
    )

    # Context engineering decisions.
    context_engineering_metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    # Memory and conversational snapshot.
    memory_snapshot: MemorySnapshot = Field(
        default_factory=MemorySnapshot
    )

    # Lightweight orchestration trace.
    trace: list[str] = Field(default_factory=list)