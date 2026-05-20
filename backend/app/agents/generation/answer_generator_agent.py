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
    Converts engineered orchestration context
    into grounded, role-aware responses.

    Design Principles
    -----------------
    1. Role-driven generation
       - Runtime role instruction controls answer behavior.

    2. Grounded generation first
       - Prefer engineered enterprise context when available.

    3. Source transparency
       - Prevent false claims about local document grounding.

    4. Thin orchestration layer
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
        Generate final role-aware response.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an enterprise AI assistant.

You must follow the Role Instruction exactly.

Global rules:
- Use grounded context when available.
- Use conversation history for continuity.
- Do not invent facts.
- If local context is missing, clearly avoid claiming it came from local documents.
- Keep the answer aligned with the resolved role.
""",
                ),
                (
                    "human",
                    """
Role Instruction:
{role_instruction}

Requested Role:
{role}

Resolved Role:
{resolved_role}

User Query:
{query}

Refined Query:
{refined_query}

Answer Mode:
{answer_mode}

Source Explanation:
{source_explanation}

Engineered Context:
{grounded_context}
""",
                ),
            ]
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "role_instruction": (
                    context.role_instruction
                    or ""
                ),
                "role": context.role,
                "resolved_role": (
                    context.resolved_role
                    or context.role
                ),
                "query": context.query,
                "refined_query": (
                    context.refined_query
                    or context.query
                ),
                "answer_mode": context.answer_mode,
                "source_explanation": (
                    context.source_explanation
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
                f"resolved_role="
                f"{context.resolved_role}, "
                f"answer_mode="
                f"{context.answer_mode}."
            ),
        )

        return context