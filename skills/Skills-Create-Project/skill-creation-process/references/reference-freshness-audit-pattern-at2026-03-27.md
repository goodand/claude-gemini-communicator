# Reference Freshness Audit Pattern

- scope: source-of-truth 변경 후 reference/KB/checklist가 stale candidate가 되는 문제를 공용 절차로 잡는 패턴
- source: 2026-03-26~27 세션에서 반복된 "코드는 바뀌었는데 문서가 옛날 그대로" 문제

## 문제 정의

source-of-truth가 바뀐 뒤 아래 파일들이 stale candidate가 된다:
- `references/*-at...md` — 타임스탬프 기반 reference
- `knowledge_bases/*` — KB 문서
- `checklist-forconsistency-evaluation/*` — 정합성 체크리스트
- `checklist-forimplementation/*` — 구현 체크리스트

현재 프로세스에서 "어떤 문서가 stale candidate인지"를 선별하는 공용 절차가 없어서, smoke 이후에도 outdated 문서가 남는다.

## 탐지 방법

### 1차: mtime 비교 (artifact-lifecycle-manager)
```bash
python3 artifact_lifecycle_guard.py scan-stale-candidates --scope references
```
- 문서 내 참조 대상(파일 경로, 코드 패턴)의 mtime > 문서 mtime → candidate_stale
- 참조 대상이 없는 문서 → needs_mapping
- 참조 대상이 존재하지 않는 문서 → missing_target

### 2차: semantic owner 분류
- `rule_bearing` 문서 (checklist, naming rule, field spec) → doc-code-sync-checker로 위임
- `claim_heavy` 문서 (설계 주장, 비교, 판정) → claim-verifier로 위임
- `informational` 문서 (예시 모음, 학습 보조, index) → 별도 도구 없이 mtime 비교 + 수동 확인으로 해제 가능

### 3차: 갱신 또는 archive 결정
- 여전히 유효 → 최소 review 기록을 남긴 뒤 candidate 해제. **touch만으로 해제 금지**
- rule_bearing 문서 → semantic recheck(doc-code-sync-checker) 없이 해제 금지
- 내용이 outdated → reference 갱신 후 sync audit 재실행
- 더 이상 필요 없음 → artifact-lifecycle-manager로 archive/delete handoff

### Review Record Shape

**필드 (저장 위치 무관, shape는 동일)**:

```yaml
freshness_review:
  reviewed_at: "2026-03-27T14:30:00+09:00"   # ISO 8601, 필수
  review_basis: "audit_contract_sync 12/12 in_sync, code 변경 없음"  # 왜 유효한지, 필수
  semantic_owner: "rule_bearing"               # rule_bearing | claim_heavy | informational, 필수
  semantic_decision: "valid"                   # valid | outdated | archive, 필수
  reviewer: "claude-session"                   # 누가 판정했는지, 선택
```

**필드 규칙**:
- `reviewed_at`: 반드시 절대 시각. 상대 날짜("오늘") 금지
- `review_basis`: 유효 근거를 1문장으로. "확인함" 같은 빈 문장 금지
- `semantic_owner`: 2차 탐지에서 분류한 유형. owner에 따라 해제 조건이 다름
- `semantic_decision`: `valid` = 현재 내용 유효, `outdated` = 갱신 필요 (갱신 후 `valid`로 재기록), `archive` = artifact-lifecycle-manager로 handoff

### 저장 위치 분기

| 대상 디렉토리 | 저장 방식 | 이유 |
|-------------|----------|------|
| `references/` | 대상 문서의 **YAML frontmatter** | reference는 자주 개별 갱신되고, review diff가 내용 diff와 함께 보여도 노이즈가 적음 |
| `knowledge_bases/` | **sidecar audit 파일** `knowledge_bases/.freshness_audit.yaml` | KB는 canonical contract 층이므로 의미 변경과 freshness 확인이 한 파일에 섞이면 canonical diff 읽기가 어려워짐 |
| `checklist-*` | **sidecar audit 파일** `checklist-*/.freshness_audit.yaml` | checklist도 판정 기준 층이므로 reviewed_at만 바뀌는 diff가 판정 항목 변경과 섞이면 review 노이즈가 큼 |

**sidecar 파일 형식**:

```yaml
# knowledge_bases/.freshness_audit.yaml
entries:
  - file: "codebase-analysis-knowledge_base-at2026-03-22-01-34.md"
    freshness_review:
      reviewed_at: "2026-03-27T14:30:00+09:00"
      review_basis: "sync audit pass, canonical design takeaways 변경 없음"
      semantic_owner: "rule_bearing"
      semantic_decision: "valid"
  - file: "another-kb.md"
    freshness_review:
      reviewed_at: "2026-03-27T15:00:00+09:00"
      review_basis: "..."
      semantic_owner: "claim_heavy"
      semantic_decision: "outdated"
```

**sidecar 규칙**:
- sidecar 파일은 `.freshness_audit.yaml`로 고정 (dot-prefix로 일반 문서와 구분)
- 대상 파일당 entry 1개. 같은 file이 중복되면 마지막 entry가 유효
- sidecar 파일 자체는 freshness audit 대상이 아니다

## stale candidate vs semantic stale

| | stale candidate | semantic stale |
|---|---|---|
| 탐지 | mtime 비교 (기계적) | 내용 비교 (의미적) |
| 판정자 | artifact-lifecycle-manager | doc-code-sync-checker 또는 claim-verifier |
| 비용 | 낮음 | 높음 |
| 정확도 | false positive 있음 | 높음 |

**stale candidate는 1차 필터. semantic stale 판정은 별도 도구에 위임.**

## 적용 시점

- Phase 5.3B (phase-guide.md)
- **source-of-truth 변경이 있는 모든 round 종료 시** — 아래 중 하나라도 해당하면 trigger:
  - code(scripts/, builder, test) 변경
  - KB(knowledge_bases/) 변경
  - reference/spec(references/) 변경
  - contract registry(references/contracts/) 변경
  - cross-skill contract 문구 변경 (provider 또는 consumer 쪽)
- executable artifact가 바뀐 round면 smoke 직후, KB/reference/spec/registry만 바뀐 round면 round 종료 직후 실행

## 실전 교훈

1. `improvement-priorities-at2026-03-26.md`가 stale인데 smoke에서 안 잡힘 → mtime 비교로 선별 가능했음
2. `claim-types.md`에서 pairwise 관련 내용을 삭제했는데 다른 reference에서 아직 참조 → missing_target으로 탐지 가능
3. freshness audit 없이 "테스트 통과"만 보면 문서 drift가 누적됨
