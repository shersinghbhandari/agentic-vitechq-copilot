from typing import List

from sqlalchemy.orm import Session
from langchain_core.documents import Document as LangChainDocument

from app.rag.models.document_models import DocumentChunk
from app.rag.vectorstore.base_vector_store import BaseVectorStore


class PgVectorStore(BaseVectorStore):

    def __init__(self, db: Session):
        self.db = db

    def add_documents(
        self,
        documents: List[LangChainDocument],
        embeddings: List[list[float]],
    ) -> int:

        if len(documents) != len(embeddings):
            raise ValueError("Documents and embeddings count mismatch")

        saved_count = 0

        for index, document in enumerate(documents):
            metadata = document.metadata or {}

            chunk = DocumentChunk(
                document_id=metadata["document_id"],
                tenant_id=metadata["tenant_id"],
                chunk_index=metadata.get("chunk_index", index),
                chunk_text=document.page_content,
                embedding=embeddings[index],
                metadata_json=metadata,
            )

            self.db.add(chunk)
            saved_count += 1

        self.db.commit()

        return saved_count