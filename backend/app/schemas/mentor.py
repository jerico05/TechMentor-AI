"""Mentor IA chat schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=8000)


class MentorChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    session_id: int | None = None


class MentorChatResponse(BaseModel):
    reply: str
    model: str
    session_id: int | None = None


class ChatSessionOut(BaseModel):
    id: int
    title: str
    created_at: str


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: str
