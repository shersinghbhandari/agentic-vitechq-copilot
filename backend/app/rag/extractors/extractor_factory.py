from app.rag.extractors.text_extractor import TextExtractor
from app.rag.extractors.code_extractor import CodeExtractor
from app.rag.extractors.pdf_extractor import PdfExtractor
from app.rag.extractors.docx_extractor import DocxExtractor
from app.rag.extractors.excel_extractor import ExcelExtractor


class ExtractorFactory:

    @staticmethod
    def get_extractor(file_type: str):
        file_type = file_type.lower()

        if file_type in ["txt", "csv", "md"]:
            return TextExtractor()

        if file_type in ["java", "sql", "py"]:
            return CodeExtractor()

        if file_type == "pdf":
            return PdfExtractor()

        if file_type == "docx":
            return DocxExtractor()

        if file_type in ["xlsx", "xls"]:
            return ExcelExtractor()

        raise ValueError(f"No extractor implemented for file type: {file_type}")