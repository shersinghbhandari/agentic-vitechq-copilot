from app.agents.core.agent_context import AgentContext


class CitationValidatorAgent:

    def validate(self, context: AgentContext) -> AgentContext:
        if not context.retrieved_context:
            context.validation_status = "NO_CONTEXT"
            context.validation_message = "No matching RAG context was found."
            return context

        if not context.citations:
            context.validation_status = "FAILED"
            context.validation_message = "Answer was generated without citations."
            return context

        context.validation_status = "PASSED"
        context.validation_message = "Answer is grounded in retrieved RAG chunks."

        return context