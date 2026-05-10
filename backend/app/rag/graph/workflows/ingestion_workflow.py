from langgraph.graph import StateGraph, END

from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.graph.nodes.parsing_node import parsing_node
from app.rag.graph.nodes.langchain_document_node import langchain_document_node
from app.rag.graph.nodes.chunking_node import chunking_node
from app.rag.graph.nodes.vectorstore_node import VectorStoreNode
from app.rag.graph.nodes.finalize_node import FinalizeNode

#Defines node order
class IngestionWorkflow:
    def __init__(self, db):
        self.db = db

    def build(self):
        graph = StateGraph(IngestionState)

        graph.add_node("parse", parsing_node)
        graph.add_node("to_langchain_document", langchain_document_node)
        graph.add_node("chunk", chunking_node)
        graph.add_node("store_chunks", VectorStoreNode(self.db))
        graph.add_node("finalize", FinalizeNode(self.db))

        graph.set_entry_point("parse")

        graph.add_edge("parse", "to_langchain_document")
        graph.add_edge("to_langchain_document", "chunk")
        graph.add_edge("chunk", "store_chunks")
        graph.add_edge("store_chunks", "finalize")
        graph.add_edge("finalize", END)

        return graph.compile()