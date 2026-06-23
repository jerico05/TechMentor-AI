"""Firebase securetoken public keys - fetch with offline fallback."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import jwt
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_CERTS_URL = (
    "https://www.googleapis.com/robot/v1/metadata/x509/"
    "securetoken@system.gserviceaccount.com"
)
_BUNDLED_CERTS = Path(__file__).resolve().parent.parent.parent / "data" / "firebase_securetoken_certs.json"
_CACHE_TTL_SECONDS = 3600

_cached_keys: dict[str, str] | None = None
_cache_expires_at = 0.0


def _pem_from_x509(cert_pem: str) -> str:
    cert = x509.load_pem_x509_certificate(cert_pem.encode())
    public_key = cert.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()


def _load_bundled_certs() -> dict[str, str]:
    if not _BUNDLED_CERTS.is_file():
        return {}
    raw = json.loads(_BUNDLED_CERTS.read_text(encoding="utf-8"))
    return {kid: _pem_from_x509(pem) for kid, pem in raw.items()}


def _fetch_remote_certs(timeout: float = 5.0) -> dict[str, str]:
    import urllib.request

    with urllib.request.urlopen(_CERTS_URL, timeout=timeout) as response:
        raw = json.loads(response.read().decode())
    return {kid: _pem_from_x509(pem) for kid, pem in raw.items()}


def get_firebase_public_keys(*, force_refresh: bool = False) -> dict[str, str]:
    """Return kid → PEM public keys, with in-memory cache and bundled fallback."""
    global _cached_keys, _cache_expires_at

    now = time.time()
    if not force_refresh and _cached_keys and _cache_expires_at > now:
        return _cached_keys

    keys: dict[str, str] = {}
    try:
        keys = _fetch_remote_certs()
        logger.info("firebase.certs_fetched_remote", count=len(keys))
    except Exception as exc:
        logger.warning("firebase.certs_remote_failed", error=str(exc))
        keys = _load_bundled_certs()
        if keys:
            logger.info("firebase.certs_loaded_bundled", count=len(keys))

    if not keys:
        raise RuntimeError("Impossible de charger les certificats Firebase.")

    _cached_keys = keys
    _cache_expires_at = now + _CACHE_TTL_SECONDS
    return keys


def verify_id_token_local(id_token: str) -> dict[str, Any]:
    """Verify a Firebase ID token using cached Google public keys (no Admin SDK network)."""
    header = jwt.get_unverified_header(id_token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("Token sans kid.")

    keys = get_firebase_public_keys()
    public_key = keys.get(kid)
    if not public_key:
        keys = get_firebase_public_keys(force_refresh=True)
        public_key = keys.get(kid)
    if not public_key:
        raise ValueError("Certificat Firebase inconnu.")

    project_id = settings.firebase_project_id
    if not project_id:
        raise ValueError("FIREBASE_PROJECT_ID manquant.")

    return jwt.decode(
        id_token,
        public_key,
        algorithms=["RS256"],
        audience=project_id,
        issuer=f"https://securetoken.google.com/{project_id}",
        options={"require": ["exp", "iat", "aud", "iss", "sub"]},
    )
