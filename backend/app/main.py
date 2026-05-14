from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.document_routes import router as document_router
from app.api.agent_chat_routes import router as agent_chat_router

app = FastAPI(
    title="Agentic VitechQ Copilot",
    description="Production-oriented RAG ingestion and agent chat foundation",
    version="1.0.0",
)

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(document_router)
app.include_router(agent_chat_router)


@app.get("/")
async def root():
    return {
        "message": "Agentic VitechQ Copilot API is running",
    }