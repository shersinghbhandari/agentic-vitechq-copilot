from app.rag.extractors.base_extractor import BaseExtractor
from app.rag.models.raw_document import RawDocument


class CodeExtractor(BaseExtractor):
    """
    Source-code extractor.

    Preferred:
    - byte-stream extraction
    - stateless processing

    Future:
    - object-storage streaming
    """

    def extract_text(
        self,
        raw_document: RawDocument,
    ) -> str:

        if not raw_document:
            raise ValueError("raw_document is required")

        # Preferred distributed-safe extraction
        if raw_document.content:

            return raw_document.content.decode(
                "utf-8",
                errors="ignore",
            ).strip()

        # Local dev fallback
        if raw_document.local_path:

            with open(
                raw_document.local_path,
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as file:

                return file.read().strip()

        # Future: storage_uri stream extraction
        if raw_document.storage_uri:
            raise NotImplementedError(
                "storage_uri extraction not implemented yet"
            )

        raise ValueError(
            f"No extractable content available for file: "
            f"{raw_document.file_name}"
        )