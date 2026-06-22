"""Generic async repository base."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import BaseModel as ORMBaseModel

ModelT = TypeVar("ModelT", bound=ORMBaseModel)
SchemaT = TypeVar("SchemaT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    """Minimal CRUD primitives shared by all repositories.

    Subclasses set `model`. Methods are async and accept an injected session.
    """

    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, pk: int) -> ModelT | None:
        return await self.db.get(self.model, pk)

    async def get_by(self, **filters: Any) -> ModelT | None:
        stmt = select(self.model).filter_by(**filters)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any] | SchemaT) -> ModelT:
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True)
        obj = self.model(**data)  # type: ignore[arg-type]
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelT, data: dict[str, Any] | SchemaT) -> ModelT:
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.db.delete(obj)
        await self.db.flush()
