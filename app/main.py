from fastapi import FastAPI

app = FastAPI(
    title="Conecta Volei Backend Lab",
    version="0.1.0",
    description="Modular backend lab for the Conecta Volei applacation.",
)

@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}