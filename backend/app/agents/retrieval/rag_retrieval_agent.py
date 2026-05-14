from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agents.core.agent_context import AgentContext


class RagRetrievalAgent:

    def __init__(
        self,
        db: Session,
        max_results: int = 5,
    ):
        self.db = db
        self.max_results = max_results

    def retrieve(self, context: AgentContext) -> AgentContext:
        if context.selected_source != "RAG_VECTOR_DB":
            context.retrieved_context = []
            return context

        if not context.keywords:
            context.retrieved_context = []
            return context

        rows = self._search_by_keywords(context)

        context.retrieved_context = [
            {
                "chunk_id": str(row["chunk_id"]),
                "document_id": str(row["document_id"]),
                "chunk_index": row["chunk_index"],
                "chunk_text": row["chunk_text"],
                "file_name": row["file_name"],
                "metadata": {},
            }
            for row in rows
        ]

        return context

    def _search_by_keywords(self, context: AgentContext):
        conditions = []
        params = {
            "tenant_id": context.tenant_id,
            "uploaded_by": context.uploaded_by,
            "limit": self.max_results,
        }

        for index, keyword in enumerate(context.keywords):
            key = f"keyword_{index}"
            conditions.append(f"dc.chunk_text ILIKE :{key}")
            params[key] = f"%{keyword}%"

        where_clause = " OR ".join(conditions)

        query = text(
            f"""
            SELECT
                dc.id AS chunk_id,
                dc.document_id AS document_id,
                dc.chunk_index AS chunk_index,
                dc.chunk_text AS chunk_text,
                d.file_name AS file_name
            FROM document_chunks dc
            JOIN documents d
                ON d.id = dc.document_id
            WHERE dc.tenant_id = :tenant_id
              AND ({where_clause})
              AND (
                    :uploaded_by IS NULL
                    OR d.uploaded_by = :uploaded_by
              )
            ORDER BY dc.chunk_index ASC
            LIMIT :limit
            """
        )

        return self.db.execute(query, params).mappings().all()