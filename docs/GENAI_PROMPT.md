# GenAI Prompt Contract

## System behavior

The model should:

1. Use supplied evidence only.
2. Never invent operational facts.
3. Separate observed facts from probable causes.
4. Return valid JSON.

## Input

```json
{
  "incident": {
    "error_type": "CONNECTION_TIMEOUT",
    "http_status": 504,
    "retry_count": 3,
    "previous_failures": 17
  },
  "ml_prediction": {
    "severity": "HIGH",
    "confidence": 0.91
  }
}
```

## Output shape

```json
{
  "incident_summary": "...",
  "probable_root_cause": "...",
  "recommended_actions": ["...", "..."],
  "priority": "P1",
  "confidence_note": "..."
}
```

The model must not claim that an endpoint is definitely unavailable unless the
supplied evidence establishes that fact.
