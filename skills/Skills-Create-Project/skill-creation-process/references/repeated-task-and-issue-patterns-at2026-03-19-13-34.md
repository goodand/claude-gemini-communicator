# Repeated Task And Issue Patterns

- generated_at: `2026-03-19-13-34`
- scope: `skill creation / contract-slice experiments / portability / evidence loop`

## Purpose

최근 반복된 작업과 반복 이슈를 분리해, 공용 process에 둘 것과 개별 skill 내부 실험 루프에 둘 것을 구분한다.

task key 기준 lookup은 [task-to-skill-mapping-at2026-03-19-13-55.md](./task-to-skill-mapping-at2026-03-19-13-55.md)를 사용한다.
issue join 기준 lookup은 `references/catalog/joins.json` 또는 `python3 skill-creation-process/scripts/catalog_lookup.py show --key JOIN-ISSUE-*`를 사용한다.
subagent 전용 반복 패턴은 [subagent-task-and-trouble-patterns-at2026-03-20-02-48.md](./subagent-task-and-trouble-patterns-at2026-03-20-02-48.md)를 본다.

canonical append surface는 이 문서의 `Repeated Tasks` / `Repeated Issues` typed block이다.
`Issue To Task Mapping` 섹션은 2026-04-07 retired — action items와 artifacts는 각 Issue 항목에 통합됨. Legacy entries는 collapsible block 안에 보존.

본문 번호는 historical append-only로 유지한다. lookup과 cross-reference는 사람이 읽는 번호보다 `TASK-xx` stable key를 우선한다.
Issue-to-Task cross-reference는 [task-to-skill-mapping](./task-to-skill-mapping-at2026-03-19-13-55.md)이 canonical retrieval index다.

## Classification Taxonomy

새 항목을 올리기 전에 분류를 먼저 고정한다. 분류 없이 올리면 문서가 회고 노트화된다.

### Task/Issue Type (1축: 항목 성격)

| 분류 | 설명 | 갱신 빈도 | 예 |
|---|---|---|---|
| **protocol** | 감사/closure 절차 자체. substep 포함 가능 | Static — 절차 변경 시에만 | Task 19 |
| **loop** | 반복 실행되는 작업 cycle | Dynamic — 매 감사 갱신 | Task 17, 24 |
| **standalone-task** | 독립 판단이 필요한 1회성 패턴이 반복 | Dynamic | Task 20, 21 |
| **repair-step** | 1회성 수정이지만 재발 가능한 구조 문제 | Dynamic | Task 25, 26 |
| **issue** | recurrence + failure signature 충분 | Dynamic | Issue 21, 22, 25 |
| **watchlist** | evidence 1건, 두 번째 사례 시 승격 | Candidate | Issue 23, 24 |

### Document Importance (2축: 문서 중요도 — 별도 axis)

| 등급 | 설명 | compaction 후 복구 대상 |
|---|---|---|
| **Essential** | protocol, canonical taxonomy — 없으면 감사 불가 | Yes |
| **Important** | loop, standalone-task, issue — 작업 품질에 직접 영향 | 선택적 |
| **Reference** | repair-step, watchlist, mapping index — 보조 참조 | No |

task type과 importance를 같은 표에서 다루지 않는다. 2축은 독립이다.

### 새 항목 추가 순서

1. 기존 taxonomy에 들어가는 분류인지 확인
2. 안 들어가면 taxonomy 표부터 수정
3. 그 다음 task/issue 추가
4. cross-workspace mirror에 넣을 때는 provenance 3필드 필수
5. `canonical source / imported from / last synced` 중 하나라도 없으면 mirror note를 `incomplete provenance`로 본다

### Document Hierarchy (이 문서 생태계의 역할)

| 문서 | 역할 | canonical 여부 |
|---|---|---|
| `family-closure-audit-checklist` | canonical protocol | Yes — 감사 절차 자체 |
| `owner-task-bands` | canonical taxonomy | Yes — band/skill 분류 |
| `repeated-task-and-issue-patterns` (이 문서) | retrospective pattern log | Yes — 패턴 기록 |
| `task-to-skill-mapping` | retrieval index | Derived — 이 문서에서 파생 |
| my-image-parser KB | mirrored local note | Not canonical — provenance로 연결 |

## Repeated Tasks

**1. Reference acquisition mode 결정 — `standalone-task`**

- 기본값은 `external_research`
- 사용자가 명시하면 `internal_codebase_only`
- mode를 먼저 고정한 뒤에만 KB 작성 시작

**2. KB profile 분기 — `standalone-task`**

- `research_index_kb -> (hybrid_kb | canonical_design_kb)`
- checklist source of truth는 `Canonical Design Takeaways`가 있는 KB로 고정

**3. KB -> consistency checklist -> implementation checklist — `protocol`**

- KB에서 바로 코드로 가지 않는다
- 먼저 정합성 평가용 checklist를 만들고
- 그 다음 구현용 checklist와 TDD로 낮춘다

**4. Contract-first vertical slice 구현 — `protocol`**

- 전체 구현을 한 번에 하지 않는다
- `contract emit -> validate -> sample -> smoke` 순서로 작은 contract slice를 닫는다

**5. TDD -> implementation -> smoke -> evidence -> quick_validate — `loop`**

- 테스트를 먼저 만들고
- 구현 후 smoke artifact를 남기고
- evidence를 남기고
- `quick_validate`로 구조 정합성을 다시 확인한다

**6. `references/` artifact triad 남기기 — `standalone-task`**

- `contract`
- `valid`
- `invalid`
- 가능하면 JSON/MD 쌍으로 남긴다

**7. Capture artifact를 canonical bundle로 bridge — `standalone-task`**

- `quick_validate_capture -> experiment bundle`
- `smoke_command_capture -> experiment bundle`
- 사람이 상태를 다시 읽어 옮기지 않도록 bridge layer를 둔다

**8. Next-slice gate 판단 — `standalone-task`**

- 현재 slice가 닫혔는지 확인한다
- 다음 slice 후보는 공용 process가 아니라 대상 skill의 implementation checklist에서 받는다

**9. Evidence -> KB promotion — `loop`**

- `evidence -> summary -> trigger -> patch plan -> apply`
- 실험 결과를 바로 KB에 복붙하지 않는다

**10. Portability / install-readiness audit — `standalone-task`**

- `internal / bridge / external_dependency / absolute_path / missing`
- portable pack 기준으로 문서와 의존성을 분류한다

**11. SKILL.md line-count warning 대응 — `standalone-task`**

- line-count warning이 나오면 먼저 자연스러운 split point를 찾는다
- 별도 파일로 옮기고 entrypoint에는 링크만 남긴다

**12. Bounded subagent delegation — `standalone-task`**

- 남은 구현 조각이 작고 경계가 명확하면 `agent-task-packet` 방식으로 범위를 고정해 subagent에 맡긴다
- delete/move/rename/overwrite 가능성이 있으면 preservation-first clause를 packet에 같이 붙인다
- lifecycle 작업이 섞이면 `artifact-lifecycle-manager`로 먼저 넘긴다

**13. Semantic owner / execution specialist split — `protocol`**

- 새 representative skill이 생겨도 기존 execution skill의 runtime/script/output ownership은 유지한다
- owner skill은 `reinject / refine / compare / close / normalize / derive` 같은 semantic verb를 소유한다
- 기존 specialist는 `run / extract / export / build / render / operate / audit` 같은 execution verb만 남긴다

**14. YAML description verb alignment before body edits — `standalone-task`**

