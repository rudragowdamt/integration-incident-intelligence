"""Generate a reproducible synthetic integration-incident dataset."""
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

ERRORS = {
    "NONE": (200, "No error"),
    "CONNECTION_TIMEOUT": (504, "Connection timed out while calling downstream API"),
    "AUTHENTICATION": (401, "Authentication token rejected by downstream service"),
    "PAYLOAD_VALIDATION": (400, "Required field missing or payload validation failed"),
    "TRANSFORMATION": (422, "Message transformation failed"),
    "DOWNSTREAM_5XX": (503, "Downstream service returned server error"),
}

INTERFACES = [
    ("SAP-to-Salesforce", "SAP", "Salesforce"),
    ("Order-to-ERP", "Web", "ERP"),
    ("CRM-to-DataLake", "CRM", "DataLake"),
    ("Order-to-Warehouse", "OrderManagement", "Warehouse"),
    ("HR-to-Payroll", "HR", "Payroll"),
]

def choose_severity(error_type, previous_failures, retries, status):
    if error_type in {"CONNECTION_TIMEOUT", "DOWNSTREAM_5XX"} and previous_failures >= 10:
        return "CRITICAL"
    if error_type in {"CONNECTION_TIMEOUT", "DOWNSTREAM_5XX"} or status >= 500:
        return "HIGH"
    if error_type in {"AUTHENTICATION", "TRANSFORMATION"} or retries >= 2:
        return "MEDIUM"
    return "LOW"

def generate(rows=1000, seed=42):
    random.seed(seed)
    base = datetime(2026, 9, 1)
    records = []

    for _ in range(rows):
        interface, source, target = random.choice(INTERFACES)
        error_type = random.choices(
            list(ERRORS),
            weights=[25, 15, 15, 15, 10, 20],
            k=1
        )[0]

        status, message = ERRORS[error_type]
        duration = (
            random.randint(30, 90)
            if error_type == "CONNECTION_TIMEOUT"
            else random.randint(1, 20)
        )
        retries = (
            random.randint(2, 5)
            if error_type in {"CONNECTION_TIMEOUT", "DOWNSTREAM_5XX"}
            else random.randint(0, 2)
        )
        previous = (
            random.randint(5, 30)
            if error_type in {"CONNECTION_TIMEOUT", "DOWNSTREAM_5XX"}
            else random.randint(0, 9)
        )

        records.append({
            "interface_name": interface,
            "source_system": source,
            "target_system": target,
            "timestamp": (
                base + timedelta(minutes=random.randint(0, 60 * 24 * 30))
            ).isoformat() + "Z",
            "error_type": error_type,
            "error_message": message,
            "duration_seconds": duration,
            "retry_count": retries,
            "payload_size_mb": round(random.uniform(0.1, 10.0), 2),
            "previous_failures": previous,
            "http_status": status,
            "environment": random.choices(
                ["PROD", "UAT", "DEV"],
                weights=[70, 20, 10],
                k=1
            )[0],
            "severity": choose_severity(error_type, previous, retries, status),
        })

    return pd.DataFrame(records)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--output", default="data/raw/incidents.csv")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    df = generate(args.rows)
    df.to_csv(output, index=False)
    print(f"Wrote {len(df)} incidents to {output}")
