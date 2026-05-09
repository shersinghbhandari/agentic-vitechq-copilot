from sqlalchemy.orm import Session
from app.rag.db.ingestion_models import IngestionJob


class IngestionJobRepository:

    def create_job(
        self,
        db: Session,
        document_id,
        tenant_id: str,
        status: str = "REGISTERED",
    ):
        job = IngestionJob(
            document_id=document_id,
            tenant_id=tenant_id,
            status=status,
        )

        db.add(job)
        db.flush()
        return job