- routing은 body보다 frontmatter `description`을 먼저 읽는 경우가 많다
- body handoff를 넣기 전에 YAML description 동사를 먼저 좁힌다
- broad rewrite 대신 description line만 먼저 고치고, body는 최소 handoff note만 덧붙인다

**15. Cross-workspace canonical skill exposure — `standalone-task`**

- canonical owner skill을 다른 workspace에서 써야 하면 local copy를 만들지 않는다
- 먼저 relative symlink를 시도하고
- symlink가 곤란하면 thin local bridge skill로 canonical source path만 노출한다

**16. Routing mirror update after family addition — `standalone-task`**

- 새 owner family를 다른 workspace에 노출했으면 local routing mirror에도 family block을 같이 추가한다
- 다만 policy는 owner skill에 두고, mirror에는 `role / owner / delegate / recreate hint` 정도만 남긴다

### 17a. Owner task band classification before YAML rewrite — `protocol`

- top-level skill을 바로 고치기 전에 먼저 공통 Task band와 owner/specialist 경계를 고정한다
- 어떤 skill을 새 owner로 만들지보다 먼저, existing skill 중 누가 owner로 승격되고 누가 family specialist로 내려가는지 분류한다
- YAML description rewrite는 이 band 분류가 끝난 뒤에만 한다
- **numbering note**: 원래 ### 17 (duplicate). task-to-skill-mapping TASK-17 참조

### 17b. Iterative multi-round YAML description verb narrowing — `loop`

- 한 라운드에 description을 완벽히 좁히기 어렵다
- 피드백 → 수정 → 재피드백을 2~4회 반복하면서 잔여 broad verb를 잡는다
- 매 라운드는 description line만 수정하고, body는 건드리지 않는다
- owner taxonomy: `reinject / refine / compare / close / normalize / derive`
- specialist taxonomy: `run / extract / export / build / render / operate / audit`

**19. Family closure audit protocol (3-step) — `protocol`**

- 감사는 반드시 3단계 순서로 한다. 순서를 깨면 재감사한다.
  1. **existence audit**: glob으로 대상 SKILL.md 존재 확인. "목록에 없다 ≠ 파일이 없다"
  2. **YAML-only band classification**: Task > Action Item > Verb > Noun 순서로 판정. noun만으로 band 결정 금지
  3. **family closure checklist**: specialist YAML → owner YAML → owner Family Roles → canonical band reference (specialist 목록 + use owner when) → owner body guardrail (When to use / Do not use / Workflow) → specialist body specificity
- gold sample: Band 1 (verification-decision-gate + evidence-trace-auditor) — 2026-04-02 closure
- 다른 band에도 같은 checklist를 그대로 복사해 감사한다
- **substep 19a. body guardrail 3-section batch insertion** — YAML 완성 후 Family Roles + Do not use + Workflow를 같은 pass에서 추가. specialist가 없으면 Do not use는 cross-band routing (구 Task 20)
- **substep 19b. canonical band reference batch sync** — multi-band closure 후 band reference + audit checklist gold samples + 각 owner SKILL.md를 batch 동기화 (구 Task 23)

**18. Bidirectional ecosystem routing closure — `loop`**

- forward link만 넣으면 절반만 닫힌다
- forward: specialist의 `Not Owned Here` → owner skill 이름
- reverse: owner의 `Ecosystem` → specialist executor 이름
- 한 pass에 양방향을 같이 닫아야 family가 완전히 navigable해진다

**20. Specialist-less owner band adapted closure — `standalone-task`**

- specialist가 없는 owner (Band 6 artifact-lifecycle-manager 등)는 7-item checklist 중 item 1, 2, 7이 N/A
- Do not use는 specialist routing 대신 cross-band routing이 된다 (다른 band의 skill로 보내기)
- Family Roles에 `none (standalone owner)` 명시 필요
- 적용 가능 항목만으로 closure 판정

**21. Standalone skill band-membership triage — `standalone-task`**

- 모든 band closure 후 남은 skill을 Task > Action > Verb > Noun 순서로 전수 판별
- adjacency risk(같은 도구/noun, 다른 audience/task)를 문서화
- 실제 사례: tmux-controller ↔ codex-tmux-orchestrator (같은 tmux, 다른 audience)
- canonical band reference에 Standalone Skills 섹션 추가

**22. Cross-workspace mirror provenance tagging for process patterns — `standalone-task`**

- canonical process pattern을 다른 workspace KB에 다시 적어야 할 때 local mirror가 provenance를 함께 남겨야 drift를 줄일 수 있다
- local mirror는 domain-local relevance만 덧붙이고, process 자체의 source of truth는 canonical process repo에 둔다
- mirror note에는 최소 `canonical source path / imported from / last synced` 3가지를 남긴다
- 3필드 중 하나라도 빠지면 sync complete로 간주하지 않는다

#### Mirror Provenance Completeness Check

- [ ] `canonical source`
- [ ] `imported from`
- [ ] `last synced`
- 하나라도 비면 `incomplete provenance`

**23. Freeze state normalization with watch separation — `standalone-task`**

- closure 완료 후에도 상태를 하나로 뭉뚱그리지 않는다
- `Frozen (routing contract)`, `Frozen (adapted closure)`, `Verified standalone (watchlist)`처럼 closure class와 watch state를 분리한다
- watch target은 canonical checklist나 band reference의 risk/watch 섹션에 남기고, freeze 표기는 현재 closure class만 말하게 한다

**24. Closure patch 작성 시 인접 band vocabulary 침범 감지 — `loop`**

- closure gap을 메우기 위해 새로 body content를 쓸 때, 작성자가 습관적으로 인접 band의 어휘를 차용하는 패턴
- 기존 Issue 19(pre-existing broad language)와 다름: 이건 *새로 만든* content가 band를 넘는 경우
- Gemini 피드백으로 발견 → micro-patch로 좁히는 cycle
- 실제 사례: Band 4 Workflow step 4 "KB/checklist/export 정리"(Band 2 어휘) → "handoff-ready evidence package"로 수정
- 점검법: 새로 쓴 action phrase의 verb/noun이 다른 band의 owner verb taxonomy에 속하는지 확인

**25. 분류 없는 문서 성장 → 사후 taxonomy retrofit — `repair-step`**

- 반복 패턴 문서에 classification label 없이 항목을 계속 추가하면, 나중에 protocol/loop/issue/watchlist가 섞여서 사후 전수 라벨링이 필요
- 실제 사례: Task 19-23이 같은 표면에 올라가서 Gemini가 "분류 레벨 혼합" 비판
- 예방: 새 항목 추가 시 반드시 classification label을 먼저 고정 (→ Classification Taxonomy 섹션)
- 이 task 자체는 1회성 repair이지만, label 누락은 반복될 수 있으므로 기록

**26. Substep 과잉 승격 → 강등 cycle — `repair-step`**

- protocol의 substep을 처음에 top-level task로 올렸다가, 리뷰 후 다시 substep으로 강등하는 낭비 cycle
- 실제 사례: 구 Task 20(body guardrail → substep 19a), 구 Task 23(batch sync → substep 19b)
- 예방: 새 항목이 기존 protocol의 일부인지 먼저 판단. parent protocol이 있으면 substep으로 직접 추가
- 판단 기준: "이 task를 parent 없이 독립 실행할 수 있는가?" — 아니면 substep

**27. Mirror provenance 3-field completion — `repair-step`**

- cross-workspace mirror를 이미 만들었더라도 `canonical source`만 남기고 끝내면 sync debugging이 어렵다
- provenance는 최소 `canonical source / imported from / last synced` 3필드를 함께 남겨야 한다
- partial provenance가 발견되면 mirror note를 한 pass에서 3필드로 보강한다
- mirror는 local relevance를 덧붙이는 곳이고, canonical process 판단은 원본 repo에 남긴다

