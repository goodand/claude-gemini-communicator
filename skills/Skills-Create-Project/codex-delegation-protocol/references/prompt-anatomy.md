# Delegation Prompt Anatomy

Codex 위임 메시지는 **5-section 구조**를 따른다.

## 구조

```
## Mission
[1-3문장] 이 작업의 목적. packet.goal을 그대로 쓰되, Codex가 즉시 행동할 수 있도록 명령형.

## Scope
- allowed_paths: [수정 가능 경로 목록]
- forbidden_paths: [절대 수정 금지 경로]
- 이 범위 밖의 파일은 읽기만 가능

## Context
- [context_file_1 경로] — 역할 설명 (1줄)
- [context_file_2 경로] — 역할 설명 (1줄)
- 참고: [packet.handoff_notes 또는 추가 맥락]

## Constraints
- must_run_tests: [true/false]
- must_not_modify: [경로 목록]
- must_not_use_network: [true/false]
- [packet.constraints에서 추출한 추가 제약]

## Done Definition
1. [검증 가능한 완료 조건 1]
2. [검증 가능한 완료 조건 2]
3. ...
작업 완료 후 각 조건의 충족 여부를 보고할 것.
```

## 섹션별 규칙

### Mission
- packet.goal을 기반으로 하되 **명령형**으로 변환
- "~해주세요" → "~하라" 또는 "~을 구현한다"
- why를 1문장으로 추가하면 Codex가 의도를 이해함

### Scope
- allowed_paths는 **repo root 상대경로**
- 빠뜨린 경로가 있으면 Codex가 수정 못 함 → 검증 필수
- `..` 또는 절대경로 포함 금지

### Context
- **파일 내용을 프롬프트에 직접 삽입하지 않는다**
- Codex는 파일을 직접 읽을 수 있으므로 경로만 전달
- 각 파일이 왜 필요한지 1줄 설명 추가

### Constraints
- packet.constraints 필드를 그대로 매핑
- 추가 제약이 있으면 명시적으로 열거
- "상식적으로 알겠지" 가정 금지 — 모든 제약은 명시

### Done Definition
- packet.done_definition을 그대로 포함
- **기계 검증 가능해야 함**: "잘 작성" ✗, "pytest 통과" ✓, "파일 존재" ✓
- required_checks가 있으면 해당 커맨드도 포함

## 나쁜 예시 (Anti-patterns)

| 패턴 | 문제 | 개선 |
|------|------|------|
| "이 코드를 개선해줘" | goal이 모호 | "validate 함수에 why 최소 5자 검증을 추가한다" |
| 코드 500줄을 프롬프트에 직접 삽입 | 토큰 낭비 + 컨텍스트 오염 | context_files 경로만 전달 |
| done_definition 없음 | 완료 판정 불가 | "python3 script.py validate 종료코드 0" |
| "네트워크 사용하지 마" (구두) | 제약이 프롬프트에 안 들어감 | Constraints 섹션에 명시 |
| allowed_paths 누락 | Codex가 수정 범위를 모름 | Scope 섹션 필수 |

## 좋은 예시

```markdown
## Mission
skill-workflow-bridge-eval 스킬을 구현한다. classify/evaluate/decide/retry-spec/handoff/run/validate
7개 서브커맨드를 가진 통합 스크립트를 작성한다.

## Scope
- allowed_paths:
  - Skills-Create-Project/skill-workflow-bridge-eval/scripts/
  - Skills-Create-Project/skill-workflow-bridge-eval/evals/
  - Skills-Create-Project/skill-workflow-bridge-eval/references/troubleshooting.md
- forbidden_paths:
  - Skills-Create-Project/skill-workflow-bridge-eval/SKILL.md
  - Skills-Create-Project/skill-workflow-bridge-eval/checklist-forconsistency-evaluation/

## Context
- Skills-Create-Project/skill-workflow-bridge-eval/SKILL.md — 스킬 진입점, 워크플로우 개요
- Skills-Create-Project/skill-workflow-bridge-eval/references/Concept-2026-03-15-04-08.md — NL=claim 원칙, decision 규칙
- Skills-Create-Project/skill-workflow-bridge-eval/references/skill-workflow-bridge-eval-reference-2026-03-16-01.md — 상세 설계 (decision algebra, artifact 스키마)

## Constraints
- must_run_tests: true (python3 scripts/workflow_bridge.py --help 종료코드 0)
- must_not_modify: SKILL.md, checklist 디렉토리
- must_not_use_network: true

## Done Definition
1. scripts/workflow_bridge.py --help 정상 출력
2. classify --raw <NL파일> → output_type 반환
3. evaluate --raw <NL파일> → bridge_eval JSON 반환
4. run --raw <파일> --contract <계약> → 전체 파이프라인 실행
5. evals/evals.json에 4개 이상 eval 존재
```
