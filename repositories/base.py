import typing as t
import uuid

import models
from utils import camel_to_lower_with_spaces

Model = t.TypeVar("Model", bound=models.BaseModel | models.CreatedAtMixin)


class RepositoryException(Exception):
    pass


class BaseRepository(t.Generic[Model]):
    """An abstract repository class."""

    def __init__(self, model: type) -> None:
        self._model = model
        self._model_name = camel_to_lower_with_spaces(self._model.__name__)

    def find_by_id(self, id: uuid.UUID) -> Model:
        raise NotImplementedError

    def find_by_slug(self, slug: str) -> Model:
        raise NotImplementedError

    def list_paginated(self, offset: int = 0, limit: int = 1000) -> list[Model]:
        raise NotImplementedError

    def create(self, record: Model) -> Model:
        raise NotImplementedError

    def update(self, record: Model) -> Model:
        raise NotImplementedError

    def delete(self, record: Model) -> None:
        raise NotImplementedError
