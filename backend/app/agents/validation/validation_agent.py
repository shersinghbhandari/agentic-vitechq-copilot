# backend/app/agents/validation/validation_agent.py

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent


class ValidationAgent(BaseAgent):
    name = "ValidationAgent"

    def run(self, context: AgentContext) -> AgentContext:
        if not context.answer:
            context.validation_status = "FAILED"
            context.validation_errors.append("Answer is empty.")
            self.trace(context, "Validation failed.")
            return context

        if context.retrieval_required and not context.retrieved_context:
            context.validation_status = "NO_CONTEXT"
            context.validation_errors.append("No retrieved context available.")
            self.trace(context, "Validation completed with no context.")
            return context

        context.validation_status = "PASSED"
        self.trace(context, "Validation passed.")
        return context