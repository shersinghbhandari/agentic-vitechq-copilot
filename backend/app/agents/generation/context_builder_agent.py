# backend/app/agents/generation/context_builder_agent.py

from app.agents.context.context_engineering_service import (
    ContextEngineeringService,
)
from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent


class ContextBuilderAgent(BaseAgent):
    """
    Converts retrieval and memory state into prompt-ready context.

    Architectural Purpose
    ---------------------
    Acts as the dedicated context engineering agent
    before answer generation.

    Design Principle
    ----------------
    Keeps prompt construction separate from retrieval
    and response generation.
    """

    name = "ContextBuilderAgent"

    def __init__(self):
        self.context_engineering_service = (
            ContextEngineeringService()
        )

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Build grounded context for downstream LLM generation.
        """

        context = self.context_engineering_service.build(context)

        self.trace(
            context,
            (
                "Context engineered. "
                f"retrieved_context_count="
                f"{len(context.retrieved_context)}."
            ),
        )

        return context