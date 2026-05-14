from dataclasses import dataclass


@dataclass(frozen=True)
class LlmModelConfig:
    provider: str
    model: str
    temperature: float
    max_retries: int
    timeout_seconds: int