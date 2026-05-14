# backend/app/rag/extractors/pdf_extractor.py

from io import BytesIO

from pypdf import PdfReader

from app.rag.extractors.base_extractor import BaseExtractor
from app.rag.models.raw_document import RawDocument


class PdfExtractor(BaseExtractor):
    """
    PDF extractor.

    Supports:
    - byte-stream ingestion
    - local filesystem fallback

    Future:
    - object-storage streaming
    - OCR fallback pipeline
    """

    def extract_text(
        self,
        raw_document: RawDocument,
    ) -> str:

        if not raw_document:
            raise ValueError("raw_document is required")

        pdf_source = self._build_pdf_source(raw_document)

        try:

            reader = PdfReader(pdf_source)

            text_parts = []

            for page_number, page in enumerate(
                reader.pages,
                start=1,
            ):

                page_text = page.extract_text() or ""

                if page_text.strip():

                    text_parts.append(
                        f"\n\n--- Page {page_number} ---\n"
                        f"{page_text.strip()}"
                    )

            extracted_text = "\n".join(text_parts).strip()

            if not extracted_text:

                raise ValueError(
                    f"No text extracted from PDF: "
                    f"{raw_document.file_name}. "
                    "Scanned PDFs may require OCR pipeline."
                )

            return extracted_text

        except Exception as ex:

            raise ValueError(
                f"Failed to extract PDF file: "
                f"{raw_document.file_name}. "
                f"error={str(ex)}"
            ) from ex

    def _build_pdf_source(
        self,
        raw_document: RawDocument,
    ):

        # Preferred distributed-safe ingestion
        if raw_document.content:

            return BytesIO(raw_document.content)

        # Local dev fallback
        if raw_document.local_path:

            return raw_document.local_path

        # Future: object-storage streaming
        if raw_document.storage_uri:

            raise NotImplementedError(
                "storage_uri PDF extraction "
                "not implemented yet"
            )

        raise ValueError(
            "PDF source missing. "
            "content/local_path/storage_uri required."
        )