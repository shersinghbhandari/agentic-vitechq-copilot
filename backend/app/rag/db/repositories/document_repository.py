from sqlalchemy.orm import Session
from app.rag.db.document_models import Document


class DocumentRepository:

    def find_by_tenant_and_checksum(
        self,
        db: Session,
        tenant_id: str,
        checksum: str,
    ):
        return (
            db.query(Document)
            .filter(
                Document.tenant_id == tenant_id,
                Document.checksum == checksum,
            )
            .first()
        )

    def create_document(
        self,
        db: Session,
        tenant_id: str,
        file_name: str,
        file_type: str,
        source_type: str,
        source_uri: str,
        checksum: str,
        status: str,
        uploaded_by: str,
    ):
        document = Document(
            tenant_id=tenant_id,
            file_name=file_name,
            file_type=file_type,
            source_type=source_type,
            source_uri=source_uri,
            checksum=checksum,
            status=status,
            uploaded_by=uploaded_by,
        )

        db.add(document)
        db.flush()
        # optional but safer when UUID/default values
        db.refresh(document)
        return document
