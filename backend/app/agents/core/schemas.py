from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    tenant_id: str = "default_tenant"
    uploaded_by: Optional[str] = None


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    file_name: Optional[str] = None


class ChatResponse(BaseModel):
    query: str
    refined_query: Optional[str]
    answer: str
    selected_source: Optional[str]
    citations: List[Citation]
    retrieved_context_count: int
    validation_status: str
    validation_message: Optional[str]
    correlation_id: str