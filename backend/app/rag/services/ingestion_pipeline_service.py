from sqlalchemy.orm import Session

from app.core.trace_logger import TraceContext, TraceLogger
from app.rag.graph.ingestion_graph import IngestionGraph


class IngestionPipelineService:
    """
    Backward-compatible ingestion orchestration wrapper.

    Real orchestration lives in:
    - IngestionGraph

    Future:
    - async workers
    - distributed execution
    - event-driven ingestion
    """

    def __init__(self, db: Session):
        self.db = db

    def process(
        self,
        db: Session,
        document_id,
        job_id,
        tenant_id: str | None = None,
        uploaded_by: str | None = None,
        correlation_id: str | None = None,
    ) -> None:

        ctx = TraceContext(
            correlation_id=correlation_id or "unknown",
            uploaded_by=uploaded_by or "unknown",
            tenant_id=tenant_id or "unknown",
            request_name="INGESTION_PIPELINE",
            document_id=str(document_id),
            job_id=str(job_id),
        )

        TraceLogger.info(
            ctx,
            "Delegating ingestion to IngestionGraph.",
        )

        ingestion_graph = IngestionGraph(db)

        ingestion_graph.run(
            db=db,
            document_id=document_id,
            job_id=job_id,
            correlation_id=correlation_id or "unknown",
            uploaded_by=uploaded_by or "unknown",
            tenant_id=tenant_id or "unknown",
        )

        TraceLogger.info(
            ctx,
            "IngestionGraph execution completed.",
        )