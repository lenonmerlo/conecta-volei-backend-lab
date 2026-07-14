from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import router as api_router
from app.core.config import settings
from app.core.errors import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.metrics import MetricsMiddleware, metrics_response

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Modular backend lab for the Conecta Volley application.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_middleware(MetricsMiddleware)
app.include_router(api_router)


@app.get("/metrics", include_in_schema=False)
def metrics():
    return metrics_response()