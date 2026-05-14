from sqlalchemy.orm import Session

from app.rag.db.document_models import Document
from app.rag.enums.document_status import DocumentStatus
from app.rag.models.raw_document import RawDocument


class DocumentService:
    """
    Centralized document persistence service.

    Future:
    - object storage integration
    - metadata enrichment
    - distributed ingestion support
    """

    def create_uploaded_document(
        self,
        db: Session,
        raw_document: RawDocument,
        tenant_id: str,
        uploaded_by: str,
        correlation_id: str,
    ) -> Document:

        metadata = {
            "content_type": raw_document.content_type,
            "correlation_id": correlation_id,
        }

        if raw_document.local_path:
            metadata["local_path"] = raw_document.local_path

        if raw_document.storage_uri:
            metadata["storage_uri"] = raw_document.storage_uri

        document = Document(
            tenant_id=tenant_id,
            source_type=raw_document.source_type,
            source_uri=raw_document.source_uri,
            file_name=raw_document.file_name,
            file_type=raw_document.file_type,
            checksum=getattr(raw_document, "checksum", None),
            uploaded_by=uploaded_by,
            status=DocumentStatus.QUEUED.value,
            metadata_json=metadata,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    def update_status(
        self,
        db: Session,
        document_id,
        status: DocumentStatus,
        error_message: str | None = None,
    ) -> None:

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        document.status = status.value

        metadata = document.metadata_json or {}

        if error_message:
            metadata["error_message"] = error_message

        document.metadata_json = metadata

        db.commit()