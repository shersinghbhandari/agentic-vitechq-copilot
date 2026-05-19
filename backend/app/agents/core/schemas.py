# backend/app/agents/core/schemas.py

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str

    tenant_id: str = "default_tenant"
    uploaded_by: str = "anonymous"
    correlation_id: str | None = None

    conversation_history: list[dict[str, str]] = Field(default_factory=list)

    user_context: dict[str, Any] = Field(default_factory=dict)
    metadata_context: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    answer: str | None

    correlation_id: str

    refined_query: str | None = None
    intent: str | None = None
    domain: str | None = None

    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)

    selected_source: str | None = None

    retrieval_required: bool = True
    retrieval_strategy: str = "HYBRID"

    retrieved_context_count: int = 0

    validation_status: str = "NOT_VALIDATED"

    validation_errors: list[str] = Field(default_factory=list)

    trace: list[str] = Field(default_factory=list)