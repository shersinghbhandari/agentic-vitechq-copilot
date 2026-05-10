from app.rag.graph.states.ingestion_state import IngestionState
from app.rag.parsing.parser_factory import ParserFactory

#Extracts text
def parsing_node(state: IngestionState) -> IngestionState:
    parser = ParserFactory.get_parser(state["file_type"])
    raw_text = parser.parse(state["local_path"])
    if not raw_text or not raw_text.strip():
        raise ValueError(
            f"No text extracted from file: {state['file_name']}"
        )
    state["raw_text"] = raw_text
    state["stage"] = "PARSING"
    return state