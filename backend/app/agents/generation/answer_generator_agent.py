# backend/app/agents/generation/answer_generator_agent.py

from langchain_core.prompts import ChatPromptTemplate

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.core.llm_factory import LlmFactory


class AnswerGeneratorAgent(BaseAgent):
    name = "AnswerGeneratorAgent"

    def __init__(self):
        self.llm = LlmFactory.create_chat_model()

    def run(self, context: AgentContext) -> AgentContext:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an enterprise AI assistant.

Rules:
- Use grounded context when available.
- Do not invent facts.
- If context is missing, clearly say what is missing.
- Keep answer architect-level but concise.
""",
                ),
                (
                    "human",
                    """
User Query:
{query}

Refined Query:
{refined_query}

Grounded Context:
{grounded_context}

Conversation History:
{conversation_history}
""",
                ),
            ]
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "query": context.query,
                "refined_query": context.refined_query,
                "grounded_context": context.grounded_context or "",
                "conversation_history": context.conversation_history,
            }
        )

        context.answer = response.content
        self.trace(context, "Answer generated.")
        return context