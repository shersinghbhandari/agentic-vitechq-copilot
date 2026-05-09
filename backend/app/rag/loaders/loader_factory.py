from app.rag.loaders.upload_loader import UploadDocumentLoader
from app.rag.loaders.base_loader import BaseDocumentLoader


class LoaderFactory:
    """
    Factory to return correct loader.

    Week 1:
    - UPLOAD

    Future:
    - S3
    - JIRA
    - CONFLUENCE
    """

    @staticmethod
    def get_loader(source_type: str) -> BaseDocumentLoader:
        source_type = source_type.upper()

        if source_type == "UPLOAD":
            return UploadDocumentLoader()

        raise ValueError(f"Unsupported source type: {source_type}")