# backend/app/agents/routing/source_router_agent.py

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent


class SourceRouterAgent(BaseAgent):
    """
    Determines answer generation strategy and source routing.

    Architectural Purpose
    ---------------------
    Responsible for deciding:
        - whether retrieval is needed
        - whether vector context already exists
        - whether direct LLM response is sufficient
        - final answer generation mode

    Design Principles
    -----------------
    1. Explicit routing decisions
       - Avoid hidden orchestration behavior.

    2. Retrieval-first architecture
       - Prefer grounded RAG when context exists.

    3. Human-readable observability
       - Exposes source explanations for UI/debugging.

    4. Future extensible
       - Supports hybrid routing, tools,
         external APIs, SQL agents, and web search.
    """

    name = "SourceRouterAgent"

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Resolve source routing and answer strategy.
        """

        # Existing retrieval context already available.
        #
        # Example:
        # vector precheck already populated context.
        if context.retrieved_context:

            context.selected_source = "VECTOR_STORE"

            context.answer_mode = "GROUNDED_RAG"

            context.source_explanation = (
                "This answer uses local vector DB "
                "context and LLM reasoning."
            )

            self.trace(
                context,
                (
                    "Source resolved from "
                    "existing vector context."
                ),
            )

            return context

        # Query determined retrieval is unnecessary.
        #
        # Example:
        # generic conceptual question.
        if not context.retrieval_required:

            context.selected_source = "LLM_ONLY"

            context.answer_mode = "GENERAL_LLM"

            context.source_explanation = (
                "No retrieval was required. "
                "Answer generated using "
                "LLM reasoning."
            )

            self.trace(
                context,
                "Source resolved as LLM only.",
            )

            return context

        # Default retrieval-first flow.
        #
        # RetrievalAgent will attempt
        # vector-based grounding next.
        context.selected_source = "VECTOR_STORE"

        context.answer_mode = "PENDING_RETRIEVAL"

        context.source_explanation = (
            "Local vector DB will be checked "
            "before generating the answer."
        )

        self.trace(
            context,
            (
                "Source resolved as "
                "vector store retrieval."
            ),
        )

        return context