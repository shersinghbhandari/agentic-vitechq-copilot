import os
import shutil
import uuid
from fastapi import UploadFile

from app.core.config import settings
from app.rag.loaders.base_loader import BaseDocumentLoader
from app.rag.models.raw_document import RawDocument
from app.security.file_validation import (
    validate_file_name,
    validate_file_extension,
    validate_file_size,
)
from app.security.virus_scanner import VirusScanner


class UploadDocumentLoader(BaseDocumentLoader):
    """
    Handles uploaded files from FastAPI UI.

    Flow:
    1. Validate filename
    2. Validate extension
    3. Validate size
    4. Save file to raw upload folder
    5. Run virus scan
    6. Return RawDocument
    """

    def __init__(self):
        self.virus_scanner = VirusScanner()

    async def load(self, file: UploadFile) -> RawDocument:
        validate_file_name(file.filename)
        file_extension = validate_file_extension(file.filename)
        await validate_file_size(file)

        os.makedirs(settings.RAW_UPLOAD_DIR, exist_ok=True)

        unique_file_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(settings.RAW_UPLOAD_DIR, unique_file_name)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            self.virus_scanner.scan_file(file_path)

            return RawDocument(
                file_name=file.filename,
                file_type=file_extension,
                source_type="UPLOAD",
                source_uri=file_path,
                local_path=file_path,
                content_type=file.content_type,
            )

        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise