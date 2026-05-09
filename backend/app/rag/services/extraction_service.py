from app.rag.extractors.extractor_factory import ExtractorFactory
from app.rag.models.raw_document import RawDocument


class ExtractionService:

    def extract(self, raw_document: RawDocument) -> str:

        extractor = ExtractorFactory.get_extractor(
            raw_document.file_type
        )

        extracted_text = extractor.extract_text(raw_document)

        if not extracted_text.strip():
            raise ValueError(
                f"No text extracted from: {raw_document.file_name}"
            )

        return extracted_text