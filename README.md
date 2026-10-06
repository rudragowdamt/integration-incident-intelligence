# AI-Powered Integration Incident Intelligence

An end-to-end **AI/ML + Generative AI incident intelligence platform** built on AWS that classifies integration failures, generates evidence-grounded incident analysis using Amazon Bedrock, and automatically creates or updates incidents in ServiceNow.

> **ML classifies. GenAI explains. ServiceNow operationalizes.**

---

## 1. Project Overview

Enterprise integration environments can contain hundreds or thousands of interfaces connecting ERP, CRM, APIs, databases, file-transfer platforms, SaaS applications, and downstream systems.

When an integration fails, support teams typically need to:

- inspect logs and payloads
- understand the type of failure
- determine severity
- identify recurring patterns
- formulate a probable root cause
- recommend investigation actions
- create an ITSM incident
- document technical findings for support teams

Much of this first-pass triage is repetitive and time-consuming.

This project demonstrates how **Machine Learning, Generative AI, AWS serverless services, and ServiceNow** can work together to automate that workflow.

---

# 2. Business Problem

A typical integration support team may receive failures such as:

- HTTP 5xx errors
- authentication failures
- authorization failures
- downstream application outages
- timeouts
- malformed payloads
- repeated retry failures
- production interface failures

Engineers often need to manually interpret these failures before creating or updating an incident.

The goal of this project is to automate the first stage of incident intelligence.

The system performs:

```text
Integration Failure
        ↓
ML Severity Classification
        ↓
GenAI Incident Analysis
        ↓
ServiceNow Incident Automation
```

This reduces repetitive triage while keeping humans responsible for final operational decisions.

---

# 3. Solution Architecture

```text
                        ┌───────────────────────┐
                        │ Integration Failure   │
                        │ JSON Payload          │
                        └───────────┬───────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │ Amazon API Gateway    │
                        └───────────┬───────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │ AWS Lambda            │
                        │ Incident Intelligence │
                        └───────────┬───────────┘
                                    │
                   ┌────────────────┼────────────────┐
                   │                │                │
                   ▼                ▼                ▼
          ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
          │ Compact ML     │ │ Amazon       │ │ AWS Secrets      │
          │ Classifier     │ │ Bedrock      │ │ Manager          │
          │                │ │ Nova Lite    │ │                  │
          └───────┬────────┘ └──────┬───────┘ └────────┬─────────┘
                  │                 │                   │
                  │                 │                   │
                  └──────────┬──────┘                   │
                             │                          │
                             ▼                          │
                   ┌───────────────────────┐            │
                   │ Incident Intelligence │            │
                   │ Report                │            │
                   └───────────┬───────────┘            │
                               │                        │
                               └───────────┬────────────┘
                                           │
                                           ▼
                                  ┌───────────────────┐
                                  │ ServiceNow REST   │
                                  │ API               │
                                  └─────────┬─────────┘
                                            │
                                            ▼
                                  ┌───────────────────┐
                                  │ Create / Update   │
                                  │ Incident          │
                                  └───────────────────┘

Monitoring and troubleshooting:
AWS CloudWatch Logs
```

---

# 4. End-to-End Workflow

The application performs the following steps.

### Step 1 — Receive Integration Incident

An integration failure is submitted as JSON through Amazon API Gateway.

Example:

```json
{
  "interface_name": "SAP_ORDER_TO_CRM",
  "error_type": "DOWNSTREAM_UNAVAILABLE",
  "environment": "PROD",
  "http_status": 503,
  "retry_count": 5,
  "previous_failures": 12
}
```

### Step 2 — Validate the Incident

AWS Lambda validates that the required incident attributes are available before processing.

Important attributes include:

```text
interface_name
error_type
environment
http_status
retry_count
previous_failures
```

### Step 3 — ML Severity Classification

A lightweight ML model performs severity classification.

Final runtime model:

```text
Compact Multinomial Logistic Regression
```

Possible classifications:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The model returns:

- predicted severity
- confidence score
- probability distribution
- model version

Example:

