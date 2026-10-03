# AWS infrastructure

## Lambda deployment architecture

The repository intentionally separates the ML development environment from
the Lambda runtime package.

```text
Repository
├── src/                 # Pandas / NumPy / scikit-learn training code
├── models/              # Local training artifacts
└── lambda/              # ONLY this directory is deployed to Lambda
    ├── handler.py
    └── model.json
```

The SAM template uses:

```yaml
CodeUri: ../lambda/
```

This is the key fix for the Lambda 250 MB unzipped deployment error. The
previous template used `CodeUri: ../`, which caused the whole repository and
its ML dependencies to be considered for the function package.

## Deploy

From the repository root:

```bash
sam build --template-file infrastructure/template.yaml
sam deploy --guided
```

The first deployment can use the generated API endpoint in the CloudFormation
outputs.

## Test

```bash
curl -X POST "YOUR_API_ENDPOINT/incident" \
  -H "Content-Type: application/json" \
  --data @payloads/incident_timeout.json
```

On Windows PowerShell:

```powershell
$body = Get-Content payloads/incident_timeout.json -Raw
Invoke-RestMethod -Method Post `
  -Uri "YOUR_API_ENDPOINT/incident" `
  -ContentType "application/json" `
  -Body $body
```

## Bedrock

Bedrock is intentionally disabled in the first deployment. This lets you
validate Lambda/API Gateway without introducing model invocation costs.

When you are ready, set `ENABLE_BEDROCK=true`, provide a model ID available in
your AWS region, and grant the Lambda execution role the minimum required
`bedrock:InvokeModel` permission. Keep this as a separate step so you can
clearly identify and control GenAI costs.

## Cleanup

When finished with the AWS exercise:

```bash
sam delete
```

Also check S3, CloudWatch Logs, API Gateway and other resources created during
experiments. AWS pricing and free-tier eligibility can change, so do not treat
this project as a guaranteed zero-cost AWS deployment.
