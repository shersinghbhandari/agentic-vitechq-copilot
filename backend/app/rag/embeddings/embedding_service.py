from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Embedding provider abstraction.

    Current:
    - Local sentence-transformers model
    - 384 dimensions

    Future:
    - AWS Bedrock Titan
    - OpenAI
    - Ollama
    """

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()