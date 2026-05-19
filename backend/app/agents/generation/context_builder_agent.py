# backend/app/agents/generation/context_builder_agent.py

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent


class ContextBuilderAgent(BaseAgent):
    name = "ContextBuilderAgent"

    def run(self, context: AgentContext) -> AgentContext:
        if not context.retrieved_context:
            context.grounded_context = ""
        else:
            context.grounded_context = "\n\n".join(context.retrieved_context)

        self.trace(context, "Grounded context built.")
        return context