**28. Task type과 document importance 2축 분리 — `repair-step`**

- `protocol / loop / standalone-task / repair-step / issue / watchlist`는 항목 성격이고, `Essential / Important / Reference`는 문서 역할이다
- 두 축을 한 표면에서 섞어 읽기 시작하면 taxonomy가 다시 흔들린다
- 새 패턴을 append할 때는 먼저 task type을 고르고, 문서 레벨 importance는 별도 axis로만 기록한다
- 실제 사례: protocol/loop 분류는 들어갔지만 Essential anchor 문서의 역할이 따로 드러나지 않아 후속 retrofit이 필요했다

**29. Stable key first, append-only numbering discipline — `repair-step`**

- repeated pattern 문서는 사람이 읽는 번호보다 stable lookup key가 우선이다
- 번호를 뒤늦게 재배열하면 task/issue 본문, mapping, mirror note가 같이 churn 난다
- 기존 번호가 조금 어색해도 새 항목은 뒤에 append하고, lookup은 stable key와 classification으로 해결한다
- 번호 이상 징후는 새 renumber보다 watch/repair note로 남기는 편이 낫다

**30. Truth-source-first pipeline preflight — `standalone-task`**

- generated artifact workspace에서는 수정 전에 `current generator / latest output / asset roots / external constraints` 4개를 먼저 고정한다
- old generator, comparison output, temporary export folder가 같이 있으면 patch target 착오가 반복된다
- 실제 사례: 같은 workspace에 예전 `generate_ppt.py`, live `generate_v7_final.py`, 이전 deck output이 공존
- preflight 결과는 path note나 작업 메모 한 번으로 남겨 이후 patch scope를 고정한다

**31. Programmatic QA 통과 후 visual export readback — `loop`**

- overlap/margin/duplicate report가 통과해도 semantic redundancy, legibility, raw token leak는 남을 수 있다
- generated artifact를 slide image로 export한 뒤 변경한 슬라이드를 직접 읽고 `patch -> regenerate -> reread` loop를 돈다
- 실제 사례: S03-S06 중복 제거와 `nan` 노출 수정이 layout report 이후 visual readback에서 발견됨
- visual export surface는 최종 close-out 전에 evidence bundle로 보관한다

**32. Structured-data truth source와 screenshot evidence 분리 — `standalone-task`**

- CSV나 structured table가 있으면 native table/card를 truth source로 두고, screenshot은 architecture/log/workflow evidence에 한정한다
- 같은 수치나 표를 native table과 screenshot으로 동시에 두지 않는다
- 중복 사실은 `redundancy triage` 메모로 남기고, 반복 insight는 note/stat card로 환원한다
- 실제 사례: RAG 슬라이드에서 left table + right screenshot이 같은 metric을 반복

**33. Presentation-surface missing-value normalization — `repair-step`**

- renderer가 CSV의 `nan`, empty cell, placeholder token을 그대로 노출하면 결과물이 빠르게 저급해진다
- display contract에서 missing value를 `—` 같은 발표용 토큰으로 normalize한다
- renderer 수정 후 visual export readback까지 한 pass에서 닫는다
- local repair처럼 보여도 table renderer를 공유하면 쉽게 재발하므로 기록

**34. Visual patch 뒤 fail-fast layout rerun — `loop`**

- 이미지 폭/높이, card 위치, panel 분할을 건드리면 인접 asset lane에서 새 overlap이 바로 열린다
- visual patch 1회마다 `generator rerun -> fail-fast layout QA -> touched slide export`까지 같이 돈다
- single pass success를 안정화로 오해하지 않고, changed slide만이라도 다시 readback한다
- 실제 사례: S04, S06에서 한 차례 patch 후 새 overlap이 다시 열림

**35. Workspace roots / reference / live generator 먼저 고정 — `standalone-task`**

- 계획 전에 `project root -> image root -> table root -> external reference -> current generator`를 그 순서로 먼저 확인한다
- 환경 확인을 뒤로 미루면 계획부터 작성했다가 실행 단계에서 다시 truth source를 찾느라 재작성 cycle이 열린다
- external evidence: `agent/skills/pptx/references/gotchas.md`의 pre-flight check 누락 패턴
- 실제 사례: 같은 workspace에서 old generator, live generator, latest output가 공존해 현재 patch target을 먼저 고정해야 했다

**36. File-system manifest scan -> resolver binding -> spec 대조 — `standalone-task`**

- 자산 단계에서는 `find` 또는 `os.walk()`로 파일시스템을 먼저 스캔하고, 실제 존재 파일명을 resolver에 묶은 뒤 spec과 대조한다
- 수동 파일명 목록이나 추측 기반 basename은 truth source가 아니라 참고 메모로만 본다
- external evidence: `agent/skills/pptx/references/gotchas.md`의 asset guessing, manual data drift, NFC/NFD 관련 패턴
- 실제 사례: `AssetResolver`의 NFC 정규화 매핑이 없으면 한글 파일명과 매뉴얼 목록 drift가 바로 재발

**37. Generator rerun 전 interpreter lineage 확인 — `loop`**

- 생성기 실행 전 `requested interpreter / sys.executable / self-reexec rule`의 계보를 먼저 확인한다
- system python을 강제하는 스크립트는 alias interpreter를 같은 계열로 인정할지 먼저 정하고 rerun한다
- 환경 계열 mismatch를 코드 로직 버그로 오인하지 않고 preflight 변형으로 분류한다
- 실제 사례: `/usr/bin/python3`를 강제했지만 실제 실행 lineage가 Xcode Python으로 잡혀 allowlist 안정화가 필요했다

## Repeated Issues

**1. Source of truth가 둘 이상으로 갈라짐 — `issue`**

- thin KB와 canonical KB를 둘 다 읽게 만들면 agent가 기준을 헷갈린다
- 해결:
  - canonical source를 하나로 고정
  - thin note는 redirect/appendix로 강등
- artifacts: KB role 정리 note, updated `SKILL.md`
**2. SKILL.md entrypoint 과적재 — `issue`**

- phase, notes, bridge, portability를 전부 entrypoint에 몰아넣으면 line-count warning이 난다
- 해결:
  - split page를 만들고 링크로 분리
- artifacts: split detail page, updated `SKILL.md`
**3. Absolute path / sibling 의존성 누적 — `issue`**

- `/Users/...` 절대경로와 외부 sibling 참조가 쌓이면 다른 workspace로 이식이 깨진다
- 해결:
  - internal 우선
  - bridge 문서로 연결
  - optional fixture bundle 분리
- artifacts: portability audit artifact, install-readiness dependency map, optional fixture manifest
**4. Artifact path만 기록하고 실제 존재를 확인하지 않음 — `issue`**

- path만 적으면 evaluator가 허상 artifact를 통과시킬 수 있다
- 해결:
  - evaluator와 bridge에서 실제 파일 존재를 같이 검사
- artifacts: invalid smoke JSON/MD, troubleshooting note
**5. `quick_validate` 결과를 사람이 해석해서 전달 — `issue`**

- stdout/stderr를 사람이 읽고 다음 판단에 옮기면 반복 오차가 생긴다
- 해결:
  - `quick_validate_capture` artifact로 먼저 정규화
- artifacts: capture smoke JSON/MD, bridge smoke JSON/MD, updated implementation checklist
**6. Smoke 결과의 exit code와 stdout status가 어긋남 — `issue`**

