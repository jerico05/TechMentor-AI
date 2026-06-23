"""CV file storage - local disk or Cloudinary (raw)."""

from __future__ import annotations

import uuid
from pathlib import Path

import httpx

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


def is_remote_url(stored_path: str) -> bool:
    return stored_path.startswith("http://") or stored_path.startswith("https://")


def _ensure_cloudinary() -> None:
    if not settings.cloudinary_configured:
        raise ValidationError(
            "Cloudinary non configuré. Définissez CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY et CLOUDINARY_API_SECRET."
        )


def _configure_cloudinary() -> None:
    import cloudinary

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def save_cv_file(user_id: int, data: bytes, original_filename: str, mime_type: str) -> str:
    """Persist CV bytes. Returns local path or Cloudinary HTTPS URL."""
    if settings.use_cloudinary_storage:
        return _upload_cloudinary(user_id, data, original_filename, mime_type)
    return _save_local(user_id, data, mime_type)


def _save_local(user_id: int, data: bytes, mime_type: str) -> str:
    ext = ".pdf" if mime_type == "application/pdf" else ".docx"
    filename = f"{user_id}_{uuid.uuid4().hex}{ext}"
    path = settings.upload_path / filename
    path.write_bytes(data)
    return str(path)


def _upload_cloudinary(user_id: int, data: bytes, original_filename: str, mime_type: str) -> str:
    _ensure_cloudinary()
    import cloudinary.uploader

    _configure_cloudinary()
    ext = Path(original_filename).suffix.lower() or (".pdf" if mime_type == "application/pdf" else ".docx")
    public_id = f"{user_id}_{uuid.uuid4().hex}"
    try:
        result = cloudinary.uploader.upload(
            data,
            resource_type="raw",
            folder=settings.cloudinary_cv_folder,
            public_id=public_id,
            format=ext.lstrip(".") or None,
        )
    except Exception as exc:
        logger.warning("cloudinary.upload.failed", error=str(exc))
        raise ValidationError("Échec de l'upload vers Cloudinary.") from exc

    url = result.get("secure_url") or result.get("url")
    if not url:
        raise ValidationError("Cloudinary n'a pas retourné d'URL de fichier.")
    logger.info("cloudinary.upload.ok", public_id=result.get("public_id"))
    return url


def read_cv_bytes(stored_path: str) -> bytes:
    if is_remote_url(stored_path):
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            response = client.get(stored_path)
            response.raise_for_status()
            return response.content
    path = Path(stored_path)
    if not path.is_file():
        raise FileNotFoundError(f"CV introuvable : {stored_path}")
    return path.read_bytes()
