from sqlalchemy.orm import Session

from app.rag.db.ingestion_models import IngestionJob


class IngestionJobRepository:

    def create_job(
        self,
        db: Session,
        document_id,
        tenant_id: str,
        uploaded_by: str,
        correlation_id: str,
        status: str = "REGISTERED",
        stage: str = "UPLOAD",
    ) -> IngestionJob:

        job = IngestionJob(
            document_id=document_id,
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            correlation_id=correlation_id,
            status=status,
            stage=stage,
        )
        db.add(job)
        # flush gets DB-generated values immediately
        # without committing transaction
        db.flush()
        # optional but safer when UUID/default values
        db.refresh(job)
        return job