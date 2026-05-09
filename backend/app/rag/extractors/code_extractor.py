from app.rag.extractors.base_extractor import BaseExtractor
from app.rag.models.raw_document import RawDocument


class CodeExtractor(BaseExtractor):

    def extract_text(self, raw_document: RawDocument) -> str:
        with open(
            raw_document.local_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:
            return file.read()