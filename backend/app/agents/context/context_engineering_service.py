# backend/app/agents/context/context_engineering_service.py

from app.agents.core.agent_context import AgentContext


class ContextEngineeringService:
    """
    Canonical prompt-context construction layer.

    Architectural Purpose
    ---------------------
    Converts distributed orchestration state into
    a grounded, role-aware, prompt-ready LLM context.

    This layer merges:
        - resolved role guidance
        - conversation memory
        - user context
        - metadata context
        - retrieval output

    Design Principles
    -----------------
    1. Deterministic context shaping
       - Same state produces same prompt context.

    2. Role-aware grounding
       - Output style adapts to developer,
         performance, analyst, or architect needs.

    3. Modular context composition
       - Each context type is isolated into sections.

    4. Future extensible
       - Supports ranking, compression,
         memory prioritization, and token optimization.
    """

    def build(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Build final prompt-ready grounded context.
        """

        sections: list[str] = []

        # Role guidance is always included.
        sections.append(
            self._format_role_context(context)
        )

        if context.user_context:
            sections.append(
                self._format_section(
                    "USER_CONTEXT",
                    context.user_context,
                )
            )

        if context.metadata_context:
            sections.append(
                self._format_section(
                    "METADATA_CONTEXT",
                    context.metadata_context,
                )
            )

        if context.conversation_history:
            sections.append(
                self._format_history(
                    context.conversation_history
                )
            )

        if context.retrieved_context:
            sections.append(
                self._format_retrieved_context(
                    context.retrieved_context
                )
            )

        context.grounded_context = "\n\n".join(
            section
            for section in sections
            if section
        )

        # Lightweight observability for context-shaping decisions.
        context.context_engineering_metadata = {
            "requested_role": context.role,
            "resolved_role": context.resolved_role,
            "has_user_context": bool(
                context.user_context
            ),
            "has_metadata_context": bool(
                context.metadata_context
            ),
            "history_message_count": len(
                context.conversation_history
            ),
            "retrieved_context_count": len(
                context.retrieved_context
            ),
            "strategy": "ROLE_MEMORY_METADATA_RETRIEVAL",
        }

        return context

    def _format_role_context(
        self,
        context: AgentContext,
    ) -> str:
        """
        Build role-specific generation guidance.

        Architectural Purpose
        ---------------------
        Keeps role behavior centralized instead of
        scattering persona rules across prompts.
        """

        role = context.resolved_role or context.role

        role_guidance = {
            "developer": (
                "Focus on code, implementation, debugging, APIs, "
                "classes, files, and practical fixes."
            ),
            "performance": (
                "Focus on latency, throughput, SQL tuning, memory, "
                "profiling, bottlenecks, and scalability."
            ),
            "analyst": (
                "Focus on requirements, business meaning, reporting, "
                "process flow, and data interpretation."
            ),
            "architect": (
                "Focus on design, trade-offs, extensibility, security, "
                "observability, reliability, and scale."
            ),
            "generic": (
                "Use the most suitable explanation style based on the query."
            ),
        }

        return (
            "[ROLE_CONTEXT]\n"
            f"requested_role: {context.role}\n"
            f"resolved_role: {role}\n"
            "guidance: "
            f"{role_guidance.get(role, role_guidance['generic'])}"
        )

    def _format_section(
        self,
        title: str,
        value: dict,
    ) -> str:
        """
        Generic structured context formatter.
        """

        lines = [
            f"{key}: {val}"
            for key, val in value.items()
        ]

        return (
            f"[{title}]\n"
            + "\n".join(lines)
        )

    def _format_history(
        self,
        history: list[dict[str, str]],
    ) -> str:
        """
        Conversation memory formatter.

        Design Principle
        ----------------
        Keeps only recent conversational state
        to reduce prompt bloat and token cost.
        """

        lines: list[str] = []

        for item in history[-8:]:
            role = item.get(
                "role",
                "unknown",
            )

            content = item.get(
                "content",
                "",
            )

            if content:
                lines.append(
                    f"{role}: {content}"
                )

        return (
            "[CONVERSATION_HISTORY]\n"
            + "\n".join(lines)
        )

    def _format_retrieved_context(
        self,
        retrieved_context: list[str],
    ) -> str:
        """
        Retrieval grounding formatter.

        Future Direction
        ----------------
        Can evolve into:
            - reranked chunks
            - citation-aware formatting
            - semantic compression
            - relevance scoring
        """

        chunks: list[str] = []

        for index, chunk in enumerate(
            retrieved_context,
            start=1,
        ):
            chunks.append(
                f"[chunk_{index}]\n{chunk}"
            )

        return (
            "[RETRIEVED_CONTEXT]\n"
            + "\n\n".join(chunks)
        )