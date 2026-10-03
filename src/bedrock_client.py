"""Optional Amazon Bedrock Runtime client.

This module is intentionally not invoked by the normal local workflow.
Configure AWS credentials, region and a model available to your account before
using it. Review current Amazon Bedrock model/API documentation first.
"""
import json
import os
import boto3
from bedrock_prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

def explain_with_bedrock(incident, prediction):
    region = os.environ["AWS_REGION"]
    model_id = os.environ["BEDROCK_MODEL_ID"]

    client = boto3.client("bedrock-runtime", region_name=region)

    prompt = USER_PROMPT_TEMPLATE.format(
        incident_json=json.dumps(incident, indent=2),
        prediction_json=json.dumps(prediction, indent=2),
    )

    response = client.converse(
        modelId=model_id,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{
            "role": "user",
            "content": [{"text": prompt}],
        }],
        inferenceConfig={
            "maxTokens": 500,
            "temperature": 0.2,
        },
    )

    text = response["output"]["message"]["content"][0]["text"]
    return json.loads(text)
