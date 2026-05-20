# backend/app/agents/context/context_engineering_service.py

from app.agents.core.agent_context import AgentContext


class ContextEngineeringService:
    """
    Canonical prompt-context construction layer.

    Architectural Purpose
    ---------------------
    Converts distributed orchestration state into
    a grounded, prompt-ready LLM context.

    This layer merges:
        - retrieval output
        - conversation memory
        - user context
        - metadata context

    Design Principles
    -----------------
    1. Deterministic context shaping
       - Same state produces same prompt context.

    2. Retrieval-grounded generation
       - Retrieved chunks become primary grounding source.

    3. Modular context composition
       - Each context type isolated into sections.

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

        # Lightweight observability for context shaping decisions.
        context.context_engineering_metadata = {
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
            "strategy":
                "USER_METADATA_HISTORY_RETRIEVAL",
        }

        return context

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

        for item in history[-6:]:
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