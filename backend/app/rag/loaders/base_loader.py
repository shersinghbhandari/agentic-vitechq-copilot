from abc import ABC, abstractmethod
from app.rag.models.raw_document import RawDocument


class BaseDocumentLoader(ABC):
    """
    Base class for all document loaders.

    Future loaders:
    - S3Loader
    - ConfluenceLoader
    - JiraLoader
    - GitHubLoader
    - SharePointLoader
    """

    @abstractmethod
    async def load(self, *args, **kwargs) -> RawDocument:
        pass