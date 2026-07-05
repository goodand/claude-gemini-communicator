# Triggering and Routing

## Why this matters

A skill that never triggers is functionally dead.
A skill that triggers too often causes confusion and overlap.

## Description design

A good description should say:

- what the skill does
- when to use it
- what kinds of requests should trigger it
- what differentiates it from nearby skills

## Good description pattern

`Use this skill when the user wants to [action], especially when [context].`

## Examples

### Weak
`A skill for documents.`

### Better
`Use this skill when the user wants to create, revise, or format structured
documents such as reports, proposals, or briefs.`

### Weak
`Skill for APIs.`

### Better
`Use this skill when the user wants to integrate, test, or troubleshoot API
workflows, especially when schemas, authentication, or request formatting matter.`

## Routing hints in AGENTS.md / CLAUDE.md

Add short routing hints for:

- when to trigger
- when not to trigger
- which nearby skills it should outrank
- keywords or task patterns that commonly appear

## Overlap management

Too many near-duplicate skills reduce routing quality.

Prefer:

- fewer skills
- clearer boundaries
- sharper descriptions
- explicit "use this instead of X when Y" guidance

## Trigger eval set

Create positive and negative trigger examples.

### Positive
Prompts that should trigger the skill.

### Negative
Prompts that should not trigger the skill.

Use these to refine wording.
