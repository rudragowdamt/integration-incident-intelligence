"""Train and export a tiny dependency-free classifier for AWS Lambda.

The normal project model remains the Random Forest in models/severity_model.joblib.
This script creates a second, compact deployment artifact using multinomial
logistic regression. Its coefficients and preprocessing metadata are exported
to JSON, allowing Lambda to perform inference using only Python's standard
library. This avoids shipping NumPy/scikit-learn/Pandas in the Lambda zip.
"""
import json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from preprocessing import FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES, load_training_data

OUTPUT = Path("lambda/model.json")


def main():
    df = load_training_data()
    train_df, _ = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["severity"]
    )

    scaler = StandardScaler()
    x_num = scaler.fit_transform(train_df[NUMERIC_FEATURES])

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    x_cat = encoder.fit_transform(train_df[CATEGORICAL_FEATURES])
    x = np.hstack([x_num, x_cat])

    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
    )
    model.fit(x, train_df["severity"])

    payload = {
        "model_type": "compact_multinomial_logistic_regression",
        "model_version": "1.0.0",
        "features": FEATURES,
        "numeric": {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(),
        },
        "categorical": {
            name: categories.tolist()
            for name, categories in zip(CATEGORICAL_FEATURES, encoder.categories_)
        },
        "classes": model.classes_.tolist(),
        "coefficients": model.coef_.tolist(),
        "intercept": model.intercept_.tolist(),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote compact Lambda model to {OUTPUT}")
    print(f"Deployment artifact size: {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
