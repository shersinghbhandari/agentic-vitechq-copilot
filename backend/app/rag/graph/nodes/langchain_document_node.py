from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.langchain.document_mapper import LangChainDocumentMapper


def langchain_document_node(state: IngestionState) -> IngestionState:
    mapper = LangChainDocumentMapper()

    document = mapper.to_langchain_document(
        text=state["raw_text"],
        tenant_id=state["tenant_id"],
        document_id=str(state["document_id"]),
        file_name=state["file_name"],
        file_type=state["file_type"],
        source_uri=state["source_uri"],
        uploaded_by=state.get("uploaded_by"),
        correlation_id=state["correlation_id"],
        metadata=state.get("metadata", {}),
    )

    state["langchain_documents"] = [document]
    state["stage"] = "LANGCHAIN_DOCUMENT_CREATED"

    return state