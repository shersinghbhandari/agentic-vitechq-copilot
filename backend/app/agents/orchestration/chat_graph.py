# backend/app/agents/orchestration/chat_graph.py

from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from app.agents.core.agent_context import AgentContext
from app.agents.retrieval.vector_precheck_agent import VectorPrecheckAgent
from app.agents.query_analyzer.query_analyzer_agent import QueryAnalyzerAgent
from app.agents.routing.source_router_agent import SourceRouterAgent
from app.agents.retrieval.retrieval_agent import RetrievalAgent
from app.agents.generation.context_builder_agent import ContextBuilderAgent
from app.agents.generation.answer_generator_agent import AnswerGeneratorAgent
from app.agents.validation.validation_agent import ValidationAgent


class ChatGraph:
    """
    Architectural purpose:
    LangGraph controls deterministic agent execution.
    """

    def __init__(self, db: Session):
        self.vector_precheck = VectorPrecheckAgent(db)
        self.query_analyzer = QueryAnalyzerAgent()
        self.source_router = SourceRouterAgent()
        self.retrieval_agent = RetrievalAgent(db)
        self.context_builder = ContextBuilderAgent()
        self.answer_generator = AnswerGeneratorAgent()
        self.validation_agent = ValidationAgent()

        self.graph = self._build_graph()

    def run(self, context: AgentContext) -> AgentContext:
        result = self.graph.invoke(context)
        return AgentContext.model_validate(result)

    def _build_graph(self):
        workflow = StateGraph(AgentContext)

        workflow.add_node(
            "vector_precheck",
            self.vector_precheck.run,
        )
        workflow.add_node(
            "query_analyzer",
            self.query_analyzer.run,
        )
        workflow.add_node(
            "source_router",
            self.source_router.run,
        )
        workflow.add_node(
            "retrieval",
            self.retrieval_agent.run,
        )
        workflow.add_node(
            "context_builder",
            self.context_builder.run,
        )
        workflow.add_node(
            "answer_generator",
            self.answer_generator.run,
        )
        workflow.add_node(
            "validation",
            self.validation_agent.run,
        )

        workflow.set_entry_point("vector_precheck")

        workflow.add_edge("vector_precheck", "query_analyzer")
        workflow.add_edge("query_analyzer", "source_router")
        workflow.add_edge("source_router", "retrieval")
        workflow.add_edge("retrieval", "context_builder")
        workflow.add_edge("context_builder", "answer_generator")
        workflow.add_edge("answer_generator", "validation")
        workflow.add_edge("validation", END)

        return workflow.compile()