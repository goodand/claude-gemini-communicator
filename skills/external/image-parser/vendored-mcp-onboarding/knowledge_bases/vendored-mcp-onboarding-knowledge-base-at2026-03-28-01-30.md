# Vendored MCP Onboarding Knowledge Base

## Purpose

This skill packages the recurring local MCP adoption workflow that has already repeated in this workspace.

## Repo-Specific Signals

The workspace already contains multiple vendored MCP onboarding examples:

- `imagesorcery-mcp`
- `macos-ocr-mcp`
- `paddleocr-mcp`
- `tigaweb-image-edit-sample-mcp`

These examples show the same underlying pattern:

- keep third-party runtimes isolated
- use thin launchers
- patch launcher-level environment first
- update local config and inventory together
- keep canonical smoke evidence

## Core Principles

1. Keep the main workspace runtime clean.
2. Prefer launcher-level fixes over downstream source churn.
3. Treat registration and real usability as separate milestones.
4. Maintain inventory, registry, and smoke artifacts as one package.

## Strong Boundaries

This skill should stop at onboarding and verification.
It should not become:

- a generic MCP builder
- a downstream experiment runner
- a replacement for tool-specific docs after onboarding is done
