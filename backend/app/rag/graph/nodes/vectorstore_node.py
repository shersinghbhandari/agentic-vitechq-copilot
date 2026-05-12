from sqlalchemy.orm import Session

from app.core.trace_logger import TraceLogger
from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.graph.tracing.trace_context_factory import build_trace_context
from app.rag.vectorstore.vector_store_factory import VectorStoreFactory


class VectorStoreNode:
    """
    Backward-compatible vector store node.

    Old flow:
    - saves chunks without embeddings

    New flow:
    - saves chunks with embeddings when state["embeddings"] exists
    """

    def __init__(self, db: Session):
        self.db = db

    def __call__(self, state: IngestionState) -> IngestionState:
        ctx = build_trace_context(state)

        chunks = state.get("chunks", [])
        embeddings = state.get("embeddings")

        TraceLogger.info(
            ctx,
            f"Vector indexing started. chunks={len(chunks)}, has_embeddings={embeddings is not None}",
        )

        vector_store = VectorStoreFactory.get_vector_store(self.db)

        indexed_count = vector_store.add_documents(
            documents=chunks,
            embeddings=embeddings,
        )

        state["processed_chunks"] = indexed_count
        state["stage"] = "VECTOR_INDEX"

        TraceLogger.info(
            ctx,
            f"Vector indexing completed. indexed_chunks={indexed_count}",
        )

        return state