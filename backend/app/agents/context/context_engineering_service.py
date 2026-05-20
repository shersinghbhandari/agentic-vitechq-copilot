# backend/app/agents/context/context_engineering_service.py

from app.agents.core.agent_context import AgentContext


class ContextEngineeringService:
    """
    Canonical prompt-context construction layer.

    Architectural Purpose
    ---------------------
    Builds source-aware, role-aware, prompt-ready
    context from orchestration state.

    Design Principles
    -----------------
    1. Deterministic context shaping
       - Same AgentContext produces same prompt context.

    2. Source transparency
       - Generator knows whether context came from vector DB,
         general LLM fallback, or another source.

    3. Explicit role behavior
       - Runtime role instruction is injected into context.

    4. Future extensible
       - Supports compression, citations, memory ranking,
         reranking metadata, and token optimization.
    """

    def build(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Build final engineered context for answer generation.
        """

        sections: list[str] = []

        sections.append(
            self._format_source_context(context)
        )

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

        context.context_engineering_metadata = {
            "requested_role": context.role,
            "resolved_role": context.resolved_role,
            "role_instruction_present": bool(
                context.role_instruction
            ),
            "selected_source": context.selected_source,
            "answer_mode": context.answer_mode,
            "source_explanation": context.source_explanation,
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
            "strategy": "SOURCE_ROLE_MEMORY_METADATA_RETRIEVAL",
        }

        return context

    def _format_source_context(
        self,
        context: AgentContext,
    ) -> str:
        """
        Format source-routing guidance.

        Architectural Purpose
        ---------------------
        Prevents false claims of local grounding
        when vector context is unavailable.
        """

        return (
            "[SOURCE_CONTEXT]\n"
            f"selected_source: {context.selected_source}\n"
            f"answer_mode: {context.answer_mode}\n"
            f"source_explanation: {context.source_explanation}"
        )

    def _format_role_context(
        self,
        context: AgentContext,
    ) -> str:
        """
        Format runtime role guidance for generation.
        """

        return (
            "[ROLE_CONTEXT]\n"
            f"requested_role: {context.role}\n"
            f"resolved_role: {context.resolved_role}\n"
            f"role_instruction:\n{context.role_instruction or ''}"
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
        Format recent conversation memory.

        Design Principle
        ----------------
        Keep recent turns only to control token growth.
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
        Format retrieved enterprise knowledge.

        Future Direction
        ----------------
        Add source metadata, citations,
        rerank scores, and chunk IDs.
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