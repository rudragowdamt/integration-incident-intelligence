# AI-Powered Integration Incident Intelligence

**Enterprise Incident Triage using Machine Learning, Generative AI, AWS Serverless and ServiceNow**

A hands-on AI engineering project that applies **Machine Learning + Generative AI + AWS + ITSM automation** to a real enterprise integration-support problem.

The solution accepts an integration failure, predicts incident severity using a supervised ML model, uses Amazon Bedrock to generate an incident explanation and recommended investigation actions, and automatically creates or updates an incident in ServiceNow.

> **Core design principle:**  
> **ML classifies. GenAI explains. ServiceNow operationalizes.**

---

## Why I Built This

Enterprise integration environments can contain hundreds or thousands of interfaces connecting ERP, CRM, APIs, databases and external systems.

When an interface fails, support engineers typically need to:

- inspect error details and logs;
- determine severity;
- identify recurring failure patterns;
- investigate possible causes;
- determine the next troubleshooting actions;
- document the incident;
- create or update an ITSM ticket.

This project explores how **ML and Generative AI can assist that workflow without replacing human validation**.

The goal is not autonomous incident resolution.

The goal is to make the **first stage of incident triage faster, more consistent and more informative**.

---

# What the Solution Does

An integration incident is submitted as JSON.

The system then:

1. Validates the incident.
2. Extracts operational features.
3. Uses a supervised ML model to predict severity.
4. Returns prediction confidence and class probabilities.
5. Sends the incident evidence and ML result to Amazon Bedrock.
6. Generates:
   - incident summary;
   - probable root-cause hypothesis;
   - recommended investigation actions.
7. Maps the intelligence into a ServiceNow incident.
8. Searches for an existing correlated active incident.
9. Creates a new ServiceNow incident or updates the existing one.
10. Returns the ServiceNow `INC` number to the caller.
11. Records runtime information through Amazon CloudWatch.

---

# End-to-End Architecture

```text
                    Integration Incident
                            |
                            v
                      API Gateway
                            |
                            v
                       AWS Lambda
                            |
                +-----------+-----------+
                |                       |
                v                       |
        ML Severity Classifier          |
                |                       |
                v                       |
        Severity + Confidence           |
                |                       |
                v                       |
          Amazon Bedrock                |
                |                       |
                v                       |
        Incident Intelligence           |
        - Incident Summary              |
        - Probable Root Cause           |
        - Recommended Actions           |
                |                       |
                v                       |
          ServiceNow Client <------ AWS Secrets Manager
                |
                v
        ServiceNow Table API
                |
         +------+------+
         |             |
         v             v
      CREATE         UPDATE
     Incident       Incident
         |             |
         +------+------+
                |
                v
           INCxxxxxxx

AWS Lambda -----------------------> CloudWatch
```

---

# Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Machine Learning | Supervised multi-class classification |
| Runtime Model | Compact multinomial logistic regression |
| Generative AI | Amazon Bedrock |
| Foundation Model | Amazon Nova Lite |
| API | Amazon API Gateway |
| Compute | AWS Lambda |
| Infrastructure as Code | AWS SAM / CloudFormation |
| ITSM | ServiceNow Table API |
| Secret Management | AWS Secrets Manager |
| Monitoring | Amazon CloudWatch |
| Local API | FastAPI |
| Testing | pytest |
| Version Control | Git / GitHub |
| CI | GitHub Actions |
| Object Storage / Learning | Amazon S3 |

---

# Example Incident

```json
{
  "interface_name": "SAP-to-Salesforce",
  "source_system": "SAP",
  "target_system": "Salesforce",
  "timestamp": "2026-09-25T10:31:00Z",
  "error_type": "CONNECTION_TIMEOUT",
  "error_message": "Connection timed out while calling downstream API",
  "duration_seconds": 45,
  "retry_count": 3,
  "payload_size_mb": 4.2,
  "previous_failures": 17,
  "http_status": 504,
  "environment": "PROD"
}
```

