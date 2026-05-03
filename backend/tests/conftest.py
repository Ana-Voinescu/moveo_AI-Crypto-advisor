import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import app.models  # register all models with Base before create_all
from main import app as fastapi_app
from app.database import Base
from app.dependencies import get_db


@pytest.fixture
def client():
    """
    TestClient backed by a fresh in-memory SQLite DB per test.

    StaticPool is required here: SQLite in-memory databases are per-connection,
    so without it each session would see an empty database. StaticPool forces
    all sessions to reuse the same underlying connection and therefore the same
    in-memory data.

    override_get_db creates a new session per request (thread-safe), instead of
    sharing one session across threads, which caused the SQLite cross-thread error.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()
