# Dependency Slice Planner Algorithm Knowledge Base
- ver: `v0.1.2`
- created_at: `2026-03-18-23-02`
- updated_at: `2026-03-18-23-43` (v0.1.2: graph partitioning family, `tree-sitter`/`grimp` parser candidates, canonical input/output contract, refinement heuristic 보강)
- kb_profile: `synthesis_kb`
- reference_acquisition_mode: `external_research`
- source_scope: `web papers + official parser/extractor repos + local dependency analysis context`
- purpose: `dependency-slice-planner 알고리즘, parser/extractor 채택 경계, canonical planner I/O를 고정`

## Document Map

| 문서 | 역할 |
|------|------|
| [AGENT.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/dependency-slice-planner/AGENT.md) | role entrypoint |
| `dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md` | canonical synthesis KB |
| [context-links-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/dependency-slice-planner/references/context-links-at2026-03-18-22-47.md) | progressive context injection용 링크 집합 |
| [tool-capability-policy-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/dependency-slice-planner/references/tool-capability-policy-at2026-03-18-22-47.md) | 허용/금지 capability |
| [dependency-slice-planner-handoff-contract-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/dependency-slice-planner/bridges/dependency-slice-planner-handoff-contract-at2026-03-18-22-47.md) | slice planner 입출력 계약 |
| [ANALYZE_DEPENDENCY_GRAPH_CONTRACT_2026-03-18-21-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/depsolve-analyzer/references/ANALYZE_DEPENDENCY_GRAPH_CONTRACT_2026-03-18-21-22.md) | upstream graph contract |
| [MECE_SUBAGENT_FANIN_FOR_DEPGRAPH_2026-03-18-21-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/depsolve-analyzer/references/MECE_SUBAGENT_FANIN_FOR_DEPGRAPH_2026-03-18-21-22.md) | planner가 fan-out 이전 단계임을 정의 |
| [dependency-slice-planner-knowledge_base-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/dependency-slice-planner/knowledge_bases/dependency-slice-planner-knowledge_base-at2026-03-18-22-47.md) | optional overview appendix |

