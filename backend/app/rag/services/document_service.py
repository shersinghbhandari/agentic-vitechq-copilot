from sqlalchemy.orm import Session

from app.rag.enums.document_status import DocumentStatus
from app.rag.models.raw_document import RawDocument
from app.rag.db.document_models import Document

class DocumentService:

    def create_uploaded_document(
        self,
        db: Session,
        raw_document: RawDocument,
        tenant_id: str,
        uploaded_by: str,
        correlation_id: str,
    ) -> Document:

        document = Document(
            tenant_id=tenant_id,
            source_type=raw_document.source_type,
            source_uri=raw_document.source_uri,
            file_name=raw_document.file_name,
            file_type=raw_document.file_type,
            checksum=getattr(raw_document, "checksum", None),
            uploaded_by=uploaded_by,
            status=DocumentStatus.QUEUED.value,
            metadata_json={
                "content_type": raw_document.content_type,
                "local_path": raw_document.local_path,
                "correlation_id": correlation_id,
            },
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

        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        document.status = status.value

        if error_message:
            metadata = document.metadata_json or {}
            metadata["error_message"] = error_message
            document.metadata_json = metadata

        db.commit()