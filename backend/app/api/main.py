from fastapi import FastAPI
from app.api.document_routes import router as document_router
from app.api.agent_chat_routes import router as agent_chat_router

app = FastAPI(
    title="Agentic VitechQ Copilot",
    description="Production-oriented RAG ingestion and agentic chat foundation",
    version="1.0.0",
)

app.include_router(document_router)
app.include_router(agent_chat_router)


@app.get("/")
async def root():
    return {
        "message": "Agentic VitechQ Copilot API is running",
    }