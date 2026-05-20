# backend/app/main.py

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.agent_chat_routes import (
    router as agent_chat_router,
)
from app.api.document_routes import (
    router as document_router,
)

app = FastAPI(
    title="Agentic VitechQ Copilot",
    description=(
        "Production-oriented RAG ingestion "
        "and agent chat foundation"
    ),
    version="1.0.0",
)

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

# Future direction:
# Support production UI hosting and CDN/static asset separation.
if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )

# Document ingestion APIs.
app.include_router(document_router)

# Agentic orchestration APIs.
app.include_router(agent_chat_router)


@app.get("/")
async def root():
    """
    API health and navigation endpoint.

    Architectural Purpose
    ---------------------
    Provides lightweight discovery for:
    - local development
    - demos
    - interview walkthroughs
    - orchestration validation
    """

    return {
        "message": (
            "Agentic VitechQ Copilot API is running"
        ),
        "document_upload_ui": (
            "/documents/upload-ui"
        ),
        "agent_chat_ui": (
            "/agent/chat-ui"
        ),
        "agent_chat_api": (
            "/agent/chat"
        ),
        "agent_logs": (
            "/agent/logs"
        ),
    }


# Temporary debugging support.
# Remove after routing verification.
for route in app.routes:
    print(route.path)