- exit code만 보면 `invalid` smoke 케이스를 잘못 판정할 수 있다
- 해결:
  - `capture-smoke-command`에서 exit code와 parsed stdout status를 함께 본다
- artifacts: valid smoke capture JSON/MD, invalid smoke capture JSON/MD, troubleshooting note
**7. Warning과 failure를 같은 수준으로 다룸 — `issue`**

- warning이 있어도 바로 invalid로 떨어뜨리면 다음 slice 판단이 너무 거칠어진다
- 해결:
  - `strict_warning_policy_gate`로 `pass / hold / invalid`를 분리
- artifacts: pass smoke JSON/MD, hold smoke JSON/MD, invalid smoke JSON/MD, vertical-slice gate note
**8. 다음 slice 후보를 공용 process에서 추론하려고 함 — `issue`**

- 공용 process는 방법론만 가져야 하고, 도메인별 다음 조각은 다르다
- 해결:
  - next-slice 후보는 각 skill의 implementation checklist에서 받는다
- artifacts: updated implementation checklist, 필요한 경우 next-slice decision note
**9. 용어 충돌 — `issue`**

- `slice`가 planner output slice인지, skill implementation slice인지 혼동되기 쉽다
- 해결:
  - 문서에서 `implementation slice`, `planner output slice`, `contract slice`를 구분해 쓴다
- artifacts: updated KB / notes, troubleshooting case or clarification note
**10. smoke/evidence는 남겼는데 vertical-slice note가 없음 — `issue`**

- artifact만 있으면 왜 이 조각을 만들었는지 맥락이 사라진다
- 해결:
  - `references/vertical-slice-*.md`를 같이 남긴다
- artifacts: `references/vertical-slice-*.md`
**11. Capture artifact는 생겼는데 evaluator 입력과 바로 연결되지 않음 — `issue`**

- capture artifact는 만들었는데 evaluator가 바로 읽을 수 있는 형태로 연결되지 않으면 수동 해석이 끼어든다
- 관련 Task: 7 (Capture bridge), 8 (Next-slice gate)
- 해결:
  - `quick_validate_capture -> bundle` bridge 추가
  - `smoke_command_capture -> bundle` bridge 추가
  - normalized bundle을 evaluator로 다시 돌려 확인
- artifacts: bridge smoke JSON/MD, normalized bundle JSON, follow-up evaluation smoke JSON/MD

**12. 남은 구현 조각이 작고 분리 가능한데 메인 agent가 전부 직접 처리함 — `issue`**

- 작고 경계가 명확한 조각을 분리하지 않으면 메인 agent의 context가 비대해지고, 병렬 처리 기회를 놓친다
- 관련 Task: 12 (Bounded subagent delegation)
- 해결:
  - `agent-task-packet` 방식으로 bounded packet 작성
  - subagent에게 disjoint ownership 할당
  - 메인 agent는 integration / verification만 담당
- artifacts: subagent handoff packet, integration verification evidence

**13. Body handoff는 넣었는데 YAML trigger가 여전히 넓음 — `issue`**

- `Not Owned Here`나 `Do Not Use`에 owner link를 넣어도 frontmatter description이 넓으면 pre-routing 단계에서 다시 잘못 고른다
- 해결:
  - body patch보다 먼저 YAML description 동사를 owner-first taxonomy로 좁힌다
- artifacts: updated `SKILL.md` descriptions, minimal diff note
**14. Semantic owner는 생겼는데 local workspace에서 바로 발견되지 않음 — `issue`**

- canonical owner skill이 다른 workspace에만 있으면 local skill list와 routing mirror에는 안 잡힌다
- 해결:
  - relative symlink 또는 thin bridge로 local skill tree에 노출
  - local routing mirror에 family block을 같이 추가
- artifacts: symlink 또는 bridge 경로 목록, updated local routing mirror
**15. Absolute symlink나 local copy가 portability / drift risk를 만든다 — `issue`**

- absolute symlink는 repo 위치가 바뀌면 깨지고, local copy는 semantic rule drift를 만든다
- 해결:
  - relative symlink 우선
  - recreate command나 fallback bridge 규칙을 같이 남긴다
- artifacts: recreate command, simple verification note
**16. Output normalization skill과 builder skill이 `review surface` 동사에서 겹친다 — `issue`**

- builder가 `review surface를 만든다`와 semantic split까지 같이 말하면 normalization owner와 trigger가 겹친다
- 해결:
  - owner는 `normalize / split / derive`
  - builder는 `build / render`
  - workspace consumer는 `operate`로 분리
- artifacts: narrowed description lines, 필요한 경우 ecosystem note
**17. Producer family와 semantic owner family 사이 bridge가 암묵적이다 — `issue`**

- capture/extract/run skill이 만든 artifact를 누가 semantic interpretation 하는지 local workspace에서 바로 보이지 않을 수 있다
- 해결:
  - owner ecosystem에 executor를 역방향으로 연결
  - 필요하면 local producer owner 한 곳에 1줄 bridge note를 남긴다
- artifacts: updated ecosystem note, 필요한 경우 local bridge note
### 18a. Owner skill을 만들기 전에 existing owner 승격 후보를 먼저 보지 않음 — `issue`

- **numbering note**: 원래 ### 18 (duplicate). task-to-skill-mapping TASK-18 범위
- broad task band가 보여도 기존 skill이 이미 owner 역할을 할 수 있는데 곧바로 새 owner부터 만들면 family가 과도하게 늘어난다
- 해결:
  - top-level skill을 Task band별로 먼저 분류
  - existing owner 승격 후보와 genuine specialist를 먼저 가른 뒤
  - 비어 있는 band에만 새 owner를 만든다
- artifacts: owner band reference, updated YAML descriptions

### 18b. Handoff 위치가 파일마다 달라서 drift가 생김 — `issue`

- **numbering note**: 원래 ### 18 (duplicate). task-to-skill-mapping TASK-18 범위
- 같은 family 안에서 어떤 skill은 `Do Not Use`에, 어떤 skill은 `Not Owned Here`에 handoff를 넣으면 다음 패치부터 정렬이 흔들린다
- 해결:
  - owner handoff는 `Not Owned Here` 끝 2줄로 통일
  - `Do Not Use`에는 trigger routing만 두고 owner link는 넣지 않는다
- artifacts: 통일 전/후 diff note, 위치 규칙 1줄 요약

**19. YAML description은 좁혔는데 body가 아직 pre-split broad language를 유지 — `issue`**

- YAML은 `Export deterministic component evidence`로 좁혔는데 body Overview가 `review surface`를 계속 쓰면, 다음 수정자가 body를 보고 description을 다시 넓힐 수 있다
- 해결:
  - YAML 먼저, body는 다음 라운드에서 최소 수정
  - 급한 drift risk가 아니면 body 수정을 강제하지 않는다
- artifacts: body broad language 잔여 목록 (파일:줄번호), 다음 라운드 수정 후보 메모
**20. Noun 유사성으로 band를 잘못 판정함 — `issue`**

- 같은 noun(tool, artifact 등)을 다루는 skill이라도 task가 다르면 다른 band에 속한다
- noun만으로 band를 판정하면 오분류가 생긴다
- 관련 Task: 19 (Family closure audit protocol — existence audit 단계)
- 해결:
  - Task > Action Item > Verb > Noun 순서를 강제
  - noun이 겹쳐도 task가 다르면 다른 band
  - existence audit를 YAML audit보다 먼저 실행
- artifacts: stale 판정 목록과 실제 존재 확인 결과

**21. YAML 완성 후 body guardrail section 누락 — `issue`**