```json
{
  "severity": "CRITICAL",
  "confidence": 0.9986,
  "probabilities": {
    "CRITICAL": 0.9986,
    "HIGH": 0.001,
    "LOW": 0.0,
    "MEDIUM": 0.0004
  },
  "model_type": "compact_multinomial_logistic_regression",
  "model_version": "1.0.0"
}
```

The compact model is intentionally designed for serverless inference.

No always-running ML endpoint is required.

---

# 5. Generative AI with Amazon Bedrock

After ML classification, the structured incident information is sent to **Amazon Bedrock**.

The deployed implementation uses an **Amazon Nova Lite APAC inference profile**.

Bedrock generates operationally useful information such as:

- incident summary
- probable root-cause hypothesis
- recommended investigation actions

Example conceptual output:

```json
{
  "summary": "Production SAP-to-CRM integration is repeatedly failing because the downstream service is returning HTTP 503 responses after multiple retries.",
  "probable_root_cause": "The downstream CRM service or one of its dependencies may be unavailable or degraded.",
  "recommended_actions": [
    "Check downstream CRM service availability.",
    "Review application and API gateway logs.",
    "Validate dependency health.",
    "Review recent deployments or infrastructure changes.",
    "Check whether similar failures are affecting other interfaces."
  ]
}
```

---

# 6. Responsible GenAI Design

The system deliberately distinguishes between:

```text
Probable Root Cause
```

and:

```text
Confirmed Root Cause
```

The LLM is instructed to work only from the available incident evidence.

It should not present an inferred root cause as a confirmed RCA.

The generated output is therefore treated as:

> **An investigation hypothesis that must be validated by an engineer.**

This is particularly important when using Generative AI in production support and incident-management workflows.

---

# 7. Why Use ML and GenAI Together?

This project intentionally uses both traditional ML and Generative AI.

## Machine Learning

ML answers:

> **How severe is this incident?**

It provides:

- deterministic structured output
- measurable probabilities
- repeatable classification
- model versioning
- confidence scores

## Generative AI

GenAI answers:

> **What does this incident mean and what should the engineer investigate?**

It provides:

- human-readable explanation
- probable root-cause hypothesis
- recommended investigation actions
- operational context

## ServiceNow

ServiceNow answers:

> **How does this intelligence enter the enterprise support workflow?**

It provides:

- incident tracking
- ownership
- SLA management
- operational workflow
- auditability

Together:

```text
ML Classifies
      ↓
GenAI Explains
      ↓
ServiceNow Operationalizes
```

---

# 8. ServiceNow Integration

The project integrates the AI workflow with ServiceNow using the ServiceNow REST API.

The Lambda function can:

```text
Search for an existing incident
        ↓
Correlation ID exists?
       / \
     YES  NO
      │    │
      │    └── Create new incident
      │
      └────── Update existing incident
```

This avoids blindly creating duplicate incidents for recurring failures.

---

# 9. Incident Correlation

A deterministic correlation ID is generated from:

```text
interface_name
error_type
environment
```

Conceptually:

```text
SHA-256(
    interface_name |
    error_type |
    environment
)
```

This allows repeated failures for the same logical incident pattern to update an existing active incident instead of continuously creating duplicates.

---

# 10. ServiceNow Priority Mapping

The ML severity classification is translated into ServiceNow impact and urgency.

| ML Severity | Impact | Urgency |
|---|---:|---:|
| CRITICAL | 1 | 1 |
| HIGH | 2 | 1 |
| MEDIUM | 2 | 2 |
| LOW | 3 | 3 |

This allows AI-generated severity to participate in the ITSM workflow while keeping the mapping explicit and auditable.

---

# 11. ServiceNow Work Notes

The ServiceNow incident contains useful AI/ML context such as:

```text
ML Severity
ML Confidence
Model Version

GenAI Probable Root Cause (NOT CONFIRMED)

Recommended Investigation Actions

Human validation warning
```

This gives support engineers both machine-generated intelligence and the context needed to validate it.

---

# 12. Secure Credential Management

ServiceNow credentials should **never be stored in source code or committed to Git**.

The AWS implementation supports retrieving ServiceNow credentials from **AWS Secrets Manager**.

Expected secret structure:

