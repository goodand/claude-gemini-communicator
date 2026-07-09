# Traceability Ratio Strict vs Proxy Experiment

- generated_at: `2026-03-16-19-58`
- checker: [kb_to_consistency_check.py](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/contract-to-concept-mapper/scripts/kb_to_consistency_check.py)
- purpose: 현재 `traceability_ratio`가 strict truth인지, heuristic proxy인지 수치 차이로 확인

## Experimental Definition

- current proxy:
  - `traceability_ratio = covered checklist items / total checklist items`
  - 기준: 현재 checker가 positive mapping 하나만 찾으면 covered로 계산
- strict experimental:
  - `strict_traceability_ratio_experimental = (covered - low_confidence_mapping_items) / total checklist items`
  - 기준: `human_review_queue` 중 `reason == low-confidence mapping`으로 분류된 항목은 분자에서 제외

이 실험의 strict 값은 아직 정식 metric이 아니라, 현재 proxy가 얼마나 낙관적인지 보기 위한 비교용 수치다.

## Results

| case | profile | proxy traceability_ratio | strict experimental | delta | covered | low-confidence | total |
|---|---|---:|---:|---:|---:|---:|---:|
| contract research | `research_index_kb` | `0.7` | `0.1` | `0.6` | `21` | `18` | `30` |
| contract hybrid | `hybrid_kb` | `1.0` | `0.6` | `0.4` | `30` | `12` | `30` |
| contract canonical | `canonical_design_kb` | `1.0` | `0.7333` | `0.2667` | `30` | `8` | `30` |
| doc hybrid | `hybrid_kb` | `1.0` | `0.4839` | `0.5161` | `31` | `16` | `31` |
| doc canonical | `canonical_design_kb` | `1.0` | `0.6452` | `0.3548` | `31` | `11` | `31` |

## Findings

1. 현재 `traceability_ratio`는 strict metric으로 읽기 어렵다.
   - 모든 case에서 strict experimental이 proxy보다 낮다.
   - delta는 `0.2667 ~ 0.6` 범위로 꽤 크다.

2. `research_index_kb`에서 가장 크게 무너진다.
   - `0.7 -> 0.1`
   - reference inventory 중심 KB는 mapping이 생겨도 low-confidence 비중이 매우 높다.

3. `canonical_design_kb`가 strict/proxy 간격을 가장 줄인다.
   - contract canonical: `1.0 -> 0.7333`
   - doc canonical: `1.0 -> 0.6452`
   - profile 정렬과 canonical wording 정렬이 strict gap을 줄이는 데 실제 효과가 있다.

4. 그래도 canonical이라고 strict gap이 0이 되지는 않는다.
   - 남는 low-confidence는 주로 section-level/summary-level 매핑과 boundary 문구에서 나온다.
   - 즉 strict gap은 KB profile뿐 아니라 wording granularity와 mapper heuristic에도 의존한다.

## Representative Low-Confidence Examples

### contract canonical

- `단일 항목이 아니라 skill/project context를 함께 볼 필요가 반영돼 있다`
- `출력은 traceability 없이 자연어만 남기지 않는다`
- `어떤 contract unit이 어떤 concept summary로 lift됐는지 남긴다`

### doc canonical

- ``knowledge_base` 전체와 `codebase와 직접 대조할 canonical design slice`가 구분돼 있다`
- `KB의 핵심 목적이 "문서 규칙과 코드 구현의 drift 검사"로 일치한다`
- `문서 표현(표/목록/다이어그램)과 코드 표현(validate/상수/전이표)을 같은 계약으로 다룰 준비가 돼 있다`

## Interpretation

- 현재 metric naming 계약 기준으로 `traceability_ratio`는 여전히 `proxy-profile`로 읽는 것이 맞다.
- strict truth에 더 가까운 값을 원하면 최소한 다음 중 하나가 필요하다.
  - stronger rule/phrase normalization
  - per-item traceability evidence threshold 상향
  - explicit traceability matrix artifact 도입

## Conclusion

- 이번 실험 기준으로 `traceability_ratio`의 현재 로직은 strict metric이 아니라 heuristic proxy다.
- canonical KB 승격은 proxy/strict gap을 줄이지만, strict interpretation으로 이름을 유지할 수준은 아직 아니다.
- 따라서 현 단계에서는:
  - 이름은 유지하더라도 `proxy-profile` note를 계속 붙이거나
  - 별도 `strict_traceability_ratio_experimental`를 추가 metric으로 분리하는 방향이 맞다.
