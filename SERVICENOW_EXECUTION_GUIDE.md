# ServiceNow Extension - Execution Guide

This package preserves the original ML + Amazon Bedrock Lambda flow and adds ServiceNow after GenAI.

## Flow
API Gateway -> Lambda -> compact ML -> Bedrock -> ServiceNow Incident -> API response

## ServiceNow fields
- short_description: environment + interface + error type
- description: GenAI incident summary (or fallback)
- impact / urgency: mapped from ML severity
- correlation_id: stable hash of interface + error type + environment
- work_notes: ML severity/confidence + probable RCA + recommended actions + human-validation warning

## Modes
- SERVICENOW_ENABLED=false: no ticketing
- SERVICENOW_ENABLED=true, SERVICENOW_MODE=mock: safe ticket simulation
- SERVICENOW_ENABLED=true, SERVICENOW_MODE=servicenow: real ServiceNow Table API

## Local Lambda-style smoke test (PowerShell)
From repository root, after activating your venv:

```powershell
$env:ENABLE_BEDROCK="false"
$env:SERVICENOW_ENABLED="true"
$env:SERVICENOW_MODE="mock"
python -c "import sys,json; sys.path.insert(0,'lambda'); import handler; p=json.load(open('payloads/incident_timeout.json')); print(json.dumps(handler.lambda_handler({'incident':p},None),indent=2))"
```

Verify response body includes `servicenow`, `ticket_created: true`, and an `INC-MOCK-...` ticket number.

## Real ServiceNow DEV configuration
Create/provision a ServiceNow DEV/PDI and confirm its Table API can create an incident first.

For local testing only:

```powershell
$env:ENABLE_BEDROCK="false"
$env:SERVICENOW_ENABLED="true"
$env:SERVICENOW_MODE="servicenow"
$env:SERVICENOW_INSTANCE_URL="https://devXXXXXX.service-now.com"
$env:SERVICENOW_USERNAME="YOUR_USER"
$env:SERVICENOW_PASSWORD="YOUR_PASSWORD"
```

Then rerun the Lambda-style smoke test above. Verify a real `INC...` appears in ServiceNow.

## Enable Bedrock + real ServiceNow locally

```powershell
$env:ENABLE_BEDROCK="true"
$env:BEDROCK_MODEL_ID="YOUR_EXISTING_WORKING_MODEL_OR_INFERENCE_PROFILE_ID"
$env:AWS_REGION="ap-south-1"
```

Rerun the same smoke test. Verify `genai_explanation` and `servicenow.ticket_number` are both present.

## AWS recommended credential setup
Do not commit a ServiceNow password. Create an AWS Secrets Manager secret containing:

```json
{"instance_url":"https://devXXXXXX.service-now.com","username":"YOUR_USER","password":"YOUR_PASSWORD"}
```

Set Lambda environment variables to:

```text
SERVICENOW_ENABLED=true
SERVICENOW_MODE=servicenow
SERVICENOW_SECRET_ARN=<secret ARN>
```

The SAM template includes permissions for Bedrock and Secrets Manager for learning/dev. Narrow the Resource permissions before production.

## Build and deploy

```powershell
python src/export_lambda_model.py
pytest -q
sam validate --template-file infrastructure/template.yaml
sam build --template-file infrastructure/template.yaml
sam deploy --guided
```

IMPORTANT: Keep `CodeUri: ../lambda/`.
