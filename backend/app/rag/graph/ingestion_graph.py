from typing import Any, List, Optional, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.core.trace_logger import TraceContext, TraceLogger
from app.rag.db.document_models import Document
from app.rag.db.repositories.document_metadata_repository import (
    DocumentMetadataRepository,
)
from app.rag.enums.document_status import DocumentStatus
from app.rag.enums.job_stage import JobStage
from app.rag.enums.job_status import JobStatus
from app.rag.jobs.ingestion_job_service import IngestionJobService
from app.rag.models.raw_document import RawDocument
from app.rag.services.chunking_service import ChunkingService
from app.rag.services.document_service import DocumentService
from app.rag.services.embedding_service import EmbeddingService
from app.rag.services.extraction_service import ExtractionService
from app.rag.services.vector_store_service import VectorStoreService


class IngestionState(TypedDict):
    db: Session
    document_id: Any
    job_id: Any

    correlation_id: str
    uploaded_by: str
    tenant_id: str

    document: Optional[Document]
    raw_document: Optional[RawDocument]
    extracted_text: Optional[str]
    chunks: Optional[List[str]]
    embeddings: Optional[List[Any]]
    error_message: Optional[str]


class IngestionGraph:
    """
    Controlled LangGraph ingestion workflow.

    Future:
    - retry-safe resume
    - object-storage streaming
    - async worker execution
    """

    def __init__(self, db: Session):
        self.db = db
        self.document_service = DocumentService()
        self.job_service = IngestionJobService()
        self.metadata_repository = DocumentMetadataRepository()
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
        workflow.add_node("index_vectors", self.index_vectors)
        workflow.add_node("finalize_job", self.finalize_job)

        workflow.add_edge(START, "validate_document")
        workflow.add_edge("validate_document", "extract_text")
        workflow.add_edge("extract_text", "chunk_text")
        workflow.add_edge("chunk_text", "create_embeddings")
        workflow.add_edge("create_embeddings", "index_vectors")
        workflow.add_edge("index_vectors", "finalize_job")
        workflow.add_edge("finalize_job", END)

        return workflow.compile()

    def run(
        self,
        db: Session,
        document_id,
        job_id,
        correlation_id: str,
        uploaded_by: str,
        tenant_id: str,
    ) -> None:

        initial_state: IngestionState = {
            "db": db,
            "document_id": document_id,
            "job_id": job_id,
            "correlation_id": correlation_id,
            "uploaded_by": uploaded_by,
            "tenant_id": tenant_id,
            "document": None,
            "raw_document": None,
            "extracted_text": None,
            "chunks": None,
            "embeddings": None,
            "error_message": None,
        }

        ctx = self._build_trace_context(
            state=initial_state,
            request_name="INGESTION_GRAPH",
        )

        try:
            TraceLogger.info(ctx, "Ingestion graph started.")

            self.graph.invoke(initial_state)

            TraceLogger.info(ctx, "Ingestion graph completed successfully.")

        except Exception as ex:
            error_message = str(ex)

            TraceLogger.error(
                ctx,
                f"Ingestion graph failed. error={error_message}",
            )

            failure_state = initial_state.copy()
            failure_state["error_message"] = error_message

            self.handle_failure(failure_state)

            raise

    def validate_document(self, state: IngestionState) -> IngestionState:
        ctx = self._build_trace_context(
            state=state,
            request_name="VALIDATE_DOCUMENT",
        )

        db = state["db"]
        document_id = state["document_id"]
        job_id = state["job_id"]

        TraceLogger.info(ctx, "Document validation started.")

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.VALIDATING,
            stage=JobStage.VALIDATION,
        )

        self.document_service.update_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.PROCESSING,
        )

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        metadata_map = self._load_document_metadata(
            db=db,
            document_id=document.id,
        )

        raw_document = RawDocument(
            file_name=document.file_name,
            file_type=document.file_type,
            source_type=document.source_type,
            source_uri=document.source_uri,
            content=None,
            local_path=metadata_map.get("local_path"),
            storage_uri=metadata_map.get("storage_uri"),
            content_type=metadata_map.get("content_type"),
            checksum=document.checksum,
            file_size=self._safe_int(metadata_map.get("file_size")),
            metadata=metadata_map,
        )

        self._validate_raw_document(raw_document)

        state["document"] = document
        state["raw_document"] = raw_document

        TraceLogger.info(
            ctx,
            f"Document validation completed. "
            f"file_name={document.file_name}, "
            f"file_type={document.file_type}",
        )

        return state

    def extract_text(self, state: IngestionState) -> IngestionState:
        ctx = self._build_trace_context(
            state=state,
            request_name="EXTRACTION",
        )

        db = state["db"]
        job_id = state["job_id"]
        document_id = state["document_id"]
        raw_document = state["raw_document"]

        if not raw_document:
            raise ValueError("Raw document is missing from ingestion state")

        TraceLogger.info(ctx, "Text extraction started.")

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.EXTRACTING,
            stage=JobStage.EXTRACTION,
        )

        extracted_text = self.extraction_service.extract(raw_document)

        if not extracted_text or not extracted_text.strip():
            raise ValueError("No text extracted from document")

        self.document_service.update_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.EXTRACTED,
        )

        state["extracted_text"] = extracted_text.strip()

        TraceLogger.info(
            ctx,
            f"Text extraction completed. "
            f"extracted_length={len(state['extracted_text'])}",
        )

        return state

    def chunk_text(self, state: IngestionState) -> IngestionState:
        ctx = self._build_trace_context(
            state=state,
            request_name="CHUNKING",
        )

        db = state["db"]
        job_id = state["job_id"]
        document_id = state["document_id"]
        extracted_text = state["extracted_text"]

        if not extracted_text:
            raise ValueError("Extracted text is missing from ingestion state")

        TraceLogger.info(ctx, "Chunking started.")

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.CHUNKING,
            stage=JobStage.CHUNKING,
        )

        chunks = self.chunking_service.chunk_text(extracted_text)

        if not chunks:
            raise ValueError("No chunks created from extracted text")

        self.job_service.update_chunk_progress(
            db=db,
            job_id=job_id,
            total_chunks=len(chunks),
            processed_chunks=0,
        )

        self.document_service.update_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.CHUNKED,
        )

        state["chunks"] = chunks

        TraceLogger.info(
            ctx,
            f"Chunking completed. total_chunks={len(chunks)}",
        )

        return state

    def create_embeddings(self, state: IngestionState) -> IngestionState:
        ctx = self._build_trace_context(
            state=state,
            request_name="EMBEDDING",
        )

        db = state["db"]
        job_id = state["job_id"]
        document_id = state["document_id"]
        chunks = state["chunks"]

        if not chunks:
            raise ValueError("Chunks are missing from ingestion state")

        TraceLogger.info(
            ctx,
            f"Embedding started. chunks={len(chunks)}",
        )

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.EMBEDDING,
            stage=JobStage.EMBEDDING,
        )

        embeddings = self.embedding_service.create_embeddings(chunks)

        if not embeddings:
            raise ValueError("No embeddings created")

        if len(embeddings) != len(chunks):
            raise ValueError(
                f"Embedding count mismatch. "
                f"chunks={len(chunks)}, "
                f"embeddings={len(embeddings)}"
            )

        self.job_service.update_chunk_progress(
            db=db,
            job_id=job_id,
            total_chunks=len(chunks),
            processed_chunks=len(chunks),
        )

        self.document_service.update_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.EMBEDDED,
        )

        state["embeddings"] = embeddings

        TraceLogger.info(
            ctx,
            f"Embedding completed. embeddings={len(embeddings)}",
        )

        return state

    def index_vectors(self, state: IngestionState) -> IngestionState:
        ctx = self._build_trace_context(
            state=state,
            request_name="VECTOR_INDEX",
        )

        db = state["db"]
        job_id = state["job_id"]
        document_id = state["document_id"]
        document = state["document"]
        chunks = state["chunks"]
        embeddings = state["embeddings"]

        if not document:
            raise ValueError("Document is missing from ingestion state")

        if not chunks:
            raise ValueError("Chunks are missing from ingestion state")

        if not embeddings:
            raise ValueError("Embeddings are missing from ingestion state")

        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Vector indexing mismatch. "
                f"chunks={len(chunks)}, "
                f"embeddings={len(embeddings)}"
            )

        TraceLogger.info(ctx, "Vector indexing started.")

        self.job_service.update_status(
            db=db,
            job_id=job_id,
            status=JobStatus.INDEXING,
            stage=JobStage.VECTOR_INDEX,
        )

        self.vector_store_service.save_vectors(
            document_id=document_id,
            tenant_id=document.tenant_id,
            chunks=chunks,
            embeddings=embeddings,
        )

        self.document_service.update_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.INDEXED,
        )

        TraceLogger.info(
            ctx,
            f"Vector indexing completed. chunks={len(chunks)}",
        )

        return state

    def finalize_job(self, state: IngestionState) -> IngestionState:
        ctx = self._build_trace_context(
            state=state,
            request_name="FINALIZATION",
        )

        TraceLogger.info(ctx, "Finalizing ingestion job.")

        self.job_service.update_status(
            db=state["db"],
            job_id=state["job_id"],
            status=JobStatus.COMPLETED,
            stage=JobStage.FINALIZATION,
        )

        TraceLogger.info(ctx, "Ingestion job finalized successfully.")

        return state

    def handle_failure(self, state: IngestionState) -> IngestionState:
        ctx = self._build_trace_context(
            state=state,
            request_name="INGESTION_FAILURE",
        )

        error_message = (
            state.get("error_message")
            or "Unknown ingestion error"
        )

        TraceLogger.error(
            ctx,
            f"Handling ingestion failure. error={error_message}",
        )

        self.document_service.update_status(
            db=state["db"],
            document_id=state["document_id"],
            status=DocumentStatus.FAILED,
            error_message=error_message,
        )

        self.job_service.update_status(
            db=state["db"],
            job_id=state["job_id"],
            status=JobStatus.FAILED,
            stage=JobStage.FINALIZATION,
            error_message=error_message,
        )

        return state

    def _build_trace_context(
        self,
        state: IngestionState,
        request_name: str,
    ) -> TraceContext:

        return TraceContext(
            correlation_id=state["correlation_id"],
            uploaded_by=state["uploaded_by"],
            tenant_id=state["tenant_id"],
            request_name=request_name,
            document_id=str(state["document_id"]),
            job_id=str(state["job_id"]),
        )

    def _load_document_metadata(
        self,
        db: Session,
        document_id,
    ) -> dict[str, Any]:

        metadata_records = (
            self.metadata_repository.find_by_document_id(
                db=db,
                document_id=document_id,
            )
        )

        return {
            item.metadata_key: item.metadata_value
            for item in metadata_records
        }

    @staticmethod
    def _validate_raw_document(raw_document: RawDocument) -> None:

        if not raw_document.file_name:
            raise ValueError("Raw document file_name is required")

        if not raw_document.file_type:
            raise ValueError("Raw document file_type is required")

        if not raw_document.source_type:
            raise ValueError("Raw document source_type is required")

        if (
            not raw_document.content
            and not raw_document.local_path
            and not raw_document.storage_uri
        ):
            raise ValueError(
                f"No content source available for document: "
                f"{raw_document.file_name}"
            )

    @staticmethod
    def _safe_int(value) -> Optional[int]:

        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None