"""LLM helpers for structured extraction."""

from __future__ import annotations

import json
import re

from app.core.config import settings
from app.core.logging import get_logger
from app.services.llm_client import get_llm_client

logger = get_logger(__name__)


async def extract_skills_from_text(text: str, known_skills: list[str]) -> list[str]:
    """Extract skill names from CV/GitHub text using keyword match + optional LLM."""
    if not text.strip():
        return []

    known_lower = {s.lower(): s for s in known_skills}
    found: set[str] = set()

    for skill in known_skills:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.I):
            found.add(skill)

    if not settings.mistral_api_key or settings.mistral_api_key == "change-me":
        return sorted(found)

    snippet = text[:6000]
    prompt = f"""Extrais les compétences techniques du texte suivant.
Réponds UNIQUEMENT avec un JSON array de strings, ex: ["Python", "SQL"].
Utilise de préférence ces compétences connues si présentes: {', '.join(known_skills[:40])}.

Texte:
{snippet}"""

    try:
        import asyncio

        client = get_llm_client()
        completion = await asyncio.wait_for(
            client.chat.completions.create(
                model=settings.mistral_default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=512,
            ),
            timeout=settings.llm_timeout_seconds,
        )
        raw = completion.choices[0].message.content or "[]"
        match = re.search(r"\[.*\]", raw, re.S)
        if match:
            parsed = json.loads(match.group())
            for item in parsed:
                if isinstance(item, str):
                    key = item.strip().lower()
                    found.add(known_lower.get(key, item.strip()))
    except Exception as exc:
        logger.warning("llm.skill_extract.failed", error=str(exc))

    return sorted(found)
