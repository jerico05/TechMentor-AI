"""Config & security helper tests."""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_token,
    hash_password,
    verify_password,
)


@pytest.mark.skip(reason="passlib/bcrypt backend issue on some Python versions")
def test_password_hash_roundtrip() -> None:
    hashed = hash_password("SecretPass1!")
    assert hashed != "SecretPass1!"
    assert verify_password("SecretPass1!", hashed) is True
    assert verify_password("wrong", hashed) is False
    assert verify_password("x", None) is False


def test_access_token_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    token, expires = create_access_token("42")
    payload = decode_token(token, "access")
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert expires > 0


def test_wrong_token_kind_rejected() -> None:
    token = create_password_reset_token("42")
    with pytest.raises(Exception) as exc:  # UnauthorizedError
        decode_token(token, "access")
    assert "Wrong token type" in str(exc.value)


def test_database_url_built_from_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    # Override env to verify URL composition.
    monkeypatch.setenv("SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("POSTGRES_USER", "u")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p")
    monkeypatch.setenv("POSTGRES_HOST", "h")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "d")
    s = Settings()
    assert s.database_url == "postgresql+asyncpg://u:p@h:5432/d"
    assert s.sync_database_url.startswith("postgresql+psycopg://")
