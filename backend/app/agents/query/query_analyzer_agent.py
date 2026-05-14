import re

from app.agents.core.agent_context import AgentContext


class QueryAnalyzerAgent:

    def analyze(self, context: AgentContext) -> AgentContext:
        raw_query = context.query.strip()

        context.refined_query = re.sub(r"\s+", " ", raw_query)

        words = re.findall(r"[a-zA-Z0-9_]+", context.refined_query.lower())

        stop_words = {
            "what", "is", "are", "the", "a", "an", "to", "for",
            "of", "in", "on", "and", "or", "how", "does", "do",
            "with", "from", "my", "please", "tell", "me"
        }

        context.keywords = [
            word for word in words
            if word not in stop_words
        ]

        context.intent = "QUESTION_ANSWERING"

        return context