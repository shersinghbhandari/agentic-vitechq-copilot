from sqlalchemy.orm import Session

from app.rag.graph.orchestrators.ingestion_orchestrator import (
    IngestionOrchestrator,
)

from app.rag.db.document_models import Document
from app.rag.db.ingestion_models import IngestionJob


class IngestionService:
    """
    Entry point for document ingestion.

    Called by:
    - document_routes.py

    Responsibilities:
    - Prepare initial LangGraph state
    - Start ingestion orchestrator
    """

    def __init__(self, db: Session):
        self.db = db

    def run_ingestion(
        self,
        document: Document,
        job: IngestionJob,
        correlation_id: str,
    ):

        initial_state = {
            "tenant_id": document.tenant_id,
            "uploaded_by": document.uploaded_by,
            "correlation_id": correlation_id,

            "document_id": document.id,
            "job_id": job.id,

            "file_name": document.file_name,
            "file_type": document.file_type,

            "source_uri": document.source_uri,

            # IMPORTANT:
            # Currently uploaded file path is stored here
            "local_path": document.source_uri,

            "status": job.status,
            "stage": job.stage or "UPLOAD",

            "metadata": document.metadata_json or {},
        }

        orchestrator = IngestionOrchestrator(self.db)

        return orchestrator.run(initial_state)