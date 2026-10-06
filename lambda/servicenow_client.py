"""Lightweight ServiceNow Incident API client using only Python stdlib.

Modes:
- disabled: no ticketing
- mock: returns a deterministic mock incident (safe local/test mode)
- servicenow: calls the ServiceNow Table API

Credentials can come from direct environment variables for local DEV testing or
from AWS Secrets Manager in Lambda. A Secrets Manager secret should contain:
{"instance_url":"https://devXXXX.service-now.com","username":"...","password":"..."}
"""
import base64
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request


def _mode():
    if os.getenv("SERVICENOW_ENABLED", "false").lower() != "true":
        return "disabled"
    return os.getenv("SERVICENOW_MODE", "mock").lower()


def _credentials():
    secret_arn = os.getenv("SERVICENOW_SECRET_ARN", "").strip()
    if secret_arn:
        import boto3
        region = os.getenv("AWS_REGION") or os.getenv("BEDROCK_REGION")
        client = boto3.client("secretsmanager", region_name=region)
        secret = json.loads(client.get_secret_value(SecretId=secret_arn)["SecretString"])
        return secret["instance_url"].rstrip("/"), secret["username"], secret["password"]

    return (
        os.environ["SERVICENOW_INSTANCE_URL"].rstrip("/"),
        os.environ["SERVICENOW_USERNAME"],
        os.environ["SERVICENOW_PASSWORD"],
    )


def correlation_id(incident):
    raw = "|".join([
        str(incident.get("interface_name", "")),
        str(incident.get("error_type", "")),
        str(incident.get("environment", "")),
    ]).upper()
    return "AIII-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20].upper()


def _priority(severity):
    # ServiceNow commonly calculates priority from impact/urgency. These values
    # are intentionally conservative defaults for a DEV project.
    return {
        "CRITICAL": {"impact": "1", "urgency": "1"},
        "HIGH": {"impact": "2", "urgency": "1"},
        "MEDIUM": {"impact": "2", "urgency": "2"},
        "LOW": {"impact": "3", "urgency": "3"},
    }.get(severity, {"impact": "3", "urgency": "3"})


def _genai_fields(genai):
    if not genai:
        return "GenAI analysis unavailable.", [], "Not generated"
    if isinstance(genai, str):
        try:
            cleaned = genai.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
                if cleaned.lstrip().startswith("json"):
                    cleaned = cleaned.lstrip()[4:].lstrip()
            genai = json.loads(cleaned)
        except Exception:
            return genai, [], "See GenAI explanation"
    return (
        genai.get("incident_summary", "GenAI incident analysis generated."),
        genai.get("recommended_actions", []),
        genai.get("probable_root_cause", "Not generated"),
    )


def build_ticket_payload(incident, prediction, genai=None):
    summary, actions, root_cause = _genai_fields(genai)
    severity = prediction.get("severity", "UNKNOWN")
    pri = _priority(severity)
    corr = correlation_id(incident)
    action_text = "\n".join(f"- {a}" for a in actions) if actions else "- Review incident evidence and integration logs"
    work_notes = (
        "AI-Powered Integration Incident Intelligence\n"
        f"ML Severity: {severity}\n"
        f"ML Confidence: {prediction.get('confidence')}\n"
        f"Model Version: {prediction.get('model_version')}\n\n"
        f"GenAI Probable Root Cause (NOT CONFIRMED):\n{root_cause}\n\n"
        f"Recommended Investigation Actions:\n{action_text}\n\n"
        "Human validation is required before confirming RCA or performing high-impact remediation."
    )
    return {
        "short_description": f"[{incident.get('environment','UNKNOWN')}] {incident.get('interface_name','Integration')} - {incident.get('error_type','Failure')}",
        "description": str(summary),
        "impact": pri["impact"],
        "urgency": pri["urgency"],
        "correlation_id": corr,
        "work_notes": work_notes,
    }


def _request(method, url, username, password, body=None):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ServiceNow HTTP {exc.code}: {detail[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"ServiceNow connection failed: {exc.reason}") from exc


def create_or_update_incident(incident, prediction, genai=None):
    mode = _mode()
    if mode == "disabled":
        return {"enabled": False, "ticket_created": False, "status": "disabled"}

    payload = build_ticket_payload(incident, prediction, genai)
    corr = payload["correlation_id"]
    if mode == "mock":
        return {
            "enabled": True,
            "mode": "mock",
            "ticket_created": True,
            "ticket_action": "created",
            "ticket_number": "INC-MOCK-" + corr[-6:],
            "correlation_id": corr,
        }
    if mode != "servicenow":
        raise ValueError(f"Unsupported SERVICENOW_MODE: {mode}")

    base, username, password = _credentials()
    query = urllib.parse.urlencode({
        "sysparm_query": f"correlation_id={corr}^active=true",
        "sysparm_fields": "sys_id,number,correlation_id",
        "sysparm_limit": "1",
    })
    _, found = _request("GET", f"{base}/api/now/table/incident?{query}", username, password)
    rows = found.get("result", [])
    if rows:
        row = rows[0]
        update = {"work_notes": payload["work_notes"] + "\n\nCorrelated repeat event received; existing incident updated."}
        _, result = _request("PATCH", f"{base}/api/now/table/incident/{row['sys_id']}", username, password, update)
        record = result.get("result", {})
        return {
            "enabled": True, "mode": "servicenow", "ticket_created": False,
            "ticket_action": "updated", "ticket_number": record.get("number", row.get("number")),
            "ticket_sys_id": record.get("sys_id", row.get("sys_id")), "correlation_id": corr,
        }

    _, result = _request("POST", f"{base}/api/now/table/incident", username, password, payload)
    record = result.get("result", {})
    return {
        "enabled": True, "mode": "servicenow", "ticket_created": True,
        "ticket_action": "created", "ticket_number": record.get("number"),
        "ticket_sys_id": record.get("sys_id"), "correlation_id": corr,
    }
