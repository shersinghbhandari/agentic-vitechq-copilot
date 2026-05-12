from sqlalchemy.orm import Session

from app.core.trace_logger import TraceLogger
from app.rag.embeddings.embedding_service import EmbeddingService
from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.graph.tracing.trace_context_factory import build_trace_context


class EmbeddingNode:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()

    def __call__(self, state: IngestionState) -> IngestionState:
        ctx = build_trace_context(state)

        chunks = state.get("chunks", [])

        TraceLogger.info(
            ctx,
            f"Embedding started. chunks={len(chunks)}",
        )

        texts = [chunk.page_content for chunk in chunks]

        embeddings = self.embedding_service.embed_texts(texts)

        state["embeddings"] = embeddings
        state["stage"] = "EMBEDDING"

        TraceLogger.info(
            ctx,
            f"Embedding completed. embeddings={len(embeddings)}",
        )

        return state