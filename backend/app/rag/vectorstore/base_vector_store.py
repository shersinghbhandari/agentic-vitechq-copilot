from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document as LangChainDocument


class BaseVectorStore(ABC):

    @abstractmethod
    def add_documents(
        self,
        documents: List[LangChainDocument],
        embeddings: List[list[float]],
    ) -> int:
        pass