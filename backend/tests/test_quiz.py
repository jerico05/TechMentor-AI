"""Quiz generation, submit & reassessment tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


SAMPLE_QUIZ_JSON = """{
  "questions": [
    {"id": "q1", "question": "Qu'est-ce que REST?", "options": ["A", "B", "C", "D"], "correct_index": 0},
    {"id": "q2", "question": "SQL?", "options": ["A", "B", "C", "D"], "correct_index": 1}
  ]
}"""


def _mock_llm(content: str) -> MagicMock:
    mock_message = MagicMock()
    mock_message.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
    return mock_client


@pytest.mark.asyncio
async def test_quiz_submit_reassessment(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await client.post("/api/v1/analysis/run", headers=auth_headers, json={"career_path_id": 1})

    mock_roadmap = MagicMock()
    mock_roadmap.id = 42

    with patch(
        "app.services.quiz_service.get_rodium_client",
        return_value=_mock_llm(SAMPLE_QUIZ_JSON),
    ), patch(
        "app.services.roadmap_service.retrieve_for_roadmap",
        return_value="",
    ), patch(
        "app.services.roadmap_service.get_rodium_client",
        return_value=_mock_llm('{"months": [], "summary": "ok"}'),
    ):
        gen = await client.post("/api/v1/quiz/generate", headers=auth_headers)
        assert gen.status_code == 200
        quiz_id = gen.json()["quiz_id"]

        submit = await client.post(
            "/api/v1/quiz/submit",
            headers=auth_headers,
            json={"quiz_id": quiz_id, "answers": {"q1": 0, "q2": 1}},
        )

    assert submit.status_code == 200
    body = submit.json()
    assert body["attempt"]["score"] == 100
    assert body["new_score"] >= body["previous_score"]
    assert "roadmap_id" in body

    history = await client.get("/api/v1/quiz/history", headers=auth_headers)
    assert history.status_code == 200
    assert len(history.json()) >= 1
