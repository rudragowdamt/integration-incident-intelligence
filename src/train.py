"""Train the severity classifier."""
import json
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from preprocessing import FEATURES, TARGET, build_pipeline, load_training_data

MODEL_PATH = Path("models/severity_model.joblib")
METADATA_PATH = Path("models/metadata.json")

if __name__ == "__main__":
    df = load_training_data()
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df[TARGET]
    )

    model = build_pipeline(
        RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            random_state=42,
            class_weight="balanced",
        )
    )

    model.fit(train_df[FEATURES], train_df[TARGET])

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    metadata = {
        "model_version": "1.0.0",
        "model_type": "RandomForestClassifier",
        "features": FEATURES,
        "target": TARGET,
        "training_rows": len(train_df),
        "test_rows": len(test_df),
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))

    print(f"Model saved to {MODEL_PATH}")
    print(f"Training rows: {len(train_df)}")
    print(f"Test rows: {len(test_df)}")
