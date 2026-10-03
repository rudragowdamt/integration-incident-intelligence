# Project Plan

## Phase 1 — Understand the data

```bash
python src/data_generator.py --rows 1000
```

Inspect the generated CSV.

## Phase 2 — Train

```bash
python src/train.py
python src/evaluate.py
```

Understand every metric.

## Phase 3 — Serve

```bash
uvicorn src.api:app --reload
```

Open `/docs`.

## Phase 4 — Git

```bash
git init
git add .
git commit -m "Initial project"
```

Push to GitHub and let CI run.

## Phase 5 — AWS

Deploy the minimal Lambda template.

## Phase 6 — S3

Store incoming incident payloads and generated reports.

## Phase 7 — GenAI

Pass the structured incident plus ML result to Bedrock and constrain the
response to JSON.

## Phase 8 — MLOps

Add:

- experiment tracking
- model versioning
- model registry
- monitoring
- drift detection
- retraining
- approval gates

Do not begin with Kubernetes, EKS, RAG or multi-agent architecture.
