from app.core.config import settings
from app.core.database import Base, SessionLocal, engine


def test_database_url_uses_postgresql_driver() -> None:
    assert settings.database_url.startswith("postgresql+psycopg://")


def test_sqlalchemy_base_has_metadata() -> None:
    assert Base.metadata is not None


def test_engine_uses_configured_database_url() -> None:
    assert engine.url.render_as_string(hide_password=False) == settings.database_url

def test_session_local_is_configured() -> None:
    session = SessionLocal()
    try:
        assert session.bind is engine
    finally:
        session.close()