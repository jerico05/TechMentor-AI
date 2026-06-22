"""Technical quiz generation & evaluation."""

from __future__ import annotations

import json
import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.models.analysis import AnalysisHistory, QuizAttempt
from app.services.analysis_service import AnalysisService, score_to_level
from app.services.roadmap_service import RoadmapService
from app.services.rodium_client import get_rodium_client

_quiz_cache: dict[str, dict] = {}


class QuizService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.analysis = AnalysisService(db)
        self.roadmap = RoadmapService(db)

    async def generate(self, user_id: int) -> dict:
        latest = await self.analysis.get_latest(user_id)
        if not latest:
            raise ValidationError("Lancez d'abord une analyse de compétences.")

        career = await self.analysis.get_career(latest.career_path_id)
        focus = ", ".join(latest.missing_skills[:5]) or "compétences générales"

        prompt = f"""Crée un quiz technique de 5 questions QCM pour un étudiant visant le métier {career.name}.
Focus sur: {focus}.
Réponds UNIQUEMENT en JSON:
{{
  "questions": [
    {{"id": "q1", "question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0}}
  ]
}}"""

        client = get_rodium_client()
        completion = await client.chat.completions.create(
            model=settings.rodium_default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1500,
        )
        raw = completion.choices[0].message.content or "{}"
        match = re.search(r"\{.*\}", raw, re.S)
        try:
            data = json.loads(match.group() if match else raw)
        except json.JSONDecodeError:
            data = {"questions": []}

        quiz_id = uuid.uuid4().hex
        _quiz_cache[quiz_id] = {
            "user_id": user_id,
            "career_path_id": latest.career_path_id,
            "questions": data.get("questions", []),
        }
        return {
            "quiz_id": quiz_id,
            "questions": [
                {"id": q["id"], "question": q["question"], "options": q["options"]}
                for q in _quiz_cache[quiz_id]["questions"]
            ],
        }

    async def submit(self, user_id: int, quiz_id: str, answers: dict[str, int]) -> dict:
        cached = _quiz_cache.get(quiz_id)
        if not cached or cached["user_id"] != user_id:
            raise ValidationError("Quiz invalide ou expiré.")

        questions = cached["questions"]
        correct = sum(1 for q in questions if answers.get(q["id"]) == q.get("correct_index"))
        total = len(questions) or 1
        quiz_score = round(correct / total * 100)
        feedback = f"{correct}/{total} bonnes réponses — score {quiz_score}%"

        attempt = QuizAttempt(
            user_id=user_id,
            career_path_id=cached["career_path_id"],
            score=quiz_score,
            total_questions=total,
            answers=answers,
            feedback=feedback,
        )
        self.db.add(attempt)
        await self.db.flush()

        latest = await self.analysis.get_latest(user_id)
        previous_score = latest.score if latest else 0
        owned = list(latest.owned_skills) if latest else []
        missing = list(latest.missing_skills) if latest else []
        career_path_id = cached["career_path_id"]

        if quiz_score >= 80 and missing:
            owned.append(missing.pop(0))

        quiz_bonus = int(quiz_score * 0.2)
        new_score = min(100, previous_score + quiz_bonus)
        new_level = score_to_level(new_score)

        reassessment = AnalysisHistory(
            user_id=user_id,
            career_path_id=career_path_id,
            score=new_score,
            level=new_level,
            owned_skills=owned,
            missing_skills=missing,
        )
        self.db.add(reassessment)
        await self.db.commit()

        roadmap = await self.roadmap.generate(user_id, career_path_id)
        await self.db.refresh(attempt)

        del _quiz_cache[quiz_id]
        return {
            "attempt": attempt,
            "previous_score": previous_score,
            "new_score": new_score,
            "new_level": new_level,
            "roadmap_id": roadmap.id,
            "feedback": feedback,
        }

    async def get_history(self, user_id: int) -> list[QuizAttempt]:
        result = await self.db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.created_at.desc())
            .limit(20)
        )
        return list(result.scalars().all())