---

# Example ML Result

For an end-to-end test of the above incident, the classifier produced:

```text
Severity: CRITICAL
Confidence: 0.9986
Model: compact_multinomial_logistic_regression
Model Version: 1.0.0
```

The model also returns probabilities across the supported severity classes.

> This result is from the learning/demo model trained on synthetic data.  
> It should not be interpreted as evidence of production model accuracy.

---

# Generative AI Analysis

The incident evidence and ML prediction are passed to Amazon Bedrock.

The GenAI layer generates:

```text
Incident Summary
        +
Probable Root Cause
        +
Recommended Investigation Actions
        +
Priority Context
```

For example:

```text
Incident:
SAP-to-Salesforce connection timeout

ML Severity:
CRITICAL

Probable Root Cause:
The connection to the downstream Salesforce API may have timed out.

Recommended Investigation:
- Check network connectivity.
- Check downstream API availability.
- Review recent HTTP 504 responses.
- Review retry behavior and related failures.
```

## Important AI Governance Principle

The system generates a:

> **Probable Root Cause — NOT a confirmed RCA**

Generative AI is used to assist investigation.

A support engineer must validate the evidence before confirming the root cause or performing high-impact remediation.

---

# Why ML + GenAI?

The project deliberately separates structured decision-making from natural-language generation.

```text
             Incident Evidence
                    |
          +---------+---------+
          |                   |
          v                   v
         ML                 GenAI
          |                   |
          v                   v
     Classification       Explanation
     Severity             Summary
     Confidence           Probable Cause
     Probabilities        Recommended Actions
```

### Machine Learning

ML provides a **structured and measurable prediction**.

It can be evaluated using metrics such as:

- precision;
- recall;
- F1 score;
- confusion matrix;
- class probabilities.

### Generative AI

GenAI provides **human-readable contextual assistance**.

It is better suited for:

- summarization;
- explanation;
- investigation guidance;
- natural-language incident notes.

This separation makes the solution easier to **test, evaluate and govern**.

---

# ServiceNow Integration

The final stage of the project connects the AI workflow to a real ITSM process.

The Lambda function calls the ServiceNow Table API after ML and Bedrock processing.

```text
ML Prediction
      |
      v
Bedrock Analysis
      |
      v
ServiceNow Payload
      |
      v
Correlation Check
      |
   +--+--+
   |     |
   v     v
Create  Update
   |     |
   +--+--+
      |
      v
  INCxxxxxxx
```

The ServiceNow incident contains information such as:

- interface name;
- error type;
- environment;
- ML severity;
- ML confidence;
- model version;
- GenAI incident summary;
- probable root cause;
- recommended investigation actions.

---

# Duplicate Incident Handling

The project creates a deterministic correlation ID using:

```text
interface_name
      +
error_type
      +
environment
```

Before creating a new incident, the ServiceNow client searches for an active incident with the same correlation ID.

```text
Incident Received
       |
       v
Generate Correlation ID
       |
       v
Search ServiceNow
       |
    +--+--+
    |     |
   YES    NO
    |     |
    v     v
 Update  Create
 Existing New Incident
 Incident
```

This demonstrates a basic **idempotency/correlation pattern** instead of blindly generating duplicate ITSM incidents.

---

# Security

No ServiceNow password or AWS credential is stored in this repository.

ServiceNow credentials are stored in:

**AWS Secrets Manager**

The deployed workflow follows this pattern:

```text
AWS Lambda
     |
     | Secret ARN
     v
AWS Secrets Manager
     |
     v
ServiceNow Credentials
     |
     v
ServiceNow API
```

The Lambda function receives only the Secrets Manager ARN and retrieves the credentials at runtime using IAM permissions.

Never commit:

- ServiceNow passwords;
- AWS access keys;
- AWS secret access keys;
- AWS session tokens;
- `.env` files;
- Secrets Manager secret values;
- private keys.

For a production implementation, a dedicated least-privilege ServiceNow integration account should be used.

