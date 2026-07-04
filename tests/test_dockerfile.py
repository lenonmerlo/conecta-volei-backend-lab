from pathlib import Path


def test_dockerfile_defines_api_image() -> None:
    dockerfile = Path("Dockerfile")

    assert dockerfile.exists()

    content = dockerfile.read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in content
    assert "WORKDIR /app" in content
    assert "COPY app ./app" in content
    assert 'CMD ["uvicorn", "app.main:app"' in content