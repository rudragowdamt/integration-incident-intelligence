"""Lightweight AWS Lambda inference handler.

No third-party Python packages are required. The model is a JSON export of a
small scikit-learn multinomial logistic regression trained offline. Lambda
reimplements the tiny amount of preprocessing and softmax inference needed
for that exported model.

Bedrock is optional and disabled by default. If ENABLE_BEDROCK=true, the
handler uses the AWS SDK included by the Lambda Python runtime and the model
ID supplied through BEDROCK_MODEL_ID.
"""
import base64
import json
import math
import os
from pathlib import Path

from servicenow_client import create_or_update_incident

MODEL = json.loads((Path(__file__).parent / "model.json").read_text())


def _one_hot(value, categories):
    return [1.0 if value == category else 0.0 for category in categories]


def _features(incident):
    numeric_values = [
        float(incident.get("duration_seconds", 0)),
        float(incident.get("retry_count", 0)),
        float(incident.get("payload_size_mb", 0)),
        float(incident.get("previous_failures", 0)),
        float(incident.get("http_status", 0)),
    ]

    vector = []
    for value, mean, scale in zip(
        numeric_values, MODEL["numeric"]["mean"], MODEL["numeric"]["scale"]
    ):
        safe_scale = scale if scale else 1.0
        vector.append((value - mean) / safe_scale)

    for name in ("error_type", "environment", "interface_name"):
        vector.extend(_one_hot(incident.get(name, ""), MODEL["categorical"][name]))

    return vector


def _predict(incident):
    x = _features(incident)
    logits = []
    for intercept, coefficients in zip(MODEL["intercept"], MODEL["coefficients"]):
        logits.append(intercept + sum(a * b for a, b in zip(coefficients, x)))

    max_logit = max(logits)
    exponentials = [math.exp(value - max_logit) for value in logits]
    total = sum(exponentials)
    probabilities = [value / total for value in exponentials]
    best = max(range(len(probabilities)), key=probabilities.__getitem__)

    return {
        "severity": MODEL["classes"][best],
        "confidence": round(probabilities[best], 4),
        "model_type": MODEL["model_type"],
        "model_version": MODEL["model_version"],
        "probabilities": {
            label: round(probability, 4)
            for label, probability in zip(MODEL["classes"], probabilities)
        },
    }


def _parse_event(event):
    if not isinstance(event, dict):
        return {}

    body = event.get("body")
    if body is None:
        return event.get("incident", event)

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    if isinstance(body, str):
        body = json.loads(body or "{}")
    if not isinstance(body, dict):
        return {}
    return body.get("incident", body)


def _recommendation(incident, prediction):
    error_type = incident.get("error_type", "UNKNOWN")
    actions = {
        "CONNECTION_TIMEOUT": [
            "Check downstream endpoint availability",
            "Review network connectivity and recent 504 responses",
            "Check correlated failures and recent infrastructure changes",
        ],
        "AUTHENTICATION": [
            "Validate credentials or token expiry",
            "Check recent secret or certificate changes",
            "Review downstream authentication logs",
        ],
        "PAYLOAD_VALIDATION": [
            "Validate required fields and schema",
            "Compare the failing payload with a successful payload",
            "Check recent contract changes",
        ],
        "TRANSFORMATION": [
            "Inspect transformation/mapping errors",
            "Compare source and target schemas",
            "Check recent mapping deployments",
        ],
        "DOWNSTREAM_5XX": [
            "Check downstream service health",
            "Review 5xx response patterns",
            "Check recent downstream deployments or incidents",
        ],
    }
    return actions.get(error_type, [
        "Review the integration logs",
        "Check dependent systems",
        "Compare the incident with recent successful transactions",
    ])


def _bedrock_explanation(incident, prediction):
    if os.getenv("ENABLE_BEDROCK", "false").lower() != "true":
        return None

    import boto3

    model_id = os.environ["BEDROCK_MODEL_ID"]
    client = boto3.client("bedrock-runtime")
    prompt = (
        "You are an integration support assistant. Return concise JSON with "
        "incident_summary, probable_root_cause, recommended_actions and priority. "
        "Do not invent facts. Use only the supplied incident and ML prediction.\n\n"
        + json.dumps({"incident": incident, "ml_prediction": prediction})
    )
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
    )
    text = response["output"]["message"]["content"][0]["text"]
    return text


def lambda_handler(event, context):
    incident = _parse_event(event)
    if not incident:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Incident payload is required"}),
        }

    prediction = _predict(incident)
    report = {
        "incident_summary": (
            f"Interface {incident.get('interface_name', 'unknown')} "
            f"reported {incident.get('error_type', 'unknown')}."
        ),
        "ml_prediction": prediction,
        "recommended_actions": _recommendation(incident, prediction),
        "environment": incident.get("environment"),
        "aws_region": os.getenv("AWS_REGION", "unknown"),
    }

    explanation = _bedrock_explanation(incident, prediction)
    if explanation:
        report["genai_explanation"] = explanation

    # ServiceNow is deliberately invoked after ML + GenAI so the ticket is
    # enriched with the existing project output. Ticket failure is returned
    # explicitly without discarding the incident intelligence result.
    try:
        report["servicenow"] = create_or_update_incident(
            incident, prediction, explanation
        )
    except Exception as exc:
        report["servicenow"] = {
            "enabled": True,
            "ticket_created": False,
            "ticket_action": "failed",
            "error": str(exc),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(report),
    }
