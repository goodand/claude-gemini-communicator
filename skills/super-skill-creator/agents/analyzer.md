# Analyzer Agent Guide

Use this when reviewing benchmark results for a skill.

## Goal

Identify patterns that raw pass/fail totals may hide.

## Look for

- assertions that always pass regardless of skill
- assertions that always fail regardless of skill
- high variance across prompts
- higher cost with little quality gain
- routing / triggering mismatch
- duplicated instructions
- opportunities to move logic into scripts
- opportunities to move bulk docs into references

## Questions to answer

1. Where did the skill clearly help?
2. Where did the skill not help?
3. Where did the skill make things worse?
4. Which assertions are weak or non-discriminating?
5. Which prompts reveal the most?
6. Is the token/time cost justified?

## Output format

## Findings

- finding
- finding
- finding

## Likely causes

- cause
- cause

## Recommended changes

- change
- change

## Keep / remove / rewrite

### Keep
- item

### Remove
- item

### Rewrite
- item