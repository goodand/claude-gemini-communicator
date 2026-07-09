# Skill Taxonomy — agent skill 분류 체계

이 PC의 agent skill에는 **이미 만들어진 분류 체계가 세 겹**으로 존재합니다. 이 문서는
그것들을 한자리에 정리하고, 발견(resolver)·검증 라우터가 그 위에 어떻게 얹히는지 보여줍니다.

## 층 1 — Family 택소노미 (owner → specialist)

각 skill의 `SKILL.md` description에 **owner-family / specialist / workflow-owner**
관계를 문장으로 박아 상하위 분류를 표현합니다. 관측된 family:

| family (owner) | 역할 | specialist 예 |
|---|---|---|
| `codebase-architecture-mapper` | Architecture analysis workflow owner | class-hierarchy-classifier, depsolve-analyzer, graph-structure-classifier |
| `cross-agent-bridge` | 멀티 에이전트 브릿지 owner | codex-user-context, gemini-cli-context (raw CLI executor) |
| `verification-decision-gate` | 검증 판정 owner | codebase-doc-alignment |
| `iOS Operation` | iOS 데모/런타임 owner | ios-demo-capture-loop (orchestration owner) |
| `destructive cleanup` / `vendored-mcp` | Canonical owner-family entrypoint | (scope classification 진입점) |

규칙: **"broader X는 owner를 써라 / 세부는 specialist를 써라"** — description에 명시하고
`super-skill-creator/references/triggering-and-routing.md` + `make_routing_doc.py`,
`--help-routing.md` 템플릿, `family-closure-audit-checklist`로 관리.

## 층 2 — Catalog (관계형 SSOT, 5 namespace)

`skills/Skills-Create-Project/skill-creation-process/references/catalog/` +
쿼리 엔진 `scripts/catalog_lookup.py` (`/control/patterns/`,
`/control/project_agent_ops/resources/skill_candidates/`에도 동일 엔진 배치).

`manifest.json`이 5개 namespace를 선언하고 각 항목은 typed key를 가집니다:

| namespace | 파일 | 항목 수 | 내용 |
|---|---|---|---|
| `SKILL-*` | skills.json | 16 | skill을 `role`로 분류 (아래) |
| `TASK-*` | tasks.json | 12 | 작업 단위 |
| `ISSUE-*` | issues.json | 12 | 문제/결정 |
| `LINK-*` | links.json | 27 | 항목 간 링크 |
| `JOIN-*` | joins.json | 12 | 관계 조인 — 전부 `issue_task_skill` (ISSUE→TASK→SKILL 삼자 결합) |

**SKILL role** (16종, 1:1 세분류): core_process · kb_to_checklist · contract_mapping ·
concept_lifting · evidence_audit · experiment_diff · kb_promotion · experiment_gate ·
artifact_management · subagent_packet · parallel_dispatch · parallel_runtime ·
parallel_coordination · doc_code_drift · codebase_partitioning · reference_validation.

즉 catalog는 **skill을 단독으로 두지 않고 issue·task와 join으로 묶은 관계형 분류**입니다.
조회: `python3 .../skill-creation-process/scripts/catalog_lookup.py`.

## 층 3 — 발견 + 검증 라우팅 (이 위에 얹힌 것)

- **발견**: `resolve_skill.py` — 여러 위치(정본 `repo/skills` #1 → external → ~/.claude →
  ~/.codex → ~/skills → /control → /agent → 프로젝트 root)를 우선순위로 스캔, 심링크
  dedup, `_stale` 제외, 이름충돌 진단. → **"어디에 있든 하나의 능력 집합"** ([SKILL_DISCOVERY.md](SKILL_DISCOVERY.md))
- **검증 라우팅**: `verification-router/router.py` — 코퍼스 1등 주제(검증)를 9개 패밀리
  (claim/evidence/consistency/decision-gate/merge-audit/semantic/runtime-truth/
  validation-run/skill-eval)로 묶어 의도→패밀리 라우팅. Hermes toolsets 패턴(재귀
  includes + 사이클 감지). 허브 = `claim-verifier`.

## 세 층의 관계

```
층1 Family        : 사람이 읽는 owner→specialist 문장 분류 (frontmatter)
층2 Catalog       : 기계가 읽는 관계형 SSOT (SKILL/TASK/ISSUE/LINK/JOIN + role)
층3 Resolver/Router: 흩어진 정본을 발견 + 의도별 검증 라우팅 (실행 진입점)
```

- **층1↔층2**: family는 description의 서술적 분류, catalog의 `role`은 그 기계 판독 버전.
  둘을 일치시키는 건 `family-closure-audit-checklist`의 역할.
- **층2↔층3**: catalog의 `SKILL-*` path와 resolver의 발견 결과는 같은 skill을 가리켜야
  함(정합성 점검 지점). router는 catalog role/ family를 검증 축으로 재그룹화한 것.

## 유지 규칙

1. 새 skill: owner-family를 description에 명시(층1) → catalog `SKILL-*`에 role 부여(층2)
   → 필요 시 router 패밀리에 추가(층3).
2. 정본은 `repo/skills`. catalog `path`와 resolver 우선순위가 이 정본을 가리키는지
   **`python3 skills/catalog_resolver_audit.py`** 로 점검 (층2↔층3 드리프트:
   PATH_MISSING / NOT_DISCOVERED / NOT_WINNER / NAME_MISMATCH, 드리프트 시 exit 1 —
   CI 게이트 가능). clone/worktree가 달라도 `skills/` 이후 상대 suffix로 판정하고
   macOS 한글 NFC/NFD를 정규화한다.
3. 이름충돌은 `resolve_skill.py conflicts`, family 누락은 family-closure-audit로 감지.