- YAML description은 routing까지 잘 좁혔는데 body에 Do not use / Family Roles / Workflow가 없어서 closure checklist item 3, 6이 fail
- Band 4, 6, 8 전부 같은 gap. YAML-first 편집 프로토콜의 구조적 부작용
- 해결:
  - YAML 완성 직후 body guardrail 3-section을 같은 pass에서 추가 (→ Task 19 substep 19a)
  - closure checklist를 YAML 편집 시점부터 함께 돌린다
- artifacts: 추가된 3-section diff, closure checklist 재검증 결과
**22. Read order와 Workflow 혼동 — `issue`**

- codebase-analysis, artifact-lifecycle-manager 둘 다 "Read order"만 있고 "Workflow"가 없었다
- Read order는 knowledge loading order (어떤 순서로 읽는가), Workflow는 action sequence (무엇을 하는가)
- Read order가 있어도 Workflow guardrail은 별도로 필요
- 해결:
  - Workflow를 추가하되 Read order는 그대로 유지
  - 두 섹션의 목적을 혼동하지 않는다
- artifacts: 분리된 Workflow + Read order
**23. Specialist-less owner의 Do not use에 cross-band routing 부재 — `watchlist`**

- specialist가 없는 owner는 Do not use가 비어 있으면 인접 task의 implicit catch-all이 된다
- Band 6 artifact-lifecycle-manager: Notes에 handoff 언급은 있었지만 Do not use에는 없었음
- evidence: Band 6 1건만. 두 번째 independent specialist-less owner 사례가 나오면 `issue`로 승격
- 해결:
  - specialist가 없으면 Do not use에 cross-band skill routing을 넣는다
  - Notes의 handoff 언급과 Do not use의 routing이 일관되게 유지
- artifacts: Do not use 추가 diff, Notes ↔ Do not use 정합성 확인
**24. Closure patch에서 새로 쓴 content가 인접 band 어휘를 차용 — `watchlist`**

- 기존 Issue 19(pre-existing broad language)와 구분: 19는 이미 있던 body가 넓은 것, 이건 closure gap을 메우려고 *새로 쓴* content가 인접 band의 verb/noun을 가져오는 것
- evidence: Band 4 1건만. 두 번째 independent 사례가 나오면 `issue`로 승격
- Band 4 Workflow step 4에서 "KB/checklist/export 정리"를 썼는데, KB/checklist는 Band 2(artifact production) 어휘
- 해결:
  - 새로 쓴 action phrase의 verb/noun을 대상 band의 owner verb taxonomy와 대조
  - 인접 band verb가 섞이면 해당 band의 handoff 표현으로 교체 (예: "KB 정리" → "handoff-ready evidence package")
- artifacts: canonical source 경로, mirror provenance note
**25. Closure rubric class를 분리하지 않아 결과표가 오독됨 — `issue`**

- specialist가 있는 family와 specialist-less standalone owner에 같은 "7/7 PASS" rubric을 적용하면, future audit에서 같은 수준의 closure로 오해
- Band 6 artifact-lifecycle-manager를 다른 band와 동급으로 표기해서 Gemini가 "방법론상 과장" 비판
- 해결:
  - family closure(specialist 있음)와 standalone owner adapted closure를 결과표에서 명시적으로 분리
  - `Frozen (routing contract)` vs `Frozen (standalone owner adapted closure)` 표기
  - N/A 항목 수를 명시 (예: "5/5 적용 항목 PASS, item 1/2/7 N/A")
- artifacts: normalized status label, watch target note
**26. 분류 label 없이 반복 패턴 추가 — `issue`**

- classification label 없이 항목을 append하면 사후 전수 라벨링이 필요해진다
- 관련 Task: 25 (분류 없는 문서 성장 → taxonomy retrofit)
- 해결:
  - Classification Taxonomy 섹션 참조하여 label 먼저 결정
  - substep이면 parent protocol 아래에 들여쓰기
- artifacts: classification label이 부착된 항목

**27. watchlist ↔ issue 승격 기준이 항목마다 흔들림 — `issue`**

- evidence 1건이면 watchlist, 2건 이상이면 issue인데, 새 항목을 올릴 때 기존 기준과 비교하지 않아 같은 evidence 수준에서 다른 분류가 붙는다
- 관련 Task: 19 (Family closure audit protocol), 23 (Freeze state normalization)
- 해결:
  - evidence 1건이면 `watchlist`, independent 사례 2건 이상이면 `issue`로 고정
  - 새 항목을 올리기 전에 기존 승격 기준과 비교한다
  - 승격/강등 이유를 항목 본문에 한 줄로 남긴다
- artifacts: 승격 조건 또는 강등 사유 메모

**29. Stable key보다 사람용 번호를 먼저 손봐 numbering churn이 생김 — `issue`**

- 사람이 읽는 번호를 재배열하면 task/issue 본문, mapping, mirror note가 같이 churn 난다
- 관련 Task: 29 (Stable key first, append-only numbering discipline)
- 해결:
  - lookup은 `TASK-xx` stable key와 classification으로 먼저 해결
  - 번호가 어색해도 기존 항목 renumber는 피하고 append-only를 유지
  - duplicate/out-of-order 번호는 repair note로 기록
- artifacts: stable key lookup note, numbering drift watch 메모

**30. 이전 generator/output를 current truth source로 잘못 잡음 — `issue`**

- generated artifact workspace 안에 old script, current script, 이전 output, compare export가 같이 있으면 수정 대상이 쉽게 어긋난다
- 관련 Task: 30 (Truth-source-first pipeline preflight)
- 해결:
  - live generator, latest output, asset roots, external constraint reference를 먼저 고정
  - preflight note에 현재 truth source를 한 줄로 남긴다
- artifacts: truth-source note, current output pointer, preflight path list

**31. Programmatic QA pass를 visual readiness로 오독 — `issue`**

- overlap 0, margin pass, duplicate 0만으로는 semantic duplication, unreadable density, raw token leak를 막지 못한다
- 관련 Task: 31 (Programmatic QA 통과 후 visual export readback), 34 (Visual patch 뒤 fail-fast layout rerun)
- 해결:
  - generated artifact를 export해서 사람이 읽는 surface로 다시 본다
  - close-out 전에 changed slide visual readback evidence를 남긴다
- artifacts: slide image export dir, review note, after-patch comparison evidence

**32. Native table와 screenshot이 같은 증거를 다시 말함 — `issue`**

- left native table과 right screenshot이 같은 metric/분류/비교를 다시 보여주면 정보 밀도는 낮아지고 patch surface만 커진다
- 관련 Task: 32 (Structured-data truth source와 screenshot evidence 분리)
- 해결:
  - structured data는 native table/card에만 남긴다
  - screenshot은 architecture, execution log, workflow evidence로 제한한다
  - 반복 insight는 note/stat card로 축소한다
- artifacts: redundancy triage note, regenerated slide image set, patched slide spec note

**33. Visual patch가 인접 lane의 새 overlap을 재개 — `issue`**

- 한 슬라이드의 이미지 폭이나 위치를 고치면 card lane, bottom band, adjacent panel에서 새 충돌이 열릴 수 있다
- 관련 Task: 34 (Visual patch 뒤 fail-fast layout rerun)
- 해결:
  - touched slide마다 rerun된 layout report를 다시 확인한다
  - overlap을 막을 때는 image/card lane을 분리하고 max height clamp를 다시 조정한다
- artifacts: failed layout report excerpt, corrected rerun report, touched slide export evidence

**34. Table renderer가 raw missing token을 presentation surface로 흘림 — `issue`**

