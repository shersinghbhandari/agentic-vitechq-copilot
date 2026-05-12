from typing import TypedDict, Optional, List, Any

from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session

from app.rag.enums.document_status import DocumentStatus
from app.rag.enums.job_status import JobStatus
from app.rag.enums.job_stage import JobStage

from app.rag.jobs.ingestion_job_service import IngestionJobService
from app.rag.services.document_service import DocumentService
from app.rag.services.extraction_service import ExtractionService
from app.rag.services.chunking_service import ChunkingService
from app.rag.services.embedding_service import EmbeddingService
from app.rag.services.vector_store_service import VectorStoreService

from app.rag.models.raw_document import RawDocument
from app.rag.db.document_models import Document


class IngestionState(TypedDict):
    db: Session
    document_id: Any
    job_id: Any
    document: Optional[Document]
    raw_document: Optional[RawDocument]
    extracted_text: Optional[str]
    chunks: Optional[List[str]]
    embeddings: Optional[List[Any]]
    error_message: Optional[str]


class IngestionGraph:

    def __init__(self, db):
        self.db = db
        self.document_service = DocumentService()
        self.job_service = IngestionJobService()
        self.extraction_service = ExtractionService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService(db)

        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(IngestionState)

        workflow.add_node("validate_document", self.validate_document)
        workflow.add_node("extract_text", self.extract_text)
        workflow.add_node("chunk_text", self.chunk_text)
        workflow.add_node("create_embeddings", self.create_embeddings)
        workflow.add_node("save_vectors", self.save_vectors)
        workflow.add_node("finalize_job", self.finalize_job)
        workflow.add_node("handle_failure", self.handle_failure)

        workflow.add_edge(START, "validate_document")
        workflow.add_edge("validate_document", "extract_text")
        workflow.add_edge("extract_text", "chunk_text")
        workflow.add_edge("chunk_text", "create_embeddings")
        workflow.add_edge("create_embeddings", "save_vectors")
        workflow.add_edge("save_vectors", "finalize_job")
        workflow.add_edge("finalize_job", END)

        return workflow.compile()

    def run(self, db: Session, document_id, job_id) -> None:
        try:
            self.graph.invoke({
                "db": db,
                "document_id": document_id,
                "job_id": job_id,
                "document": None,
                "raw_document": None,
                "extracted_text": None,
                "chunks": None,
                "embeddings": None,
                "error_message": None,
            })
        except Exception as ex:
            self.handle_failure({
                "db": db,
                "document_id": document_id,
                "job_id": job_id,
                "document": None,
                "raw_document": None,
                "extracted_text": None,
                "chunks": None,
                "embeddings": None,
                "error_message": str(ex),
            })
            raise

    def validate_document(self, state: IngestionState) -> IngestionState:
        db = state["db"]
        document_id = state["document_id"]
        job_id = state["job_id"]

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.VALIDATING,
            stage=JobStage.VALIDATION,
        )

        self.document_service.update_status(
            db,
            document_id,
            DocumentStatus.PROCESSING,
        )

        document = db.query(Document).filter(
            Document.id == document_id
        ).first()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        metadata = document.metadata_json or {}

        raw_document = RawDocument(
            file_name=document.file_name,
            file_type=document.file_type,
            source_type=document.source_type,
            source_uri=document.source_uri,
            local_path=metadata.get("local_path"),
            content_type=metadata.get("content_type"),
        )

        state["document"] = document
        state["raw_document"] = raw_document

        return state

    def extract_text(self, state: IngestionState) -> IngestionState:
        db = state["db"]
        job_id = state["job_id"]
        document_id = state["document_id"]

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.EXTRACTING,
            stage=JobStage.EXTRACTION,
        )

        extracted_text = self.extraction_service.extract(
            state["raw_document"]
        )

        if not extracted_text:
            raise ValueError("No text extracted from document")

        self.document_service.update_status(
            db,
            document_id,
            DocumentStatus.EXTRACTED,
        )

        state["extracted_text"] = extracted_text
        return state

    def chunk_text(self, state: IngestionState) -> IngestionState:
        db = state["db"]
        job_id = state["job_id"]
        document_id = state["document_id"]

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.CHUNKING,
            stage=JobStage.CHUNKING,
        )

        chunks = self.chunking_service.chunk_text(
            state["extracted_text"]
        )

        if not chunks:
            raise ValueError("No chunks created from extracted text")

        self.job_service.update_chunk_progress(
            db=db,
            job_id=job_id,
            total_chunks=len(chunks),
            processed_chunks=0,
        )

        self.document_service.update_status(
            db,
            document_id,
            DocumentStatus.CHUNKED,
        )

        state["chunks"] = chunks
        return state

    def create_embeddings(self, state: IngestionState) -> IngestionState:
        db = state["db"]
        job_id = state["job_id"]
        document_id = state["document_id"]
        chunks = state["chunks"]

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.EMBEDDING,
            stage=JobStage.EMBEDDING,
        )

        embeddings = self.embedding_service.create_embeddings(chunks)

        self.job_service.update_chunk_progress(
            db=db,
            job_id=job_id,
            total_chunks=len(chunks),
            processed_chunks=len(chunks),
        )

        self.document_service.update_status(
            db,
            document_id,
            DocumentStatus.EMBEDDED,
        )

        state["embeddings"] = embeddings
        return state

    def save_vectors(self, state: IngestionState) -> IngestionState:
        db = state["db"]
        job_id = state["job_id"]
        document_id = state["document_id"]
        document = state["document"]

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.INDEXING,
            stage=JobStage.VECTOR_INDEX,
        )

        self.vector_store_service.save_vectors(
            document_id=document_id,
            tenant_id=document.tenant_id,
            chunks=state["chunks"],
            embeddings=state["embeddings"],
        )

        self.document_service.update_status(
            db,
            document_id,
            DocumentStatus.INDEXED,
        )

        return state

    def finalize_job(self, state: IngestionState) -> IngestionState:
        self.job_service.update_status(
            db=state["db"],
            job_id=state["job_id"],
            status=JobStatus.COMPLETED,
            stage=JobStage.FINALIZATION,
        )

        return state

    def handle_failure(self, state: IngestionState) -> IngestionState:
        error_message = state.get("error_message") or "Unknown ingestion error"

        self.document_service.update_status(
            state["db"],
            state["document_id"],
            DocumentStatus.FAILED,
            error_message,
        )

        self.job_service.update_status(
            db=state["db"],
            job_id=state["job_id"],
            status=JobStatus.FAILED,
            stage=JobStage.FINALIZATION,
            error_message=error_message,
        )

        return state