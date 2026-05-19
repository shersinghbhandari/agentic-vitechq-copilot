# backend/app/agents/retrieval/vector_precheck_agent.py

from sqlalchemy.orm import Session

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.retrieval.vector_search_service import VectorSearchService


class VectorPrecheckAgent(BaseAgent):
    name = "VectorPrecheckAgent"

    def __init__(self, db: Session):
        self.vector_search_service = VectorSearchService(db)

    def run(self, context: AgentContext) -> AgentContext:
        # Design principle: check grounded enterprise knowledge before LLM reasoning.
        retrieved_context = self.vector_search_service.search(
            query=context.query,
            tenant_id=context.tenant_id,
        )

        context.retrieved_context = retrieved_context

        if retrieved_context:
            context.selected_source = "VECTOR_STORE"
            context.retrieval_required = True
            self.trace(
                context,
                f"Vector DB matched. count={len(retrieved_context)}.",
            )
        else:
            self.trace(
                context,
                "Vector DB precheck found no context.",
            )

        return context