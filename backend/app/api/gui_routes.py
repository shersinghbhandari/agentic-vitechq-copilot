# backend/app/api/gui_routes.py

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(
    tags=["GUI"],
)


@router.get("/agent-chat")
async def agent_chat_ui():

    project_root = Path(__file__).resolve().parents[3]

    html_file = project_root / "gui" / "agent-chat.html"

    return FileResponse(
        path=str(html_file),
        media_type="text/html",
    )