import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Form,
    Depends,
    BackgroundTasks,
)
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db_session
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


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/upload-ui", response_class=HTMLResponse)
async def upload_ui():
    return """
    <html>
        <head>
            <title>VitechQ RAG Upload</title>
            <style>
                body { font-family: Arial; margin: 30px; background: #f7f7f7; }
                .container { display: flex; gap: 20px; }
                .left, .right {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 8px #ddd;
                }
                .left { width: 35%; }
                .right { width: 60%; }
                input, select { padding: 6px; margin-top: 4px; }
                button { padding: 8px 12px; cursor: pointer; }
                .tabs button { margin-right: 5px; }
                .tab-content {
                    margin-top: 15px;
                    background: #111;
                    color: #0f0;
                    padding: 15px;
                    height: 420px;
                    overflow-y: auto;
                    white-space: pre-wrap;
                    font-family: Consolas, monospace;
                    font-size: 13px;
                }
                .success { color: green; font-weight: bold; }
                .error { color: red; font-weight: bold; }
                .warn { color: orange; font-weight: bold; }
                .log-filter {
                    background: #f2f2f2;
                    padding: 10px;
                    border-radius: 6px;
                    margin-top: 10px;
                }
                .log-filter input {
                    width: 180px;
                    margin-right: 5px;
                    margin-bottom: 5px;
                }
            </style>
        </head>

        <body>
            <h2>VitechQ RAG - Document Upload</h2>

            <div class="container">
                <div class="left">
                    <form id="uploadForm">
                        <label>Tenant ID:</label><br>
                        <input name="tenant_id" id="tenant_id" type="text" value="default_tenant" required>
                        <br><br>

                        <label>User Name:</label><br>
                        <input name="uploaded_by" id="uploaded_by" type="text" value="sher" required>
                        <br><br>

                        <label>Select File:</label><br>
                        <input name="file" type="file" required>
                        <br><br>

                        <button type="submit">Upload</button>
                    </form>

                    <p><b>Supported:</b> PDF, TXT, Java, SQL, Images, Excel, CSV, DOCX</p>
                </div>

                <div class="right">
                    <div class="tabs">
                        <button onclick="showTab('result')">Upload Result</button>
                        <button onclick="showTab('logs')">User Logs</button>
                    </div>

                    <div id="resultTab" class="tab-content">
                        Upload result will appear here.
                    </div>

                    <div id="logsContainer" style="display:none;">
                        <div class="log-filter">
                            <input id="log_uploaded_by" placeholder="Search username">
                            <input id="log_correlation_id" placeholder="Correlation ID">
                            <input id="log_job_id" placeholder="Job ID">
                            <input id="log_document_id" placeholder="Document ID">

                            <select id="log_level">
                                <option value="">All Levels</option>
                                <option value="INFO">INFO</option>
                                <option value="WARN">WARN</option>
                                <option value="ERROR">ERROR</option>
                            </select>

                            <button onclick="loadLogs()">Search Logs</button>
                        </div>

                        <div id="logsTab" class="tab-content">
                            Logs will appear here.
                        </div>
                    </div>
                </div>
            </div>

            <script>
                function showTab(tab) {
                    document.getElementById("resultTab").style.display =
                        tab === "result" ? "block" : "none";

                    document.getElementById("logsContainer").style.display =
                        tab === "logs" ? "block" : "none";

                    if (tab === "logs") {
                        document.getElementById("log_uploaded_by").value =
                            document.getElementById("uploaded_by").value;

                        document.getElementById("log_uploaded_by").disabled = true;
                        loadLogs();
                    }
                }

                document.getElementById("uploadForm").addEventListener("submit", async function(event) {
                    event.preventDefault();

                    const form = document.getElementById("uploadForm");
                    const formData = new FormData(form);

                    const resultTab = document.getElementById("resultTab");
                    resultTab.innerHTML = "Uploading...";

                    try {
                        const response = await fetch("/documents/upload", {
                            method: "POST",
                            body: formData
                        });

                        const data = await response.json();

                        if (response.ok) {
                            resultTab.innerHTML =
                                "<div class='success'>SUCCESS</div><br>" +
                                "<pre>" + escapeHtml(JSON.stringify(data, null, 2)) + "</pre>";
                        } else {
                            resultTab.innerHTML =
                                "<div class='error'>FAILED</div><br>" +
                                "<pre>" + escapeHtml(JSON.stringify(data, null, 2)) + "</pre>";
                        }

                        showTab("result");
                    } catch (error) {
                        resultTab.innerHTML =
                            "<div class='error'>FAILED</div><br>" +
                            escapeHtml(String(error));
                    }
                });

                async function loadLogs() {
                    const uploadedBy = document.getElementById("log_uploaded_by").value;
                    const correlationId = document.getElementById("log_correlation_id").value;
                    const jobId = document.getElementById("log_job_id").value;
                    const documentId = document.getElementById("log_document_id").value;
                    const level = document.getElementById("log_level").value;

                    const params = new URLSearchParams();

                    if (uploadedBy) params.append("uploaded_by", uploadedBy);
                    if (correlationId) params.append("correlation_id", correlationId);
                    if (jobId) params.append("job_id", jobId);
                    if (documentId) params.append("document_id", documentId);
                    if (level) params.append("level", level);

                    const response = await fetch("/documents/logs?" + params.toString());
                    const data = await response.json();

                    const logHtml = data.logs.map(line => {
                        const lower = line.toLowerCase();

                        if (
                            lower.includes("level=error") ||
                            lower.includes("failed") ||
                            lower.includes("failure") ||
                            lower.includes("exception") ||
                            lower.includes("virus detected") ||
                            lower.includes("malware")
                        ) {
                            return "<div style='color:red; font-weight:bold;'>" + escapeHtml(line) + "</div>";
                        }

                        if (lower.includes("level=warn") || lower.includes("duplicate")) {
                            return "<div style='color:orange; font-weight:bold;'>" + escapeHtml(line) + "</div>";
                        }

                        return "<div style='color:#00ff66;'>" + escapeHtml(line) + "</div>";
                    }).join("");

                    document.getElementById("logsTab").innerHTML =
                        "<b>Total Logs: " + data.count + "</b><br><br>" + logHtml;
                }

                function escapeHtml(text) {
                    return text
                        .replaceAll("&", "&amp;")
                        .replaceAll("<", "&lt;")
                        .replaceAll(">", "&gt;");
                }
            </script>
        </body>
    </html>
    """


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    uploaded_by: str = Form(...),
    db: Session = Depends(get_db_session),
):
    correlation_id = str(uuid.uuid4())

    trace_ctx = TraceContext(
        correlation_id=correlation_id,
        uploaded_by=uploaded_by,
        tenant_id=tenant_id,
        request_name="DOCUMENT_UPLOAD",
    )

    TraceLogger.info(
        trace_ctx,
        f"Upload request received. file={file.filename}",
    )

    try:
        validate_file_name(file.filename)
        file_extension = validate_file_extension(file.filename)
        await validate_file_size(file)

        TraceLogger.info(
            trace_ctx,
            f"File validation passed. file={file.filename}, file_type={file_extension}",
        )

        loader = LoaderFactory.get_loader("UPLOAD")
        raw_document = await loader.load(file)

        TraceLogger.info(
            trace_ctx,
            f"File saved successfully. path={raw_document.local_path}",
        )

        virus_scanner = VirusScanner()
        virus_scanner.scan_file(raw_document.local_path)

        TraceLogger.info(
            trace_ctx,
            f"Virus validation passed. file={file.filename}",
        )

        checksum = ChecksumService.calculate_sha256(raw_document.local_path)

        document_repo = DocumentRepository()
        metadata_repo = DocumentMetadataRepository()
        job_repo = IngestionJobRepository()

        existing_document = document_repo.find_by_tenant_and_checksum(
            db=db,
            tenant_id=tenant_id,
            checksum=checksum,
        )

        if existing_document:
            trace_ctx.document_id = str(existing_document.id)

            TraceLogger.warning(
                trace_ctx,
                f"Duplicate document detected. file={file.filename}, checksum={checksum}",
            )

            db.rollback()

            return {
                "status": "DUPLICATE",
                "correlation_id": correlation_id,
                "message": "Document already exists. Skipping ingestion.",
                "existing_document_id": str(existing_document.id),
                "file_name": existing_document.file_name,
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

        metadata_entries = metadata_repo.create_metadata_entries(
            db=db,
            document_id=document.id,
            tenant_id=tenant_id,
            metadata={
                "content_type": raw_document.content_type,
                "local_path": raw_document.local_path,
                "source_type": raw_document.source_type,
                "original_file_name": raw_document.file_name,
                "correlation_id": correlation_id,
            },
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
            f"Document queued successfully. file={file.filename}, checksum={checksum}",
        )

        db.commit()

        background_tasks.add_task(
            run_ingestion_job,
            document.id,
            job.id,
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
            "message": "Document uploaded successfully. Ingestion job queued.",
            "document_id": str(document.id),
            "metadata_count": len(metadata_entries),
            "metadata_ids": [str(item.id) for item in metadata_entries],
            "ingestion_job_id": str(job.id),
            "checksum": checksum,
        }

    except HTTPException as ex:
        db.rollback()

        TraceLogger.error(
            trace_ctx,
            f"Upload validation failed. file={file.filename}, error={ex.detail}",
        )

        raise ex

    except Exception as ex:
        db.rollback()

        TraceLogger.error(
            trace_ctx,
            f"Upload failed. file={file.filename}, error={str(ex)}",
        )

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Document upload failed. Please check logs.",
                "correlation_id": correlation_id,
            },
        )


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