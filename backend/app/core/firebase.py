"""Firebase Admin SDK — verify ID tokens issued by the client SDK.

The frontend authenticates users via Firebase Auth (email/password, Google,
GitHub). The backend only verifies ID tokens and syncs a local `User` row.
"""

from __future__ import annotations

import json
from typing import Any

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.logging import get_logger

logger = get_logger(__name__)

_app: firebase_admin.App | None = None


def _build_credentials() -> credentials.Base:
    """Load service-account credentials from path or inline JSON."""
    if settings.firebase_credentials_path:
        return credentials.Certificate(settings.firebase_credentials_path)
    if settings.firebase_credentials_json:
        return credentials.Certificate(json.loads(settings.firebase_credentials_json))
    return credentials.ApplicationDefault()


def get_firebase_app() -> firebase_admin.App:
    """Return the singleton Firebase app (lazy init)."""
    global _app
    if _app is not None:
        return _app
    if firebase_admin._apps:
        _app = firebase_admin.get_app()
        return _app

    options: dict[str, str] = {}
    if settings.firebase_project_id:
        options["projectId"] = settings.firebase_project_id

    _app = firebase_admin.initialize_app(_build_credentials(), options=options or None)
    logger.info("firebase.initialized", project_id=settings.firebase_project_id)
    return _app


def verify_firebase_token(id_token: str) -> dict[str, Any]:
    """Decode and validate a Firebase ID token. Raises `UnauthorizedError` on failure."""
    try:
        return auth.verify_id_token(id_token, app=get_firebase_app())
    except Exception as exc:
        raise UnauthorizedError("Token Firebase invalide ou expiré.") from exc


def map_firebase_provider(claims: dict[str, Any]) -> str:
    """Map Firebase sign-in provider to our `oauth_provider` enum value."""
    sign_in = claims.get("firebase", {}).get("sign_in_provider", "password")
    mapping = {
        "password": "local",
        "google.com": "google",
        "github.com": "github",
    }
    return mapping.get(sign_in, "local")


def enrich_claims_email(claims: dict[str, Any]) -> dict[str, Any]:
    """Fill missing email from Firebase Admin (common with GitHub OAuth)."""
    if claims.get("email"):
        return claims
    uid = claims.get("uid")
    if not uid:
        return claims
    try:
        record = auth.get_user(uid, app=get_firebase_app())
        if record.email:
            enriched = dict(claims)
            enriched["email"] = record.email
            enriched["email_verified"] = record.email_verified
            if record.display_name and not enriched.get("name"):
                enriched["name"] = record.display_name
            return enriched
    except Exception as exc:
        logger.warning("firebase.email_enrichment_failed", uid=uid, error=str(exc))
    return claims
