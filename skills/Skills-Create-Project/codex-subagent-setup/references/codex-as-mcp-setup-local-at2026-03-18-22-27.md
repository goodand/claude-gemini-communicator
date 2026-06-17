# Codex-as-MCP Local Setup

- recorded_at: `2026-03-18-22-27`
- source_scope: `local_codebase_only`
- purpose: `현재 로컬 Codex subagent 실행 경로와 MCP 연결 상태를 정리`

## Current local facts

- Codex CLI version was rechecked after update: `0.115.0`
- `codex features list` showed `multi_agent = stable true`
- local MCP server name in Codex config: `codex-subagent`
- command: `uvx codex-as-mcp@latest`
- `tool_timeout_sec = 600` was added to `~/.codex/config.toml`
- workspace-local Claude-compatible MCP file exists at:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/.mcp.json`

## Important constraint

`codex-as-mcp` is broad. It is suitable for trusted local repositories, but role boundaries should still be enforced through agent guides and task packets.

## Practical implication

This skill should not assume that runtime nickname state is enough. File-backed role guides under `agents/*.md` are the stable source of subagent identity.
