from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentContext:
    query: str
    tenant_id: str
    uploaded_by: Optional[str]
    correlation_id: str

    refined_query: Optional[str] = None
    intent: Optional[str] = None
    selected_source: Optional[str] = None

    keywords: List[str] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)

    retrieved_context: List[Dict[str, Any]] = field(default_factory=list)
    integrated_context: Optional[str] = None

    answer: Optional[str] = None
    citations: List[Dict[str, Any]] = field(default_factory=list)

    validation_status: str = "NOT_VALIDATED"
    validation_message: Optional[str] = None