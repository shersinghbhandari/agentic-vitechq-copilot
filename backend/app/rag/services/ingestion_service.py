from app.core.db_session import transactional_session
from app.rag.graph.ingestion_graph import IngestionGraph


class IngestionService:

    def run_ingestion(self, document_id: str, job_id: str) -> None:
        with transactional_session() as db:
            graph = IngestionGraph(db=db)
            graph.run({
                "document_id": document_id,
                "job_id": job_id,
            })