---

# Project Evolution

This project was deliberately built incrementally.

### V1 — Machine Learning

```text
Incident
   ↓
Feature Engineering
   ↓
ML Severity Classification
```

### V2 — Generative AI

```text
Incident
   ↓
ML Classification
   ↓
Amazon Bedrock
   ↓
Incident Explanation
```

### V3 — Enterprise ITSM Automation

```text
Incident
   ↓
API Gateway
   ↓
AWS Lambda
   ↓
ML Classification
   ↓
Amazon Bedrock
   ↓
AWS Secrets Manager
   ↓
ServiceNow
   ↓
INCxxxxxxx
```

This incremental approach made it possible to validate each layer independently before adding the next capability.

---

# Key Engineering Learnings

This project provided hands-on experience across **ML, GenAI, serverless AWS, MLOps and enterprise ITSM integration**.

Key lessons included:

- separating ML training dependencies from inference dependencies;
- exporting a compact model for serverless inference;
- using ML for measurable classification and GenAI for explanation;
- integrating Amazon Bedrock with AWS Lambda;
- designing prompts that distinguish probable from confirmed root cause;
- integrating ServiceNow through the Table API;
- implementing correlation logic to reduce duplicate incidents;
- storing credentials securely in AWS Secrets Manager;
- applying IAM permissions to runtime secret retrieval;
- deploying infrastructure using AWS SAM / CloudFormation;
- troubleshooting Lambda package-size limitations;
- diagnosing deployed Lambda environment configuration;
- troubleshooting malformed Secrets Manager JSON;
- using CloudWatch and API responses for production-style troubleshooting;
- validating the complete workflow through Postman.

---

# Important Lambda Packaging Lesson

One of the most useful engineering lessons from this project involved the AWS Lambda deployment package.

The repository contains the complete ML development environment, including libraries used for training.

Lambda does **not** need those training dependencies.

The SAM deployment therefore intentionally uses:

```yaml
CodeUri: ../lambda/
```

and **not**:

```yaml
CodeUri: ../
```

The Lambda runtime contains only the lightweight inference components.

```text
Full Repository
│
├── NumPy
├── Pandas
├── scikit-learn
├── training code
├── evaluation code
│
└── lambda/
      ├── handler.py
      ├── model.json
      └── servicenow_client.py
             |
             v
       AWS Lambda Package
```

The compact deployment model is generated using:

```bash
python src/export_lambda_model.py
```

This separation resolved a real Lambda deployment failure caused by exceeding the AWS unzipped deployment-package size limit.

---

# Another Real Troubleshooting Lesson

During the ServiceNow integration, the ML and Bedrock stages worked but no ServiceNow incident was initially created.

Runtime inspection showed:

```text
SERVICENOW_ENABLED=false
SERVICENOW_MODE=mock
```

The deployed configuration was corrected to use the real ServiceNow integration.

A subsequent request reached ServiceNow processing but returned a JSON parsing error.

The root cause was a malformed secret stored in AWS Secrets Manager.

The secret was corrected to valid JSON:

```json
{
  "instance_url": "https://<YOUR_INSTANCE>.service-now.com",
  "username": "<YOUR_INTEGRATION_USER>",
  "password": "<STORED_ONLY_IN_SECRETS_MANAGER>"
}
```

No Lambda code change was required.

This reinforced an important operational lesson:

> **When troubleshooting distributed systems, first identify which layer is failing before changing working code.**

---

# Local Setup

## Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

# Generate Training Data

```bash
python src/data_generator.py --rows 1500
```

The project uses synthetic integration incidents so the complete ML lifecycle can be reproduced without exposing enterprise production data.

---

# Train the Model

```bash
python src/train.py
```

---

# Evaluate

```bash
python src/evaluate.py
```

---

# Export the Lambda Model

```bash
python src/export_lambda_model.py
```

This generates the compact model representation required by the Lambda runtime.

---

# Run a Local Prediction

