# backend/app/agents/core/llm_factory.py

import os

from langchain_openai import ChatOpenAI


class LlmFactory:
    """
    Future direction:
    Replace this factory to support Bedrock, Ollama, Groq, or fallback models.
    """

    @staticmethod
    def create_chat_model():
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
        )