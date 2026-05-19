# backend/app/main.py

from fastapi import FastAPI

from app.api.chat_routes import router as chat_router

app = FastAPI(
    title="Agentic VitechQ Copilot",
    description="LangChain + LangGraph based agentic chat framework",
    version="1.0.0",
)

app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "Agentic VitechQ Copilot API is running",
        "chat_url": "/agent/chat",
    }