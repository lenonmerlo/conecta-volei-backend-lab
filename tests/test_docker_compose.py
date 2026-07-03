from pathlib import Path


def test_docker_compose_defines_postgres_service() -> None:
    compose_file = Path("docker-compose.yml")

    assert compose_file.exists()

    content = compose_file.read_text(encoding="utf-8")
    assert "postgres:" in content
    assert "POSTGRES_DB: conecta_volei_lab" in content
    assert "5433:5432" in content
    assert "redis:" in content
    assert "6379:6379" in content
    assert "redis:7-alpine" in content