import os
import re
import logging
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Optional


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "vitechq-rag-trace.log")

os.makedirs(LOG_DIR, exist_ok=True)

#class for tracking all the log messages in strick format we want
@dataclass
class TraceContext:
    correlation_id: str
    uploaded_by: str
    tenant_id: str
    request_name: str
    document_id: Optional[str] = None
    job_id: Optional[str] = None

    def with_request_name(
            self,
            request_name: str,
    ) -> "TraceContext":
        return replace(
            self,
            request_name=request_name,
        )

class TraceLogger:

    @staticmethod
    def _safe_value(value: Optional[str]) -> str:
        value = value or "-"
        return re.sub(r"[\r\n]", " ", str(value))

    @staticmethod
    def _get_logger() -> logging.Logger:
        logger = logging.getLogger("vitechq-rag-trace")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if logger.handlers:
            return logger

        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=500 * 1024,   # 500 KB
            backupCount=5,
            encoding="utf-8",
        )

        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

        return logger

    @staticmethod
    def info(ctx: TraceContext, log_message: str):
        TraceLogger._write("INFO", ctx, log_message)

    @staticmethod
    def warning(ctx: TraceContext, log_message: str):
        TraceLogger._write("WARN", ctx, log_message)

    @staticmethod
    def error(ctx: TraceContext, log_message: str):
        TraceLogger._write("ERROR", ctx, log_message)

    @staticmethod
    def _write(level: str, ctx: TraceContext, log_message: str):
        timestamp = datetime.now(timezone.utc).isoformat()

        formatted_message = (
            f"level={level}, "
            f"uploaded_by={TraceLogger._safe_value(ctx.uploaded_by)}, "
            #f"tenant_id={TraceLogger._safe_value(ctx.tenant_id)}, "
            f"correlation_id={TraceLogger._safe_value(ctx.correlation_id)}, "
            #f"job_id={TraceLogger._safe_value(ctx.job_id)}, "
            #f"document_id={TraceLogger._safe_value(ctx.document_id)}, "
            #f"timestamp={timestamp}, "
            f"request_name={TraceLogger._safe_value(ctx.request_name)} : "
            f"{TraceLogger._safe_value(log_message)}"
        )

        TraceLogger._get_logger().info(formatted_message)

    @staticmethod
    def read_logs(
        uploaded_by: Optional[str] = None,
        correlation_id: Optional[str] = None,
        job_id: Optional[str] = None,
        document_id: Optional[str] = None,
        level: Optional[str] = None,
        max_lines: int = 300,
    ):
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()
        filters = {
            "uploaded_by": uploaded_by,
            "correlation_id": correlation_id,
            "job_id": job_id,
            "document_id": document_id,
            "level": level,
        }
        filtered = []
        for line in lines:
            matched = True
            for key, value in filters.items():
                if value:
                    search_text = f"{key}={value}"
                    if search_text.lower() not in line.lower():
                        matched = False
                        break
            if matched:
                filtered.append(line.strip())
        latest_lines = filtered[-max_lines:]
        latest_lines.reverse()
        return latest_lines