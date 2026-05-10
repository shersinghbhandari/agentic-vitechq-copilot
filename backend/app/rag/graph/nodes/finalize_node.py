from sqlalchemy.orm import Session

from app.rag.enums.job_status import JobStatus
from app.rag.enums.job_stage import JobStage
from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.jobs.ingestion_job_service import IngestionJobService

#Marks job complete
class FinalizeNode:
    def __init__(self, db: Session):
        self.db = db
        self.job_service = IngestionJobService()

    def __call__(self, state: IngestionState) -> IngestionState:
        self.job_service.update_status(
            db=self.db,
            job_id=state["job_id"],
            status=JobStatus.COMPLETED,
            stage=JobStage.FINALIZATION,
        )

        self.job_service.update_chunk_progress(
            db=self.db,
            job_id=state["job_id"],
            total_chunks=state.get("total_chunks", 0),
            processed_chunks=state.get("processed_chunks", 0),
        )

        state["status"] = "COMPLETED"
        state["stage"] = "FINALIZATION"

        return state