- CSV의 `nan`이나 empty token이 deck에 그대로 보이면 data artifact가 발표 surface를 오염시킨다
- 관련 Task: 33 (Presentation-surface missing-value normalization)
- 해결:
  - render 직전 missing token을 display-safe token으로 normalize한다
  - visual export에서 실제 표면 표시를 다시 확인한다
- artifacts: renderer diff, before/after slide evidence

**35. 계획부터 쓰고 workspace truth surfaces 확인을 뒤로 미룸 — `issue`**

- project root, asset roots, external reference, live generator를 먼저 고정하지 않으면 설계가 현재 workspace 상태와 어긋난다
- 관련 Task: 35 (Workspace roots / reference / live generator 먼저 고정)
- 해결:
  - planning보다 먼저 workspace root matrix를 적는다
  - current generator와 latest output pointer를 같은 메모에 고정한다
- artifacts: workspace root matrix, truth-source pointer note

**36. 파일명 추측/하드코딩이 resolver truth source를 덮어씀 — `issue`**

- 자산을 실제로 스캔하지 않고 문서나 기억에 있는 basename을 코드에 적으면 `FileNotFoundError`, warning 다발, 수동 수정 loop가 다시 열린다
- NFC/NFD 차이와 문서-코드 drift가 겹치면 증상이 더 커진다
- 관련 Task: 36 (File-system manifest scan -> resolver binding -> spec 대조)
- 해결:
  - asset manifest를 먼저 생성한다
  - `AssetResolver` 같은 정규화 매핑을 truth source로 사용한다
  - 수동 목록은 spec reconciliation note로만 남긴다
- artifacts: asset manifest, resolver evidence, spec reconciliation note

**37. Interpreter alias drift가 generator self-reexec를 다시 흔듦 — `issue`**

- `/usr/bin/python3`와 Xcode Python처럼 같은 계열 interpreter가 다르게 보이면 rerun 단계에서 환경 이슈가 코드 버그처럼 보일 수 있다
- 관련 Task: 37 (Generator rerun 전 interpreter lineage 확인)
- 해결:
  - active interpreter lineage를 로그에 남긴다
  - self-reexec allowlist를 명시하고 alias 계열을 같은 class로 처리한다
  - generator rerun 전에 preflight 출력으로 실제 interpreter를 다시 확인한다
- artifacts: interpreter lineage note, allowlist diff, rerun log excerpt

## Issue To Task Mapping (Retired 2026-04-07)

이 섹션의 action procedures와 artifact lists는 각 Repeated Issue 항목의 `해결:` / `artifacts:` 블록으로 통합됨.
Skill routing lookup은 [task-to-skill-mapping](./task-to-skill-mapping-at2026-03-19-13-55.md)을 사용한다.

<details>
<summary>Legacy Mapping Entries (archived — 새 항목을 여기에 추가하지 말 것)</summary>

**1. Source of truth가 둘 이상으로 갈라짐**

- Repeated Task:
  - `2. KB profile 분기`
- 우선 수행할 Task:
  - canonical source를 1개로 고정
  - 나머지 KB는 redirect note / appendix로 강등
  - `SKILL.md`와 load order를 canonical source 기준으로 수정
- Related Skills:
  - `skill-creation-process`
  - `kb-checklist-pipeline`
- 같이 남길 것:
  - KB role 정리 note
  - updated `SKILL.md`

**2. SKILL.md entrypoint 과적재**

- Repeated Task:
  - `11. SKILL.md line-count warning 대응`
- 우선 수행할 Task:
  - `quick_validate` line-count warning 확인
  - 자연스러운 split point 탐색
  - 상세 페이지 생성
  - `SKILL.md`에는 링크만 남김
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - split detail page
  - updated `SKILL.md`

**3. Absolute path / sibling 의존성 누적**

- Repeated Task:
  - `10. Portability / install-readiness audit`
- 우선 수행할 Task:
  - portability audit 실행
  - `internal / bridge / external_dependency / absolute_path / missing` 분류
  - bridge 문서 추가 또는 optional fixture bundle 분리
- Related Skills:
  - `skill-creation-process`
  - `artifact-lifecycle-manager`
- 같이 남길 것:
  - portability audit artifact
  - install-readiness dependency map
  - optional fixture manifest

**4. Artifact path만 기록하고 실제 존재를 확인하지 않음**

- Repeated Task:
  - `4. Contract-first vertical slice 구현`
  - `6. references/ artifact triad 남기기`
- 우선 수행할 Task:
  - evaluator 또는 bridge에서 `Path.is_file()` 확인 추가
  - invalid sample 추가
  - smoke에서 missing file 케이스 확인
- Related Skills:
  - `slice-experiment-lab`
  - `evidence-trace-auditor`
- 같이 남길 것:
  - invalid smoke JSON/MD
  - troubleshooting note

**5. `quick_validate` 결과를 사람이 해석해서 전달**

- Repeated Task:
  - `5. TDD -> implementation -> smoke -> evidence -> quick_validate`
  - `7. Capture artifact를 canonical bundle로 bridge`
- 우선 수행할 Task:
  - `quick_validate_capture_adapter` 구현
  - `stdout/stderr/exit_code -> passed|failed + warnings/errors` 정규화
  - bridge layer에서 capture artifact를 canonical bundle로 연결
- Related Skills:
  - `slice-experiment-lab`
  - `skill-creation-process`
- 같이 남길 것:
  - capture smoke JSON/MD
  - bridge smoke JSON/MD
  - updated implementation checklist

**6. Smoke 결과의 exit code와 stdout status가 어긋남**

- Repeated Task:
  - `5. TDD -> implementation -> smoke -> evidence -> quick_validate`
  - `7. Capture artifact를 canonical bundle로 bridge`
- 우선 수행할 Task:
  - `smoke_command_capture_adapter` 구현
  - exit code와 parsed stdout status를 같이 읽도록 규칙 고정
  - valid/invalid 양쪽 sample로 smoke 확인
- Related Skills:
  - `slice-experiment-lab`
  - `evidence-trace-auditor`
- 같이 남길 것:
  - valid smoke capture JSON/MD
  - invalid smoke capture JSON/MD
  - troubleshooting note

**7. Warning과 failure를 같은 수준으로 다룸**

- Repeated Task:
  - `5. TDD -> implementation -> smoke -> evidence -> quick_validate`
  - `8. Next-slice gate 판단`
- 우선 수행할 Task:
  - `strict_warning_policy_gate` 구현
  - `pass / hold / invalid` 3단계 정책 고정
  - pass/hold/invalid sample 각각 실행
- Related Skills:
  - `slice-experiment-lab`
- 같이 남길 것:
  - pass smoke JSON/MD
  - hold smoke JSON/MD
  - invalid smoke JSON/MD
  - vertical-slice gate note

**8. 다음 slice 후보를 공용 process에서 추론하려고 함**

- Repeated Task:
  - `8. Next-slice gate 판단`
- 우선 수행할 Task:
  - next-slice 후보를 대상 skill implementation checklist에 기록
  - evaluator는 그 후보를 읽기만 하게 유지
  - 공용 process 문서에서는 방법론만 유지
- Related Skills:
  - `slice-experiment-lab`
  - `skill-creation-process`
- 같이 남길 것:
  - updated implementation checklist
  - 필요한 경우 next-slice decision note

**9. 용어 충돌**

- Repeated Task:
  - `3. KB -> consistency checklist -> implementation checklist`
  - `4. Contract-first vertical slice 구현`
