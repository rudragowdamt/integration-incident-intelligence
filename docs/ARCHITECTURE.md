# Architecture

## V1

```text
JSON/CSV
  |
  v
Python preprocessing
  |
  v
Random Forest
  |
  +--> severity
  |
  +--> confidence
  |
  v
FastAPI
```

## V2 AWS

```text
S3 -> Lambda -> ML inference
              |
              +-> Bedrock explanation
              |
              +-> S3 report
              |
              +-> CloudWatch
```

## V3 MLOps

```text
S3
 |
 v
Training data
 |
 v
SageMaker training
 |
 v
Evaluation
 |
 v
Model Registry
 |
 v
Approved model
 |
 v
Inference
 |
 v
Monitoring
 |
 +------> retraining
```
