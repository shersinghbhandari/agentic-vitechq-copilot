class ChunkingService:

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ) -> list[str]:

        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start = end - chunk_overlap

            if start < 0:
                start = 0

            if start >= text_length:
                break

        return chunks