- 우선 수행할 Task:
  - 문서에서 `implementation slice`, `contract slice`, `planner output slice`를 구분
  - `SKILL.md`와 KB Notes의 용어를 맞춤
- Related Skills:
  - `skill-creation-process`
  - `dependency-slice-planner`
- 같이 남길 것:
  - updated KB / notes
  - troubleshooting case or clarification note

**10. smoke/evidence는 남겼는데 vertical-slice note가 없음**

- Repeated Task:
  - `5. TDD -> implementation -> smoke -> evidence -> quick_validate`
  - `6. references/ artifact triad 남기기`
- 우선 수행할 Task:
  - 목적/입력/출력/결과/다음 후보를 적은 `vertical-slice-*.md` 작성
  - 관련 smoke artifact를 note에 링크
- Related Skills:
  - `skill-creation-process`
  - `slice-experiment-lab`
- 같이 남길 것:
  - `references/vertical-slice-*.md`

**11. Capture artifact는 생겼는데 evaluator 입력과 바로 연결되지 않음**

- Repeated Task:
  - `7. Capture artifact를 canonical bundle로 bridge`
  - `8. Next-slice gate 판단`
- 우선 수행할 Task:
  - `quick_validate_capture -> bundle` bridge 추가
  - `smoke_command_capture -> bundle` bridge 추가
  - normalized bundle을 evaluator로 다시 돌려 확인
- Related Skills:
  - `slice-experiment-lab`
- 같이 남길 것:
  - bridge smoke JSON/MD
  - normalized bundle JSON
  - follow-up evaluation smoke JSON/MD

**12. 남은 구현 조각이 작고 분리 가능한데 메인 agent가 전부 직접 처리함**

- Repeated Task:
  - `12. Bounded subagent delegation`
- 우선 수행할 Task:
  - `agent-task-packet` 방식으로 bounded packet 작성
  - subagent에게 disjoint ownership 할당
  - 메인 agent는 integration / verification만 담당
- Related Skills:
  - `agent-task-packet`
  - `codex-worktree-dispatch`
  - `codex-tmux-orchestrator`
- 같이 남길 것:
  - subagent handoff packet 또는 equivalent prompt
  - integration verification evidence

**13. Body handoff는 넣었는데 YAML trigger가 여전히 넓음**

- Repeated Task:
  - `13. Semantic owner / execution specialist split`
  - `14. YAML description verb alignment before body edits`
- 우선 수행할 Task:
  - frontmatter `description`만 먼저 수정
  - owner verb와 specialist verb를 분리
  - body는 handoff note만 최소 수정
- Related Skills:
  - `skill-creation-process`
  - `multimodal-evidence-refinement-loop`
  - `image-text-cot-review`
- 같이 남길 것:
  - updated `SKILL.md` descriptions
  - minimal diff note

**14. Semantic owner는 생겼는데 local workspace에서 바로 발견되지 않음**

- Repeated Task:
  - `15. Cross-workspace canonical skill exposure`
  - `16. Routing mirror update after family addition`
- 우선 수행할 Task:
  - relative symlink 또는 thin bridge 생성
  - local routing mirror에 family block 추가
  - local copy는 만들지 않음
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - symlink 또는 bridge 경로 목록
  - updated local routing mirror

**15. Absolute symlink나 local copy가 portability / drift risk를 만든다**

- Repeated Task:
  - `15. Cross-workspace canonical skill exposure`
- 우선 수행할 Task:
  - absolute symlink를 relative symlink로 교체
  - recreate command 또는 fallback bridge rule 추가
  - canonical source of truth를 하나로 유지
- Related Skills:
  - `skill-creation-process`
  - `artifact-lifecycle-manager`
- 같이 남길 것:
  - recreate command
  - simple verification note

**16. Output normalization skill과 builder skill이 `review surface` 동사에서 겹친다**

- Repeated Task:
  - `13. Semantic owner / execution specialist split`
  - `14. YAML description verb alignment before body edits`
- 우선 수행할 Task:
  - owner는 `normalize / split / derive`만 남김
  - builder는 `build / render`, workspace consumer는 `operate`로 축소
  - `review surface` 문구가 semantic ownership처럼 읽히지 않게 정리
- Related Skills:
  - `image-text-cot-review`
- 같이 남길 것:
  - narrowed description lines
  - 필요한 경우 ecosystem note

**17. Producer family와 semantic owner family 사이 bridge가 암묵적이다**

- Repeated Task:
  - `13. Semantic owner / execution specialist split`
  - `16. Routing mirror update after family addition`
- 우선 수행할 Task:
  - owner ecosystem에 executor를 역방향으로 연결
  - local producer owner에 optional bridge note 1줄 추가 여부 판단
  - routing mirror만 읽는 세션과 skill body만 읽는 세션 둘 다 고려
- Related Skills:
  - `multimodal-evidence-refinement-loop`
  - `image-text-cot-review`
- 같이 남길 것:
  - updated ecosystem note
  - 필요한 경우 local bridge note

**18. Owner skill을 만들기 전에 existing owner 승격 후보를 먼저 보지 않음**

- Repeated Task:
  - `17. Owner task band classification before YAML rewrite`
- 우선 수행할 Task:
  - top-level skill을 공통 Task band 기준으로 분류
  - existing owner 승격 후보와 specialist를 먼저 구분
  - 비어 있는 band에만 새 owner를 추가
- Related Skills:
  - `workspace-artifact-production-process`
- 같이 남길 것:
  - owner band reference
  - updated YAML descriptions

**18. Handoff 위치가 파일마다 달라서 drift가 생김**

- Repeated Task:
  - `13. Semantic owner / execution specialist split`
  - `14. YAML description verb alignment before body edits`
- 우선 수행할 Task:
  - 같은 family의 specialist skill 전체를 한 pass에서 handoff 위치 통일
  - `Not Owned Here` 끝 2줄로 고정
  - `Do Not Use`에서 owner link를 제거하고 trigger routing만 남김
- Related Skills:
  - `skill-creation-process`
  - `multimodal-evidence-refinement-loop`
  - `image-text-cot-review`
- 같이 남길 것:
  - 통일 전/후 diff note
  - 위치 규칙 1줄 요약

**19. YAML description은 좁혔는데 body가 아직 broad language를 유지**

- Repeated Task:
  - `17. Iterative multi-round YAML description verb narrowing`
- 우선 수행할 Task:
  - YAML 먼저 닫고 body는 다음 라운드로 미룬다
  - body 수정 시에는 Overview와 Workflow의 broad noun만 최소 교체
  - 큰 rewrite는 하지 않는다
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - body broad language 잔여 목록 (파일:줄번호)
  - 다음 라운드 수정 후보 메모

**20. Noun 유사성으로 band를 잘못 판정함**

- Repeated Task:
  - `19. Family closure audit protocol (3-step)`
- 우선 수행할 Task:
  - Task > Action Item > Verb > Noun 순서를 강제
  - noun이 겹쳐도 task가 다르면 다른 band
  - existence audit를 YAML audit보다 먼저 실행
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - stale 판정 목록과 실제 존재 확인 결과

**21. YAML 완성 후 body guardrail section 누락**

- Repeated Task:
  - `19. Family closure audit protocol` — substep 19a
- 우선 수행할 Task:
  - YAML 편집 완료 직후 closure checklist item 3, 6을 미리 확인
  - Family Roles + Do not use + Workflow를 같은 pass에서 추가
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - 추가된 3-section diff
  - closure checklist 재검증 결과

**22. Read order와 Workflow 혼동**

- Repeated Task:
  - `19. Family closure audit protocol` — substep 19a
