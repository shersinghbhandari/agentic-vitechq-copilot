from app.core.trace_logger import TraceContext
from app.rag.graph.states.ingestion_state import IngestionState


def build_trace_context(state: IngestionState) -> TraceContext:
    """
    Converts LangGraph IngestionState into TraceContext.

    This ensures:
    - all nodes log consistently
    - no repeated TraceContext creation code
    - correlation_id flows across the graph
    """

    return TraceContext(
        correlation_id=state.get("correlation_id", "-"),
        uploaded_by=state.get("uploaded_by", "-"),
        tenant_id=state.get("tenant_id", "-"),
        request_name=state.get("stage", "INGESTION"),
        document_id=str(state.get("document_id", "-")),
        job_id=str(state.get("job_id", "-")),
    )