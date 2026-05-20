# backend/app/agents/core/agent_context.py

from typing import Any

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """
    Canonical shared orchestration state across the agent workflow.

    Architectural Purpose
    ---------------------
    Centralized execution context passed across:
        Supervisor -> Analyzer -> Retrieval -> Context Builder
        -> Generator -> Validator

    Design Principles
    -----------------
    1. Stateful orchestration safe
       - Single mutable workflow contract.

    2. Agent decoupling
       - Agents communicate through shared state only.

    3. Observability first
       - Trace, token usage, validation,
         and context decisions tracked.

    4. Future extensible
       - Supports memory, tools, citations,
         evaluation, and autonomous workflows.
    """

    # Original raw user query.
    query: str

    # Multi-tenant orchestration metadata.
    tenant_id: str = "default_tenant"
    uploaded_by: str = "anonymous"

    # Distributed trace correlation ID.
    correlation_id: str

    # User-selected role/persona.
    role: str = "generic"

    # Runtime resolved role from orchestration logic.
    resolved_role: str | None = None

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

    # Query analysis output.
    refined_query: str | None = None
    intent: str | None = None
    domain: str | None = None

    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)

    # Retrieval routing state.
    selected_source: str | None = None

    retrieval_required: bool = True
    retrieval_strategy: str = "HYBRID"

    metadata_filters: dict[str, Any] = Field(
        default_factory=dict
    )

    # Raw retrieval output.
    retrieved_context: list[str] = Field(
        default_factory=list
    )

    # Final engineered prompt context.
    grounded_context: str | None = None

    # Context engineering observability metadata.
    context_engineering_metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    # Final generated answer.
    answer: str | None = None

    # Validation workflow state.
    validation_status: str = "NOT_VALIDATED"

    validation_errors: list[str] = Field(
        default_factory=list
    )

    # Agent-level token and cost observability.
    token_usage: dict[str, dict[str, int]] = Field(
        default_factory=dict
    )

    # Lightweight orchestration execution trace.
    trace: list[str] = Field(default_factory=list)

    def add_trace(
        self,
        message: str,
    ) -> None:
        """
        Append orchestration trace message.

        Future Direction
        ----------------
        Can evolve into structured trace events
        integrated with OpenTelemetry.
        """

        self.trace.append(message)