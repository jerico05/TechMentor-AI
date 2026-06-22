"""RAG retriever tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.rag.retriever import retrieve_context


def test_retrieve_context_returns_formatted_string() -> None:
    with patch("app.rag.retriever.embed_query", return_value=[0.1] * 1536), patch(
        "app.rag.retriever.get_qdrant_client"
    ) as mock_client, patch("app.rag.retriever.search_similar") as mock_search:
        mock_search.return_value = [
            {"category": "roadmap", "title": "Docker", "content": "Apprendre Docker", "score": 0.9}
        ]
        result = retrieve_context("Comment apprendre Docker ?")
        assert "Docker" in result
        assert "Base de connaissances" in result


def test_retrieve_context_empty_on_failure() -> None:
    with patch("app.rag.retriever.embed_query", side_effect=RuntimeError("down")):
        assert retrieve_context("test") == ""
