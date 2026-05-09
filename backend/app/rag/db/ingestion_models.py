import uuid

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    tenant_id = Column(String(100), nullable=False)

    uploaded_by = Column(String(255), nullable=True)
    correlation_id = Column(String(255), nullable=True)

    status = Column(
        String(50),
        nullable=False,
        default="PENDING",
    )

    stage = Column(
        String(100),
        nullable=True,
        default="UPLOAD",
    )

    total_chunks = Column(Integer, default=0)
    processed_chunks = Column(Integer, default=0)

    error_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)

    error_message = Column(Text, nullable=True)

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
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


class IngestionError(Base):
    __tablename__ = "ingestion_errors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ingestion_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    tenant_id = Column(String(100), nullable=False)

    correlation_id = Column(String(255), nullable=True)

    stage = Column(String(100), nullable=False)

    error_message = Column(Text, nullable=False)

    stack_trace = Column(Text, nullable=True)

    retry_count = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )