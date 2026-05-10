import traceback
from sqlalchemy.orm import Session

from app.rag.enums.job_status import JobStatus
from app.rag.enums.job_stage import JobStage
from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.jobs.ingestion_job_service import IngestionJobService
from app.rag.db.repositories.ingestion_error_repository import IngestionErrorRepository


class ErrorNode:
    def __init__(self, db: Session):
        self.db = db
        self.job_service = IngestionJobService()
        self.error_repository = IngestionErrorRepository()

    def __call__(
        self,
        state: IngestionState,
        exception: Exception,
    ) -> IngestionState:

        error_message = str(exception)

        self.job_service.update_status(
            db=self.db,
            job_id=state["job_id"],
            status=JobStatus.FAILED,
            stage=JobStage(state.get("stage", "FINALIZATION"))
            if state.get("stage") in JobStage.__members__
            else JobStage.FINALIZATION,
            error_message=error_message,
        )

        self.error_repository.create_error(
            db=self.db,
            job_id=state["job_id"],
            document_id=state["document_id"],
            tenant_id=state["tenant_id"],
            correlation_id=state.get("correlation_id"),
            stage=state.get("stage", "UNKNOWN"),
            error_message=error_message,
            stack_trace=traceback.format_exc(),
            retry_count=0,
        )

        state["status"] = "FAILED"
        state["error_message"] = error_message

        return state