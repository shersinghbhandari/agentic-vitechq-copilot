# backend/app/agents/roles/role_resolution_agent.py

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.roles.role_policy_service import RolePolicyService


class RoleResolutionAgent(BaseAgent):
    """
    Dedicated role-resolution orchestration agent.

    Architectural Purpose
    ---------------------
    Resolves the effective runtime role and
    builds role-specific prompt instructions.

    Design Principles
    -----------------
    1. Explicit role boundary
       - Keeps persona decisions outside generation.

    2. Centralized policy usage
       - Delegates role rules to RolePolicyService.

    3. Observable routing behavior
       - Records requested and resolved role in trace.

    4. Future extensible
       - Supports tenant-specific roles,
         multi-role blending, and adaptive personas.
    """

    name = "RoleResolutionAgent"

    def __init__(self):
        self.role_policy_service = RolePolicyService()

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Resolve role and attach prompt instruction.
        """

        context.resolved_role = (
            self.role_policy_service.resolve_role(context)
        )

        context.role_instruction = (
            self.role_policy_service.build_instruction(
                context.resolved_role
            )
        )

        self.trace(
            context,
            (
                "Role resolved. "
                f"requested_role={context.role}, "
                f"resolved_role={context.resolved_role}."
            ),
        )

        return context