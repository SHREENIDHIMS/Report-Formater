from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="VTU Report Studio API",
    version="0.1.0",
    description="Student-first VTU project report formatting API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "If-Match"],
)


@app.get("/api/v1/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "vtu-report-studio-api"}
