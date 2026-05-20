# backend/app/agents/core/schemas.py

from typing import Any

from pydantic import BaseModel, Field


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
        - vector memory integration
        - long-running session persistence
    """

    # Recent conversational state.
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
         and future multi-agent coordination.

    3. Role-aware orchestration
       - Allows dynamic persona specialization.
    """

    # Original raw user query.
    query: str

    # Multi-tenant orchestration metadata.
    tenant_id: str = "default_tenant"

    uploaded_by: str = "anonymous"

    # Generated if caller does not provide one.
    correlation_id: str | None = None

    # User-selected role/persona.
    #
    # generic:
    #     role inferred dynamically at runtime.
    role: str = "generic"

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
    Exposes:
        - generated response
        - orchestration metadata
        - retrieval visibility
        - routing visibility
        - role resolution visibility
        - validation output
        - lightweight observability

    Design Principles
    -----------------
    1. Debuggable AI workflows
       - Trace and token visibility included.

    2. Retrieval transparency
       - Retrieval decisions and grounding exposed.

    3. Role-aware generation
       - Final resolved role and instructions returned.

    4. Future extensible
       - Supports citations, confidence scoring,
         evaluation metadata, and tool traces.
    """

    # Final generated response.
    answer: str | None

    # Distributed tracing identifier.
    correlation_id: str

    # User-selected role/persona.
    role: str = "generic"

    # Runtime resolved role from orchestration.
    resolved_role: str | None = None

    # Final role instruction used during generation.
    role_instruction: str | None = None

    # Query analysis output.
    refined_query: str | None = None

    intent: str | None = None

    domain: str | None = None

    keywords: list[str] = Field(
        default_factory=list
    )

    entities: list[str] = Field(
        default_factory=list
    )

    # Retrieval routing metadata.
    selected_source: str | None = None

    # Final answer generation mode.
    #
    # Examples:
    # - GROUNDED_RAG
    # - GENERAL_LLM
    # - HYBRID
    # - MEMORY_ONLY
    # - TOOL_ASSISTED
    answer_mode: str = "UNKNOWN"

    # Human-readable routing explanation.
    source_explanation: str = (
        "Source has not been resolved yet."
    )

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

    # Validation workflow state.
    validation_status: str = "NOT_VALIDATED"

    validation_errors: list[str] = Field(
        default_factory=list
    )

    # Agent-level LLM usage tracking.
    token_usage: dict[str, dict[str, int]] = Field(
        default_factory=dict
    )

    # Context engineering observability metadata.
    context_engineering_metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    # Lightweight conversational memory snapshot.
    memory_snapshot: MemorySnapshot = Field(
        default_factory=MemorySnapshot
    )

    # Lightweight orchestration execution trace.
    trace: list[str] = Field(
        default_factory=list
    )