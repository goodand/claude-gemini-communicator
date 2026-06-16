---
name: codebase-analysis-gate-sequence-kb-seed
kb_profile: hybrid_kb
role: codebase analysis slice stage gate-sequence seed
ver: 1
created_at: 2026-03-18-23-02
updated_at: 2026-03-22-01-34
reference_acquisition_mode: external_research
source_scope: web papers + official parser/extractor repos + local dependency analysis context
purpose: codebase-analysis의 gate sequence 중 slice stage를 dependency-slice-planner 기준으로 좁히기 위한 seed
---

# Codebase Analysis Gate Sequence KB Seed
## Problem Framing

`codebase-analysis`의 slice stage는 단순 디렉토리 분할기가 아니다.
목표는 아래 둘을 동시에 만족하는 slice를 만드는 것이다.

1. 사람이 병렬로 분석하거나 작업해도 충돌이 적다.
2. 그래프 관점에서 잘못 자른 경계 때문에 핵심 의존성이 끊기지 않는다.

즉 이 역할은 `tree-based partitioning`과 `dependency-aware refinement`를 결합한 slice-planning stage에 가깝다.

## Role Boundary

이 KB 기준 역할 경계는 아래처럼 잡는다.

- `depsolve-analyzer`
  - graph extraction main skill
  - source graph / manifest graph / wrapper-path graph를 분리해서 추출
- slice-planning stage
  - coarse partition + refinement + stop rule + handoff artifact 생성
- downstream worker subagents
  - slice stage가 만든 slice manifest와 handoff packet을 소비

핵심:
- slice stage는 graph extractor가 아니다
- slice stage는 fan-out orchestrator 자체도 아니다
- slice stage는 `slice decision + handoff artifact producer` 성격을 가진다

## Canonical Input Signals

slice stage가 최소한 직접 이해해야 하는 입력은 아래다.

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

## Recommended Slice Stage Sequence

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

이 seed를 바탕으로도 slice stage 출력 shape를 이해할 수 있어야 한다.

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

slice stage의 직접 책임은 실제 fan-out 실행이 아니라 handoff artifact 생성까지다.

### Global artifact
- `slice_manifest.json`

### Per-slice artifacts
- `slices/<slice_id>/context-links.md`
- `slices/<slice_id>/handoff_packet.json`

### Orchestration rule
- if slice count is `N`, slice stage returns `N` slice packets
- upper agent or `context-broker` decides whether to fan out to `N` workers directly
- slice stage should not own the final launch step by default

## Canonical Design Takeaways

1. `codebase-analysis`는 slice stage에서 dependency-aware 분할과 handoff artifact 생성을 소비하는 구조가 맞다.
2. 최종 알고리즘은 `tree/size seed -> static dependency refinement -> runtime overlay -> stop rules -> final slices`의 hybrid가 가장 안정적이다.
3. GitHub에서는 parser/extractor 계층과 syntax-tree inventory 계층을 가져오고, slice-planning/refinement/handoff 계층은 내부에 유지하는 편이 맞다.
4. `cycle`, `diamond`, `phantom`, `wrapper/path-mutation`은 graph-side evidence로 취급하고, slice decision은 그 evidence 위에서 내려야 한다.
5. slice stage의 최종 책임은 launch가 아니라 `slice_manifest.json`과 per-slice handoff artifact를 만드는 데 있다.
6. slice stage는 self-contained해야 하므로, 입력 신호와 출력 계약이 KB 자체 안에 닫혀 있어야 한다.
