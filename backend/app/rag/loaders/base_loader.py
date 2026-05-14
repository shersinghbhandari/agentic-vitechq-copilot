from abc import ABC, abstractmethod

from app.rag.models.raw_document import RawDocument


class BaseDocumentLoader(ABC):
    """
    Stateless ingestion source contract.

    Current:
    - Upload/UI ingestion
    - Local dev ingestion

    Future:
    - S3
    - Confluence
    - Jira
    - GitHub
    - SharePoint
    - Distributed ingestion workers
    """

    @abstractmethod
    async def load(self, *args, **kwargs) -> RawDocument:
        """
        Returns normalized RawDocument contract.
        """
        pass