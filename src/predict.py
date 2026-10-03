"""Run one incident prediction."""
import argparse
import json
from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path("models/severity_model.joblib")

def predict(payload):
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model missing. Run: python src/train.py")

    model = joblib.load(MODEL_PATH)
    df = pd.DataFrame([payload])
    probabilities = model.predict_proba(df)[0]
    classes = model.classes_
    index = probabilities.argmax()

    return {
        "severity": str(classes[index]),
        "confidence": round(float(probabilities[index]), 4),
        "model_version": "1.0.0",
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text())
    print(json.dumps(predict(payload), indent=2))
