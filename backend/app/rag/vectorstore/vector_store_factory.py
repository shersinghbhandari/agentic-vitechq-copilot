from sqlalchemy.orm import Session

from app.core.config import settings
from app.rag.vectorstore.pgvector_store import PgVectorStore


class VectorStoreFactory:

    @staticmethod
    def get_vector_store(db: Session):
        provider = settings.VECTOR_STORE_PROVIDER.lower()

        if provider == "pgvector":
            return PgVectorStore(db)

        raise ValueError(f"Unsupported vector store provider: {provider}")