from abc import ABC, abstractmethod
from app.rag.models.raw_document import RawDocument


class BaseExtractor(ABC):

    @abstractmethod
    def extract_text(self, raw_document: RawDocument) -> str:
        pass