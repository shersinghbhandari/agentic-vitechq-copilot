# backend/app/agents/retrieval/vector_search_service.py

from sqlalchemy import text
from sqlalchemy.orm import Session

from langchain_openai import OpenAIEmbeddings


class VectorSearchService:
    """
    Architectural purpose:
    Centralizes vector DB search behind one service boundary.
    """

    def __init__(self, db: Session):
        self.db = db
        self.embeddings = OpenAIEmbeddings()

    def search(
        self,
        query: str,
        tenant_id: str,
        limit: int = 5,
    ) -> list[str]:
        query_embedding = self.embeddings.embed_query(query)

        embedding_value = (
            "["
            + ",".join(str(value) for value in query_embedding)
            + "]"
        )

        sql = text(
            """
            SELECT
                chunk_text
            FROM document_chunks
            WHERE tenant_id = :tenant_id
              AND embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """
        )

        rows = self.db.execute(
            sql,
            {
                "tenant_id": tenant_id,
                "embedding": embedding_value,
                "limit": limit,
            },
        ).fetchall()

        return [
            row.chunk_text
            for row in rows
            if row.chunk_text
        ]