# backend/app/agents/generation/answer_generator_agent.py

from langchain_core.prompts import ChatPromptTemplate

from app.agents.core.agent_context import AgentContext
from app.agents.core.base_agent import BaseAgent
from app.agents.core.llm_factory import LlmFactory


class AnswerGeneratorAgent(BaseAgent):
    """
    Final response generation agent.

    Architectural Purpose
    ---------------------
    Converts engineered context into
    grounded, role-aware natural language responses.

    This agent is responsible for:
        - answer synthesis
        - role-aware generation
        - retrieval-grounded generation
        - conversation-aware continuity
        - hallucination reduction

    Design Principles
    -----------------
    1. Grounded generation first
       - Engineered context is preferred over model memory.

    2. Role-aware answering
       - Uses resolved role guidance from context engineering.

    3. Conversation continuity
       - Uses recent history when available.

    4. Thin orchestration layer
       - Prompt execution only.
       - Business state remains in AgentContext.
    """

    name = "AnswerGeneratorAgent"

    def __init__(self):
        self.llm = LlmFactory.create_chat_model()

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Generate final grounded answer.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an enterprise AI assistant.

Rules:
- Follow the resolved role guidance from engineered context.
- Use grounded context when available.
- Use conversation history for continuity.
- Do not invent facts.
- If context is missing, clearly say what is missing.
- Keep answer practical and concise.
""",
                ),
                (
                    "human",
                    """
User Query:
{query}

Refined Query:
{refined_query}

Engineered Context:
{grounded_context}
""",
                ),
            ]
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "query": context.query,
                "refined_query": (
                    context.refined_query
                    or context.query
                ),
                "grounded_context": (
                    context.grounded_context
                    or ""
                ),
            }
        )

        # Centralized LLM observability.
        self.track_token_usage(
            context,
            response,
        )

        context.answer = response.content

        self.trace(
            context,
            (
                "Answer generated. "
                f"resolved_role={context.resolved_role}, "
                f"context_present="
                f"{bool(context.grounded_context)}."
            ),
        )

        return context