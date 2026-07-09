---
name: xcode-mcp-setup
description: >-
  Set up Xcode Model Context Protocol (MCP) access for agentic coding on macOS.
  Use this skill when the user wants to connect Xcode to Codex CLI, Claude Code,
  Gemini CLI, or another MCP-capable agent. This skill covers Xcode selection,
  first-launch setup, mcpbridge verification, the required Xcode UI toggle, and
  CLI registration commands.
license: MIT
---

# Xcode MCP Setup

## Purpose

Use this skill when the user wants to enable Xcode's MCP integration so an external coding agent can interact with Xcode for tasks like build, test, documentation lookup, and project automation.

This skill is specifically for:

- setting the active Xcode installation
- running first-launch setup
- verifying `xcrun mcpbridge`
- enabling the Xcode MCP server in the UI
- registering Xcode MCP with Codex CLI, Claude Code, or Gemini CLI

Do not use this skill for general Xcode troubleshooting unless it directly blocks MCP setup.

## Core rules

- Prefer the user's actual installed Xcode path.
- Do not assume the stable app name; check whether they use `Xcode.app` or `Xcode-beta.app`.
- Be explicit that one step is still manual: the Xcode UI toggle for **Xcode Tools**.
- Keep instructions CLI-first.
- If the user wants automation, use the bundled shell script.
- If `mcpbridge` is missing, diagnose Xcode selection and first-launch status before guessing.
- If a CLI registration command is broken, use the app's config file as a fallback instead of stopping.

## Workflow

### 1. Identify the target Xcode path

Common locations:

- `/Applications/Xcode.app`
- `/Applications/Xcode-beta.app`

If the user already told you which one they use, do not ask again.

### 2. Switch to that Xcode

Run:

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

### 3. Verify MCP bridge

Run:

```bash
xcrun mcpbridge -h
```

If this fails, do not proceed to agent registration yet.

### 4. Register the MCP server with the target agent

Preferred commands:

```bash
codex mcp add xcode -- xcrun mcpbridge
claude mcp add --transport stdio --scope user xcode -- xcrun mcpbridge
gemini mcp add -s user xcode xcrun mcpbridge
```

Fallback:

- If `claude mcp add` is broken, update `~/Library/Application Support/Claude/claude_desktop_config.json`
- Add `mcpServers.xcode` with `command: "xcrun"` and `args: ["mcpbridge"]`

### 5. Manual Xcode UI step

In Xcode:

- `Settings > Intelligence > Model Context Protocol`
- Enable `Xcode Tools`
