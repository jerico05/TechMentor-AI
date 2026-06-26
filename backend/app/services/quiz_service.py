"""Technical quiz generation & evaluation."""

from __future__ import annotations

import json
import re
import uuid

from pydantic import BaseModel, Field, ValidationError as PydanticValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.models.analysis import AnalysisHistory, Quiz, QuizAttempt
from app.services.analysis_service import AnalysisService
from app.services.roadmap_service import RoadmapService
from app.services.llm_client import get_llm_client
from app.utils.skill_gap_score import SkillEvidence
from app.utils.user_level import compute_experience_level


class _QuizQuestionLLM(BaseModel):
    id: str
    question: str
    options: list[str]
    correct_index: int = Field(ge=0)


class _QuizLLMResponse(BaseModel):
    questions: list[_QuizQuestionLLM] = Field(default_factory=list)


def _parse_quiz_llm(raw: str) -> list[dict]:
    match = re.search(r"\{.*\}", raw, re.S)
    try:
        data = json.loads(match.group() if match else raw)
        parsed = _QuizLLMResponse.model_validate(data)
        return [q.model_dump() for q in parsed.questions]
    except (json.JSONDecodeError, PydanticValidationError):
        return []


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

        if not settings.mistral_api_key or settings.mistral_api_key == "change-me":
            raise ValidationError(
                "Génération de quiz indisponible : configurez MISTRAL_API_KEY dans le backend."
            )

        try:
            client = get_llm_client()
            completion = await client.chat.completions.create(
                model=settings.mistral_default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1500,
            )
            raw = completion.choices[0].message.content or "{}"
        except Exception as exc:
            raise ValidationError(
                "Impossible de générer un quiz pour le moment. Réessayez plus tard."
            ) from exc

        questions = _parse_quiz_llm(raw)
        if not questions:
            raise ValidationError("Impossible de générer un quiz valide. Réessayez.")

        quiz_id = uuid.uuid4().hex
        quiz = Quiz(
            quiz_id=quiz_id,
            user_id=user_id,
            career_path_id=latest.career_path_id,
            questions=questions,
        )
        self.db.add(quiz)
        await self.db.commit()

        return {
            "quiz_id": quiz_id,
            "questions": [
                {"id": q["id"], "question": q["question"], "options": q["options"]}
                for q in questions
            ],
        }

    async def submit(self, user_id: int, quiz_id: str, answers: dict[str, int]) -> dict:
        result = await self.db.execute(select(Quiz).where(Quiz.quiz_id == quiz_id))
        quiz = result.scalar_one_or_none()
        if not quiz or quiz.user_id != user_id:
            raise ValidationError("Quiz invalide ou expiré.")

        questions = quiz.questions
        correct = sum(1 for q in questions if answers.get(q["id"]) == q.get("correct_index"))
        total = len(questions) or 1
        quiz_score = round(correct / total * 100)
        feedback = f"{correct}/{total} bonnes réponses, score {quiz_score}%"

        attempt = QuizAttempt(
            user_id=user_id,
            career_path_id=quiz.career_path_id,
            score=quiz_score,
            total_questions=total,
            answers=answers,
            feedback=feedback,
        )
        self.db.add(attempt)
        await self.db.delete(quiz)
        await self.db.flush()

        latest = await self.analysis.get_latest(user_id)
        previous_score = latest.score if latest else 0
        career_path_id = quiz.career_path_id
        career = await self.analysis.get_career(career_path_id)

        extra_evidence: dict[str, SkillEvidence] = {}
        if quiz_score >= 80 and latest and latest.missing_skills:
            validated_skill = latest.missing_skills[0]
            extra_evidence[validated_skill] = SkillEvidence(
                confidence=min(95, max(80, quiz_score)),
                source="manual",
            )

        new_score, owned, missing = await self.analysis.compute_career_skill_gap(
            user_id,
            career,
            extra_evidence=extra_evidence or None,
        )
        ctx = await self.analysis._experience_context(user_id)
        new_level = compute_experience_level(
            projects_completed=ctx["projects_completed"],
            experience_years=ctx.get("experience_years"),
        )

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