```bash
python src/predict.py --payload payloads/incident_timeout.json
```

---

# Run the Local API

```bash
uvicorn src.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Use the Swagger interface to test the local prediction API.

---

# Run Tests

```bash
pytest -q
```

Tests should be run before every deployment.

---

# AWS Deployment

## Prerequisites

Install and configure:

- AWS CLI;
- AWS SAM CLI;
- Python 3.11+;
- Git.

Verify AWS access:

```bash
aws sts get-caller-identity
```

Validate the SAM template:

```bash
sam validate --template-file infrastructure/template.yaml
```

Verify the Lambda deployment boundary:

```powershell
Select-String `
  -Path .\infrastructure\template.yaml `
  -Pattern "CodeUri"
```

Expected:

```text
CodeUri: ../lambda/
```

---

# Build

```bash
sam build --template-file infrastructure/template.yaml
```

Expected:

```text
Build Succeeded
```

---

# Deploy

For the first deployment:

```bash
sam deploy --guided
```

For subsequent deployments:

```bash
sam deploy
```

AWS SAM / CloudFormation manages the serverless infrastructure.

---

# Bedrock Configuration

The deployed Lambda uses environment configuration similar to:

```text
ENABLE_BEDROCK=true
BEDROCK_REGION=<AWS_REGION>
BEDROCK_MODEL_ID=<BEDROCK_MODEL_OR_INFERENCE_PROFILE>
```

Only use models available to your AWS account and region.

The completed implementation was validated using Amazon Nova Lite through Amazon Bedrock.

---

# ServiceNow Configuration

The Lambda runtime uses:

```text
SERVICENOW_ENABLED=true
SERVICENOW_MODE=servicenow
SERVICENOW_SECRET_ARN=<AWS_SECRETS_MANAGER_ARN>
```

The actual ServiceNow password must **not** be placed in the SAM template.

Credentials belong in AWS Secrets Manager.

---

# Monitoring

AWS Lambda execution can be monitored using Amazon CloudWatch.

For SAM deployments:

```powershell
sam logs `
  --stack-name integration-incident-intelligence-servicenow `
  --region <AWS_REGION> `
  --tail
```

CloudWatch is useful for diagnosing:

- Lambda errors;
- Bedrock invocation failures;
- ServiceNow authentication errors;
- malformed configuration;
- runtime exceptions.

---

# Cost-Conscious Design

This project deliberately uses a lightweight architecture.

Cost-conscious decisions include:

- serverless Lambda instead of an always-on application server;
- API Gateway for managed API access;
- compact ML inference inside Lambda;
- no always-on SageMaker endpoint;
- on-demand Amazon Bedrock inference;
- a lightweight foundation model for incident explanation;
- small prompts and controlled output sizes;
- no OpenSearch/vector database for this version;
- no Bedrock Agent or Knowledge Base;
- cleanup of experimental AWS resources after testing.

AWS pricing, free-tier eligibility and service availability vary by account, region and current AWS policies.

This project therefore does **not** claim that AWS execution will always be zero-cost.

---

# Project Structure

```text
integration-incident-intelligence/
├── data/
│   ├── raw/
│   └── processed/
│
├── payloads/
│   ├── incident_timeout.json
│   ├── incident_authentication.json
│   ├── incident_payload.json
│   ├── incident_transformation.json
│   └── incident_success.json
│
├── lambda/
│   ├── handler.py
│   ├── model.json
│   └── servicenow_client.py
│
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
│   └── s3_uploader.py
│
├── tests/
│
├── infrastructure/
│   ├── template.yaml
│   └── iam-policy-example.json
│
├── docs/
│   ├── AWS_LAMBDA_DEPLOYMENT.md
│   ├── LEARNING_GUIDE.md
│   ├── PROJECT_PLAN.md
│   ├── GENAI_PROMPT.md
│   └── ARCHITECTURE.md
│
├── SERVICENOW_EXECUTION_GUIDE.md
├── .github/workflows/ci.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── samconfig.toml
├── Makefile
├── LICENSE
└── CONTRIBUTING.md
```

