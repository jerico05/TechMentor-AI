"""Bulk user skill sync (avoids N+1 SELECT per detected skill)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill, UserSkill


async def sync_detected_skills(
    db: AsyncSession,
    user_id: int,
    detected: list[str],
    *,
    source: str,
    confidence: int,
    upgrade_github_source: bool = False,
) -> None:
    """Insert or update user skills from a detected name list."""
    if not detected:
        return

    skills = (await db.execute(select(Skill))).scalars().all()
    name_to_id = {s.name.lower(): s.id for s in skills}
    skill_ids = [name_to_id[name.lower()] for name in detected if name.lower() in name_to_id]
    if not skill_ids:
        return

    existing_rows = (
        await db.execute(
            select(UserSkill).where(
                UserSkill.user_id == user_id,
                UserSkill.skill_id.in_(skill_ids),
            )
        )
    ).scalars().all()
    existing_by_skill = {row.skill_id: row for row in existing_rows}

    for name in detected:
        skill_id = name_to_id.get(name.lower())
        if not skill_id:
            continue
        row = existing_by_skill.get(skill_id)
        if row:
            if upgrade_github_source and row.source != "cv":
                row.source = "github"
            continue
        db.add(UserSkill(user_id=user_id, skill_id=skill_id, source=source, confidence=confidence))
