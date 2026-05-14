import uuid
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Form,
    BackgroundTasks,
    Request,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.db_session import transactional_session
from app.core.trace_logger import TraceContext, TraceLogger

from app.rag.loaders.loader_factory import LoaderFactory
from app.rag.ingestion.checksum_service import ChecksumService

from app.rag.db.repositories.document_repository import DocumentRepository
from app.rag.db.repositories.document_metadata_repository import (
    DocumentMetadataRepository,
)
from app.rag.db.repositories.ingestion_job_repository import (
    IngestionJobRepository,
)

from app.rag.jobs.ingestion_worker import run_ingestion_job

from app.security.file_validation import (
    validate_file_name,
    validate_file_extension,
    validate_file_size,
)
from app.security.virus_scanner import VirusScanner


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

BASE_DIR = Path(__file__).resolve().parents[1]

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get(
    "/upload-ui",
    response_class=HTMLResponse,
)
async def upload_ui(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={
            "default_tenant": "default_tenant",
            "default_user": "sher",
        },
    )


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    uploaded_by: str = Form(...),
):

    correlation_id = str(uuid.uuid4())

    trace_ctx = TraceContext(
        correlation_id=correlation_id,
        uploaded_by=uploaded_by,
        tenant_id=tenant_id,
        request_name="DOCUMENT_UPLOAD",
    )

    try:

        TraceLogger.info(
            trace_ctx,
            f"Upload request received. "
            f"file={file.filename}",
        )

        raw_document, checksum = (
            await _validate_scan_and_load_file(
                file=file,
                trace_ctx=trace_ctx,
            )
        )

        db_result = _create_document_and_job(
            raw_document=raw_document,
            checksum=checksum,
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            correlation_id=correlation_id,
            trace_ctx=trace_ctx,
        )

        if db_result["status"] == "DUPLICATE":
            return db_result

        background_tasks.add_task(
            run_ingestion_job,
            db_result["document_id"],
            db_result["job_id"],
            correlation_id,
            uploaded_by,
            tenant_id,
        )

        TraceLogger.info(
            trace_ctx,
            "Background ingestion job submitted.",
        )

        return {
            "status": "QUEUED",
            "correlation_id": correlation_id,
            "message": (
                "Document uploaded successfully. "
                "Ingestion job queued."
            ),
            "document_id": str(
                db_result["document_id"]
            ),
            "metadata_count": len(
                db_result["metadata_ids"]
            ),
            "metadata_ids": db_result["metadata_ids"],
            "ingestion_job_id": str(
                db_result["job_id"]
            ),
            "checksum": checksum,
        }

    except HTTPException as ex:

        TraceLogger.error(
            trace_ctx,
            f"Upload validation failed. "
            f"file={file.filename}, "
            f"error={ex.detail}",
        )

        raise

    except Exception as ex:

        TraceLogger.error(
            trace_ctx,
            f"Upload failed. "
            f"file={file.filename}, "
            f"error={str(ex)}",
        )

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Document upload failed. "
                    "Please check logs."
                ),
                "correlation_id": correlation_id,
            },
        )


async def _validate_scan_and_load_file(
    file: UploadFile,
    trace_ctx: TraceContext,
):

    validate_file_name(file.filename)

    file_extension = validate_file_extension(
        file.filename
    )

    await validate_file_size(file)

    TraceLogger.info(
        trace_ctx,
        f"File validation passed. "
        f"file={file.filename}, "
        f"file_type={file_extension}",
    )

    loader = LoaderFactory.get_loader("UPLOAD")

    raw_document = await loader.load(file)

    # Defensive ingestion validation
    if not raw_document.content:
        raise ValueError(
            f"Raw document content is empty. "
            f"file={file.filename}"
        )

    TraceLogger.info(
        trace_ctx,
        f"File saved successfully. "
        f"path={raw_document.local_path}",
    )

    # Local filesystem scan
    if raw_document.local_path:

        VirusScanner().scan_file(
            raw_document.local_path
        )

        TraceLogger.info(
            trace_ctx,
            f"Virus validation passed. "
            f"file={file.filename}",
        )

        checksum = (
            ChecksumService.calculate_sha256(
                raw_document.local_path
            )
        )

    else:

        # Future: stream-based checksum/scanning
        raise ValueError(
            "Local file path missing for "
            "virus scan/checksum processing."
        )

    return raw_document, checksum


def _create_document_and_job(
    raw_document,
    checksum: str,
    tenant_id: str,
    uploaded_by: str,
    correlation_id: str,
    trace_ctx: TraceContext,
):

    with transactional_session() as db:

        document_repo = DocumentRepository()

        metadata_repo = (
            DocumentMetadataRepository()
        )

        job_repo = IngestionJobRepository()

        existing_document = (
            document_repo.find_by_tenant_and_checksum(
                db=db,
                tenant_id=tenant_id,
                checksum=checksum,
            )
        )

        if existing_document:

            trace_ctx.document_id = str(
                existing_document.id
            )

            TraceLogger.warning(
                trace_ctx,
                f"Duplicate document detected. "
                f"file={raw_document.file_name}, "
                f"checksum={checksum}",
            )

            return {
                "status": "DUPLICATE",
                "correlation_id": correlation_id,
                "message": (
                    "Document already exists. "
                    "Skipping ingestion."
                ),
                "existing_document_id": str(
                    existing_document.id
                ),
                "file_name": (
                    existing_document.file_name
                ),
                "checksum": checksum,
            }

        document = document_repo.create_document(
            db=db,
            tenant_id=tenant_id,
            file_name=raw_document.file_name,
            file_type=raw_document.file_type,
            source_type=raw_document.source_type,
            source_uri=raw_document.source_uri,
            checksum=checksum,
            status="QUEUED",
            uploaded_by=uploaded_by,
        )

        metadata_entries = (
            metadata_repo.create_metadata_entries(
                db=db,
                document_id=document.id,
                tenant_id=tenant_id,
                metadata={
                    "content_type": (
                        raw_document.content_type
                    ),
                    "local_path": (
                        raw_document.local_path
                    ),
                    "storage_uri": (
                        raw_document.storage_uri
                    ),
                    "source_type": (
                        raw_document.source_type
                    ),
                    "original_file_name": (
                        raw_document.file_name
                    ),
                    "correlation_id": correlation_id,
                },
            )
        )

        job = job_repo.create_job(
            db=db,
            document_id=document.id,
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            correlation_id=correlation_id,
            status="PENDING",
            stage="UPLOAD",
        )

        trace_ctx.document_id = str(document.id)

        trace_ctx.job_id = str(job.id)

        TraceLogger.info(
            trace_ctx,
            f"Document queued successfully. "
            f"file={raw_document.file_name}, "
            f"checksum={checksum}",
        )

        return {
            "status": "QUEUED",
            "document_id": document.id,
            "job_id": job.id,
            "metadata_ids": [
                str(item.id)
                for item in metadata_entries
            ],
        }


@router.get("/logs")
async def get_logs(
    uploaded_by: Optional[str] = None,
    correlation_id: Optional[str] = None,
    job_id: Optional[str] = None,
    document_id: Optional[str] = None,
    level: Optional[str] = None,
):

    logs = TraceLogger.read_logs(
        uploaded_by=uploaded_by,
        correlation_id=correlation_id,
        job_id=job_id,
        document_id=document_id,
        level=level,
    )

    return {
        "count": len(logs),
        "logs": logs,
    }