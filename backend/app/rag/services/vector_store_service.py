class VectorStoreService:
    """
    Placeholder for pgvector insert.

    Later this will save:
    - document_id
    - tenant_id
    - chunk_text
    - chunk_index
    - embedding
    - metadata
    """

    def save_vectors(
        self,
        document_id,
        tenant_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:

        for index, chunk in enumerate(chunks):
            print(
                f"Saving vector: document_id={document_id}, "
                f"tenant_id={tenant_id}, chunk_index={index}, "
                f"chunk_length={len(chunk)}"
            )