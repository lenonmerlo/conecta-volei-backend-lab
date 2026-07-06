from collections.abc import Generator
from os import getenv

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db_session
from app.main import app
from app.modules.audit_logs import model as audit_logs_model  # noqa: F401
from app.modules.games import model as games_model  # noqa: F401
from app.modules.players import model as players_model  # noqa: F401
from app.modules.registrations import model as registrations_model  # noqa: F401

TEST_DATABASE_URL = getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/conecta_volei_test",
)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

Base.metadata.drop_all(bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db_session() -> Generator[Session]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db_session


@pytest.fixture(autouse=True)
def clean_test_database() -> None:
    with TestSessionLocal() as session:
        session.execute(text("DELETE FROM audit_logs"))
        session.execute(text("DELETE FROM game_registrations"))
        session.execute(text("DELETE FROM players"))
        session.execute(text("DELETE FROM games"))
        session.commit()