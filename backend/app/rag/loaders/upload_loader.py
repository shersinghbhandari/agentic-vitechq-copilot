import hashlib
import os

from fastapi import UploadFile

from app.core.config import settings
from app.rag.loaders.base_loader import (
    BaseDocumentLoader,
)
from app.rag.models.raw_document import RawDocument


class UploadDocumentLoader(BaseDocumentLoader):
    """
    Handles file uploaded from FastAPI UI.

    Current:
    - byte-stream ingestion
    - local filesystem persistence

    Future:
    - S3/object storage
    - distributed ingestion workers
    - stream-based ingestion
    """

    async def load(
        self,
        file: UploadFile,
    ) -> RawDocument:

        if not file:
            raise ValueError("file is required")

        if not file.filename:
            raise ValueError("file filename is required")

        os.makedirs(
            settings.RAW_UPLOAD_DIR,
            exist_ok=True,
        )

        file_path = os.path.join(
            settings.RAW_UPLOAD_DIR,
            file.filename,
        )

        # Preferred distributed-safe ingestion
        file_bytes = await file.read()

        if not file_bytes:
            raise ValueError(
                f"Uploaded file is empty: {file.filename}"
            )

        # Local dev persistence
        with open(file_path, "wb") as buffer:

            buffer.write(file_bytes)

        file_extension = (
            os.path.splitext(file.filename)[1]
            .lower()
            .replace(".", "")
        )

        checksum = hashlib.sha256(
            file_bytes
        ).hexdigest()

        return RawDocument(
            file_name=file.filename,
            file_type=file_extension,
            source_type="UPLOAD",
            source_uri=file_path,

            # Preferred production-safe content
            content=file_bytes,

            # Local dev fallback
            local_path=file_path,

            # Future cloud-native ingestion
            storage_uri=None,

            content_type=file.content_type,
            checksum=checksum,
            file_size=len(file_bytes),

            metadata={
                "checksum": checksum,
                "file_size": len(file_bytes),
                "content_type": file.content_type,
                "local_path": file_path,
            },
        )