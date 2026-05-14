from abc import ABC, abstractmethod

from app.rag.models.raw_document import RawDocument


class BaseExtractor(ABC):
    """
    Stateless extraction contract.

    Supports:
    - in-memory bytes extraction
    - local filesystem extraction
    - future object-storage extraction
    """

    @abstractmethod
    def extract_text(self, raw_document: RawDocument) -> str:
        """
        Preferred extraction order:
        1. content
        2. local_path
        3. storage_uri
        """
        pass