"""Database helper functions."""

from sqlalchemy.engine import Engine
from sqlmodel import create_engine

import models


def setup() -> Engine:
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})
    models.SQLModel.metadata.create_all(engine)
    return engine