```json
{
  "instance_url": "https://devXXXXXX.service-now.com",
  "username": "your-servicenow-integration-user",
  "password": "stored-only-in-secrets-manager"
}
```

Lambda references the secret through:

```text
SERVICENOW_SECRET_ARN
```

For local development, environment variables can also be used.

Real credentials must never be placed in:

```text
README.md
.env.example
CloudFormation/SAM templates
Python source code
Git commits
GitHub
```

---

# 13. AWS Services Used

| Service | Purpose |
|---|---|
| Amazon API Gateway | REST API entry point |
| AWS Lambda | Serverless orchestration and ML inference |
| Amazon Bedrock | Generative AI incident analysis |
| Amazon Nova Lite | LLM used for incident explanation |
| AWS Secrets Manager | Secure ServiceNow credential storage |
| AWS CloudWatch | Logging and troubleshooting |
| AWS SAM | Infrastructure deployment |
| AWS CloudFormation | Infrastructure provisioning |

External enterprise platform:

```text
ServiceNow
```

---

# 14. Technology Stack

```text
Python
FastAPI
scikit-learn
AWS Lambda
Amazon API Gateway
Amazon Bedrock
Amazon Nova Lite
AWS Secrets Manager
AWS CloudWatch
AWS SAM
AWS CloudFormation
ServiceNow REST API
pytest
Git
GitHub
```

---

# 15. Project Structure

```text
integration-incident-intelligence/
│
├── .github/
│
├── data/
│
├── docs/
│
├── infrastructure/
│   └── template.yaml
│
├── lambda/
│   ├── handler.py
│   ├── model.json
│   └── servicenow_client.py
│
├── models/
│
├── payloads/
│
├── src/
│
├── tests/
│   └── test_servicenow.py
│
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── requirements.txt
├── samconfig.toml
└── SERVICENOW_EXECUTION_GUIDE.md
```

---

# 16. Local Setup

Clone the repository:

```bash
git clone <repository-url>
cd integration-incident-intelligence
```

Create a Python virtual environment.

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# 17. Run Tests

Run:

```powershell
pytest -q
```

Current validated result:

```text
7 passed
```

Some dependency deprecation warnings may appear from FastAPI/Starlette test dependencies; these do not affect the current functional test result.

---

# 18. AWS Deployment

The infrastructure is deployed using AWS SAM.

Validate the template:

```powershell
sam validate --template-file .\infrastructure\template.yaml
```

Build:

```powershell
sam build --template-file .\infrastructure\template.yaml
```

Deploy:

```powershell
sam deploy
```

The deployed workflow includes:

```text
API Gateway
    ↓
Lambda
    ↓
ML Inference
    ↓
Amazon Bedrock
    ↓
ServiceNow
```

---

# 19. Lambda Packaging Optimization

One of the important engineering lessons from this project was Lambda deployment-package size.

An early deployment failed because the uncompressed Lambda package exceeded the AWS Lambda size limit.

The initial architecture risked packaging training libraries and unnecessary project files into the Lambda deployment.

The design was improved by:

- separating training from inference
- exporting a compact model
- keeping Lambda runtime dependencies minimal
- packaging only the Lambda runtime directory
- configuring SAM `CodeUri` to point to the Lambda package

The SAM template therefore uses the Lambda-specific source directory rather than packaging the entire repository.

This is an important MLOps principle:

> **Training environments and inference environments have different dependency requirements.**

---

# 20. Model Development Lifecycle

The project demonstrates a simplified ML lifecycle:

```text
Synthetic Incident Data
        ↓
Feature Engineering
        ↓
Model Training
        ↓
Evaluation
        ↓
Compact Model Export
        ↓
Lambda Inference
        ↓
Production API
```

The current model is intended as a portfolio and architecture demonstration.

The training data is synthetic.

Therefore, high model accuracy or confidence should **not** be interpreted as evidence that the model is production-ready.

A production implementation should train and validate against historical enterprise incident data.

---

# 21. MLOps Concepts Demonstrated

The project demonstrates several practical MLOps concepts:

