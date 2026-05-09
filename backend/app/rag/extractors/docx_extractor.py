from docx import Document

from app.rag.extractors.base_extractor import BaseExtractor
from app.rag.models.raw_document import RawDocument


class DocxExtractor(BaseExtractor):
    """
    Extracts text from DOCX paragraphs and tables.
    """

    def extract_text(self, raw_document: RawDocument) -> str:
        document = Document(raw_document.local_path)

        text_parts = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if text:
                text_parts.append(text)

        for table_index, table in enumerate(document.tables, start=1):
            text_parts.append(f"\n--- Table {table_index} ---")

            for row in table.rows:
                row_values = []

                for cell in row.cells:
                    cell_text = cell.text.strip()
                    row_values.append(cell_text)

                text_parts.append(" | ".join(row_values))

        extracted_text = "\n".join(text_parts).strip()

        if not extracted_text:
            raise ValueError(
                f"No text extracted from DOCX: {raw_document.file_name}"
            )

        return extracted_text