---

# MLOps Lifecycle Demonstrated

```text
Synthetic Data
      ↓
Preprocessing
      ↓
Training
      ↓
Evaluation
      ↓
Model Artifact
      ↓
Lambda Export
      ↓
Automated Tests
      ↓
SAM Build
      ↓
Deployment
      ↓
Inference
      ↓
CloudWatch
      ↓
Operational Feedback
```

This is a **compact MLOps implementation**, not a full enterprise ML platform.

---

# Production Roadmap

A production implementation could evolve toward:

```text
Historical Enterprise Incidents
              ↓
      Data Validation
              ↓
      Feature Engineering
              ↓
           Training
              ↓
          Evaluation
              ↓
      Model Registry
              ↓
      CI/CD Approval
              ↓
         Deployment
              ↓
         Monitoring
              ↓
       Drift Detection
              ↓
          Retraining
```

Additional enhancements could include:

- historical labeled enterprise incidents;
- model registry and model versioning;
- prompt versioning;
- drift monitoring;
- authenticated API access;
- SQS / Step Functions for resilient orchestration;
- dead-letter queues and retry handling;
- dashboards and operational metrics;
- human feedback capture;
- ServiceNow least-privilege integration account;
- structured GenAI output validation;
- RAG over approved enterprise runbooks;
- retrieval of similar historical incidents;
- human-in-the-loop approval.

---

# Future RAG Extension

A logical next step is to ground incident recommendations using approved enterprise support documentation.

```text
Incident
   |
   v
ML + Bedrock
   |
   +----------------------+
   |                      |
   v                      v
Incident Evidence    Enterprise Runbooks
                          |
                          v
                     Vector Search
                          |
                          v
                    Relevant Context
                          |
                          v
                     Grounded GenAI
                          |
                          v
                Recommended Procedure
```

This would evolve the project from general incident intelligence toward an **enterprise integration support assistant**.

---

# Important Limitations

This is a **learning and portfolio project**, not a production incident-management system.

The dataset is synthetic.

High model accuracy or confidence on synthetic data does not demonstrate production performance.

Production use would require:

- representative historical incident data;
- independent model validation;
- security review;
- authentication and authorization;
- least-privilege access;
- privacy and data-retention controls;
- model and prompt governance;
- monitoring and alerting;
- drift detection;
- resilience and retry mechanisms;
- human oversight.

AI-generated probable root causes must not be treated as confirmed RCA without supporting operational evidence.

---

# What This Project Demonstrates

This project demonstrates practical experience across:

**Machine Learning**
- supervised classification;
- feature engineering;
- model evaluation;
- inference;
- model packaging.

**Generative AI**
- Amazon Bedrock;
- prompt design;
- grounding;
- hallucination awareness;
- human-in-the-loop design.

**AWS**
- API Gateway;
- Lambda;
- Bedrock;
- Secrets Manager;
- CloudWatch;
- SAM;
- CloudFormation;
- IAM.

**Enterprise Integration**
- incident triage;
- API failures;
- retry patterns;
- HTTP errors;
- correlation;
- downstream-system failures.

**ITSM Automation**
- ServiceNow Table API;
- incident creation;
- incident updates;
- correlation-based duplicate handling.

**MLOps / Engineering**
- Git;
- automated testing;
- model packaging;
- infrastructure as code;
- CI;
- deployment troubleshooting;
- observability;
- cost-conscious architecture.

---

## Final Perspective

The most important part of this project is not any single AWS service or ML algorithm.

It demonstrates how **existing enterprise operational knowledge can be combined with modern AI engineering** to solve a realistic business problem.

The project progressed from:

```text
Machine Learning
      ↓
Generative AI
      ↓
Cloud Deployment
      ↓
Security
      ↓
Enterprise ITSM Integration
      ↓
Operational Troubleshooting
```

That evolution is the core engineering story behind the repository.
