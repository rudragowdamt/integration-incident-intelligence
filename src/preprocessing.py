"""Shared feature engineering for the classifier."""
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

NUMERIC_FEATURES = [
    "duration_seconds",
    "retry_count",
    "payload_size_mb",
    "previous_failures",
    "http_status",
]

CATEGORICAL_FEATURES = [
    "error_type",
    "environment",
    "interface_name",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "severity"

def build_preprocessor():
    return ColumnTransformer([
        ("num", "passthrough", NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])

def load_training_data(path="data/raw/incidents.csv"):
    if not Path(path).exists():
        raise FileNotFoundError(
            f"{path} not found. Run: python src/data_generator.py"
        )
    return pd.read_csv(path)

def build_pipeline(model):
    return Pipeline([
        ("preprocessor", build_preprocessor()),
        ("model", model),
    ])
