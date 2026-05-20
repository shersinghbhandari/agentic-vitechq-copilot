# backend/app/agents/roles/role_policy_agent.py

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.roles.role_policy_service import (
    RolePolicyService,
)


class RolePolicyAgent(BaseAgent):
    """
    Runtime role-policy orchestration agent.

    Architectural Purpose
    ---------------------
    Applies deterministic role behavior policies
    to the shared orchestration state.

    This agent is responsible for:
        - resolved role assignment
        - runtime instruction injection
        - persona-policy enforcement

    Design Principles
    -----------------
    1. Explicit role orchestration
       - Role behavior remains outside generation prompts.

    2. Centralized policy management
       - Delegates all role logic to RolePolicyService.

    3. Deterministic runtime behavior
       - Same role produces same instruction policy.

    4. Future extensible
       - Supports adaptive personas,
         tenant-specific policies,
         and multi-role execution.
    """

    name = "RolePolicyAgent"

    def __init__(self):
        self.role_policy_service = (
            RolePolicyService()
        )

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Apply runtime role policy to orchestration state.
        """

        context = self.role_policy_service.apply(
            context
        )

        self.trace(
            context,
            (
                "Role policy applied. "
                f"resolved_role="
                f"{context.resolved_role}."
            ),
        )

        return context