- separation of training and inference
- lightweight model serving
- model versioning
- probability-based classification
- serverless inference
- infrastructure as code
- automated testing
- cloud logging
- secure secret management
- reproducible deployment
- Git-based source control
- model + GenAI orchestration

---

# 22. GenAI Engineering Concepts Demonstrated

The project also demonstrates practical Generative AI concepts:

- prompt construction from structured operational data
- grounding LLM responses in incident evidence
- controlled generation
- structured JSON output
- defensive JSON parsing
- hallucination-risk reduction
- probable-vs-confirmed RCA distinction
- human validation
- integration of LLM output into enterprise workflows

---

# 23. Enterprise Integration Concepts Demonstrated

The solution is designed around real integration-support patterns:

- interface failures
- downstream availability
- authentication failures
- HTTP status analysis
- retry behavior
- recurring failures
- production severity
- incident correlation
- duplicate suppression
- RCA support
- ITSM integration

This makes the project more than an isolated ML demonstration.

It applies AI to an enterprise operational workflow.

---

# 24. Observability

AWS CloudWatch is used to monitor and troubleshoot Lambda execution.

Important areas to monitor include:

```text
Request received
Incident validation
ML prediction
Bedrock invocation
GenAI parsing
Secrets retrieval
ServiceNow request
ServiceNow response
Exceptions
Execution duration
```

Production implementations should additionally introduce structured logging and operational metrics.

---

# 25. Cost-Aware Architecture

The architecture was intentionally designed to avoid unnecessary always-on infrastructure.

Cost-conscious choices include:

- AWS Lambda pay-per-use execution
- API Gateway request-based usage
- compact ML inference inside Lambda
- no continuously running SageMaker endpoint
- Amazon Bedrock on-demand inference
- lightweight Nova model
- small prompts and controlled output
- no vector database required for this use case
- no Bedrock Agent required
- no OpenSearch cluster required

AWS Secrets Manager may incur a small charge and Bedrock/API usage depends on consumption.

The project should therefore be considered **cost-conscious**, not universally zero-cost.

---

# 26. Production Hardening Roadmap

This project demonstrates the complete architecture, but additional controls would be required before enterprise production use.

Recommended improvements include:

### ML

- train on historical labeled incidents
- create train/validation/test datasets
- evaluate class imbalance
- monitor precision/recall by severity
- calibrate probabilities
- implement model registry/versioning
- detect model drift

### GenAI

- stronger structured-output validation
- prompt versioning
- evaluation datasets
- hallucination evaluation
- output safety controls
- token and latency monitoring

### AWS

- API authentication
- least-privilege IAM
- retries
- dead-letter queues
- alarms
- dashboards
- encryption policies
- CI/CD pipelines

### ServiceNow

- dedicated integration user
- least-privilege ServiceNow roles
- OAuth where appropriate
- assignment-group routing
- incident categorization
- SLA integration
- change-management controls

### Governance

- human approval for high-impact remediation
- PII and secret redaction
- audit trails
- data-retention policies
- model/prompt traceability

---

# 27. Project Evolution

The project was intentionally developed incrementally.

## Version 1 — ML Incident Intelligence

```text
Integration Incident
        ↓
AWS Lambda
        ↓
ML Severity Classification
```

Goal:

Learn ML inference and AWS serverless deployment.

---

## Version 2 — Generative AI

```text
Integration Incident
        ↓
ML Classification
        ↓
Amazon Bedrock
        ↓
Incident Explanation
```

Goal:

Add contextual incident analysis and recommended investigation actions.

---

## Version 3 — Enterprise ITSM Automation

```text
Integration Incident
        ↓
ML
        ↓
Amazon Bedrock
        ↓
ServiceNow
```

Goal:

Connect AI intelligence to a real operational ITSM workflow.

This incremental evolution demonstrates how an AI prototype can progress toward an enterprise AI workflow.

---

# 28. Key Engineering Challenges Solved

Several practical issues were encountered and resolved during implementation.

### Lambda Deployment Package Too Large

Problem:

```text
Unzipped size must be smaller than 262144000 bytes
```

Resolution:

- separated training and inference dependencies
- reduced Lambda packaging scope
- exported a compact model
- packaged only runtime components

