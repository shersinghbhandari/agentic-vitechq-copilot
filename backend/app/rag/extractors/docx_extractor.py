from docx import Document

from app.rag.models.raw_document import RawDocument


class DocxExtractor:

    @staticmethod
    def extract_text(raw_document: RawDocument) -> str:

        document = Document(raw_document.local_path)

        extracted_parts = []

        # -----------------------------
        # Paragraph extraction
        # -----------------------------
        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                extracted_parts.append(text)

        # -----------------------------
        # Table extraction
        # -----------------------------
        for table in document.tables:
            for row in table.rows:
                row_values = []

                for cell in row.cells:
                    cell_text = cell.text.strip()

                    if cell_text:
                        row_values.append(cell_text)

                if row_values:
                    extracted_parts.append(" | ".join(row_values))

        extracted_text = "\n".join(extracted_parts).strip()

        # -----------------------------
        # Graceful fallback
        # -----------------------------
        if not extracted_text:
            return (
                f"[WARN] No readable text extracted "
                f"from DOCX file: {raw_document.file_name}"
            )

        return extracted_text