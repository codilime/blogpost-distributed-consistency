import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import Session
from sqlmodel.pool import StaticPool

from dependencies import get_session
from main import create_application
from models import SQLModel


@pytest.fixture
def client():
    # Create all tables in the test database
    # Use SQLite in-memory database instead of file-based
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def db_override():
        with Session(engine) as session:
            try:
                yield session
            finally:
                session.close()

    app = create_application()
    app.dependency_overrides[get_session] = db_override
    client = TestClient(app)
    yield client
    SQLModel.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
