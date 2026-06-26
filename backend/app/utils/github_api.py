"""GitHub REST API helpers with token fallback."""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "TechMentor-AI",
}


async def github_get(url: str, *, timeout: float = 20.0, params: dict | None = None) -> httpx.Response:
    """GET GitHub API; retries without token if the configured token is rejected."""
    async def _request(with_token: bool) -> httpx.Response:
        headers = dict(_DEFAULT_HEADERS)
        if with_token and settings.github_api_token:
            headers["Authorization"] = f"Bearer {settings.github_api_token}"
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            return await client.get(url, params=params)

    response = await _request(with_token=bool(settings.github_api_token))
    if response.status_code in (401, 403) and settings.github_api_token:
        logger.warning("github.api.token_rejected", status=response.status_code, url=url)
        response = await _request(with_token=False)
    return response
