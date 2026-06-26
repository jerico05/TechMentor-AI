"""LinkedIn profile text analysis for mentor context."""

from __future__ import annotations

import json
import re

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.services.llm_client import get_llm_client
from app.utils.linkedin_fetch import (
    extract_linkedin_html_text,
    extract_text_from_linkedin_pdf,
    fetch_linkedin_html,
)
from app.utils.url_extract import extract_linkedin_slug, normalize_url

logger = get_logger(__name__)

_LINKEDIN_PDF_HINT = (
    "Sur LinkedIn : Profil > Plus > Enregistrer au format PDF, puis importez le fichier ci-dessous."
)


async def _text_from_url_or_raise(normalized: str) -> str:
    try:
        html = await fetch_linkedin_html(normalized)
        extracted = extract_linkedin_html_text(html)
        if len(extracted) >= 80:
            return extracted
    except Exception:
        pass

    raise ValidationError(
        "LinkedIn bloque l'accès direct au profil. "
        f"{_LINKEDIN_PDF_HINT}"
    )


async def _parse_with_llm(text: str, normalized: str) -> dict:
    fallback = {
        "profile_url": normalized,
        "headline": None,
        "summary": text[:600].strip() or None,
        "experiences": [],
        "education": [],
        "skills": [],
        "raw_text": text[:4000],
    }

    if not settings.mistral_api_key or settings.mistral_api_key == "change-me":
        return fallback

    prompt = f"""Extrais le parcours professionnel LinkedIn depuis ce texte.
Réponds UNIQUEMENT en JSON valide :
{{
  "headline": "titre / headline",
  "summary": "résumé du parcours en 3-4 phrases",
  "experiences": [
    {{"title": "poste", "company": "entreprise", "duration": "dates ou durée", "description": "mission courte"}}
  ],
  "education": [
    {{"school": "école", "degree": "diplôme", "duration": "dates"}}
  ],
  "skills": ["compétence1", "compétence2"]
}}

Texte:
{text[:6000]}"""

    try:
        client = get_llm_client()
        completion = await client.chat.completions.create(
            model=settings.mistral_default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1200,
        )
        raw = completion.choices[0].message.content or "{}"
        match = re.search(r"\{.*\}", raw, re.S)
        if not match:
            return fallback
        data = json.loads(match.group())
    except Exception as exc:
        logger.warning("linkedin.llm_parse.failed", error=str(exc))
        return fallback

    return {
        "profile_url": normalized,
        "headline": (str(data.get("headline")).strip()[:500] if data.get("headline") else None),
        "summary": (str(data.get("summary")).strip()[:2000] if data.get("summary") else fallback["summary"]),
        "experiences": data.get("experiences") or [],
        "education": data.get("education") or [],
        "skills": [str(s).strip() for s in (data.get("skills") or []) if str(s).strip()][:30],
        "raw_text": text[:4000],
    }


async def extract_linkedin_profile(
    url: str,
    profile_text: str | None = None,
    pdf_bytes: bytes | None = None,
) -> dict:
    normalized = normalize_url(url)
    if not extract_linkedin_slug(normalized):
        raise ValidationError("URL LinkedIn invalide. Utilisez https://linkedin.com/in/votre-profil")

    if pdf_bytes:
        try:
            text = extract_text_from_linkedin_pdf(pdf_bytes)
        except ValueError as exc:
            raise ValidationError(f"{exc} {_LINKEDIN_PDF_HINT}") from exc
        return await _parse_with_llm(text, normalized)

    pasted = (profile_text or "").strip()
    if pasted:
        if len(pasted) < 80:
            raise ValidationError(
                "Texte trop court. Collez au moins vos expériences et compétences, "
                f"ou utilisez l'export PDF. {_LINKEDIN_PDF_HINT}"
            )
        return await _parse_with_llm(pasted, normalized)

    text = await _text_from_url_or_raise(normalized)
    return await _parse_with_llm(text, normalized)
