from langgraph.graph import StateGraph, END

from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.graph.nodes.parsing_node import parsing_node
from app.rag.graph.nodes.langchain_document_node import langchain_document_node
from app.rag.graph.nodes.chunking_node import chunking_node
from app.rag.graph.nodes.embedding_node import EmbeddingNode
from app.rag.graph.nodes.vectorstore_node import VectorStoreNode
from app.rag.graph.nodes.finalize_node import FinalizeNode


class IngestionWorkflow:
    def __init__(self, db):
        self.db = db

    def build(self):
        graph = StateGraph(IngestionState)

        graph.add_node("parse", parsing_node)
        graph.add_node("to_langchain_document", langchain_document_node)
        graph.add_node("chunk", chunking_node)
        graph.add_node("embed", EmbeddingNode(self.db))
        graph.add_node("store_vectors", VectorStoreNode(self.db))
        graph.add_node("finalize", FinalizeNode(self.db))

        graph.set_entry_point("parse")

        graph.add_edge("parse", "to_langchain_document")
        graph.add_edge("to_langchain_document", "chunk")
        graph.add_edge("chunk", "embed")
        graph.add_edge("embed", "store_vectors")
        graph.add_edge("store_vectors", "finalize")
        graph.add_edge("finalize", END)

        return graph.compile()