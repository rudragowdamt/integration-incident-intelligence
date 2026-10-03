# Optional SageMaker / MLOps path

The first version deliberately trains with scikit-learn locally. A later
version can move training to SageMaker.

Conceptual lifecycle:

```text
S3 training data
      |
      v
SageMaker training job
      |
      v
Model artifact
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
CloudWatch monitoring
```

For a cost-conscious learning project, avoid leaving an always-on real-time
endpoint running. Study batch/serverless inference and endpoint lifecycle
options before creating resources.

Suggested V2 work:

- package training code
- upload training data to S3
- create a training job
- evaluate the model
- register the model
- deploy only for a short test window
- collect metrics
- delete the endpoint
