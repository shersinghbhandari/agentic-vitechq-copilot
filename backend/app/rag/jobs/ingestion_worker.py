from app.core.database import SessionLocal
from app.rag.services.ingestion_pipeline_service import IngestionPipelineService


def run_ingestion_job(document_id, job_id) -> None:
    db = SessionLocal()

    try:
        pipeline_service = IngestionPipelineService()
        pipeline_service.process(
            db=db,
            document_id=document_id,
            job_id=job_id,
        )

    finally:
        db.close()