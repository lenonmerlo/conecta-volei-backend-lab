from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db_session
from app.main import app
from app.modules.games import model as games_model  # noqa: F401
from app.modules.players import model as players_model  # noqa: F401
from app.modules.registrations import model as registrations_model  # noqa: F401

TEST_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5433/conecta_volei_test"
)


def _ensure_test_database() -> None:
    maintenance_url = (
        "postgresql+psycopg://postgres:postgres@localhost:5433/postgres"
    )

    admin_engine = create_engine(
        maintenance_url,
        isolation_level="AUTOCOMMIT",
    )

    with admin_engine.connect() as connection:
        database_exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'conecta_volei_test'"),
        ).scalar()

        if not database_exists:
            connection.execute(text("CREATE DATABASE conecta_volei_test"))

    admin_engine.dispose()


_ensure_test_database()

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
        session.execute(text("DELETE FROM game_registrations"))
        session.execute(text("DELETE FROM players"))
        session.execute(text("DELETE FROM games"))
        session.commit()