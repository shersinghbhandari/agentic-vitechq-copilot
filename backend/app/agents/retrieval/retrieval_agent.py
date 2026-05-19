# backend/app/agents/retrieval/retrieval_agent.py

from sqlalchemy.orm import Session

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.retrieval.vector_search_service import VectorSearchService


class RetrievalAgent(BaseAgent):
    name = "RetrievalAgent"

    def __init__(self, db: Session):
        self.vector_search_service = VectorSearchService(db)

    def run(self, context: AgentContext) -> AgentContext:
        if context.retrieved_context:
            self.trace(
                context,
                "Retrieval skipped because vector precheck already found context.",
            )
            return context

        if context.selected_source == "LLM_ONLY":
            context.retrieved_context = []
            self.trace(context, "Retrieval skipped.")
            return context

        # Future direction: add hybrid search, reranking, metadata filters.
        context.retrieved_context = self.vector_search_service.search(
            query=context.refined_query or context.query,
            tenant_id=context.tenant_id,
        )

        self.trace(
            context,
            f"Retrieved context count={len(context.retrieved_context)}.",
        )

        return context