from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()

class ChatSendRequest(BaseModel):
    user: str
    text: str

class ChatMessage(BaseModel):
    id: str
    user: str
    text: str
    timestamp: str

chat_history: list[ChatMessage] = []

@router.post("/chat/send")
async def send_chat(body: ChatSendRequest):
    message = ChatMessage(
        id=str(uuid.uuid4()),
        user=body.user,
        text=body.text,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    chat_history.append(message)
    return {"ok": True, "message": message}

@router.get("/chat/history", response_model=list[ChatMessage])
async def get_history():
    return chat_history

@router.post("/chat/clear")
async def clear_chat():
    global chat_history
    chat_history = []
    return {"ok": True}