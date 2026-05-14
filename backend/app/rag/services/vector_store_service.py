from app.rag.db.document_models import DocumentChunk


class VectorStoreService:

    def __init__(self, db):
        self.db = db

    def save_vectors(
        self,
        document_id,
        tenant_id: str,
        chunks: list[str],
        embeddings: list[list[float]] | None = None,
    ) -> int:

        if embeddings is not None and len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks and embeddings count mismatch. "
                f"chunks={len(chunks)}, embeddings={len(embeddings)}"
            )

        db_chunks = []

        for index, chunk in enumerate(chunks):
            embedding = embeddings[index] if embeddings else None

            db_chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    tenant_id=tenant_id,
                    chunk_index=index,
                    chunk_text=chunk,
                    embedding=embedding,
                    metadata_json={},
                )
            )

        self.db.add_all(db_chunks)

        # Flush only. Commit is handled by transactional_session().
        self.db.flush()
        return len(db_chunks)