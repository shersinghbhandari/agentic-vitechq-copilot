# backend/app/agents/core/agent_context.py

from typing import Any
from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    query: str

    tenant_id: str = "default_tenant"
    uploaded_by: str = "anonymous"
    correlation_id: str

    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    user_context: dict[str, Any] = Field(default_factory=dict)
    metadata_context: dict[str, Any] = Field(default_factory=dict)

    refined_query: str | None = None
    intent: str | None = None
    domain: str | None = None

    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)

    selected_source: str | None = None
    retrieval_required: bool = True
    retrieval_strategy: str = "HYBRID"
    metadata_filters: dict[str, Any] = Field(default_factory=dict)

    retrieved_context: list[str] = Field(default_factory=list)
    grounded_context: str | None = None

    answer: str | None = None
    validation_status: str = "NOT_VALIDATED"
    validation_errors: list[str] = Field(default_factory=list)

    trace: list[str] = Field(default_factory=list)

    def add_trace(self, message: str) -> None:
        self.trace.append(message)