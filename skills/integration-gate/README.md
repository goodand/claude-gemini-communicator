# Integration Gate — feat→main 통합 판정기

skill catalog 브랜치를 `main`에 통합하기 전에 통과해야 하는 4-subflow gate.
독립 runner이며 `agent-tool-benchmark`에 속하지 않는다(그쪽은 메트릭 정의용,
평가 skill은 이 결과를 소비만 한다).

## 실행

```bash
# repo 루트에서
python3 skills/integration-gate/run_integration_gate.py          # 사람용 md 요약
python3 skills/integration-gate/run_integration_gate.py --json   # 기계용
# 종료코드: PASS·PASS_WITH_WARNING=0, FAIL=1 → CI 게이트로 사용 가능
```

리포트는 `reports/integration_gate_report.{json,md}`에 기록된다.

## 4 Subflow

| # | gate | 검사 | FAIL 조건 |
|---|---|---|---|
| 1 | canonical_winner | 핵심 5 skill(claim-verifier 생태계)의 발견 승자 | 하나라도 `repo-skills-createproject`가 아님 |
| 2 | conflict | 이름 충돌을 클래스로 분류 | `REPO_INTERNAL`(정본 루트 내 중복) 존재 |
| 3 | catalog_drift | 층2 catalog ↔ 층3 resolver 정합 (`catalog_resolver_audit`) | drift ≥ 1 |
| 4 | policy_sync | 문서 선언(발견 우선순위·`_stale` 제외) = 코드 동작 | 불일치 ≥ 1 |

## Conflict 분류 규칙 (환경 독립성)

충돌 **개수**는 환경에 따라 변한다 — Desktop 프로젝트 루트가 macOS TCC에
막힌 세션에서는 7건, 보이는 세션에서는 약 55건이 실측됐다(2026-07-09).
추가분은 전부 미러↔원소유repo, 정본↔프로젝트사본 클래스였다. 따라서 gate는
개수가 아니라 **충돌에 참여한 root 클래스**로 판정한다:

- `REPO_INTERNAL` — **FAIL**. 정본 루트 두 곳에 같은 이름 → 정본이 모호해짐.
- `EXTERNAL_MIRROR_DUP` / `EXTERNAL_VS_USER_GLOBAL` / `MIRROR_VS_ORIGIN_REPO`
  / `CANONICAL_VS_PROJECT_COPY` / `OTHER_NON_CANONICAL` — **WARN**.
  미러는 출처와 이름이 겹치는 게 설계상 정상이고("external은 미러, 출처가
  정본" — SKILL_DISCOVERY.md §2), 사본은 resolver 우선순위가 정본을 이기므로
  실행 정합성을 깨지 않는다.
