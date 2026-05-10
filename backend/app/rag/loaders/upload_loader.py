import os
import shutil
from fastapi import UploadFile
from app.core.config import settings
from app.rag.loaders.base_loader import BaseDocumentLoader
from app.rag.models.raw_document import RawDocument


class UploadDocumentLoader(BaseDocumentLoader):
    """
    Handles file uploaded from FastAPI UI.
    """

    async def load(self, file: UploadFile) -> RawDocument:
        os.makedirs(settings.RAW_UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.RAW_UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_extension = os.path.splitext(file.filename)[1].lower().replace(".", "")
        return RawDocument(
            file_name=file.filename,
            file_type=file_extension,
            source_type="UPLOAD",
            source_uri=file_path,
            local_path=file_path,
            content_type=file.content_type,
        )