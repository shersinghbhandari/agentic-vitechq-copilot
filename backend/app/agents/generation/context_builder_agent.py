from app.agents.core.agent_context import AgentContext


class ContextBuilderAgent:

    def build(self, context: AgentContext) -> AgentContext:
        if not context.retrieved_context:
            context.integrated_context = None
            return context

        parts = []

        for item in context.retrieved_context:
            parts.append(
                f"[Document: {item['file_name']} | "
                f"Chunk: {item['chunk_index']}]\n"
                f"{item['chunk_text']}"
            )

        context.integrated_context = "\n\n---\n\n".join(parts)

        return context