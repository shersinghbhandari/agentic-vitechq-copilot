from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class RawDocument:
    """
    Canonical raw document contract used across the ingestion pipeline.

    Architectural Purpose
    ---------------------
    This model represents the original uploaded/source document
    BEFORE extraction, chunking, embedding, or indexing.

    This object flows through:
        Loader -> Extractor -> Chunking -> Embedding -> Vector Indexing

    Design Principles
    -----------------
    1. Cloud / Distributed Safe
       - Supports in-memory byte processing.
       - Avoids hard dependency on local filesystem paths.

    2. Backward Compatible
       - local_path is still supported for local development
         and legacy extractors.

    3. Future Extensible
       - storage_uri supports future S3 / Blob Storage integration.
       - metadata supports arbitrary ingestion enrichment.

    4. Stateless Processing Friendly
       - content bytes allow workers/containers/functions
         to process documents without relying on shared disk.

    Future Production Direction
    ---------------------------
    Production deployments should gradually move toward:
        storage_uri + streaming/bytes processing

    instead of:
        local filesystem dependency.
    """

    # Document identity
    file_name: str
    file_type: str

    # Source information
    # Example: UPLOAD / S3 / CONFLUENCE
    source_type: str
    source_uri: str

    # Preferred production-safe content
    # Future: stream/S3-based ingestion
    content: Optional[bytes] = None

    # Local development fallback
    local_path: Optional[str] = None

    # Future cloud/object storage support
    # Example: s3://bucket/file.pdf
    storage_uri: Optional[str] = None

    # Content metadata
    content_type: Optional[str] = None
    file_size: Optional[int] = None

    # Duplicate detection / audit tracking
    checksum: Optional[str] = None

    # Flexible ingestion enrichment
    # Example: tenant_id / source metadata / custom tags
    metadata: Dict[str, Any] = field(default_factory=dict)