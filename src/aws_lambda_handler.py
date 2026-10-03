"""Minimal Lambda handler for a serverless incident response.

The first AWS version intentionally returns a structured report without
automatically invoking Bedrock. This keeps the deployment inexpensive and
makes permissions easy to understand.
"""
import json
import os

def lambda_handler(event, context):
    incident = event.get("incident", {})
    prediction = event.get("ml_prediction", {})

    report = {
        "incident_summary": (
            f"Interface {incident.get('interface_name', 'unknown')} "
            f"reported {incident.get('error_type', 'unknown')}."
        ),
        "severity": prediction.get("severity", "UNKNOWN"),
        "confidence": prediction.get("confidence"),
        "recommended_next_step": (
            "Review downstream dependency health, recent deployments, "
            "network connectivity and correlated failures."
        ),
        "environment": incident.get("environment"),
        "aws_region": os.getenv("AWS_REGION", "unknown"),
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(report),
    }
