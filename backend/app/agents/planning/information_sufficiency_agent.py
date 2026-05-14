from app.agents.core.agent_context import AgentContext


class InformationSufficiencyAgent:

    def check(self, context: AgentContext) -> AgentContext:
        if not context.refined_query:
            context.missing_information.append("query")

        if len(context.keywords) == 0:
            context.missing_information.append("search_keywords")

        return context