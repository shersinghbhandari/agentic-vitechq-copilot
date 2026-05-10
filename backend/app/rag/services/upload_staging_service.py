# app/rag/services/upload_staging_service.py

import os
import uuid
import shutil
import hashlib

from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

from app.rag.models.staged_document import StagedDocument


class UploadStagingService:

    TEMP_DIR = "uploaded_files/temp"
    QUARANTINE_DIR = "uploaded_files/quarantine"
    APPROVED_DIR = "uploaded_files/approved"

    def __init__(self):
        os.makedirs(self.TEMP_DIR, exist_ok=True)
        os.makedirs(self.QUARANTINE_DIR, exist_ok=True)
        os.makedirs(self.APPROVED_DIR, exist_ok=True)

    async def stage(self, file: UploadFile) -> StagedDocument:

        unique_name = f"{uuid.uuid4()}_{file.filename}"

        temp_path = os.path.join(self.TEMP_DIR, unique_name)
        quarantine_path = os.path.join(self.QUARANTINE_DIR, unique_name)
        approved_path = os.path.join(self.APPROVED_DIR, unique_name)

        content = await file.read()

        with open(temp_path, "wb") as f:
            f.write(content)

        checksum = hashlib.sha256(content).hexdigest()

        return StagedDocument(
            original_filename=file.filename,
            local_path=temp_path,
            quarantine_path=quarantine_path,
            approved_path=approved_path,
            content_type=file.content_type,
            file_size=len(content),
            checksum=checksum,
            staged_at=datetime.utcnow()
        )

    async def quarantine(self, staged_document: StagedDocument):

        shutil.move(
            staged_document.local_path,
            staged_document.quarantine_path
        )

        staged_document.local_path = staged_document.quarantine_path

        return staged_document

    async def approve(self, staged_document: StagedDocument):

        shutil.move(
            staged_document.local_path,
            staged_document.approved_path
        )

        staged_document.local_path = staged_document.approved_path

        return staged_document