---

### ServiceNow Integration Not Executing

The Lambda initially had ServiceNow integration disabled through configuration.

Resolution:

- enabled ServiceNow integration
- configured ServiceNow mode
- added Secrets Manager
- added required IAM permission

---

### Secrets Manager JSON Parsing Error

The application later reached the ServiceNow integration path but failed while parsing the stored secret.

Resolution:

- corrected the Secrets Manager value to valid JSON
- validated the required credential fields
- retested without requiring application-code changes

These troubleshooting experiences were an important part of the project because real AI systems require operational debugging in addition to model development.

---

# 29. Testing Strategy

Testing includes the ServiceNow integration logic without requiring every test to create a real ServiceNow incident.

The test suite validates important application behavior such as:

- incident processing
- ServiceNow payload construction
- priority mapping
- correlation behavior
- integration logic

Run:

```powershell
pytest -q
```

Validated project result:

```text
7 passed
```

---

# 30. What I Learned

This project helped strengthen practical knowledge across several areas:

### Machine Learning

- feature engineering
- multiclass classification
- probabilities and confidence
- lightweight inference
- model packaging

### AWS

- Lambda
- API Gateway
- Bedrock
- Secrets Manager
- IAM
- CloudWatch
- SAM
- CloudFormation

### Generative AI

- prompt engineering
- grounded generation
- structured output
- hallucination risk
- human-in-the-loop design

### Enterprise Integration

- incident triage
- production failures
- retry patterns
- RCA workflows
- incident correlation
- ITSM automation

### DevOps / MLOps

- Git
- testing
- infrastructure as code
- packaging
- environment configuration
- deployment troubleshooting

---

# 31. Skills Demonstrated

This project demonstrates hands-on experience with:

```text
AI/ML Engineering
MLOps
Generative AI
Amazon Bedrock
Amazon Nova
AWS Lambda
API Gateway
AWS Secrets Manager
AWS CloudWatch
AWS SAM
CloudFormation
ServiceNow REST APIs
Python
Machine Learning
Prompt Engineering
Incident Management
Enterprise Integration
Production Support Automation
Git / GitHub
pytest
```

---

# 32. Future Enhancement — RAG

A natural next evolution of this project is a **Retrieval-Augmented Generation (RAG) Incident Assistant**.

Instead of asking the LLM to reason only from the incoming incident, the system could retrieve relevant information from:

- integration runbooks
- previous incident resolutions
- known-error databases
- support documentation
- architecture documents
- operational procedures

Future architecture:

```text
Incident
   ↓
ML Classification
   ↓
Retrieve Relevant Runbooks / Historical Knowledge
   ↓
RAG Context
   ↓
Amazon Bedrock
   ↓
Grounded Incident Recommendation
   ↓
ServiceNow
```

This would allow the AI assistant to answer questions such as:

> “Have we seen this failure before?”

> “Which runbook should the engineer follow?”

> “How was a similar incident resolved?”

> “What evidence supports the recommended action?”

This is the planned next stage toward an enterprise **AI-powered integration support assistant**.

---

# 33. Important Limitations

This repository is an educational and portfolio implementation.

Important limitations include:

- training data is synthetic
- model performance does not represent production performance
- GenAI output requires human validation
- probable root cause is not confirmed RCA
- production IAM should be further restricted
- production ServiceNow access should use a dedicated least-privilege integration identity
- enterprise security, compliance, resilience, and governance controls would need additional implementation

---

# 34. Core Design Principle

The core architecture can be summarized in one sentence:

> **Use ML where a measurable decision is required, use GenAI where contextual explanation is required, and use enterprise workflow integration to turn that intelligence into operational action.**

---

# 35. Conclusion

This project demonstrates an end-to-end AI workflow built around a real enterprise integration-support problem.

It combines:

```text
Enterprise Integration Experience
            +
Machine Learning
            +
Generative AI
            +
AWS Serverless Architecture
            +
ServiceNow ITSM Automation
```

The result is a practical example of how traditional production-support workflows can evolve into **AI-assisted enterprise operations** while maintaining human oversight, security, traceability, and operational governance.
