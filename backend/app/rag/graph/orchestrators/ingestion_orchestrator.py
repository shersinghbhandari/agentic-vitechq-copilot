from sqlalchemy.orm import Session

from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.graph.workflows.ingestion_workflow import IngestionWorkflow
from app.rag.graph.nodes.error_node import ErrorNode

#Runs graph and handles failure
class IngestionOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.workflow = IngestionWorkflow(db).build()
        self.error_node = ErrorNode(db)

    def run(self, initial_state: IngestionState) -> IngestionState:
        try:
            result = self.workflow.invoke(initial_state)
            return result

        except Exception as exception:
            return self.error_node(
                initial_state,
                exception,
            )