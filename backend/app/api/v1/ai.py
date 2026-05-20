import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import monitor_ai

router = APIRouter(tags=["ai"])


class ChatRequest(BaseModel):
    message: str
    service_id: uuid.UUID | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    reply = await monitor_ai.chat(body.message, body.service_id, db)
    return ChatResponse(reply=reply)
