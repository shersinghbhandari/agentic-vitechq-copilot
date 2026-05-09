from app.rag.db.repositories.document_repository import DocumentRepository


class DuplicateService:

    def __init__(self):
        self.document_repository = DocumentRepository()

    def check_duplicate(self, tenant_id: str, checksum: str):
        return self.document_repository.find_by_tenant_and_checksum(
            tenant_id=tenant_id,
            checksum=checksum,
        )