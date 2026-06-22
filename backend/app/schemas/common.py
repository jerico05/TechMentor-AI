"""Shared schema building blocks."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base for schemas that map from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list envelope."""

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def has_more(self) -> bool:  # pragma: no cover - convenience
        return self.page * self.page_size < self.total


class MessageResponse(BaseModel):
    """Simple message envelope (success / info)."""

    message: str
