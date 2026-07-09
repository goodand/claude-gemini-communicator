# Improvement Loop

This document explains how to iteratively improve a skill.

## Loop

1. define the skill
2. write realistic eval prompts
3. run with-skill and baseline
4. grade assertions
5. aggregate benchmark data
6. review qualitative outputs
7. identify weak points
8. improve the skill
9. repeat

## Common improvement targets

- too much text in SKILL.md
- unclear trigger description
- duplicated docs
- no scripts for deterministic logic
- unrealistic eval prompts
- weak assertions
- poor cost/performance tradeoff

## Anti-patterns

- adding more text instead of better structure
- overfitting to one example prompt
- grading subjectively when assertions could be objective
- changing both prompts and skill at once
- keeping too many overlapping skills

## Good iteration questions

- what failed most often?
- what improved most?
- what costs increased?
- what can move into scripts?
- what can move into references?
- what should be removed?