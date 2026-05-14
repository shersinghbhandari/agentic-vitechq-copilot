from sqlalchemy.orm import Session

from app.agents.core.agent_context import AgentContext
from app.agents.generation.answer_generator_agent import AnswerGeneratorAgent
from app.agents.generation.context_builder_agent import ContextBuilderAgent
from app.agents.planning.information_sufficiency_agent import InformationSufficiencyAgent
from app.agents.query.query_analyzer_agent import QueryAnalyzerAgent
from app.agents.retrieval.rag_retrieval_agent import RagRetrievalAgent
from app.agents.routing.source_router_agent import SourceRouterAgent
from app.agents.validation.citation_validator_agent import CitationValidatorAgent


class ChatOrchestrator:

    def __init__(self, db: Session):
        self.query_analyzer = QueryAnalyzerAgent()
        self.sufficiency_agent = InformationSufficiencyAgent()
        self.source_router = SourceRouterAgent()
        self.retrieval_agent = RagRetrievalAgent(db)
        self.context_builder = ContextBuilderAgent()
        self.answer_generator = AnswerGeneratorAgent()
        self.citation_validator = CitationValidatorAgent()

    def run(self, context: AgentContext) -> AgentContext:
        context = self.query_analyzer.analyze(context)
        context = self.sufficiency_agent.check(context)
        context = self.source_router.route(context)
        context = self.retrieval_agent.retrieve(context)
        context = self.context_builder.build(context)
        context = self.answer_generator.generate(context)
        context = self.citation_validator.validate(context)

        return context