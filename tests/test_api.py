import json
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

def ensure_model():
    if not Path("models/severity_model.joblib").exists():
        subprocess.run(
            ["python", "src/data_generator.py", "--rows", "300"],
            check=True,
        )
        subprocess.run(["python", "src/train.py"], check=True)

def test_health():
    ensure_model()
    from src.api import app
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_prediction():
    ensure_model()
    from src.api import app
    payload = json.loads(Path("payloads/incident_timeout.json").read_text())
    response = TestClient(app).post("/predict", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "ml_prediction" in body
    assert body["ml_prediction"]["severity"] in {
        "LOW", "MEDIUM", "HIGH", "CRITICAL"
    }
