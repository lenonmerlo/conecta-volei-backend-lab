from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import settings
from app.core.metrics import MetricsMiddleware, metrics_response

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Modular backend lab for the Conecta Volley application.",
)

app.add_middleware(MetricsMiddleware)
app.include_router(api_router)


@app.get("/metrics", include_in_schema=False)
def metrics():
    return metrics_response()