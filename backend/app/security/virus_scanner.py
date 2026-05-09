import shutil
import subprocess
from fastapi import HTTPException
from app.core.config import settings


class VirusScanner:
    """
    Virus scanner wrapper.

    Production option:
    - Use ClamAV / clamd in Docker or server environment.

    Local fallback:
    - If virus scanning is disabled, skip scan.
    """

    def scan_file(self, file_path: str) -> None:
        if not settings.ENABLE_VIRUS_SCAN:
            return

        clamscan_path = shutil.which("clamscan")

        if not clamscan_path:
            raise HTTPException(
                status_code=500,
                detail="Virus scan is enabled but clamscan is not installed",
            )

        result = subprocess.run(
            [clamscan_path, "--no-summary", file_path],
            capture_output=True,
            text=True,
        )

        if result.returncode == 1:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file failed virus scan",
            )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Virus scan failed: {result.stderr or result.stdout}",
            )