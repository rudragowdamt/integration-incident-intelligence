# AWS Lambda deployment — fixed low-size package

This guide is the replacement for the original deployment approach that could
attempt to package the entire repository.

## 1. Why the original deployment failed

AWS Lambda enforces a maximum unzipped deployment package size of 250 MB
(262,144,000 bytes). The original SAM template used the repository root as the
Lambda `CodeUri`.

That repository contains the local ML stack, including packages such as:

- NumPy
- Pandas
- scikit-learn
- joblib
- FastAPI and related development packages

Those packages belong in the development/training environment, not in this
Lambda function.

## 2. New deployment design

```text
                    Git repository
                         |
          +--------------+--------------+
          |                             |
          v                             v
    Local ML training             lambda/ directory
  Pandas/NumPy/sklearn                 |
          |                             v
          |                    Tiny JSON ML model
          |                             |
          |                             v
          |                    AWS Lambda + API Gateway
          |                             |
          +----> optional GenAI <------+
                       Bedrock
```

The Lambda function performs inference from a compact JSON representation of a
trained multinomial logistic regression model. The inference implementation
uses only Python's standard library.

This is an important ML engineering pattern: **training and inference have
different dependency requirements**.

## 3. Generate the compact deployment model

Activate your normal project virtual environment and install the project
requirements.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Generate training data:

```powershell
python src/data_generator.py --rows 1500
```

Export the Lambda model:

```powershell
python src/export_lambda_model.py
```

The command writes:

```text
lambda/model.json
```

The model file is intentionally small. It contains learned coefficients,
normalization values, category metadata and class names rather than the full
Python ML runtime.

## 4. Validate locally

Run the standard ML tests:

```powershell
pytest -q
```

Run the Lambda handler directly:

```powershell
python -c "import sys; sys.path.insert(0, 'lambda'); import handler; import json; print(handler.lambda_handler({'incident': json.load(open('payloads/incident_timeout.json'))}, None))"
```

## 5. Build with SAM

From the repository root:

```powershell
sam build --template-file infrastructure/template.yaml
```

The important setting is:

```yaml
CodeUri: ../lambda/
```

SAM must package only the `lambda` directory.

## 6. Inspect the package before deployment

After `sam build`, inspect `.aws-sam/build/IncidentFunction`.

The directory should contain only a few small files, including:

```text
handler.py
model.json
```

It should NOT contain:

```text
numpy/
pandas/
sklearn/
fastapi/
models/severity_model.joblib
```

You can also inspect the size from PowerShell:

```powershell
Get-ChildItem .aws-sam/build/IncidentFunction -Recurse |
  Measure-Object -Property Length -Sum
```

## 7. Deploy

```powershell
sam deploy --guided
```

For the first deployment, accept the generated CloudFormation stack name or
choose a clear name such as:

```text
integration-incident-intelligence
```

Keep the default Bedrock setting disabled.

## 8. Test the API

Use the API URL shown by the SAM/CloudFormation deployment output.

PowerShell:

```powershell
$body = Get-Content payloads/incident_timeout.json -Raw
Invoke-RestMethod -Method Post `
  -Uri "YOUR_API_ENDPOINT/incident" `
  -ContentType "application/json" `
  -Body $body
```

The response should contain fields similar to:

```json
{
  "incident_summary": "Interface SAP-to-Salesforce reported CONNECTION_TIMEOUT.",
  "ml_prediction": {
    "severity": "HIGH",
    "confidence": 0.8
  },
  "recommended_actions": [
    "Check downstream endpoint availability"
  ]
}
```

The exact prediction and confidence are learned from the generated training
data and therefore should be treated as model output, not hard-coded facts.

## 9. Optional Bedrock phase

Do not enable Bedrock until Lambda/API Gateway works.

Then configure:

```text
ENABLE_BEDROCK=true
BEDROCK_MODEL_ID=<model available in your region>
```

Add only the required Bedrock invocation permission to the Lambda execution
role. The exact model ID and availability should be checked for your selected
AWS region before deployment.

## 10. Cost-control workflow

For a learning project:

1. Train locally.
2. Deploy the lightweight Lambda with Bedrock disabled.
3. Send only a few test requests.
4. Enable Bedrock only when you are ready to learn the GenAI integration.
5. Avoid loops that repeatedly invoke a foundation model.
6. Set an AWS budget alert.
7. Delete the stack when finished:

```powershell
sam delete
```

This design reduces deployment size and avoids the need for an always-on ML
inference endpoint. It does not guarantee that AWS usage will cost zero; AWS
service pricing and free-tier eligibility depend on the account, region and
current AWS terms.
