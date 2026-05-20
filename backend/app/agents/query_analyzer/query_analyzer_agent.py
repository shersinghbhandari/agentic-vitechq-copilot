# backend/app/agents/query_analyzer/query_analyzer_agent.py

import json

from langchain_core.prompts import ChatPromptTemplate

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.core.llm_factory import LlmFactory


class QueryAnalyzerAgent(BaseAgent):
    """
    Converts raw user input into structured orchestration state.

    Architectural Purpose
    ---------------------
    Responsible for:
        - query refinement
        - intent detection
        - domain classification
        - keyword extraction
        - entity extraction
        - retrieval decisioning

    Design Principles
    -----------------
    1. LLM-driven semantic understanding
       - Better than regex/rule-only parsing.

    2. Structured orchestration contract
       - Produces deterministic downstream state.

    3. Retrieval-aware routing
       - Determines whether RAG lookup is needed.

    4. Fail-safe execution
       - Graceful fallback if LLM parsing fails.
    """

    name = "QueryAnalyzerAgent"

    def __init__(self):
        self.llm = LlmFactory.create_chat_model()

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Analyze incoming user query.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a query analysis agent.

Return only valid JSON.

Fields:
- refined_query
- intent
- domain
- keywords
- entities
- retrieval_required

Rules:
- Fix typos.
- Preserve original meaning.
- Use retrieval_required=true if answer needs documents, DB, or project context.
""",
                ),
                ("human", "{query}"),
            ]
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "query": context.query,
            }
        )

        # Centralized LLM observability.
        self.track_token_usage(
            context,
            response,
        )

        try:
            data = json.loads(
                response.content
            )

        except Exception:
            # Fail-safe fallback for malformed LLM output.
            data = {
                "refined_query": context.query,
                "intent": "QUESTION_ANSWERING",
                "domain": "GENERAL",
                "keywords": [],
                "entities": [],
                "retrieval_required": True,
            }

        context.refined_query = data.get(
            "refined_query",
            context.query,
        )

        context.intent = data.get(
            "intent",
            "QUESTION_ANSWERING",
        )

        context.domain = data.get(
            "domain",
            "GENERAL",
        )

        context.keywords = data.get(
            "keywords",
            [],
        )

        context.entities = data.get(
            "entities",
            [],
        )

        context.retrieval_required = data.get(
            "retrieval_required",
            True,
        )

        self.trace(
            context,
            (
                "Query analyzed. "
                f"intent={context.intent}, "
                f"domain={context.domain}, "
                f"retrieval_required="
                f"{context.retrieval_required}."
            ),
        )

        return context