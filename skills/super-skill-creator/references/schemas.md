# Schemas

## evals.json

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 0,
      "prompt": "User task prompt",
      "expected_output": "Description of expected result",
      "files": [],
      "assertions": [
        "Output includes X",
        "Output follows Y format"
      ]
    }
  ]
}
```

## eval_metadata.json

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name",
  "prompt": "User task prompt",
  "assertions": [
    "Output includes X",
    "Output follows Y format"
  ]
}
```

## timing.json

```json
{
  "total_tokens": 12000,
  "duration_ms": 8500,
  "total_duration_seconds": 8.5
}
```

## grading.json

```json
{
  "expectations": [
    {
      "text": "Output includes X",
      "passed": true,
      "evidence": "Found X in paragraph 2"
    }
  ],
  "overall_notes": "Short summary"
}
```

## benchmark.json

```json
{
  "skill_name": "example-skill",
  "iteration": "iteration-1",
  "variants": [
    {
      "name": "with_skill",
      "mean_pass_rate": 0.75,
      "mean_duration_ms": 8200,
      "mean_tokens": 11800
    },
    {
      "name": "baseline",
      "mean_pass_rate": 0.5,
      "mean_duration_ms": 7600,
      "mean_tokens": 9800
    }
  ]
}
```
