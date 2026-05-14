from app.agents.core.agent_context import AgentContext


class AnswerGeneratorAgent:

    def generate(self, context: AgentContext) -> AgentContext:
        if not context.integrated_context:
            context.answer = (
                "I could not find relevant information in the indexed RAG data "
                "for this query."
            )
            context.citations = []
            return context

        answer_parts = [
            "Based on the indexed RAG content, here is the relevant information:"
        ]

        citations = []

        for index, item in enumerate(context.retrieved_context, start=1):
            chunk_text = item["chunk_text"]

            trimmed_text = (
                chunk_text[:700] + "..."
                if len(chunk_text) > 700
                else chunk_text
            )

            answer_parts.append(
                f"\n[{index}] {trimmed_text}"
            )

            citations.append(
                {
                    "document_id": item["document_id"],
                    "chunk_id": item["chunk_id"],
                    "chunk_index": item["chunk_index"],
                    "file_name": item["file_name"],
                }
            )

        context.answer = "\n".join(answer_parts)
        context.citations = citations

        return context