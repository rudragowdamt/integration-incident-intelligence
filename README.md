# AI-Powered Integration Incident Intelligence

A Git-ready AI/ML learning project that applies supervised machine learning,
Generative AI concepts, APIs, AWS serverless services, and MLOps to enterprise
integration incident triage.

## Business problem

Integration support teams receive failed transactions and often inspect logs
manually before deciding severity, likely failure category, and next action.

This prototype uses:

- **Supervised ML** for structured severity classification.
- **Generative AI** for explanation/summarization.
- **FastAPI** for local model serving.
- **AWS Lambda** for serverless execution.
- **Amazon S3** for object storage.
- **Amazon Bedrock** as an optional GenAI layer.
- **GitHub Actions** for CI.
- **MLOps concepts** for versioning, evaluation, monitoring and retraining.

## Example

Input:

```json
{
  "interface_name": "SAP-to-Salesforce",
  "error_type": "CONNECTION_TIMEOUT",
  "duration_seconds": 45,
  "retry_count": 3,
  "previous_failures": 17,
  "http_status": 504
}
```

Example interpretation:

```text
Severity: HIGH
Likely category: DOWNSTREAM_CONNECTIVITY
Pattern: repeated timeout failures
Suggested action: check downstream endpoint availability and network connectivity
```

The actual model in this package learns severity from synthetic data. The
example above is an illustration, not a claim that the model will always
produce a specific result.

## Architecture

### Local-first

```text
Synthetic Integration Logs
          |
          v
     CSV / JSON
          |
          v
 Feature Engineering
          |
          v
 Supervised ML Model
          |
          +----------+
          |          |
          v          v
      Evaluation   Prediction
                       |
                       v
                    FastAPI
```

### AWS extension — lightweight Lambda deployment

```text
              API Gateway
                   |
                   v
              AWS Lambda
                   |
          compact model.json
                   |
                   v
           ML severity result
                   |
          +--------+--------+
          |                 |
          v                 v
     next actions       optional Bedrock
          |                 |
          +--------+--------+
                   |
                   v
            Incident Report

Training dependencies such as NumPy, Pandas and scikit-learn remain outside
the Lambda package. SAM packages only `lambda/`.

## Important AWS Lambda deployment fix

The Lambda deployment intentionally uses `infrastructure/template.yaml` with:

```yaml
CodeUri: ../lambda/
```

Do **not** change this to `CodeUri: ../`. The repository contains the full ML
training stack, while Lambda needs only the lightweight `lambda/` directory.
The compact deployment model is generated with:

```bash
python src/export_lambda_model.py
```

This avoids packaging NumPy, Pandas, scikit-learn and the local Random Forest
artifact into Lambda. See `docs/AWS_LAMBDA_DEPLOYMENT.md` for the full recovery
procedure.

## Cost-conscious deployment

**Local execution is the recommended starting point and does not require AWS.**

AWS pricing, free-tier eligibility, quotas and service availability vary by
account, region and current AWS policies. Therefore this project deliberately
does not promise a zero-cost AWS deployment.

Before using AWS:

1. Set a cost/budget alert.
2. Use a small dataset.
3. Prefer serverless/on-demand resources.
4. Avoid an always-on SageMaker endpoint for the first version.
5. Do not call Bedrock in a loop during development.
6. Delete test resources when finished.
7. Never commit credentials or secrets.

## Prerequisites

- Python 3.11+
- Git
- Optional: AWS CLI
- Optional: AWS SAM CLI

## Local setup

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate data

```bash
python src/data_generator.py --rows 1000
```

## Train

```bash
python src/train.py
```

## Evaluate

```bash
python src/evaluate.py
```

## Predict from a payload

```bash
python src/predict.py --payload payloads/incident_timeout.json
```

## Run the API

```bash
uvicorn src.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

POST a payload to `/predict`.

## Run tests

```bash
pytest -q
```

## Git

```bash
git init
git add .
git commit -m "Initial AI incident intelligence project"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

## AWS Lambda / SAM deployment

From the repository root:

```bash
python src/export_lambda_model.py
sam build --template-file infrastructure/template.yaml
sam deploy --guided
```

The SAM template packages **only `lambda/`**. Do not change `CodeUri: ../lambda/`
to the repository root. The Lambda deployment deliberately avoids packaging
NumPy, Pandas, scikit-learn, FastAPI or the local Random Forest artifact.

Bedrock is disabled in the first deployment. Validate Lambda/API Gateway first,
then enable Bedrock as a separate learning step if desired. See
`docs/AWS_LAMBDA_DEPLOYMENT.md` for the detailed procedure and cleanup steps.

## S3 example

```bash
python src/s3_uploader.py \
  --bucket YOUR_BUCKET \
  --file payloads/incident_timeout.json \
  --key incidents/incident_timeout.json
```

## Bedrock

The project contains a prompt contract and an optional Bedrock client.

Set:

```text
AWS_REGION
BEDROCK_MODEL_ID
```

Only select a model that is available to your AWS account and region. Check
current Amazon Bedrock documentation and pricing before invoking it.

## Project structure

```text
integration-incident-intelligence/
├── data/
│   ├── raw/
│   │   └── sample_incidents.json
│   └── processed/
├── payloads/
│   ├── incident_timeout.json
│   ├── incident_authentication.json
│   ├── incident_payload.json
│   ├── incident_transformation.json
│   └── incident_success.json
├── lambda/
│   ├── handler.py
│   ├── model.json
│   └── README.md
├── src/
│   ├── data_generator.py
│   ├── preprocessing.py
│   ├── train.py
│   ├── export_lambda_model.py
│   ├── evaluate.py
│   ├── predict.py
│   ├── api.py
│   ├── bedrock_prompt.py
│   ├── bedrock_client.py
│   ├── aws_lambda_handler.py
│   └── s3_uploader.py
├── tests/
├── infrastructure/
│   ├── template.yaml
│   ├── iam-policy-example.json
│   └── sagemaker/
├── docs/
│   ├── AWS_LAMBDA_DEPLOYMENT.md
│   ├── LEARNING_GUIDE.md
│   ├── PROJECT_PLAN.md
│   ├── GENAI_PROMPT.md
│   └── ARCHITECTURE.md
├── .github/workflows/ci.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── Makefile
├── LICENSE
└── CONTRIBUTING.md
```

## Production roadmap

The learning prototype can evolve into:

```text
Data
  ↓
Validation
  ↓
Feature Engineering
  ↓
Training
  ↓
Evaluation
  ↓
Model Versioning / Registry
  ↓
Deployment
  ↓
Monitoring
  ↓
Drift Detection
  ↓
Retraining
```

Do not start with Kubernetes, EKS, RAG, vector databases or multi-agent
systems. First make the small system understandable and testable.

## Important limitation

The dataset is synthetic. This is a learning/demo artifact, not a production
incident automation system. Production use would require real data,
validation, security controls, observability, model governance, access
controls, privacy review and human oversight.

## ServiceNow incident creation extension

This version adds ServiceNow **after the existing ML + Bedrock processing**. See `SERVICENOW_EXECUTION_GUIDE.md`.

The Lambda runtime remains lightweight and uses Python standard-library HTTPS for the ServiceNow Table API. It supports disabled, mock, and real ServiceNow modes, correlation-based duplicate lookup/update, and AWS Secrets Manager credentials.
