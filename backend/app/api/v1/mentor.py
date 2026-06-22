"""Mentor IA endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import CurrentUser, DBSession
from app.core.exceptions import NotFoundError
from app.schemas.mentor import ChatMessageOut, ChatSessionOut, MentorChatRequest, MentorChatResponse
from app.services.mentor_service import MentorService

router = APIRouter()


def get_mentor_service(db: DBSession) -> MentorService:
    return MentorService(db)


@router.post("/chat", response_model=MentorChatResponse, summary="Chat with the AI mentor")
async def mentor_chat(
    payload: MentorChatRequest,
    current: CurrentUser,
    service: MentorService = Depends(get_mentor_service),
) -> MentorChatResponse:
    return await service.chat(current, payload)


@router.post("/chat/stream", summary="Stream chat with the AI mentor (SSE)")
async def mentor_chat_stream(
    payload: MentorChatRequest,
    current: CurrentUser,
    service: MentorService = Depends(get_mentor_service),
) -> StreamingResponse:
    return StreamingResponse(
        service.stream_chat(current, payload),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/sessions", response_model=list[ChatSessionOut], summary="List chat sessions")
async def list_sessions(
    current: CurrentUser,
    service: MentorService = Depends(get_mentor_service),
) -> list[ChatSessionOut]:
    sessions = await service.list_sessions(current.id)
    return [
        ChatSessionOut(
            id=s.id,
            title=s.title,
            created_at=s.created_at.isoformat() if s.created_at else "",
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut], summary="Session messages")
async def get_session_messages(
    session_id: int,
    current: CurrentUser,
    service: MentorService = Depends(get_mentor_service),
) -> list[ChatMessageOut]:
    messages = await service.get_session_messages(current.id, session_id)
    if not messages:
        sessions = await service.list_sessions(current.id)
        if not any(s.id == session_id for s in sessions):
            raise NotFoundError("Session introuvable.")
    return [
        ChatMessageOut(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat() if m.created_at else "",
        )
        for m in messages
    ]
