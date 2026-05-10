from app.core.database import SessionLocal
from app.core.trace_logger import TraceContext, TraceLogger

from app.rag.services.ingestion_pipeline_service import (
    IngestionPipelineService,
)


def run_ingestion_job(
    document_id,
    job_id,
    correlation_id: str,
    uploaded_by: str,
    tenant_id: str,
) -> None:

    db = SessionLocal()

    trace_ctx = TraceContext(
        correlation_id=correlation_id,
        uploaded_by=uploaded_by,
        tenant_id=tenant_id,
        request_name="DOCUMENT_INGESTION",
        document_id=str(document_id),
        job_id=str(job_id),
    )

    try:
        TraceLogger.info(
            trace_ctx,
            "Background ingestion worker started.",
        )

        pipeline_service = IngestionPipelineService()

        pipeline_service.process(
            db=db,
            document_id=document_id,
            job_id=job_id,
            correlation_id=correlation_id,
        )

        TraceLogger.info(
            trace_ctx,
            "Background ingestion worker completed.",
        )

    except Exception as ex:

        TraceLogger.error(
            trace_ctx,
            f"Background ingestion worker failed. error={str(ex)}",
        )

        raise

    finally:
        db.close()