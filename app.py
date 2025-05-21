"""Definition of FactoryApp (FastAPI) application."""

from fastapi import FastAPI
from sqlalchemy.engine import Engine


class FactoryApp(FastAPI):
    """FactoryApp class is a specialized extension of FastAPI class.

    This class is designed to encapsulate additional functionality for
    a factory application. It integrates with FastAPI and provides an
    optional database engine attribute, allowing seamless database
    operations within the framework.

    :ivar db_engine: Optional database engine instance used to connect to
        the application's database. If None, no database engine is configured.
    :type db_engine: sqlalchemy.engine.Engine or None
    """

    db_engine: Engine | None = None
