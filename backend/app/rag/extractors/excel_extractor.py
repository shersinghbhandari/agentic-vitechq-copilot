from openpyxl import load_workbook

from app.rag.extractors.base_extractor import BaseExtractor
from app.rag.models.raw_document import RawDocument


class ExcelExtractor(BaseExtractor):
    """
    Extracts basic readable text from XLSX files.
    XLS support is not implemented yet.
    """

    def extract_text(self, raw_document: RawDocument) -> str:
        if raw_document.file_type.lower() == "xls":
            raise ValueError(
                "XLS extraction is not implemented yet. "
                "Please upload XLSX for now."
            )

        workbook = load_workbook(
            filename=raw_document.local_path,
            read_only=True,
            data_only=True
        )

        text_parts = []

        for sheet in workbook.worksheets:
            text_parts.append(f"\n--- Sheet: {sheet.title} ---")

            for row in sheet.iter_rows(values_only=True):
                row_values = []

                for cell in row:
                    if cell is not None:
                        row_values.append(str(cell).strip())

                if row_values:
                    text_parts.append(" | ".join(row_values))

        workbook.close()

        extracted_text = "\n".join(text_parts).strip()

        if not extracted_text:
            raise ValueError(
                f"No text extracted from Excel file: {raw_document.file_name}"
            )

        return extracted_text