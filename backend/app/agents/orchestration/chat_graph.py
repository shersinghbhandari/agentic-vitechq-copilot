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
from app.agents.routing.source_router_agent import SourceRouterAgent
from app.agents.validation.validation_agent import ValidationAgent


class ChatGraph:
    """
    Deterministic LangGraph orchestration for agent chat.

    Architectural Purpose
    ---------------------
    Controls the end-to-end agent execution flow:
        Vector Precheck -> Query Analyzer -> Source Router
        -> Retrieval -> Context Builder -> Answer Generator
        -> Validation

    Design Principles
    -----------------
    1. Controlled orchestration
       - Agents execute in a predictable sequence.

    2. Explicit state transitions
       - AgentContext is the shared workflow contract.

    3. Production extensibility
       - Supports future conditional routing,
         retries, checkpoints, and human review.

    4. Separation of responsibility
       - Graph controls flow.
       - Agents own business behavior.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.vector_precheck = VectorPrecheckAgent(db)
        self.query_analyzer = QueryAnalyzerAgent()
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
        Compile the agent workflow graph.

        Future Direction
        ----------------
        Add conditional edges for:
            - no vector data
            - no retrieval needed
            - clarification required
            - validation retry
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