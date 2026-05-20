# backend/app/agents/core/agent_context.py

from typing import Any

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """
    Canonical shared orchestration state.

    Architectural Purpose
    ---------------------
    Centralized workflow state shared across:
        - retrieval
        - routing
        - role policy
        - context engineering
        - generation
        - validation

    Design Principles
    -----------------
    1. Shared workflow contract
       - Agents communicate only through AgentContext.

    2. Deterministic orchestration
       - State transitions remain explicit and traceable.

    3. Observability-first design
       - Routing, validation, token usage,
         and orchestration traces are preserved.

    4. Future extensible
       - Supports tools, citations, memory,
         evaluators, and autonomous workflows.
    """

    # Original raw user query.
    query: str

    # Multi-tenant orchestration metadata.
    tenant_id: str = "default_tenant"

    uploaded_by: str = "anonymous"

    # Distributed trace correlation ID.
    correlation_id: str

    # Requested runtime persona.
    role: str = "generic"

    # Final resolved runtime role.
    resolved_role: str | None = None

    # Final role instruction injected into prompts.
    role_instruction: str | None = None

    # Conversational memory state.
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

    keywords: list[str] = Field(
        default_factory=list
    )

    entities: list[str] = Field(
        default_factory=list
    )

    # Source-routing state.
    selected_source: str | None = None

    # Final answer generation mode.
    #
    # Examples:
    # - GROUNDED_RAG
    # - GENERAL_LLM
    # - HYBRID
    # - TOOL_ASSISTED
    answer_mode: str = "UNKNOWN"

    # Human-readable routing explanation.
    source_explanation: str = (
        "Source has not been resolved yet."
    )

    retrieval_required: bool = True

    retrieval_strategy: str = "HYBRID"

    # Future direction:
    # metadata-aware retrieval filtering.
    metadata_filters: dict[str, Any] = Field(
        default_factory=dict
    )

    # Raw retrieval output.
    retrieved_context: list[str] = Field(
        default_factory=list
    )

    # Final engineered prompt context.
    grounded_context: str | None = None

    # Context-engineering observability metadata.
    context_engineering_metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    # Final generated response.
    answer: str | None = None

    # Validation workflow state.
    validation_status: str = "NOT_VALIDATED"

    validation_errors: list[str] = Field(
        default_factory=list
    )

    # Agent-level LLM usage observability.
    token_usage: dict[str, dict[str, int]] = Field(
        default_factory=dict
    )

    # Lightweight orchestration execution trace.
    trace: list[str] = Field(
        default_factory=list
    )

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