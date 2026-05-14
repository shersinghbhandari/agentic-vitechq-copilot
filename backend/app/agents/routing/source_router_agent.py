from app.agents.core.agent_context import AgentContext


class SourceRouterAgent:

    def route(self, context: AgentContext) -> AgentContext:
        context.selected_source = "RAG_VECTOR_DB"
        return context