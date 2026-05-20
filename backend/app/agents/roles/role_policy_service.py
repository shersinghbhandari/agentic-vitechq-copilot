# backend/app/agents/roles/role_policy_service.py

from app.agents.core.agent_context import AgentContext


class RolePolicyService:
    """
    Canonical runtime role-policy engine.

    Architectural Purpose
    ---------------------
    Centralizes role-specific answer behavior
    across the orchestration pipeline.

    This service is responsible for:
        - runtime role normalization
        - role instruction generation
        - deterministic persona behavior

    Design Principles
    -----------------
    1. Centralized role governance
       - Prevents prompt duplication across agents.

    2. Deterministic role behavior
       - Same role produces same instruction policy.

    3. Thin policy layer
       - Generates instructions without owning orchestration flow.

    4. Future extensible
       - Supports:
            - tenant-specific personas
            - adaptive prompting
            - multi-role orchestration
            - domain-specialized experts
    """

    ROLE_INSTRUCTIONS = {

        "developer": """
Act as a senior developer.

Focus on:
- concrete implementation
- full file paths
- code correctness
- debugging
- APIs/classes/functions
- minimal theory

Prefer:
- exact code
- step-by-step fixes
- practical examples
""",

        "performance": """
Act as a performance engineer.

Focus on:
- latency
- throughput
- memory
- SQL/query tuning
- bottlenecks
- profiling
- scalability impact

Prefer:
- measurable diagnosis
- root cause thinking
- optimization trade-offs
""",

        "analyst": """
Act as a business/system analyst.

Focus on:
- requirement clarity
- business meaning
- workflow
- data interpretation
- acceptance criteria
- edge cases

Prefer:
- simple language
- structured requirement flow
- examples from user/business view
""",

        "architect": """
Act as an enterprise architect.

Focus on:
- system design
- extensibility
- reliability
- observability
- security
- scalability
- trade-offs
- future evolution

Prefer:
- architecture reasoning
- design principles
- enterprise-grade patterns
""",

        "generic": """
Act as a helpful AI assistant.

Infer the best explanation style from the query.
Keep the answer clear, practical, and concise.
""",
    }

    def apply(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Apply deterministic runtime role policy.

        Design Principle
        ----------------
        Resolved role always takes precedence over
        requested role once orchestration begins.
        """

        resolved_role = (
            context.resolved_role
            or context.role
            or "generic"
        )

        # Fail-safe fallback for unsupported roles.
        if resolved_role not in self.ROLE_INSTRUCTIONS:
            resolved_role = "generic"

        context.resolved_role = resolved_role

        context.role_instruction = (
            self.ROLE_INSTRUCTIONS[
                resolved_role
            ]
        )

        return context