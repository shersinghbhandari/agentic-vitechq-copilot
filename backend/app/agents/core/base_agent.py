# backend/app/agents/core/base_agent.py

from abc import ABC, abstractmethod

from app.agents.core.agent_context import AgentContext


class BaseAgent(ABC):
    """
    Architectural purpose:
    Common contract for all agents participating in the graph.
    """

    name: str = "BaseAgent"

    @abstractmethod
    def run(self, context: AgentContext) -> AgentContext:
        pass

    def trace(self, context: AgentContext, message: str) -> None:
        context.add_trace(f"{self.name}: {message}")