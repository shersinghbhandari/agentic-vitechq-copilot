# backend/app/agents/retrieval/retrieval_agent.py

from sqlalchemy.orm import Session

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.retrieval.vector_search_service import (
    VectorSearchService,
)


class RetrievalAgent(BaseAgent):
    """
    Canonical retrieval orchestration agent.

    Architectural Purpose
    ---------------------
    Responsible for retrieving grounded enterprise
    knowledge before answer generation.

    This agent:
        - executes vector retrieval
        - avoids duplicate retrieval work
        - determines final retrieval source
        - updates answer generation mode

    Design Principles
    -----------------
    1. Retrieval-first architecture
       - Prefer grounded enterprise context over pure LLM reasoning.

    2. Idempotent retrieval behavior
       - Avoid repeated vector lookups if context already exists.

    3. Thin orchestration layer
       - Delegates retrieval implementation to VectorSearchService.

    4. Future extensible
       - Supports:
            - hybrid retrieval
            - reranking
            - metadata filtering
            - semantic caching
            - web/tool augmentation
    """

    name = "RetrievalAgent"

    def __init__(
        self,
        db: Session,
    ):
        self.vector_search_service = (
            VectorSearchService(db)
        )

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Execute retrieval workflow.
        """

        # Retrieval already resolved during vector precheck.
        if context.retrieved_context:

            context.selected_source = (
                "VECTOR_STORE"
            )

            context.answer_mode = (
                "GROUNDED_RAG"
            )

            context.source_explanation = (
                "This answer uses local vector DB "
                "context and LLM reasoning."
            )

            self.trace(
                context,
                (
                    "Retrieval skipped because "
                    "vector precheck already "
                    "found context."
                ),
            )

            return context

        # Query determined retrieval is unnecessary.
        if context.selected_source == "LLM_ONLY":

            context.retrieved_context = []

            context.answer_mode = (
                "GENERAL_LLM"
            )

            context.source_explanation = (
                "Answer generated using LLM "
                "reasoning without local "
                "vector DB context."
            )

            self.trace(
                context,
                (
                    "Retrieval skipped because "
                    "source is LLM only."
                ),
            )

            return context

        # Future direction:
        # add hybrid search, reranking,
        # metadata filtering, and semantic caching.
        context.retrieved_context = (
            self.vector_search_service.search(
                query=(
                    context.refined_query
                    or context.query
                ),
                tenant_id=context.tenant_id,
            )
        )

        # Grounded enterprise context found.
        if context.retrieved_context:

            context.selected_source = (
                "VECTOR_STORE"
            )

            context.answer_mode = (
                "GROUNDED_RAG"
            )

            context.source_explanation = (
                "This answer uses local vector DB "
                "context and LLM reasoning."
            )

        # Fallback to generalized LLM reasoning.
        else:

            context.selected_source = (
                "LLM_ONLY"
            )

            context.answer_mode = (
                "GENERAL_LLM"
            )

            context.source_explanation = (
                "No matching local vector DB "
                "context was found. "
                "Answer generated using "
                "LLM general reasoning."
            )

        self.trace(
            context,
            (
                "Retrieval completed. "
                f"source={context.selected_source}, "
                f"answer_mode={context.answer_mode}, "
                f"context_count="
                f"{len(context.retrieved_context)}."
            ),
        )

        return context