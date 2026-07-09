# research URL Knowledge Base
- ver: `v0.0.0`
- generated_at: `2026-03-17`
- updated_at: `2026-03-17` (v0.0.0: initial research_index_kb)
- kb_profile: `research_index_kb`
- canonical_role: `evidence-to-knowledge-promoter를 위한 research_index_kb`
- format: `- [한 줄 설명](URL)`
- generation_method: `공식 documentation/specification 위주로 evidence -> insight -> reusable KB promotion 기준을 조사`
- total_urls: `6`
- paper_like_urls: `2`
- other_urls: `4`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · 현재 단계 |
| `evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md` (이 파일) | evidence-to-insight 승격용 research_index_kb |
| [troubleshooting.md](../references/troubleshooting.md) | 과승격/근거 부족 실패 패턴 누적 |

## Table of Contents
- [Profile](#profile)
- [Research Focus](#research-focus)
- [Candidate Promotion Units](#candidate-promotion-units)
- [Candidate Output KB Forms](#candidate-output-kb-forms)
- [Candidate Promotion Triggers](#candidate-promotion-triggers)
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Profile

- 이 문서는 `evidence-to-knowledge-promoter`의 첫 `research_index_kb`다.
- 목적은 `관측/증거 공간 -> 개념 공간` 승격에 필요한 외부 기준을 모으는 것이다.
- 아직 checklist source of truth는 아니며, 다음 단계에서 `Canonical Design Takeaways`를 뽑아 `hybrid_kb`로 승격할 수 있다.
- 핵심 질문은 `어떤 evidence가 reusable lesson 또는 KB insight로 승격될 만큼 안정적인가`다.

## Research Focus

- experiment tracking artifact에서 `result`, `parameter`, `run metadata`를 어떻게 구조화하는가
- lineage/provenance 시스템에서 `run -> artifact -> dataset/code version` 연결을 어떻게 남기는가
- evidence를 단발성 run note가 아니라 `reproducible insight`로 승격하려면 어떤 최소 조건이 필요한가
- delta/before-after 비교를 lesson learned로 올릴 때 어떤 요약 단위를 쓰는가
- KB 승격 시 `finding`, `measurement delta`, `lesson`, `adoption rule`을 어떻게 구분하는가

## Candidate Promotion Units

- `finding`
  - 단일 smoke/audit에서 관찰된 사실
- `delta`
  - pre/post 비교로 측정된 변화
- `lesson`
  - 반복 가능한 수정/해석 규칙
- `promotion_trigger`
  - `hybrid_kb` 또는 `canonical_design_kb`로 올릴 충분 조건
- `residual_uncertainty`
  - 아직 KB로 승격하면 안 되는 미해결 관측

## Candidate Output KB Forms

- `research_index_kb`
  - 조사 자산과 사례를 넓게 유지
- `hybrid_kb`
  - 조사 자산을 유지하면서 `Canonical Design Takeaways`를 같이 둠
- `canonical_design_kb`
  - 반복 검증된 lesson/adoption rule만 남김

## Candidate Promotion Triggers

- 같은 유형의 evidence가 2회 이상 반복되고 해석이 안정적일 때
- before/after diff가 있고 개선 방향이 수치로 닫힐 때
- evidence provenance가 분명하고 raw artifact로 역추적 가능할 때
- residual uncertainty가 낮고 action rule로 일반화 가능할 때

## Paper-like URLs

- [Tracking Experiments](https://mlflow.org/docs/latest/ml/tracking/)
  - sources: `official MLflow documentation`
  - taxonomy: `[[experiment_tracking]] · run/result metadata`
  - key_idea: run, metric, parameter, artifact를 한 실험 단위로 추적하면 결과를 재현 가능한 비교 단위로 유지할 수 있다.
  - execution_conditions: evidence를 run-level object로 묶고 artifact/metric linkage를 유지해야 한다.
  - pseudocode_3lines:
    - 1) evidence artifact를 run 단위로 수집한다.
    - 2) metric/parameter/artifact를 같은 실험 object에 연결한다.
    - 3) 반복 run 비교에서 재사용 가능한 delta를 뽑는다.

- [PROV-Overview](https://www.w3.org/TR/prov-overview/)
  - sources: `official W3C note`
  - taxonomy: `[[provenance_model]] · evidence lineage`
  - key_idea: entity, activity, agent 관계를 남기면 어떤 insight가 어떤 evidence와 활동에서 왔는지 역추적할 수 있다.
  - execution_conditions: KB insight에도 최소 provenance link가 있어야 한다.
  - pseudocode_3lines:
    - 1) evidence를 entity로 식별한다.
    - 2) 생성/수정 활동을 activity로 남긴다.
    - 3) agent와 artifact를 연결해 insight provenance를 기록한다.

## Other research References URLs

- [What are experiments?](https://dvc.org/doc/user-guide/experiment-management)
  - sources: `official DVC docs`
  - taxonomy: `[[experiment_management]] · reproducible delta`
  - key_idea: 실험 결과를 commit-like 단위로 비교하면 재현 가능한 before/after insight를 축적할 수 있다.
  - pseudocode_3lines:
    - 1) pre/post 상태를 experiment 단위로 저장한다.
    - 2) 바뀐 metric과 artifact를 비교한다.
    - 3) 반복 가능한 개선 규칙만 KB로 승격한다.

- [Experiment tracking](https://docs.wandb.ai/models/track)
  - sources: `official Weights & Biases docs`
  - taxonomy: `[[experiment_tracking]] · dashboarded evidence`
  - key_idea: metrics, config, artifacts, notes를 같은 run 문맥에 유지하면 나중에 lesson과 decision trace를 연결하기 쉽다.
  - pseudocode_3lines:
    - 1) run 결과와 설정을 함께 남긴다.
    - 2) artifacts와 notes를 링크한다.
    - 3) 반복 패턴을 lesson candidate로 승격한다.

- [OpenLineage Overview](https://openlineage.io/docs/1.37.0/)
  - sources: `official OpenLineage docs`
  - taxonomy: `[[lineage]] · run-to-artifact graph`
  - key_idea: dataset, job, run 관계를 남기면 결과 insight의 입력과 출력 범위를 더 명확히 경계지을 수 있다.
  - pseudocode_3lines:
    - 1) run과 artifact 사이의 lineage를 기록한다.
    - 2) 어떤 입력에서 어떤 산출이 나왔는지 연결한다.
    - 3) 범위가 명확한 insight만 KB로 승격한다.

- [Experiments and Runs](https://sacred.readthedocs.io/en/latest/experiment.html)
  - sources: `official Sacred docs`
  - taxonomy: `[[run_metadata]] · immutable experiment context`
  - key_idea: config, captured output, result를 함께 남기면 나중에 단순 finding이 아니라 해석 가능한 실험 기록으로 재구성할 수 있다.
  - pseudocode_3lines:
    - 1) config와 output을 run에 묶는다.
    - 2) result와 환경 정보를 같이 보존한다.
    - 3) KB insight에 필요한 최소 맥락만 추출한다.
