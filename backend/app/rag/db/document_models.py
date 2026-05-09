import uuid

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_uri = Column(Text, nullable=False)

    file_name = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)

    checksum = Column(String(128), nullable=False)

    uploaded_by = Column(String(255), nullable=True)

    status = Column(
        String(50),
        nullable=False,
        default="UPLOADED",
    )

    metadata_json = Column(
        "metadata",
        JSONB,
        nullable=True,
        default=dict,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    tenant_id = Column(String(100), nullable=False)

    metadata_key = Column(String(150), nullable=False)
    metadata_value = Column(Text, nullable=False)

    metadata_type = Column(
        String(50),
        nullable=False,
        default="STRING",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    tenant_id = Column(String(100), nullable=False)

    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)

    embedding = Column(Vector(384), nullable=True)

    metadata_json = Column(
        "metadata",
        JSONB,
        nullable=True,
        default=dict,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )