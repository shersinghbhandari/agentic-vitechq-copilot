from sqlalchemy.orm import Session

from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.db.repositories.chunk_repository import ChunkRepository

#Saves chunks
class VectorStoreNode:
    """
    For now this stores chunks without embeddings.
    Embedding/vector insertion can be added next.
    """

    def __init__(self, db: Session):
        self.db = db
        self.chunk_repository = ChunkRepository()

    def __call__(self, state: IngestionState) -> IngestionState:
        chunks = state["chunks"]

        for chunk in chunks:
            self.chunk_repository.create_chunk(
                db=self.db,
                document_id=state["document_id"],
                tenant_id=state["tenant_id"],
                chunk_index=chunk.metadata["chunk_index"],
                chunk_text=chunk.page_content,
                metadata_json=chunk.metadata,
            )

        state["processed_chunks"] = len(chunks)
        state["stage"] = "VECTOR_STORE"

        return state