## Table of Contents
- [Problem Framing](#problem-framing)
- [Role Boundary](#role-boundary)
- [Research Families](#research-families)
- [Parser And Extractor Candidates](#parser-and-extractor-candidates)
- [Adapter Matrix](#adapter-matrix)
- [Fork Boundary](#fork-boundary)
- [Canonical Input Signals](#canonical-input-signals)
- [Recommended Planner Algorithm](#recommended-planner-algorithm)
- [Canonical Output Contract](#canonical-output-contract)
- [Downstream Handoff Model](#downstream-handoff-model)
- [Canonical Design Takeaways](#canonical-design-takeaways)
- [Sources](#sources)

## Problem Framing

`dependency-slice-planner`는 단순 디렉토리 분할기가 아니다.
목표는 아래 둘을 동시에 만족하는 slice를 만드는 것이다.

1. 사람이 병렬로 분석하거나 작업해도 충돌이 적다.
2. 그래프 관점에서 잘못 자른 경계 때문에 핵심 의존성이 끊기지 않는다.

즉 이 역할은 `tree-based partitioning`과 `dependency-aware refinement`를 결합한 planner에 가깝다.

## Role Boundary

이 KB 기준 역할 경계는 아래처럼 잡는다.

- `depsolve-analyzer`
  - graph extraction main skill
  - source graph / manifest graph / wrapper-path graph를 분리해서 추출
- `dependency-slice-planner`
  - coarse partition + refinement + stop rule + handoff artifact 생성
- downstream worker subagents
  - planner가 만든 slice manifest와 handoff packet을 소비

핵심:
- planner는 graph extractor가 아니다
- planner는 fan-out orchestrator 자체도 아니다
- planner는 `slice decision + handoff artifact producer`다

## Research Families

### 1. Program Slicing
핵심 아이디어:
- 실행점/변수 기준으로 필요한 부분만 남긴다.
- 작은 단위로 내려갈수록 정밀하지만, 코드베이스 병렬 분할의 직접 해답은 아니다.

Planner에 주는 의미:
- 무엇이 무엇에 영향을 주는가를 기준으로 slice boundary를 생각하게 만든다.
- coarse directory split 이후 fine-grained refinement 원리로 참고한다.

대표 source:
- [Weiser, Program Slicing (1984)](https://dblp.org/rec/journals/tse/Weiser84)
- [Horwitz, Reps, Binkley, Interprocedural Slicing Using Dependence Graphs (1990)](https://doi.org/10.1145/77606.77608)

### 2. Software Clustering / Architecture Recovery
핵심 아이디어:
- dependency graph를 subsystem cluster로 묶어 architecture를 복원한다.
- 네가 고민한 분할 후 refinement에 가장 직접적이다.

Planner에 주는 의미:
- 디렉토리 단위가 아니라 graph 응집도/결합도로 slice 경계를 조정해야 한다.
- cluster quality와 cross-edge density를 같이 봐야 한다.

대표 source:
- [Bunch: a clustering tool for the recovery and maintenance of software system structures (1999)](https://doi.org/10.1109/ICSM.1999.792498)
- [Information-Theoretic Software Clustering / LIMBO (2005)](https://www.cs.toronto.edu/~periklis/pubs/tse05.pdf)
- [The Weighted Combined Algorithm: a linkage algorithm for software clustering (2004)](https://doi.org/10.1109/CSMR.2004.1281402)

### 3. Graph Partitioning / Multilevel Refinement
핵심 아이디어:
- 초기 분할을 만든 뒤 coarsen -> partition -> uncoarsen/refine 과정을 거쳐 cut을 줄이고 균형을 맞춘다.
- partition quality를 빠르게 개선하는 데 강하다.

Planner에 주는 의미:
- directory seed를 그대로 확정하지 말고 refinement 단계에서 cut을 줄이는 휴리스틱을 적용해야 한다.
- 완전한 METIS 복제를 할 필요는 없지만, `high cut edge 감소`, `shared hub 회피`, `균형 유지` 원리는 직접 차용할 가치가 있다.

대표 source:
- [KarypisLab/METIS](https://github.com/KarypisLab/METIS)
- [Karypis and Kumar, Multilevel k-way Hypergraph Partitioning (1998)](https://hdl.handle.net/11299/215392)
- [Karypis, Kumar, Schloegel, Parallel Multilevel Algorithms for Multi-Constraint Graph Partitioning (1999)](https://hdl.handle.net/11299/215387)

### 4. Directory-Based Recovery
핵심 아이디어:
- 디렉토리 구조 자체를 architectural signal로 활용한다.
- 네가 제안한 tree CLI 기반 1차 분할과 가장 가깝다.

Planner에 주는 의미:
- tree/size/depth는 버릴 게 아니라 coarse seed 생성에 좋다.
- 다만 이것만으로 최종 분할을 결정하면 wrapper/path/import crossing을 놓친다.

대표 source:
- [Directory-Based Dependency Processing for Software Architecture Recovery (2018)](https://doi.org/10.1109/ACCESS.2018.2870118)

### 5. Static + Dynamic Fusion
핵심 아이디어:
- static graph만으로는 실제 활성 경로를 모르고,
- dynamic trace만으로는 실행하지 않은 경로를 모른다.
- 둘을 겹쳐 boundary를 찾는다.

Planner에 주는 의미:
- slice planner는 static-only로 시작하되, runtime overlay를 보강 신호로 써야 한다.
- 실행되지 않은 경로는 `unobserved_path_register`로 관리하고 probe를 요청한다.

대표 source:
- [Microservice Decomposition via Static and Dynamic Analysis of the Monolith (2020)](https://eprints.soton.ac.uk/488757/)
- [Determining Microservice Boundaries: A Case Study Using Static and Dynamic Software Analysis / MonoBreaker (2020)](https://arxiv.org/abs/2007.05948)
- [From Monolith to Microservices: Static and Dynamic Analysis Comparison (2022)](https://www.emergentmind.com/articles/2204.11844)

### 6. Reflexion / Drift Modeling
핵심 아이디어:
- high-level intended structure와 실제 source structure의 차이를 본다.
- graph와 checklist를 연결하는 역할을 한다.

Planner에 주는 의미:
- slice boundary는 단순 import edge가 아니라 intended ownership과 drift도 함께 봐야 한다.
- 병렬 분할 전에 boundary policy와 예외를 명시한 checklist가 필요하다.

대표 source:
- [Software Reflexion Models: Bridging the Gap Between Source and High-Level Models (1995)](https://www.cs.ubc.ca/~murphy/papers/rm/fse95.html)
- [Extending and Managing Software Reflexion Models (1997)](https://www.cs.ubc.ca/tr/1997/tr-97-15)

### 7. Service Decomposition / Coupling Criteria
핵심 아이디어:
- 단순 dependency 외에도 coupling criteria를 weighted graph로 합친다.

Planner에 주는 의미:
- size만이 아니라 coupling score, shared hub count, blast radius를 같이 봐야 한다.
- 향후에는 ownership, change history, runtime affinity도 포함할 수 있다.

대표 source:
- [Service Cutter: A Systematic Approach to Service Decomposition](https://inria.hal.science/hal-01638590)

## Parser And Extractor Candidates

외부 로직을 들여올 때는 planner 전체를 가져오기보다 parser/extractor 계층을 가져오는 편이 맞다.

### Syntax / language-agnostic base
- [tree-sitter](https://github.com/tree-sitter/tree-sitter)
  - language-neutral incremental parser system
  - 장점: multi-language repo에서 syntax tree 기반 inventory와 import-site candidate 추출에 유리
  - 한계: dependency graph를 바로 주지 않으므로 language-specific query와 normalization이 필요

### Python side
- [pydeps](https://github.com/thebjorn/pydeps)
  - Python import graph 추출에 적합
  - 장점: 빠른 import graph 시각화와 dependency edge 확보
  - 한계: wrapper, `sys.path`, `runpy`, manifest drift는 직접 보강 필요
- [import-linter](https://github.com/seddonym/import-linter)
  - Python import graph 위에 architecture contract를 얹는 데 적합
  - 장점: boundary rule / layering contract 자동화에 좋음
  - 한계: slice planning 자체를 해주진 않음
- [grimp](https://github.com/seddonym/grimp)
  - queryable Python internal import graph builder
  - 장점: planner 쪽에서 Python import graph를 직접 소비하기 좋다
  - 한계: 프로젝트 설치 상태와 import resolution에 영향을 받는다

### JS/TS side
- [dependency-cruiser](https://github.com/sverweij/dependency-cruiser)
  - JS/TS graph extraction + architecture rule engine
  - 장점: dependency graph와 규칙 검증을 함께 제공
  - 한계: mixed repo planner 전체는 아님
- [madge](https://github.com/pahen/madge)
  - cycle/orphan/graph smoke용 lightweight extractor
  - 장점: 빠른 검사
  - 한계: 심화 planner logic은 없음

### Mixed or decomposition-oriented references
- [MonoBreaker](https://arxiv.org/abs/2007.05948)
  - static + dynamic evidence로 service boundary를 다룸
  - 장점: runtime overlay 사고에 직접적
  - 한계: 바로 clone해서 slice planner로 쓰긴 무거움
- [Service Cutter](https://inria.hal.science/hal-01638590)
  - weighted criteria decomposition 사고를 제공
  - 장점: coupling criteria 사고에 유용
  - 한계: 코드베이스 slice planner보다는 서비스 분해에 더 가깝다

### What still needs custom collection
외부 parser만으로는 아래를 놓치기 쉽다.
- `runpy.run_path` wrapper chain
- `sys.path.insert/append` path mutation
- root inference/bootstrap logic
- mixed manifest crossing
- test boundary piercing via local path tricks

즉 parser는 외부에서 가져와도, wrapper/path mutation collector는 로컬 보강이 필요하다.

## Adapter Matrix

| Layer | Candidate | Use | Keep external? | Keep internal? |
|------|------|------|------|------|
| Syntax tree base | `tree-sitter` | multi-language syntax inventory / import-site candidate extraction | yes | adapter only |
| Python import parser | `pydeps` | source import edge extraction | yes | adapter only |
| Python import graph API | `grimp` | queryable Python import graph for planner-side scoring | yes | adapter + mapping |
| Python contract checker | `import-linter` | boundary/layer contract checks | yes | adapter + mapping |
| JS/TS graph parser | `dependency-cruiser` | JS/TS dependency graph + rules | yes | adapter only |
| JS/TS smoke graph | `madge` | cycle/orphan quick scan | yes | optional adapter |
| Wrapper detector | custom collector | `runpy`, wrapper chain | no | yes |
| Path mutation detector | custom collector | `sys.path`, bootstrap | no | yes |
| Normalized graph schema | local | cross-tool graph merge | no | yes |
| Slice planner logic | local | coarse partition + refinement + stop rule | no | yes |
| Handoff artifact generator | local | `slice_manifest.json`, packet, links | no | yes |

## Fork Boundary

### Good to bring from GitHub
- parser
- syntax-tree inventory layer
- graph extractor
- contract/rule engine
- lightweight cycle/orphan detector

### Keep local
- normalized graph schema
- mixed-repo overlay logic
- wrapper/path-mutation collector
- refinement logic
- stop rules
- slice manifest generation
- handoff packet generation
- subagent fan-out contract

한 줄 규칙:
- **parser는 외부에서 가져와도 된다**
- **planner는 내부에서 가져야 한다**

## Canonical Input Signals

planner가 최소한 직접 이해해야 하는 입력은 아래다.

### Required
- directory tree
- file count
- total bytes
- file extension buckets
- manifest locations
- static dependency overlay

### Strongly recommended
- known entrypoints
- wrapper/path-mutation register
- shared hub summary
- cross-region edge summary
- cycle / diamond / phantom anomaly ledger

### Optional overlay
- observed runtime edges
- unobserved path register
- ownership policy checklist
- prior slice feedback or merge-conflict history

한 줄 규칙:
- **tree만으로 시작할 수는 있지만, static dependency overlay 없이 최종 slice를 확정하면 안 된다.**

## Recommended Planner Algorithm

### Phase 0. Inventory
입력:
- directory tree
- file count
- total bytes
- language buckets
- manifest files
- known entrypoints

산출물:
- `inventory_snapshot.json`

### Phase 1. Coarse slice seed
규칙:
- tree, size, file count, depth로 1차 후보를 만든다.
- 너무 작은 디렉토리는 병합 후보로 둔다.
- 너무 큰 디렉토리는 하위 디렉토리 단위로 split 후보를 만든다.
- 단일 대형 파일은 `large_single_file`로 태그하고 멈춤 후보로 둔다.

산출물:
- `slice_seed_candidates.json`

### Phase 2. Static dependency graph overlay
추가 신호:
- source import graph
- manifest/package graph
- wrapper/runpy/path-mutation edges
- cross-region edges
- shared hubs
- cycle
- diamond
- phantom

산출물:
- `static_dependency_overlay.json`

### Phase 3. Refinement
핵심:
- coarse seed를 graph evidence로 다시 조정한다.

조정 규칙:
- cross-edge ratio가 높은 경계는 분할 취소 또는 재병합
- shared hub가 큰 영역은 write-safe split 금지
- wrapper/path mutation crossing이 많은 영역은 별도 위험 표시
- manifest crossing이 큰 영역은 boundary exception 등록
- multilevel refinement 사고를 차용해, seed 이후 `merge`와 `re-cut`을 둘 다 허용한다
- directory boundary보다 dependency cut cost가 더 나쁘면 tree split을 포기한다

추천 scoring 신호:
- `size_score`
- `internal_cohesion_score`
- `cross_edge_ratio`
- `shared_hub_penalty`
- `runtime_condition_penalty`
- `ownership_conflict_penalty`

산출물:
- `slice_refinement_report.md`

### Phase 4. Runtime overlay
목적:
- static에 있지만 실제 활성화되었는지 확인
- 실행되지 않은 경로는 따로 등록

규칙:
- observed runtime edge는 confidence 상승
- static-only edge는 `unobserved_path_register.json`에 남김
- 필요 시 probe entrypoint를 생성해 follow-up 실행

산출물:
- `runtime_overlay.json`
- `unobserved_path_register.json`

### Phase 5. Stop rules
아래면 더 자르지 않는다.
- single large hub file
- wrapper indirection으로 ownership이 불명확함
- cross-edge density가 너무 높음
- path-order/runtime condition에 과도하게 의존함
- split 후 균형 개선보다 coordination cost 증가가 더 큼

### Phase 6. Final slice proposal
최종 출력:
- `parallel_slices.json`
- `write_safe_slices.json` 또는 `analysis_only_slices.json`
- `do_not_split_regions.json`

## Canonical Output Contract

planner KB만 읽고도 출력 shape를 이해할 수 있어야 한다.

### Global outputs
- `inventory_snapshot.json`
- `slice_seed_candidates.json`
- `static_dependency_overlay.json`
- `slice_refinement_report.md`
- `runtime_overlay.json` (optional)
- `unobserved_path_register.json` (optional)
- `slice_manifest.json`
- `parallel_slices.json`
- `write_safe_slices.json` or `analysis_only_slices.json`
- `do_not_split_regions.json`

### Per-slice outputs
- `slices/<slice_id>/context-links.md`
- `slices/<slice_id>/handoff_packet.json`

### Minimal `slice_manifest.json`
```json
{
  "slice_count": 2,
  "slices": [
    {
      "slice_id": "slice_01",
      "root_dirs": ["src/rag"],
      "files": ["src/rag/graph.py", "src/rag/bootstrap.py"],
      "entrypoints": ["src/rag/graph.py"],
      "classification": "write_safe",
      "reason": "high internal cohesion, low external crossing"
    }
  ]
}
```

### Minimal `handoff_packet.json`
```json
{
  "slice_id": "slice_01",
  "root_dirs": ["src/rag"],
  "files": ["src/rag/graph.py", "src/rag/bootstrap.py"],
  "entrypoints": ["src/rag/graph.py"],
  "allowed_paths": ["src/rag"],
  "non_goals": ["do not modify plans/codex"],
  "upstream_artifacts": [
    "initial_graph_summary.json",
    "risk_report.md"
  ]
}
```

## Downstream Handoff Model

planner의 직접 책임은 실제 fan-out 실행이 아니라 handoff artifact 생성까지다.

### Global artifact
- `slice_manifest.json`

### Per-slice artifacts
- `slices/<slice_id>/context-links.md`
- `slices/<slice_id>/handoff_packet.json`

### Orchestration rule
- if slice count is `N`, planner returns `N` slice packets
- upper agent or `context-broker` decides whether to fan out to `N` workers directly
- planner should not own the final launch step by default

## Canonical Design Takeaways

1. `dependency-slice-planner`는 top-level skill로 두고, 실행 시 planner role subagent가 그 skill을 소비하는 구조가 가장 맞다.
2. 최종 알고리즘은 `tree/size seed -> static dependency refinement -> runtime overlay -> stop rules -> final slices`의 hybrid가 가장 안정적이다.
3. GitHub에서는 parser/extractor 계층과 syntax-tree inventory 계층을 가져오고, planner/refinement/handoff 계층은 내부에 유지하는 편이 맞다.
4. `cycle`, `diamond`, `phantom`, `wrapper/path-mutation`은 graph-side evidence로 취급하고, slice decision은 그 evidence 위에서 내려야 한다.
5. planner의 최종 책임은 launch가 아니라 `slice_manifest.json`과 per-slice handoff artifact를 만드는 데 있다.
6. planner는 self-contained해야 하므로, 입력 신호와 출력 계약이 KB 자체 안에 닫혀 있어야 한다.

## Sources

- [Weiser 1984, Program Slicing](https://dblp.org/rec/journals/tse/Weiser84)
- [Horwitz, Reps, Binkley 1990, Interprocedural Slicing Using Dependence Graphs](https://doi.org/10.1145/77606.77608)
- [Bunch 1999](https://doi.org/10.1109/ICSM.1999.792498)
- [Andritsos & Tzerpos 2005, Information-Theoretic Software Clustering](https://www.cs.toronto.edu/~periklis/pubs/tse05.pdf)
- [Maqbool & Babri 2004, Weighted Combined Algorithm](https://doi.org/10.1109/CSMR.2004.1281402)
- [KarypisLab/METIS](https://github.com/KarypisLab/METIS)
- [Karypis and Kumar 1998, Multilevel k-way Hypergraph Partitioning](https://hdl.handle.net/11299/215392)
- [Karypis, Kumar, Schloegel 1999, Parallel Multilevel Algorithms for Multi-Constraint Graph Partitioning](https://hdl.handle.net/11299/215387)
- [Kong et al. 2018, Directory-Based Dependency Processing for Software Architecture Recovery](https://doi.org/10.1109/ACCESS.2018.2870118)
- [Krause et al. 2020, Microservice Decomposition via Static and Dynamic Analysis of the Monolith](https://eprints.soton.ac.uk/488757/)
- [Matias et al. 2020, Determining Microservice Boundaries / MonoBreaker](https://arxiv.org/abs/2007.05948)
- [Andrade et al. 2022, Static and Dynamic Analysis Comparison](https://www.emergentmind.com/articles/2204.11844)
- [Murphy, Notkin, Sullivan 1995, Software Reflexion Models](https://www.cs.ubc.ca/~murphy/papers/rm/fse95.html)
- [Murphy, Notkin, Sullivan 1997, Extending and Managing Software Reflexion Models](https://www.cs.ubc.ca/tr/1997/tr-97-15)
- [Service Cutter](https://inria.hal.science/hal-01638590)
- [tree-sitter](https://github.com/tree-sitter/tree-sitter)
- [pydeps](https://github.com/thebjorn/pydeps)
- [grimp](https://github.com/seddonym/grimp)
- [import-linter](https://github.com/seddonym/import-linter)
- [dependency-cruiser](https://github.com/sverweij/dependency-cruiser)
- [madge](https://github.com/pahen/madge)
