"""Mentor IA - contextual chat with persistence."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.logging import get_logger
from app.database.session import AsyncSessionLocal
from app.models.analysis import Roadmap
from app.models.chat import ChatMessage, ChatSession
from app.models.cv_file import CVFile
from app.models.github_analysis import GitHubAnalysis
from app.models.user import User
from app.rag.retriever import retrieve_context_async
from app.repositories.student_profile_repository import StudentProfileRepository
from app.schemas.mentor import MentorChatRequest, MentorChatResponse
from app.services.analysis_service import AnalysisService
from app.services.llm_client import get_llm_client
from app.utils.user_level import level_label_fr, normalize_level
from app.utils.text_sanitize import sanitize_mentor_reply

logger = get_logger(__name__)

SYSTEM_PROMPT = """Tu es TechMentor, un mentor IA bienveillant et expert pour étudiants en informatique.
Tu aides sur : orientation carrière, compétences techniques, projets, stages, roadmap d'apprentissage.
Réponds en français, de façon claire et structurée. Sois concret avec des actions recommandées.
Si tu manques d'informations sur l'étudiant, pose une question ciblée.

Format de réponse : texte simple uniquement.
- N'utilise JAMAIS de markdown : pas de *, **, #, ##, ###, backticks, ni titres markdown.
- Pour structurer, utilise des numéros (1. 2. 3.) et des paragraphes courts.
- Pas de listes à puces avec des symboles *, utilise des phrases ou des numéros."""


async def _load_cv_snapshot(user_id: int) -> CVFile | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CVFile)
            .where(CVFile.user_id == user_id)
            .order_by(CVFile.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


async def _load_github_snapshot(user_id: int) -> GitHubAnalysis | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(GitHubAnalysis).where(GitHubAnalysis.user_id == user_id))
        return result.scalar_one_or_none()


async def _load_roadmap_snapshot(user_id: int) -> Roadmap | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Roadmap)
            .where(Roadmap.user_id == user_id, Roadmap.status == "active")
            .order_by(Roadmap.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


async def _load_analysis_snapshot(user_id: int) -> tuple:
    async with AsyncSessionLocal() as db:
        service = AnalysisService(db)
        latest = await service.get_latest(user_id)
        skills = await service.get_user_skills(user_id)
        return latest, skills


class MentorService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = StudentProfileRepository(db)
        self.analysis = AnalysisService(db)

    async def chat(self, user: User, payload: MentorChatRequest) -> MentorChatResponse:
        try:
            profile = await self.profile_repo.get_for_user(user.id)
            context = await self._build_context(user, profile)
            rag_context = await retrieve_context_async(payload.message)
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

            client = get_llm_client()
            completion = await client.chat.completions.create(
                model=settings.mistral_default_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            reply = sanitize_mentor_reply(
                (completion.choices[0].message.content or "Je n'ai pas pu générer de réponse.").strip()
            )

            self.db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
            self.db.add(ChatMessage(session_id=session.id, role="assistant", content=reply))
            await self.db.commit()

            return MentorChatResponse(
                reply=reply,
                model=settings.mistral_default_model,
                session_id=session.id,
            )
        except Exception as exc:
            await self.db.rollback()
            logger.exception("mentor.chat.failed", user_id=user.id, error=str(exc))
            from app.core.exceptions import AppError

            raise AppError(
                "Le mentor est temporairement indisponible. Réessayez dans un instant.",
                details=None,
            ) from exc

    async def stream_chat(self, user: User, payload: MentorChatRequest) -> AsyncIterator[str]:
        """Stream tokens via SSE. Uses dedicated DB sessions (request session closes before stream ends)."""
        user_id = user.id
        try:
            async with AsyncSessionLocal() as db:
                mentor = MentorService(db)
                profile = await mentor.profile_repo.get_for_user(user_id)
                context = await mentor._build_context(user, profile)
                rag_context = await retrieve_context_async(payload.message)
                if rag_context:
                    context = f"{context}\n\n{rag_context}"

                session = await mentor._get_or_create_session(user_id, payload.session_id)
                history_msgs: list[dict[str, str]] = []
                if payload.history:
                    history_msgs = [{"role": m.role, "content": m.content} for m in payload.history[-10:]]
                elif payload.session_id:
                    prior = await mentor.get_session_messages(user_id, session.id)
                    history_msgs = [{"role": m.role, "content": m.content} for m in prior[-10:]]

                messages = [
                    {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context}"},
                    *history_msgs,
                    {"role": "user", "content": payload.message},
                ]

                db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
                await db.commit()
                session_id = session.id

            client = get_llm_client()
            stream = await client.chat.completions.create(
                model=settings.mistral_default_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True,
            )

            full_reply = ""
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_reply += delta
                    yield f"data: {json.dumps({'token': delta})}\n\n"

            reply = sanitize_mentor_reply(full_reply.strip() or "Je n'ai pas pu générer de réponse.")

            async with AsyncSessionLocal() as db:
                db.add(ChatMessage(session_id=session_id, role="assistant", content=reply))
                await db.commit()

            yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'reply': reply})}\n\n"
        except Exception as exc:
            logger.exception("mentor.stream.failed", user_id=user_id, error=str(exc))
            yield f"data: {json.dumps({'error': 'Le mentor est temporairement indisponible. Réessayez dans un instant.'})}\n\n"

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

        user_id = user.id

        cv_row, gh_row, roadmap, analysis_snapshot = await asyncio.gather(
            _load_cv_snapshot(user_id),
            _load_github_snapshot(user_id),
            _load_roadmap_snapshot(user_id),
            _load_analysis_snapshot(user_id),
        )
        latest, skills = analysis_snapshot

        if cv_row and cv_row.extracted_text:
            lines.append(f"CV (extrait) : {cv_row.extracted_text[:800]}...")

        if gh_row:
            langs = ", ".join((gh_row.languages or {}).keys())
            lines.append(f"GitHub @{gh_row.username} : {gh_row.repo_count} repos, langages: {langs}")

        if latest:
            exp_level = level_label_fr(normalize_level(latest.level))
            lines.append(f"Niveau d'expérience : {exp_level}")
            lines.append(f"Score préparation métier : {latest.score}/100")
            lines.append(f"Compétences : {', '.join(latest.owned_skills)}")
            lines.append(f"Lacunes : {', '.join(latest.missing_skills)}")

        if roadmap and roadmap.content:
            summary = roadmap.content.get("summary", "")
            if summary:
                lines.append(f"Roadmap active : {summary[:400]}")

        if skills:
            lines.append(f"Toutes compétences détectées : {', '.join(skills)}")

        return "Contexte étudiant :\n" + "\n".join(f"- {l}" for l in lines)
