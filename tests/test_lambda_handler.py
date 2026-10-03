import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lambda"))
import handler


def load_payload(name):
    return json.loads(
        (Path(__file__).resolve().parents[1] / "payloads" / name).read_text()
    )


def test_lambda_timeout_payload():
    event = {"incident": load_payload("incident_timeout.json")}
    response = handler.lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["ml_prediction"]["severity"] in {
        "LOW", "MEDIUM", "HIGH", "CRITICAL"
    }
    assert 0 <= body["ml_prediction"]["confidence"] <= 1


def test_lambda_api_gateway_style_body():
    event = {
        "body": json.dumps(load_payload("incident_authentication.json")),
        "isBase64Encoded": False,
    }
    response = handler.lambda_handler(event, None)
    assert response["statusCode"] == 200


def test_lambda_missing_payload():
    response = handler.lambda_handler({}, None)
    assert response["statusCode"] == 400
