import os
import re
from fastapi import UploadFile, HTTPException
from app.core.config import settings


ALLOWED_EXTENSIONS = {
    "pdf", "docx", "txt", "csv", "xlsx", "xls", "java", "sql", "py", "md"
}

SAFE_FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.\- ]+$")


def validate_file_name(filename: str) -> None:
    if not filename:
        raise HTTPException(status_code=400, detail="File name is missing")

    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid file name")

    if not SAFE_FILENAME_PATTERN.match(filename):
        raise HTTPException(
            status_code=400,
            detail="File name contains unsafe characters"
        )


def validate_file_extension(filename: str) -> str:
    extension = os.path.splitext(filename)[1].lower().replace(".", "")

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )

    return extension


async def validate_file_size(file: UploadFile) -> None:
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max allowed size is {settings.MAX_UPLOAD_SIZE_MB} MB"
        )