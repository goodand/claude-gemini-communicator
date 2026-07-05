# Grader Agent Guide

Use this to grade a single run against assertions.

## Goal

Evaluate whether each assertion passed.

## Rules

- read the prompt
- read the output
- grade each assertion independently
- use evidence from the output
- do not infer missing content as present
- keep explanations short and concrete

## Required grading schema

Return JSON with this shape:

```json
{
  "expectations": [
    {
      "text": "assertion text",
      "passed": true,
      "evidence": "brief evidence"
    }
  ],
  "overall_notes": "short summary"
}
``` 
Grading guidance
Pass

Use when the assertion is clearly satisfied.

Fail

Use when the assertion is clearly not satisfied.

Edge case

If the assertion is ambiguous, mark fail and explain why the assertion needs rewriting.
