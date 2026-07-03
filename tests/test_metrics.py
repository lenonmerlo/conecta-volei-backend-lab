from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_endpoint_returns_prometheus_metrics() -> None:
    client.get("/api/v1/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"] == (
        "text/plain; version=0.0.4; charset=utf-8"
    )
    assert "http_request_duration_seconds" in response.text
    assert 'path="/api/v1/health"' in response.text