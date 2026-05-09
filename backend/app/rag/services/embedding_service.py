class EmbeddingService:
    """
    Placeholder for Day 3.

    Later:
    - AWS Bedrock Titan Embeddings
    - OpenAI embeddings
    - local embedding model
    """

    def create_embeddings(self, chunks: list[str]) -> list[list[float]]:
        return [[0.0] * 1536 for _ in chunks]