from sqlalchemy.orm import Session
from app.rag.db.document_models import DocumentMetadata


class DocumentMetadataRepository:

    def create_metadata_entries(
        self,
        db: Session,
        document_id,
        tenant_id: str,
        metadata: dict,
    ):
        metadata_rows = []
        for key, value in metadata.items():
            metadata_type = type(value).__name__.upper()
            metadata_row = DocumentMetadata(
                document_id=document_id,
                tenant_id=tenant_id,
                metadata_key=key,
                metadata_value=str(value),
                metadata_type=metadata_type,
            )
            metadata_rows.append(metadata_row)
        db.add_all(metadata_rows)
        return metadata_rows

    def find_by_document_id(self, db, document_id):
        return (
            db.query(DocumentMetadata).filter(
                DocumentMetadata.document_id == document_id
            ).all()
        )

    def find_metadata_map_by_document_id(self, db, document_id) -> dict:
        metadata_records = self.find_by_document_id(db, document_id)
        return {
            record.metadata_key: record.metadata_value
            for record in metadata_records
        }