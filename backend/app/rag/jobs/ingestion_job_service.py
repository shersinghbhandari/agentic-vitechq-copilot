from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.rag.enums.job_status import JobStatus
from app.rag.enums.job_stage import JobStage
from app.rag.db.ingestion_models import IngestionJob


class IngestionJobService:

    def create_job(
        self,
        db: Session,
        document_id,
        tenant_id: str,
        uploaded_by: str,
        correlation_id: str,
    ) -> IngestionJob:

        job = IngestionJob(
            document_id=document_id,
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            correlation_id=correlation_id,
            status=JobStatus.PENDING.value,
            stage=JobStage.UPLOAD.value,
            total_chunks=0,
            processed_chunks=0,
            error_count=0,
            retry_count=0,
            error_message=None,
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    def update_status(
        self,
        db: Session,
        job_id,
        status: JobStatus,
        stage: JobStage | None = None,
        error_message: str | None = None,
    ) -> IngestionJob:

        job = db.query(IngestionJob).filter(
            IngestionJob.id == job_id
        ).first()

        if not job:
            raise ValueError(f"Ingestion job not found: {job_id}")

        job.status = status.value

        if stage:
            job.stage = stage.value

        job.error_message = error_message

        if status == JobStatus.FAILED:
            job.error_count = (job.error_count or 0) + 1
            job.completed_at = datetime.now(timezone.utc)

        if status == JobStatus.COMPLETED:
            job.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(job)

        return job

    def update_chunk_progress(
        self,
        db: Session,
        job_id,
        total_chunks: int,
        processed_chunks: int,
    ) -> IngestionJob:

        job = db.query(IngestionJob).filter(
            IngestionJob.id == job_id
        ).first()

        if not job:
            raise ValueError(f"Ingestion job not found: {job_id}")

        job.total_chunks = total_chunks
        job.processed_chunks = processed_chunks

        db.commit()
        db.refresh(job)

        return job

    def increment_retry(
        self,
        db: Session,
        job_id,
    ) -> IngestionJob:

        job = db.query(IngestionJob).filter(
            IngestionJob.id == job_id
        ).first()

        if not job:
            raise ValueError(f"Ingestion job not found: {job_id}")

        job.retry_count = (job.retry_count or 0) + 1
        job.status = JobStatus.RETRYING.value

        db.commit()
        db.refresh(job)

        return job