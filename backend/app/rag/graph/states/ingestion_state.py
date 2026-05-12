from typing import Any, Dict, List, Optional, TypedDict
from uuid import UUID

from langchain_core.documents import Document as LangChainDocument

#shared Langgraph state
class IngestionState(TypedDict, total=False):
    tenant_id: str
    uploaded_by: str
    correlation_id: str
    request_name: str

    document_id: UUID
    job_id: UUID

    file_name: str
    file_type: str
    source_uri: str
    local_path: str

    raw_text: str

    langchain_documents: List[LangChainDocument]
    chunks: List[LangChainDocument]
    embeddings: List[list[float]]

    total_chunks: int
    processed_chunks: int

    status: str
    stage: str
    error_message: Optional[str]

    metadata: Dict[str, Any]