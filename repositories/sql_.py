import typing as t
import uuid
from typing import Sequence

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

import models
from repositories.base import BaseRepository, RepositoryException

Model = t.TypeVar("Model", bound=models.SQLModel | models.CreatedAtMixin)


class SQLRepository(BaseRepository[Model]):
    """A repository using SQL database for persistence operations."""

    def __init__(self, model: type) -> None:
        super().__init__(model)
        self._session: Session | None = None

    def use_session(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, id: uuid.UUID) -> Model:
        if self._session is None:
            raise RepositoryException("database session not initialized")
        if self._model is None or not hasattr(self._model, "id"):
            raise RepositoryException(f"{self._model_name} have not got 'id' attribute.")
        try:
            return self._session.exec(select(self._model).where(self._model.id == id)).one()
        except NoResultFound as exc:
            raise RepositoryException(f"{self._model_name} not found") from exc

    def find_by_slug(self, slug: str) -> Model:
        if self._session is None:
            raise RepositoryException("database session not initialized")
        if self._model is None or not hasattr(self._model, "slug"):
            raise RepositoryException(f"{self._model_name} have not got 'slug' attribute.")
        try:
            return self._session.exec(select(self._model).where(self._model.slug == slug)).one()
        except NoResultFound as exc:
            raise RepositoryException(f"{self._model_name} not found") from exc

    def list_paginated(self, offset: int = 0, limit: int = 1000) -> Sequence[Model]:
        if self._session is None:
            raise RepositoryException("database session not initialized")
        return self._session.exec(
            select(self._model).order_by((self._model).created_at).offset(offset).limit(limit)
        ).all()

    def create(self, record: Model) -> Model:
        if self._session is None:
            raise RepositoryException("database session not initialized")
        self._session.add(record)
        self._session.flush()
        return record

    def update(self, record: Model) -> Model:
        if self._session is None:
            raise RepositoryException("database session not initialized")
        self._session.add(record)
        self._session.flush()
        return record

    def delete(self, record: Model) -> None:
        if self._session is None:
            raise RepositoryException("database session not initialized")
        self._session.delete(record)


class MaterialSQLRepository(SQLRepository[models.Material]):
    def __init__(self) -> None:
        super().__init__(models.Material)


class ProductSQLRepository(SQLRepository[models.Product]):
    def __init__(self) -> None:
        super().__init__(models.Product)


class StockPositionSQLRepository(SQLRepository[models.StockPosition]):
    def __init__(self) -> None:
        super().__init__(models.StockPosition)

    def find_by_warehouse_id_and_material_id(
        self, warehouse_id: uuid.UUID, material_id: uuid.UUID
    ) -> models.StockPosition:
        if self._session is None:
            raise RepositoryException("database session not initialized")
        try:
            return self._session.exec(
                select(models.StockPosition)
                .where(models.StockPosition.warehouse_id == warehouse_id)
                .where(models.StockPosition.material_id == material_id)
            ).one()
        except NoResultFound as exc:
            raise RepositoryException(f"{self._model_name} not found") from exc


class WarehouseSQLRepository(SQLRepository[models.Warehouse]):
    def __init__(self) -> None:
        super().__init__(models.Warehouse)
