# Lambda deployment package

This directory is intentionally isolated from the full ML development stack.
SAM packages only this directory for the Lambda function.

## Why this exists

The full project uses Pandas, NumPy, scikit-learn and joblib for training and
local model serving. Those libraries should not be copied into this Lambda
function. The AWS Lambda deployment uses a compact JSON export of a trained
multinomial logistic regression model and performs inference with Python's
standard library only.

This keeps the deployment package small and demonstrates an important ML
engineering concept: **training dependencies and inference dependencies do not
have to be the same**.

## Optional Bedrock

Bedrock is disabled by default. To enable it, set:

- `ENABLE_BEDROCK=true`
- `BEDROCK_MODEL_ID=<a model ID available in your AWS region>`

The Lambda execution role must then have the required `bedrock:InvokeModel`
permission for the selected model. Keep it disabled while validating the
serverless deployment if cost control is the priority.
