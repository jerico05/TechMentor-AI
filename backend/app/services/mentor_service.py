"""Mentor IA — contextual chat with persistence."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.logging import get_logger
from app.models.analysis import Roadmap
from app.models.chat import ChatMessage, ChatSession
from app.models.cv_file import CVFile
from app.models.github_analysis import GitHubAnalysis
from app.models.user import User
from app.rag.retriever import retrieve_context
from app.repositories.student_profile_repository import StudentProfileRepository
from app.schemas.mentor import MentorChatRequest, MentorChatResponse
from app.services.analysis_service import AnalysisService
from app.services.rodium_client import get_rodium_client

logger = get_logger(__name__)

SYSTEM_PROMPT = """Tu es TechMentor, un mentor IA bienveillant et expert pour étudiants en informatique.
Tu aides sur : orientation carrière, compétences techniques, projets, stages, roadmap d'apprentissage.
Réponds en français, de façon claire et structurée. Sois concret avec des actions recommandées.
Si tu manques d'informations sur l'étudiant, pose une question ciblée."""


class MentorService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = StudentProfileRepository(db)
        self.analysis = AnalysisService(db)

    async def chat(self, user: User, payload: MentorChatRequest) -> MentorChatResponse:
        profile = await self.profile_repo.get_for_user(user.id)
        context = await self._build_context(user, profile)
        rag_context = retrieve_context(payload.message)
        if rag_context:
            context = f"{context}\n\n{rag_context}"

        session = await self._get_or_create_session(user.id, payload.session_id)
        history_msgs: list[dict[str, str]] = []
        if payload.history:
            history_msgs = [{"role": m.role, "content": m.content} for m in payload.history[-10:]]
        elif payload.session_id:
            prior = await self.get_session_messages(user.id, session.id)
            history_msgs = [{"role": m.role, "content": m.content} for m in prior[-10:]]

        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context}"},
            *history_msgs,
            {"role": "user", "content": payload.message},
        ]

        client = get_rodium_client()
        completion = await client.chat.completions.create(
            model=settings.rodium_default_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        reply = (completion.choices[0].message.content or "Je n'ai pas pu générer de réponse.").strip()

        self.db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
        self.db.add(ChatMessage(session_id=session.id, role="assistant", content=reply))
        await self.db.commit()

        return MentorChatResponse(
            reply=reply,
            model=settings.rodium_default_model,
            session_id=session.id,
        )

    async def stream_chat(self, user: User, payload: MentorChatRequest) -> AsyncIterator[str]:
        profile = await self.profile_repo.get_for_user(user.id)
        context = await self._build_context(user, profile)
        rag_context = retrieve_context(payload.message)
        if rag_context:
            context = f"{context}\n\n{rag_context}"

        session = await self._get_or_create_session(user.id, payload.session_id)
        history_msgs: list[dict[str, str]] = []
        if payload.history:
            history_msgs = [{"role": m.role, "content": m.content} for m in payload.history[-10:]]
        elif payload.session_id:
            prior = await self.get_session_messages(user.id, session.id)
            history_msgs = [{"role": m.role, "content": m.content} for m in prior[-10:]]

        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context}"},
            *history_msgs,
            {"role": "user", "content": payload.message},
        ]

        self.db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
        await self.db.flush()

        client = get_rodium_client()
        stream = await client.chat.completions.create(
            model=settings.rodium_default_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            stream=True,
        )

        full_reply = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full_reply += delta
                yield f"data: {json.dumps({'token': delta})}\n\n"

        reply = full_reply.strip() or "Je n'ai pas pu générer de réponse."
        self.db.add(ChatMessage(session_id=session.id, role="assistant", content=reply))
        await self.db.commit()
        yield f"data: {json.dumps({'done': True, 'session_id': session.id, 'reply': reply})}\n\n"

    async def list_sessions(self, user_id: int) -> list[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(50)
        )
        return list(result.scalars().all())

    async def get_session_messages(self, user_id: int, session_id: int) -> list[ChatMessage]:
        session = await self.db.get(ChatSession, session_id)
        if not session or session.user_id != user_id:
            return []
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def _get_or_create_session(self, user_id: int, session_id: int | None) -> ChatSession:
        if session_id:
            result = await self.db.execute(
                select(ChatSession)
                .options(selectinload(ChatSession.messages))
                .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
            )
            session = result.scalar_one_or_none()
            if session:
                return session
        session = ChatSession(user_id=user_id)
        self.db.add(session)
        await self.db.flush()
        return session

    async def _build_context(self, user: User, profile) -> str:  # type: ignore[no-untyped-def]
        lines = [f"Étudiant : {user.firstname} {user.lastname}", f"Email : {user.email}"]
        if profile:
            if profile.university:
                lines.append(f"Université : {profile.university}")
            if profile.department:
                lines.append(f"Filière : {profile.department}")
            lines.append(f"Niveau : {profile.academic_level}")
            if profile.career_goal:
                lines.append(f"Objectif carrière : {profile.career_goal}")
            if profile.github_url:
                lines.append(f"GitHub : {profile.github_url}")
            if profile.bio:
                lines.append(f"Bio : {profile.bio}")

        cv = await self.db.execute(
            select(CVFile).where(CVFile.user_id == user.id).order_by(CVFile.created_at.desc()).limit(1)
        )
        cv_row = cv.scalar_one_or_none()
        if cv_row and cv_row.extracted_text:
            lines.append(f"CV (extrait) : {cv_row.extracted_text[:800]}...")

        gh = await self.db.execute(select(GitHubAnalysis).where(GitHubAnalysis.user_id == user.id))
        gh_row = gh.scalar_one_or_none()
        if gh_row:
            langs = ", ".join((gh_row.languages or {}).keys())
            lines.append(f"GitHub @{gh_row.username} : {gh_row.repo_count} repos, langages: {langs}")

        latest = await self.analysis.get_latest(user.id)
        if latest:
            lines.append(f"Score compétences : {latest.score}/100 ({latest.level})")
            lines.append(f"Compétences : {', '.join(latest.owned_skills)}")
            lines.append(f"Lacunes : {', '.join(latest.missing_skills)}")

        roadmap = (
            await self.db.execute(
                select(Roadmap)
                .where(Roadmap.user_id == user.id, Roadmap.status == "active")
                .order_by(Roadmap.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if roadmap and roadmap.content:
            summary = roadmap.content.get("summary", "")
            if summary:
                lines.append(f"Roadmap active : {summary[:400]}")

        skills = await self.analysis.get_user_skills(user.id)
        if skills:
            lines.append(f"Toutes compétences détectées : {', '.join(skills)}")

        return "Contexte étudiant :\n" + "\n".join(f"- {l}" for l in lines)
