# Image-to-table exchange schema

```json
{
  "records": [
    {
      "source": "report-001.jpg",
      "fields": {
        "WBC": {
          "value": "5.55",
          "unit": "10^9/L",
          "flag": "high",
          "confidence": 0.96,
          "status": "read"
        },
        "HGB": {
          "status": "unreadable",
          "raw": "blurred"
        }
      }
    }
  ]
}
```

`source` is required and unique. A field may be a scalar or an object. Object keys supported by the
normalizer are `value`, `unit`, `flag`, `confidence`, `status`, and `raw`. Keep raw text only when it
helps human review; do not place PHI in a public artifact.

