# backend/app/agents/query_analyzer/query_analyzer_agent.py

import json

from langchain_core.prompts import ChatPromptTemplate

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.core.llm_factory import LlmFactory


class QueryAnalyzerAgent(BaseAgent):
    """
    Semantic query analysis orchestration agent.

    Architectural Purpose
    ---------------------
    Converts raw user input into structured
    orchestration metadata for downstream agents.

    This agent is responsible for:
        - query refinement
        - intent detection
        - domain classification
        - keyword extraction
        - entity extraction
        - retrieval decisioning
        - runtime role inference

    Design Principles
    -----------------
    1. Structured orchestration contract
       - Produces deterministic downstream state.

    2. Retrieval-aware analysis
       - Determines whether enterprise retrieval is needed.

    3. Runtime role inference
       - Allows adaptive response specialization.

    4. Fail-safe execution
       - Falls back safely if LLM output is malformed.

    5. Future extensible
       - Supports:
            - query decomposition
            - metadata filters
            - tool planning
            - multi-hop retrieval
            - semantic routing
    """

    name = "QueryAnalyzerAgent"

    def __init__(self):
        self.llm = LlmFactory.create_chat_model()

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Analyze query and populate orchestration metadata.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a query analysis agent.

Return only valid JSON.

Required fields:
- refined_query
- intent
- domain
- keywords
- entities
- retrieval_required
- resolved_role

Role resolution rules:
- If input role is developer, resolved_role must be developer.
- If input role is performance, resolved_role must be performance.
- If input role is analyst, resolved_role must be analyst.
- If input role is architect, resolved_role must be architect.
- If input role is generic, infer the best role from the query.

Available resolved_role values:
- developer
- performance
- analyst
- architect
- generic

Inference examples:
- code, class, API, error, stack trace, implementation -> developer
- latency, throughput, memory, SQL tuning, slow query -> performance
- requirement, business flow, report, process, data meaning -> analyst
- architecture, design, scalability, reliability, trade-off -> architect
- unclear -> generic

Other rules:
- Fix typos.
- Preserve original meaning.
- Use retrieval_required=true if answer needs documents, DB, or project context.
""",
                ),
                (
                    "human",
                    """
Input Role:
{role}

Query:
{query}
""",
                ),
            ]
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "role": context.role,
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
                "resolved_role": (
                    context.role
                    or "generic"
                ),
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

        context.resolved_role = data.get(
            "resolved_role",
            context.role or "generic",
        )

        self.trace(
            context,
            (
                "Query analyzed. "
                f"resolved_role="
                f"{context.resolved_role}, "
                f"intent={context.intent}, "
                f"retrieval_required="
                f"{context.retrieval_required}."
            ),
        )

        return context