- 우선 수행할 Task:
  - Read order 존재 여부와 무관하게 Workflow 섹션 유무를 따로 확인
  - Workflow(action sequence)와 Read order(knowledge loading order)를 별도 유지
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - 분리된 Workflow + Read order

**23. Specialist-less owner의 cross-band routing 부재 (watchlist)**

- Repeated Task:
  - `20. Specialist-less owner band adapted closure`
- 우선 수행할 Task:
  - Do not use에 cross-band routing을 넣어 implicit catch-all 방지
  - Notes의 기존 handoff 언급과 Do not use routing을 정렬
- 승격 조건: 두 번째 independent specialist-less owner 사례 발생 시 `issue`로 승격
- Related Skills:
  - `artifact-lifecycle-manager`
- 같이 남길 것:
  - Do not use 추가 diff
  - Notes ↔ Do not use 정합성 확인

**24. Canonical process pattern을 mirror KB에 복제하면서 provenance를 남기지 않음**

- Repeated Task:
  - `22. Cross-workspace mirror provenance tagging for process patterns`
- 우선 수행할 Task:
  - local mirror에 canonical source path를 남긴다
  - imported from / last synced를 같이 기록한다
  - canonical 문서와 local mirror의 역할을 분리한다
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - canonical source 경로
  - mirror provenance note

**25. `Frozen` 표기가 watch 상태를 가려서 영구 불변처럼 읽힘**

- Repeated Task:
  - `23. Freeze state normalization with watch separation`
- 우선 수행할 Task:
  - freeze class와 watch state를 별도 표기로 나눈다
  - watch가 있는 skill은 canonical checklist 또는 band reference에 risk target으로 남긴다
  - 결과표에는 `Frozen (routing contract)` / `Frozen (adapted closure)` / `Verified standalone (watchlist)`처럼 closure class를 명시한다
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - normalized status label
  - watch target note

**24. Closure patch에서 인접 band 어휘 차용 (watchlist)**

- Repeated Task:
  - `24. Closure patch 작성 시 인접 band vocabulary 침범 감지`
- 승격 조건: 두 번째 independent band에서 같은 어휘 침범 사례 발생 시 `issue`로 승격
- 우선 수행할 Task:
  - 새로 쓴 Workflow/Do not use의 verb/noun을 대상 band owner verb taxonomy와 대조
  - 인접 band verb가 보이면 해당 band의 handoff 표현으로 교체
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - 수정 전/후 action phrase diff

**25. Closure rubric class 미분리**

- Repeated Task:
  - `23. Freeze state normalization with watch separation`
  - `20. Specialist-less owner band adapted closure`
- 우선 수행할 Task:
  - 결과표에 closure class를 명시적으로 분리
  - N/A 항목 수 포함
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - normalized 결과표

**26. 분류 label 없이 반복 패턴 추가**

- Repeated Task:
  - `25. 분류 없는 문서 성장 → 사후 taxonomy retrofit`
- 우선 수행할 Task:
  - Classification Taxonomy 섹션 참조하여 label 먼저 결정
  - substep이면 parent protocol 아래에 들여쓰기
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - classification label이 부착된 항목

**27. watchlist ↔ issue 승격 기준이 항목마다 흔들림**

- Repeated Task:
  - `19. Family closure audit protocol (3-step)`
  - `23. Freeze state normalization with watch separation`
- 우선 수행할 Task:
  - evidence 1건이면 `watchlist`, independent 사례 2건 이상이면 `issue`로 고정
  - 새 항목을 올리기 전에 기존 승격 기준과 비교한다
  - 승격/강등 이유를 항목 본문에 한 줄로 남긴다
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - 승격 조건 또는 강등 사유 메모

**28. Canonical provenance를 일부만 적고 mirror sync 정보를 빼먹음**

- Repeated Task:
  - `22. Cross-workspace mirror provenance tagging for process patterns`
  - `27. Mirror provenance 3-field completion`
- 우선 수행할 Task:
  - `canonical source`만 있으면 partial provenance로 본다
  - `imported from / last synced`를 같은 pass에서 채운다
  - local mirror의 domain note와 canonical process note를 섞지 않는다
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - provenance 3필드가 모두 보이는 mirror note

**29. Stable key보다 사람용 번호를 먼저 손봐 numbering churn이 생김**

- Repeated Task:
  - `29. Stable key first, append-only numbering discipline`
- 우선 수행할 Task:
  - lookup은 `TASK-xx` stable key와 classification으로 먼저 해결
  - 번호가 어색해도 기존 항목 renumber는 피하고 append-only를 유지
  - duplicate/out-of-order 번호는 repair note로 기록하고, 별도 대수술 없이는 건드리지 않는다
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - stable key lookup note
  - numbering drift watch 메모

**30. Task type 축과 document importance 축을 한 표면에서 섞어 읽음**

- Repeated Task:
  - `28. Task type과 document importance 2축 분리`
- 우선 수행할 Task:
  - 항목 분류는 task type 표에서만 결정
  - `Essential / Important / Reference`는 문서 역할 표에서만 판단
  - task type과 importance를 한 문장에 같이 쓰지 않는다
- Related Skills:
  - `skill-creation-process`
- 같이 남길 것:
  - 2축 taxonomy note

</details>

## Placement Rule

- 공용 process에 둘 것:
  - mode branch
  - KB profile branch
  - checklist/TDD/evidence/quick_validate 흐름
  - portability audit
  - line-count warning 대응
- 개별 skill 내부에 둘 것:
  - 다음 slice 후보
  - domain-specific contract order
  - 실험용 sample pair나 fixture 선택

## Current High-Value Reusable Loops

각 loop의 classification을 명시한다. protocol은 Static(절차 변경 시에만), loop는 Dynamic(매 감사 갱신).

- `execution contract -> smoke -> evidence -> audit -> diff` — `loop`
- `evidence -> summary -> trigger -> KB patch` — `loop`
- `contract / valid / invalid triad -> quick_validate capture -> bridge -> next-slice gate` — `loop`
- `semantic owner split -> YAML verb narrowing -> minimal body handoff -> cross-workspace exposure` — `loop`
- `owner task band classification -> existing owner promotion -> YAML routing rewrite -> new owner only for empty bands` — `loop`
- `YAML verb taxonomy enforcement -> multi-round review narrowing -> bidirectional ecosystem closure -> handoff placement unification` — `loop`
- `existence audit -> YAML band classification (Task>Action>Verb>Noun) -> family closure checklist (7-item) -> body guardrail backfill -> freeze` — `protocol` (Task 19 통합)
- `all-band closure -> standalone triage (Task>Action>Verb>Noun) -> adjacency risk documentation -> canonical reference batch sync` — `protocol` (Task 19b + Task 21)
- `canonical process pattern append -> task mapping sync -> optional mirror provenance note` — `loop`
- `closure complete -> freeze class labeling -> watch registration -> later re-triage` — `loop`
- `new pattern candidate -> taxonomy fit check -> classification assign -> append -> mapping sync` — `loop`
- `mirror sync -> canonical source + imported from + last synced -> local role note -> later sync audit` — `loop`

## Related References

- [phase-guide.md](./phase-guide.md)
- [execution-evidence-pattern-at2026-03-17-04-03.md](./execution-evidence-pattern-at2026-03-17-04-03.md)
- [evidence-promotion-pattern-at2026-03-17-03-45.md](./evidence-promotion-pattern-at2026-03-17-03-45.md)
- [portable-skill-hierarchy-rules-at2026-03-17-09-22.md](./portable-skill-hierarchy-rules-at2026-03-17-09-22.md)
