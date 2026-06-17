# doc-code-sync-checker 구현용 체크리스트

> 위치: `knowledge_base` 아래, `codebase` 위
> 역할: KB의 설계 takeaways를 현재 구현 가능한 작업 항목으로 낮춘다.
> source of truth: `checklist-forconsistency-evaluation/consistency-checklist.md`

## A. Implemented Vertical Slices

- [ ] 첫 구현 대상 pair를 `agent-task-packet/references/packet-fields.md <-> agent-task-packet/scripts/packet_builder.py`로 고정한다
- [ ] 첫 rule kind `required_field`를 유지한다
- [ ] 두 번째 구현 대상 pair를 `codex-worktree-dispatch/references/dispatch-fields.md <-> codex-worktree-dispatch/scripts/dispatch_manager.py`로 고정한다
- [ ] 두 번째 rule kind `path_safety`를 유지한다
- [ ] 세 번째 구현 대상 pair를 `codex-worktree-dispatch/references/dispatch-fields.md <-> codex-worktree-dispatch/scripts/dispatch_manager.py`로 고정한다
- [ ] 세 번째 rule kind `transition_rule`를 유지한다
- [ ] 네 번째 구현 대상 pair를 `codex-worktree-dispatch/references/dispatch-fields.md <-> codex-worktree-dispatch/scripts/dispatch_manager.py`로 고정한다
- [ ] 네 번째 rule kind `enum_value`를 유지한다
- [ ] 현재까지의 비목표를 고정한다
  - 선택 필드 비교
  - value constraint 비교
  - enum 비교
  - 상태 전이표 비교
  - repo-wide crawl

## B. Scope 고정

- [ ] v0.1 범위를 `문서 1개 + 코드 1개` pairwise checker로 고정한다
- [ ] repo-wide scan, semantic diff engine, 자동 수정 기능은 제외한다
- [ ] 네트워크 비의존 로컬 CLI로 유지한다

## C. Rule Model 최소 스키마

- [ ] rule object 최소 필드를 정한다
  - `kind`
  - `name`
  - `source`
  - `value`
  - `evidence`
- [ ] 현재 구현 slice에서는 `required_field`, `path_safety`, `transition_rule`, `enum_value`를 다룬다
- [ ] `extract-doc`와 `extract-code`가 같은 rule shape를 반환하게 한다
- [ ] 첫 slice에서는 `mismatch`를 비워 두는지 명시한다

## D. extract-doc

- [ ] `packet-fields.md`의 `## 필수 필드` 표만 읽는다
- [ ] 표의 `필드` 열을 `required_field.name`으로 변환한다
- [ ] `설명` 열은 compare key가 아니라 evidence로 남긴다
- [ ] `dispatch-fields.md`의 `## locked_paths 규칙` bullet을 읽는다
- [ ] `path_safety.name` 규칙 집합으로 변환한다
- [ ] `dispatch-fields.md`의 `### 유효 전이 테이블`을 읽는다
- [ ] `transition_rule.name=from->to` 규칙 집합으로 변환한다
- [ ] `dispatch-fields.md`의 상태 전이표에서 unique status 값을 모은다
- [ ] `enum_value.name=status:<value>` 규칙 집합으로 변환한다
- [ ] 출력은 JSON rules artifact로 고정한다

## E. extract-code

- [ ] `packet_builder.py`의 `REQUIRED_FIELDS` set을 읽는다
- [ ] 각 항목을 `required_field.name`으로 변환한다
- [ ] `validate_packet()`의 missing-field 분기를 보조 evidence로 남긴다
- [ ] `dispatch_manager.py`의 `_normalize_path()`와 `validate_dispatch()`를 읽는다
- [ ] `path_safety.name` 규칙 집합으로 변환한다
- [ ] `dispatch_manager.py`의 `VALID_TRANSITIONS` dict를 읽는다
- [ ] `transition_rule.name=from->to` 규칙 집합으로 변환한다
- [ ] `dispatch_manager.py`의 `VALID_STATUSES` set을 읽는다
- [ ] `enum_value.name=status:<value>` 규칙 집합으로 변환한다
- [ ] 첫 slice에서는 AST보다 단순 구조 추출이 가능한 쪽을 우선한다
- [ ] 출력은 `extract-doc`와 같은 rule shape로 고정한다

## F. normalize

- [ ] 별도 CLI를 만들지 않고 compare 내부 단계로 둔다
- [ ] 문서 rule과 코드 rule을 공통 object로 바꾼다
- [ ] 현재 slice에서는 `<rule_kind>.name` 기준 exact match를 우선한다
- [ ] `transition_rule`에서는 `from->to` 관계만 first-class compare key로 둔다
- [ ] `enum_value`에서는 `field:value` 형태를 first-class compare key로 둔다

## G. compare

- [ ] 출력 필드 3개를 유지한다
  - `missing_in_code`
  - `missing_in_doc`
  - `mismatch`
- [ ] compare는 normalize 이후 결과만 사용한다
- [ ] 첫 slice에서는 `missing_in_code / missing_in_doc` 양방향 비교를 먼저 닫는다
- [ ] `mismatch`는 구조 충돌이 없으면 빈 리스트로 둔다

## H. report

- [ ] 사람이 읽을 수 있는 drift 요약을 만든다
- [ ] pair 정보, `missing_in_code`, `missing_in_doc`를 항상 포함한다
- [ ] 각 항목에 후속 액션 1줄을 붙인다
- [ ] smoke test용으로 과한 장문 보고는 피한다

## I. TDD

- [ ] `scripts/test_doc_code_sync.py`에 required_field, path_safety, transition_rule, enum_value vertical slice fixture를 추가한다
- [ ] `extract-doc` 단위 테스트를 만든다
- [ ] `extract-code` 단위 테스트를 만든다
- [ ] `compare/report` smoke 테스트를 만든다
- [ ] 최소 1개 negative fixture로 `missing_in_code` 또는 `missing_in_doc`를 재현한다

## J. Scaffold 명시

- [ ] 구현 전까지 `status: scaffold`를 유지한다
- [ ] 미구현 단계는 TODO 메시지로 숨기지 말고 명시한다
- [ ] `normalize`가 internal compare stage라는 점을 help/docstring에 유지한다

## K. Next Slice Candidate

- [ ] `mismatch`를 typed mismatch로 확장하는 다음 slice를 유지한다
- [ ] 첫 typed mismatch slice를 `enum_value_set_changed`로 고정한다
- [ ] 두 번째 typed mismatch slice를 `transition_rule_set_changed`로 고정한다
- [ ] 세 번째 typed mismatch slice를 `path_rule_condition_changed`로 고정한다
