from langchain_core.documents import Document as LangChainDocument

#Converts raw text to LangChain Document
class LangChainDocumentMapper:
    """
    Converts extracted text into LangChain Document format.
    """

    def to_langchain_document(
        self,
        text: str,
        tenant_id: str,
        document_id: str,
        file_name: str,
        file_type: str,
        source_uri: str,
        uploaded_by: str | None,
        correlation_id: str,
        metadata: dict | None = None,
    ) -> LangChainDocument:

        base_metadata = {
            "tenant_id": tenant_id,
            "document_id": str(document_id),
            "file_name": file_name,
            "file_type": file_type,
            "source_uri": source_uri,
            "uploaded_by": uploaded_by,
            "correlation_id": correlation_id,
        }

        if metadata:
            base_metadata.update(metadata)

        return LangChainDocument(
            page_content=text,
            metadata=base_metadata,
        )