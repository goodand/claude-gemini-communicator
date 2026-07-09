# hybrid research Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-17`
- updated_at: `2026-03-17` (v0.1.0: initial local-pattern KB)
- canonical_role: `python-static-diagnostic-fixer를 위한 hybrid_kb`
- canonical_slice: `Canonical Design Takeaways 섹션은 정적 진단 처리의 source of truth`
- source_research_files: `codex-tmux-orchestrator/scripts/orchestrator.py`, `edge-case-generator/scripts/edgegen.py`
- format: `local example + fix pattern`
- generation_method: `반복적으로 발생한 Pylance/linter 수정 작업에서 패턴을 추출`
- total_urls: `0`
- paper_like_urls: `0`
- other_urls: `0`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · 사용 시점 |
| `python-static-diagnostic-fixer-knowledge_base-at2026-03-17-01-18.md` (이 파일) | 정적 진단 수정 패턴 KB |
| [troubleshooting.md](../references/troubleshooting.md) | 반복 버그와 수정 규칙 저장 |

## Table of Contents
- [Profile](#profile)
- [Canonical Design Takeaways](#canonical-design-takeaways)
- [Current Implementation Target](#current-implementation-target)
- [Pattern Taxonomy](#pattern-taxonomy)
- [Local Examples](#local-examples)

## Profile

- 이 문서는 local 반복 패턴에서 올린 `hybrid_kb`다.
- 넓은 외부 조사보다, 실제 repo에서 반복된 Pylance/linter 정리 순서를 source of truth로 삼는다.

## Canonical Design Takeaways

- 첫 단계는 항상 `런타임 오류`와 `정적 진단`을 분리하는 것이다.
- `py_compile`과 기존 테스트가 통과하면, 그 다음에만 Pylance/linter 수정을 적용한다.
- 정적 진단 수정은 기본적으로 동작 변경보다 `unused 제거`, `typing 보강`, `optional guard 추가`를 우선한다.
- `spec is None or spec.loader is None` 같은 optional guard는 동적 import 계열의 반복 패턴이다.
- `unused import`, `unused variable`은 먼저 제거하거나 `_`로 명시하는 쪽이 안전하다.
- `ModuleType`, `from __future__ import annotations` 같은 typing 보강은 에디터 진단을 줄이면서 런타임 영향이 적다.
- 정적 진단을 없애기 위해 로직을 크게 재구성하는 것은 v0.1 비목표다.
- 수정 후에는 다시 `py_compile`과 관련 테스트를 돌려 회귀를 막는다.

## Current Implementation Target

- v0.1은 문서형 skill로 시작한다.
- 첫 구현 대상은 `diagnostic taxonomy + safe-fix sequence`다.
- 이후 필요하면 `diagnostic_audit.py` 같은 보조 script로 내려갈 수 있다.

## Pattern Taxonomy

- `runtime_first_gate`
  - 에디터 경고가 보여도 먼저 런타임 정상 여부를 확인한다.
- `unused_cleanup`
  - unused import, unused variable, dead local을 가장 먼저 정리한다.
- `optional_loader_guard`
  - `spec.loader is None` 류의 optional guard를 추가한다.
- `typing_support`
  - `ModuleType`, return annotation, `from __future__ import annotations` 같은 typing 보강을 적용한다.
- `minimal_behavior_change`
  - 구조를 크게 바꾸지 않고 경고만 줄이는 방향을 우선한다.

## Local Examples

- `codex-tmux-orchestrator/scripts/orchestrator.py`
  - unused import, unused local variable 정리 패턴
- `edge-case-generator/scripts/edgegen.py`
  - `spec is None or spec.loader is None` guard 추가 패턴
- `codex-tmux-orchestrator/scripts/test_orchestrator.py`
  - `ModuleType`와 type annotation으로 Pylance 정리한 패턴
