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
from app.rag.db.repositories.document_metadata_repository import (
    DocumentMetadataRepository,
)

from app.core.trace_logger import TraceContext, TraceLogger


class IngestionPipelineService:

    def __init__(self, db):
        self.db = db

        self.document_service = DocumentService()
        self.job_service = IngestionJobService()

        self.extraction_service = ExtractionService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService(db)

        self.metadata_repository = DocumentMetadataRepository()

    def process(
        self,
        db: Session,
        document_id,
        job_id,
        tenant_id: str | None = None,
        uploaded_by: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        ctx = None
        document = None
        try:
            document = (
                db.query(Document)
                .filter(Document.id == document_id)
                .first()
            )

            if not document:
                raise ValueError(f"Document not found: {document_id}")

            tenant_id = tenant_id or document.tenant_id
            uploaded_by = uploaded_by or document.uploaded_by
            correlation_id = correlation_id or document.correlation_id
            ctx = TraceContext(
                uploaded_by=uploaded_by,
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                document_id=str(document.id),
                job_id=str(job_id),
                request_name="INGESTION_PIPELINE",
            )

            TraceLogger.info(ctx, "Ingestion pipeline started.",)

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

            metadata = (
                self.metadata_repository
                .find_metadata_map_by_document_id(
                    db,
                    document.id,
                )
            )

            raw_document = RawDocument(
                file_name=document.file_name,
                file_type=document.file_type,
                source_type=document.source_type,
                source_uri=document.source_uri,
                local_path=metadata.get("local_path"),
                content_type=metadata.get("content_type"),
            )

            TraceLogger.info(ctx.with_request_name("EXTRACTION"), f"Starting extraction for file={document.file_name}",)

            self.job_service.update_status(
                db=db,
                job_id=job_id,
                status=JobStatus.EXTRACTING,
                stage=JobStage.EXTRACTION,
            )

            extracted_text = self.extraction_service.extract(raw_document)

            self.document_service.update_status(
                db,
                document_id,
                DocumentStatus.EXTRACTED,
            )

            TraceLogger.info(ctx.with_request_name("CHUNKING"), "Chunking started.",)

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
                db,
                document_id,
                DocumentStatus.CHUNKED,
            )

            TraceLogger.info(ctx.with_request_name("EMBEDDING"), f"Embedding started. chunks={len(chunks)}",)

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

            TraceLogger.info(ctx.with_request_name("VECTOR_INDEX"), "Vector indexing started.",)

            self.job_service.update_status(
                db=db,
                job_id=job_id,
                status=JobStatus.INDEXING,
                stage=JobStage.VECTOR_INDEX,
            )

            self.vector_store_service.save_vectors(
                document_id=document_id,
                tenant_id=tenant_id,
                chunks=chunks,
                embeddings=embeddings,
            )

            self.document_service.update_status(
                db,
                document_id,
                DocumentStatus.INDEXED,
            )

            self.job_service.update_status(
                db=db,
                job_id=job_id,
                status=JobStatus.COMPLETED,
                stage=JobStage.FINALIZATION,
            )

            TraceLogger.info(ctx.with_request_name("INGESTION_PIPELINE"), "Ingestion pipeline completed successfully.",)

        except Exception as ex:
            error_message = str(ex)

            if document:
                self.document_service.update_status(
                    db,
                    document_id,
                    DocumentStatus.FAILED,
                    error_message,
                )

                self.job_service.update_status(
                    db=db,
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    stage=JobStage.FINALIZATION,
                    error_message=error_message,
                )
                TraceLogger.error(ctx.with_request_name("INGESTION_PIPELINE"), f"Pipeline failed: {error_message}",)
            raise