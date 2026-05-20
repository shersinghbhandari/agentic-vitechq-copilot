# backend/app/agents/orchestration/chat_graph.py

from sqlalchemy.orm import Session
from langgraph.graph import END, StateGraph

from app.agents.core.agent_context import AgentContext
from app.agents.generation.answer_generator_agent import (
    AnswerGeneratorAgent,
)
from app.agents.generation.context_builder_agent import (
    ContextBuilderAgent,
)
from app.agents.query_analyzer.query_analyzer_agent import (
    QueryAnalyzerAgent,
)
from app.agents.retrieval.retrieval_agent import RetrievalAgent
from app.agents.retrieval.vector_precheck_agent import (
    VectorPrecheckAgent,
)
from app.agents.roles.role_policy_agent import RolePolicyAgent
from app.agents.routing.source_router_agent import SourceRouterAgent
from app.agents.validation.validation_agent import ValidationAgent


class ChatGraph:
    """
    Deterministic LangGraph orchestration for agent chat.

    Architectural Purpose
    ---------------------
    Controls the agent execution flow from retrieval
    precheck through validation.

    Design Principles
    -----------------
    1. Controlled orchestration
       - Agents execute in a predictable sequence.

    2. Explicit state transition
       - AgentContext is the shared workflow contract.

    3. Role-aware generation
       - Role policy is applied before context building.

    4. Future extensible
       - Supports conditional routing, retries,
         checkpoints, and tool-assisted workflows.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.vector_precheck = VectorPrecheckAgent(db)
        self.query_analyzer = QueryAnalyzerAgent()
        self.role_policy = RolePolicyAgent()
        self.source_router = SourceRouterAgent()
        self.retrieval_agent = RetrievalAgent(db)
        self.context_builder = ContextBuilderAgent()
        self.answer_generator = AnswerGeneratorAgent()
        self.validation_agent = ValidationAgent()

        self.graph = self._build_graph()

    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Execute compiled chat workflow.
        """

        result = self.graph.invoke(context)

        return AgentContext.model_validate(result)

    def _build_graph(self):
        """
        Compile deterministic agent workflow.
        """

        workflow = StateGraph(AgentContext)

        workflow.add_node(
            "vector_precheck",
            self.vector_precheck.execute,
        )

        workflow.add_node(
            "query_analyzer",
            self.query_analyzer.execute,
        )

        workflow.add_node(
            "role_policy",
            self.role_policy.execute,
        )

        workflow.add_node(
            "source_router",
            self.source_router.execute,
        )

        workflow.add_node(
            "retrieval",
            self.retrieval_agent.execute,
        )

        workflow.add_node(
            "context_builder",
            self.context_builder.execute,
        )

        workflow.add_node(
            "answer_generator",
            self.answer_generator.execute,
        )

        workflow.add_node(
            "validation",
            self.validation_agent.execute,
        )

        workflow.set_entry_point("vector_precheck")

        workflow.add_edge(
            "vector_precheck",
            "query_analyzer",
        )

        workflow.add_edge(
            "query_analyzer",
            "role_policy",
        )

        workflow.add_edge(
            "role_policy",
            "source_router",
        )

        workflow.add_edge(
            "source_router",
            "retrieval",
        )

        workflow.add_edge(
            "retrieval",
            "context_builder",
        )

        workflow.add_edge(
            "context_builder",
            "answer_generator",
        )

        workflow.add_edge(
            "answer_generator",
            "validation",
        )

        workflow.add_edge(
            "validation",
            END,
        )

        return workflow.compile()