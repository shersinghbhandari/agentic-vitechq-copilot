# app/rag/models/staged_document.py

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class StagedDocument:
    original_filename: str
    local_path: str
    quarantine_path: str
    approved_path: str
    content_type: str
    file_size: int
    checksum: str
    staged_at: datetime