---
name: image-commit-manager
description: Apply only approved rename and metadata changes for image jobs. Use when audited and human-approved records are ready to be committed through filesystem and ExifTool MCPs.
---

# Image Commit Manager

## Overview

Use this skill only at the final commit stage.
It applies conservative file mutations for approved images and leaves unresolved items untouched.

## Use This Skill When

- Human review is complete.
- Approved image records already exist in the registry.
- Rename and metadata actions must be applied with conflict checks.

## Required MCPs

- `conport`
- `agent-task-manager`
- `filesystem`

## Optional MCPs

- `exiftool`

## Commit Workflow

1. Load approved image records from the registry.
2. Re-check path existence and rename collisions.
3. Apply approved rename operations.
4. Apply approved metadata writes when enabled.
5. Mark final commit status and record evidence.

## Guardrails

- Skip items with unresolved conflicts.
- Never rename files using unapproved captions.
- Do not bulk-commit uncertain rows.
- Preserve a clear audit trail in MCP state after each mutation.
