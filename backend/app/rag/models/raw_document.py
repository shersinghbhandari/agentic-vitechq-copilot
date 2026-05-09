from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class RawDocument:
    file_name: str
    file_type: str
    source_type: str
    source_uri: str
    local_path: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
