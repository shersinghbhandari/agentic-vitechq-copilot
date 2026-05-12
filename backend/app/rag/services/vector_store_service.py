from app.rag.db.document_models import DocumentChunk


class VectorStoreService:

    def __init__(self, db):
        self.db = db

    def save_vectors(
        self,
        document_id,
        tenant_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> int:

        saved_count = 0

        for index, chunk in enumerate(chunks):
            embedding = embeddings[index] if embeddings else None

            db_chunk = DocumentChunk(
                document_id=document_id,
                tenant_id=tenant_id,
                chunk_index=index,
                chunk_text=chunk,
                embedding=embedding,
                metadata_json={}
            )

            self.db.add(db_chunk)
            saved_count += 1

        self.db.commit()
        return saved_count