from app.rag.extractors.extractor_factory import (
    ExtractorFactory,
)
from app.rag.models.raw_document import RawDocument


class ExtractionService:
    """
    Centralized extraction orchestration.

    Responsibilities:
    - defensive validation
    - extractor resolution
    - normalized extraction flow

    Future:
    - stream-based extraction
    - async/distributed workers
    - object-storage integration
    """

    def extract(
        self,
        raw_document: RawDocument,
    ) -> str:

        if not raw_document:
            raise ValueError("raw_document is required")

        if not raw_document.file_type:
            raise ValueError(
                "file_type is required for extraction"
            )

        # Preferred distributed-safe extraction
        has_content_source = any([
            raw_document.content,
            raw_document.local_path,
            raw_document.storage_uri,
        ])

        if not has_content_source:

            raise ValueError(
                f"No content source available for: "
                f"{raw_document.file_name}"
            )

        extractor = (
            ExtractorFactory.get_extractor(
                raw_document.file_type
            )
        )

        extracted_text = (
            extractor.extract_text(raw_document)
        )

        if not extracted_text:
            raise ValueError(
                f"No text extracted from: "
                f"{raw_document.file_name}"
            )

        extracted_text = extracted_text.strip()

        if not extracted_text:
            raise ValueError(
                f"Extracted text is empty for: "
                f"{raw_document.file_name}"
            )

        return extracted_text