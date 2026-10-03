# AI/ML/GenAI/AWS Learning Guide

## 1. Supervised ML

You have examples with a target label:

```text
incident features -> severity label
```

The algorithm learns a relationship between features and the target.

## 2. Features

This project uses:

- duration_seconds
- retry_count
- payload_size_mb
- previous_failures
- http_status
- error_type
- environment
- interface_name

Ask whether each field would really be available at decision time.

## 3. Classification

Severity is a categorical target:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The model predicts one of these classes.

## 4. Why Random Forest?

It is a practical baseline for mixed operational features and is easier to
understand than starting with a neural network.

## 5. Evaluation

Learn:

- accuracy
- precision
- recall
- F1
- confusion matrix

For incident triage, class imbalance can make accuracy misleading.

## 6. GenAI

The GenAI layer has a different responsibility:

```text
structured evidence + ML result
             |
             v
       foundation model
             |
             v
human-readable explanation
```

Do not use the LLM as a substitute for all deterministic logic.

## 7. Hallucination control

Supply only evidence you trust and instruct the model not to invent facts.

## 8. APIs

FastAPI teaches:

- HTTP
- JSON
- request validation
- response contracts
- model serving

## 9. AWS

S3 teaches object storage.

Lambda teaches serverless compute.

Bedrock teaches managed foundation-model access.

CloudWatch teaches observability.

SageMaker teaches managed ML workflows.

## 10. MLOps

The important concept is not the number of AWS services. It is lifecycle
control:

```text
data -> train -> evaluate -> version -> deploy -> monitor -> retrain
```

## 11. Interview questions

Be ready to answer:

1. Why is this supervised learning?
2. What is the target?
3. Why one-hot encoding?
4. Why Random Forest?
5. What is overfitting?
6. What is data leakage?
7. Precision vs recall?
8. Why F1?
9. Why separate ML and GenAI?
10. What is an LLM hallucination?
11. Why FastAPI?
12. Why Lambda?
13. Why S3?
14. What is CI?
15. What is model drift?
16. What would you change with real production data?

## Enterprise positioning

A useful explanation is:

> I chose an integration incident use case because it lets me apply ML and
> GenAI to an operational problem I understand. The classifier handles
> structured severity prediction while the GenAI layer turns evidence into a
> controlled explanation. The project then extends from local Python to API,
> Git CI and AWS serverless deployment.
