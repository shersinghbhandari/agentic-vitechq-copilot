from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.langchain.splitter_service import LangChainSplitterService

#Splits documents into chunks
def chunking_node(state: IngestionState) -> IngestionState:
    splitter_service = LangChainSplitterService()

    chunks = splitter_service.split_documents(
        state["langchain_documents"]
    )

    state["chunks"] = chunks
    state["total_chunks"] = len(chunks)
    state["processed_chunks"] = 0
    state["stage"] = "CHUNKING"

    return state