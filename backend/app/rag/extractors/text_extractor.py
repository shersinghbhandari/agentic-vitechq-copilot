from app.rag.extractors.base_extractor import BaseExtractor
from app.rag.models.raw_document import RawDocument


class TextExtractor(BaseExtractor):

    def extract_text(self, raw_document: RawDocument) -> str:
        with open(raw_document.local_path, "r", encoding="utf-8") as file:
            return file.read()