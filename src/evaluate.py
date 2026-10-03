"""Evaluate the trained model."""
import joblib
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from preprocessing import FEATURES, TARGET, load_training_data

if __name__ == "__main__":
    df = load_training_data()
    _, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df[TARGET]
    )

    model = joblib.load("models/severity_model.joblib")
    predictions = model.predict(test_df[FEATURES])

    print(f"Accuracy: {accuracy_score(test_df[TARGET], predictions):.4f}")
    print(classification_report(
        test_df[TARGET], predictions, zero_division=0
    ))
