# Integration Gate Report

- verdict: **PASS_WITH_WARNING**
- generated: 2026-07-11T13:01:45+09:00
- HEAD: `165cfd7`

| gate | status | summary |
|---|---|---|
| canonical_winner | PASS | core 5/5 winner=repo-skills-createproject |
| conflict | WARN | 55 conflicts, REPO_INTERNAL=0 |
| catalog_drift | PASS | OK 16/16, drift 0 |
| policy_sync | PASS | 4/4 checks |

## Conflict classes

| class | count | 판정 |
|---|---|---|
| CANONICAL_VS_PROJECT_COPY | 20 | WARN |
| EXTERNAL_VS_USER_GLOBAL | 13 | WARN |
| MIRROR_VS_ORIGIN_REPO | 22 | WARN |

충돌 수는 환경(보이는 발견 루트)에 따라 변하므로 개수가 아니라 클래스로 판정한다. FAIL은 `REPO_INTERNAL`(정본 루트 내 중복)뿐이다.

## Core skill winners

| skill | winner root | ok |
|---|---|---|
| claim-verifier | repo-skills-createproject | ✅ |
| skill-creation-process | repo-skills-createproject | ✅ |
| doc-code-sync-checker | repo-skills-createproject | ✅ |
| skill-workflow-bridge-eval | repo-skills-createproject | ✅ |
| agent-tool-benchmark | repo-skills-createproject | ✅ |
