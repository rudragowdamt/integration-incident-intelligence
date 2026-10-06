import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lambda"))
import servicenow_client as sn


def test_ticket_payload_contains_ai_fields():
    incident = {"interface_name":"SAP-to-Salesforce","error_type":"CONNECTION_TIMEOUT","environment":"PROD"}
    prediction = {"severity":"HIGH","confidence":0.91,"model_version":"1"}
    genai = '{"incident_summary":"Repeated timeout","probable_root_cause":"Endpoint latency","recommended_actions":["Check endpoint"]}'
    p = sn.build_ticket_payload(incident, prediction, genai)
    assert p["short_description"].startswith("[PROD]")
    assert "Endpoint latency" in p["work_notes"]
    assert "NOT CONFIRMED" in p["work_notes"]
    assert p["correlation_id"].startswith("AIII-")


def test_mock_ticket(monkeypatch):
    monkeypatch.setenv("SERVICENOW_ENABLED", "true")
    monkeypatch.setenv("SERVICENOW_MODE", "mock")
    result = sn.create_or_update_incident(
        {"interface_name":"A","error_type":"AUTHENTICATION","environment":"PROD"},
        {"severity":"CRITICAL","confidence":0.9,"model_version":"1"},
        None,
    )
    assert result["ticket_created"] is True
    assert result["ticket_number"].startswith("INC-MOCK-")
