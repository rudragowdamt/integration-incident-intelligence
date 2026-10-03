"""FastAPI model-serving API."""
import sys
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predict import predict

app = FastAPI(
    title="Integration Incident Intelligence API",
    version="1.0.0",
)

class Incident(BaseModel):
    interface_name: str
    source_system: str
    target_system: str
    timestamp: str
    error_type: str
    error_message: str
    duration_seconds: float = Field(ge=0)
    retry_count: int = Field(ge=0)
    payload_size_mb: float = Field(ge=0)
    previous_failures: int = Field(ge=0)
    http_status: int = Field(ge=100, le=599)
    environment: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict_incident(incident: Incident) -> dict[str, Any]:
    data = incident.model_dump()
    return {
        "incident": data,
        "ml_prediction": predict(data),
        "genai_context": {
            "purpose": "Pass the incident and ML result to the GenAI layer.",
            "do_not_invent": True,
        },
    }
