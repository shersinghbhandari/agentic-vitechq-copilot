from fastapi import FastAPI
from app.api.document_routes import router as document_router

app = FastAPI(
    title="Agentic VitechQ Copilot",
    description="Production-oriented RAG ingestion foundation",
    version="1.0.0",
)

app.include_router(document_router)


@app.get("/")
async def root():
    return {
        "message": "Agentic VitechQ Copilot API is running",
        "upload_ui": "/documents/upload-ui",
    }