"""CV upload tests."""

from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cv_upload_pdf(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    pdf_bytes = b"%PDF-1.4 minimal"

    with patch("app.services.cv_service.CVService._extract_text", return_value="Python FastAPI Docker"), patch(
        "app.utils.llm_helpers.extract_skills_from_text", return_value=["Python"]
    ):
        response = await client.post(
            "/api/v1/cv/upload",
            headers=auth_headers,
            files={"file": ("cv.pdf", BytesIO(pdf_bytes), "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "cv.pdf"
    assert data["status"] == "parsed"

    me = await client.get("/api/v1/cv/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json() is not None
