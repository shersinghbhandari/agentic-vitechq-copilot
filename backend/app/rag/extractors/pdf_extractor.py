from pypdf import PdfReader

from app.rag.extractors.base_extractor import BaseExtractor
from app.rag.models.raw_document import RawDocument


class PdfExtractor(BaseExtractor):
    """
    Extracts text from normal text-based PDFs.
    OCR fallback is not implemented yet.
    """

    def extract_text(self, raw_document: RawDocument) -> str:
        text_parts = []

        reader = PdfReader(raw_document.local_path)

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""

            if page_text.strip():
                text_parts.append(
                    f"\n\n--- Page {page_number} ---\n{page_text}"
                )

        extracted_text = "\n".join(text_parts).strip()

        if not extracted_text:
            raise ValueError(
                f"No text extracted from PDF: {raw_document.file_name}. "
                "This may be a scanned PDF and may need OCR."
            )

        return extracted_text