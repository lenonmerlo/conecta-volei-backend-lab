from pathlib import Path


def test_dockerfile_defines_api_image() -> None:
    dockerfile = Path("Dockerfile")

    assert dockerfile.exists()

    content = dockerfile.read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in content
    assert "WORKDIR /app" in content
    assert "COPY app ./app" in content
    assert "COPY scripts ./scripts" in content
    assert 'CMD ["sh", "scripts/start_api.sh"]' in content


def test_start_api_script_runs_migrations_before_server() -> None:
    script = Path("scripts/start_api.sh")

    assert script.exists()

    content = script.read_text(encoding="utf-8")

    assert "alembic upgrade head" in content
    assert "exec uvicorn app.main:app" in content