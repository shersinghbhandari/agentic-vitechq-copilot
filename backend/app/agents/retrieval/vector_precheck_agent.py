# backend/app/agents/retrieval/vector_precheck_agent.py

from sqlalchemy.orm import Session

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.retrieval.vector_search_service import (
    VectorSearchService,
)


class VectorPrecheckAgent(BaseAgent):
    """
    Lightweight early-stage vector retrieval validation.

    Architectural Purpose
    ---------------------
    Performs a fast vector DB precheck before
    full orchestration continues.

    This helps:
        - reduce unnecessary LLM reasoning
        - prioritize grounded enterprise knowledge
        - improve hallucination resistance
        - expose retrieval observability early

    Design Principles
    -----------------
    1. Retrieval-first architecture
       - Enterprise context preferred over pure LLM answers.

    2. Early grounding optimization
       - Detects usable context before expensive orchestration.

    3. Thin orchestration layer
       - Delegates retrieval implementation to VectorSearchService.

    4. Future extensible
       - Can evolve into:
            - similarity thresholding
            - reranking
            - metadata filtering
            - hybrid retrieval
            - semantic cache lookup
    """

    name = "VectorPrecheckAgent"

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
        Execute lightweight vector retrieval precheck.
        """

        # Design Principle:
        # check grounded enterprise knowledge
        # before generalized LLM reasoning.
        retrieved_context = (
            self.vector_search_service.search(
                query=context.query,
                tenant_id=context.tenant_id,
            )
        )

        context.retrieved_context = (
            retrieved_context
        )

        # Vector DB returned grounded context.
        if retrieved_context:

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
                    "Vector DB matched. "
                    f"retrieved_context_count="
                    f"{len(retrieved_context)}."
                ),
            )

        # No vector match found yet.
        #
        # Retrieval flow may continue later.
        else:

            context.selected_source = (
                "NO_LOCAL_CONTEXT_YET"
            )

            context.answer_mode = (
                "PENDING_RETRIEVAL"
            )

            context.source_explanation = (
                "No matching local vector DB "
                "context was found during precheck."
            )

            self.trace(
                context,
                (
                    "Vector DB precheck "
                    "found no context."
                ),
            )

        return context