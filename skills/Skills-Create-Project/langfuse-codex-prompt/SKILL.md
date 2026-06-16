---
name: langfuse-codex-prompt
description: >-
  Use this skill when you need to fetch Langfuse prompt templates for Codex CLI
  execution, record traces, or hook up agent evaluation scores via Langfuse SDK.
  Langfuse 프롬프트 fetch/실행/trace 기록, 또는 agent evaluation score 연동이 필요할 때 사용한다.
---

# Langfuse-Codex Prompt Manager

Langfuse 프롬프트 템플릿 ↔ Codex CLI 실행 연동 + agent evaluation score hookup.

## When to use

- Langfuse 프롬프트 템플릿을 가져와 Codex에 주입할 때
- Codex 실행 결과를 Langfuse trace로 기록할 때
- agent tool-use 평가 결과를 Langfuse score로 push할 때

## Scripts

> scripts/ 미구현. 아래는 목표 인터페이스이며, 구현 전까지 curl/Python SDK를 직접 사용한다.

상세 workflow와 명령 예시는 [entrypoint 상세 안내](references/langfuse-codex-prompt-entrypoint-details-at2026-03-24.md)를 따른다.

## Depends on

- **langfuse-agent-evaluation KB**: score taxonomy, dataset-run 평가 규칙, score push boundary 제공
- **agent-tool-benchmark**: metric formula 정의 (계산 함수)

## Knowledge Bases

- [knowledge_bases/langfuse-agent-evaluation-kb-at2026-03-24.md](knowledge_bases/langfuse-agent-evaluation-kb-at2026-03-24.md)

## References

- [references/langfuse-codex-prompt-entrypoint-details-at2026-03-24.md](references/langfuse-codex-prompt-entrypoint-details-at2026-03-24.md)
- [references/troubleshooting.md](references/troubleshooting.md)

## Not owned here

- metric formula 정의 자체 → `agent-tool-benchmark`
- codebase graph 구조 평가 → `codebase-analysis`
- Codex sandbox 제약 → `codex-subagent-setup`
