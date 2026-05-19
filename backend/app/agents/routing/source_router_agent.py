# backend/app/agents/routing/source_router_agent.py

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent


class SourceRouterAgent(BaseAgent):
    name = "SourceRouterAgent"

    def run(self, context: AgentContext) -> AgentContext:
        if not context.retrieval_required:
            context.selected_source = "LLM_ONLY"
        elif context.metadata_context.get("source"):
            context.selected_source = context.metadata_context["source"]
        else:
            context.selected_source = "VECTOR_STORE"

        self.trace(context, f"Selected source={context.selected_source}.")
        return context