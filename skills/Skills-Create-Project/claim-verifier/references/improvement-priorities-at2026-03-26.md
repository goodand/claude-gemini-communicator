# Claim Verifier — 개선 방향 우선순위

- recorded_at: `2026-03-26`

## 현재 해결된 것

| 항목 | 해결 방법 |
|------|----------|
| 문서≠구현 오판 | `is_file()` + evidence type 분리 |
| line evidence 부족 | file-level fallback + 이유 명시 (설계 의도) |
| keyword-only → true 방지 | keyword-only → `partial`, true는 keyword + file 모두 필요 |
| unverifiable vs false 분리 | 별도 분기 |
| 디렉토리 vs 파일 혼동 | `is_file()` 사용, `dir_exists` type 분리 |

## 미해결 갭 — 우선순위순

### ~~1. 외부 피드백 batch 입력 포맷 고정~~ (해결됨 2026-03-26)

`verify_batch()` + `batch` CLI 서브커맨드 구현.
- `--items file1.md file2.md` (텍스트 파일 묶음)
- `--claims-json bundle.json` (구조화된 claim 배열)
- str/dict 혼합 입력 지원, 자동 id 부여, 자동 type 분류.
테스트: TestVerifyBatch (4건).

### 2. evidence schema 세분화

현재 evidence type: `file_exists` / `dir_exists` / `keyword_match` (3종).
필요: `doc_evidence` / `code_evidence` / `artifact_evidence` 분리.

### ~~3. consistency claim 전용 pairwise 검증 모드~~ (doc-code-sync-checker로 위임, 2026-03-26)

claim-verifier에서 직접 pairwise 비교하는 것은 skill 경계 위반. doc-code-sync-checker가 이미 4종 rule_kind (`required_field`, `path_safety`, `transition_rule`, `enum_value`)를 AST 기반으로 지원.
claim-verifier는 consistency claim에 partial/unverifiable 판정 + "doc-code-sync-checker로 정밀 비교 필요" follow_up을 반환.
테스트: TestConsistencyDelegation (4건).

### 4. evidence 강도 구분

keyword hit만으로는 true가 안 되게 하는 것은 구현됨 (partial).
추가 필요: mention / definition / usage 수준 구분.

### ~~5. follow-up 구체화~~ (부분 해결, 2026-03-26)

`claim_lint.py follow-up` 서브커맨드로 skeleton 자동 생성 구현.
- false → 수정 대상 (파일/키워드 추출)
- partial → 누락 항목 (evidence gap 추론)
- unverifiable → 추가 탐색 대상
테스트: TestFollowUpSkeleton (5건).
남은 갭: claim_verifier.py 자체의 verify_claim() 내부에서 동적 follow_up 생성은 미구현.

### ~~6. verdict 표 출력 형식 고정~~ (해결됨 2026-03-26)

`format_verdict_table()` + `table` CLI 서브커맨드 구현.
claim_id / verdict / evidence / reason / follow_up 5열 markdown 표 출력.
테스트: TestVerdictTable (2건).

### 7. 반복 이슈 troubleshooting 승격

CASE-001~007 기록 완료. 반복 패턴은 검증 로직에 guardrail로 승격.
