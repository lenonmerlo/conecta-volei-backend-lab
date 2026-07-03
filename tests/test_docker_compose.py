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
    assert "rabbitmq:" in content
    assert "rabbitmq:4-management-alpine" in content
    assert "5672:5672" in content
    assert "15672:15672" in content
    assert "prometheus:" in content
    assert "prom/prometheus" in content
    assert "9090:9090" in content
    assert "grafana:" in content
    assert "grafana/grafana" in content
    assert "3000:3000" in content
    assert "observability/prometheus.yml" in content