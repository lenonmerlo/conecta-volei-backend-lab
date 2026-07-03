from pathlib import Path


def test_prometheus_config_scrapes_api_metrics() -> None:
    config_file = Path("observability/prometheus.yml")

    assert config_file.exists()

    content = config_file.read_text(encoding="utf-8")

    assert 'job_name: "conecta-volei-api"' in content
    assert 'metrics_path: "/metrics"' in content
    assert "host.docker.internal:8000" in content