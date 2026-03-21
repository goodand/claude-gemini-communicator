# Skill Usage Details

- recorded_at: `2026-03-21-23-25`
- purpose: `entrypoint를 얇게 유지하고, 상세 사용 지침과 보조 링크를 분리하기 위한 detail page`

## Details

- canonical graph artifact contract: [canonical-graph-artifact-contract-at2026-03-20-21-04.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/canonical-graph-artifact-contract-at2026-03-20-21-04.md)
- normalized graph schema sample: [normalized-graph-json-sample-schema-at2026-03-20-21-51.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/normalized-graph-json-sample-schema-at2026-03-20-21-51.md)
- export implementation checklist: [export-checklist-at2026-03-20-21-51.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forimplementation/export-checklist-at2026-03-20-21-51.md)
- graph sample fixture: [README.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/fixtures/graph-sample-at2026-03-20-22-45/README.md)
- decision queue rule: [decision-queue-rule-at2026-03-21-19-20.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/decision-queue/decision-queue-rule-at2026-03-21-19-20.md)
- decision template: [decision-template-at2026-03-21-19-20.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/decision-queue/decision-template-at2026-03-21-19-20.md)
- graphviz view: [codebase-analysis-3layer-kb-at2026-03-20-17-32.svg](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/graphviz/codebase-analysis-3layer-kb-at2026-03-20-17-32.svg)

## Built-in agent packages

- `agents/reviewer/AGENT.md`
- `agents/context-broker/AGENT.md`
- `agents/dependency-graph-analyst/AGENT.md`
- `agents/dependency-risk-auditor/AGENT.md`
- `agents/synthesizer/AGENT.md`

## Execution entrypoints

- quick coarse survey: `scripts/analyze_codebase.py <repo_root>`
- canonical graph export example is tracked in the smoke/reference layer, not in the entrypoint itself

## Notes

- 현재 skill은 코드베이스 분석과 orchestration prework를 함께 다룬다.
- 각 subagent는 `AGENT.md + knowledge_bases/ + references/ + bridges/ + scripts/` 구조를 가진다.
- `AGENT.md`는 entrypoint로 유지하고, 길어지는 역할/순서/입출력/handoff/context 설명은 `package_details` 링크로 분리한다.
- tool/permission 정보는 `AGENT.md` 본문에 뭉개지지 않고 `references/tool-capability-policy-*.md`에 분리한다.
- 상위 agent용 setup context와 하위 agent용 code/context 링크는 분리한다.
- 하위 agent에는 필요한 파일 링크만 주고 점진적으로 context를 주입한다.
- flow는 시간표가 아니라 artifact gate 기반 절차로 관리한다.
- 그래프 표현 전략은 canonical graph artifact(`normalized_graph.json + nodes.jsonl + edges.jsonl`)를 source of truth로 두고, Graphviz/Neo4j/Cytoscape/Gephi는 export 또는 view layer로 취급한다.
- agent는 `persistent structural`, `run-scoped interpretive`, `artifact-backed synthesizer` 클래스로 구분한다.
- lint/static warning은 subagent discipline enforcement로 사용하고, 가능하면 subagent 실행 구간에만 켠다.
- dependency 작업은 `dependency-slice-planner`를 포함한 planning tool들과 연결되지만, 이 skill은 codebase analysis 전반을 다룬다.
- 상세 예외와 실패 패턴은 `(→ references/troubleshooting.md)`에 기록한다.
