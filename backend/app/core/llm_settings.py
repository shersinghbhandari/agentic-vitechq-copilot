from pydantic_settings import BaseSettings


class LlmSettings(BaseSettings):
    LLM_DEFAULT_PROVIDER: str = "openai"
    LLM_DEFAULT_MODEL: str = "gpt-4o-mini"
    LLM_DEFAULT_TEMPERATURE: float = 0.0
    LLM_DEFAULT_MAX_RETRIES: int = 2
    LLM_DEFAULT_TIMEOUT_SECONDS: int = 30

    LLM_QUERY_ANALYZER_PROVIDER: str | None = None
    LLM_QUERY_ANALYZER_MODEL: str | None = None
    LLM_QUERY_ANALYZER_TEMPERATURE: float | None = None

    LLM_RETRIEVAL_PLANNER_PROVIDER: str | None = None
    LLM_RETRIEVAL_PLANNER_MODEL: str | None = None
    LLM_RETRIEVAL_PLANNER_TEMPERATURE: float | None = None

    LLM_ANSWER_GENERATOR_PROVIDER: str | None = None
    LLM_ANSWER_GENERATOR_MODEL: str | None = None
    LLM_ANSWER_GENERATOR_TEMPERATURE: float | None = None

    LLM_CITATION_VALIDATOR_PROVIDER: str | None = None
    LLM_CITATION_VALIDATOR_MODEL: str | None = None
    LLM_CITATION_VALIDATOR_TEMPERATURE: float | None = None

    QUERY_ANALYZER_USE_LLM: bool = True
    QUERY_ANALYZER_LLM_CONFIDENCE_THRESHOLD: float = 0.70
    QUERY_ANALYZER_PASS_CONVERSATION_CONTEXT: bool = True
    QUERY_ANALYZER_PASS_USER_CONTEXT: bool = True
    QUERY_ANALYZER_MAX_HISTORY_MESSAGES: int = 6
    QUERY_ANALYZER_INCLUDE_TRACE_CONTEXT: bool = True
    QUERY_ANALYZER_ENABLE_METADATA_FILTERS: bool = True

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    AWS_REGION: str = "us-east-1"

    class Config:
        env_file = ".env"
        extra = "ignore"


llm_settings = LlmSettings()