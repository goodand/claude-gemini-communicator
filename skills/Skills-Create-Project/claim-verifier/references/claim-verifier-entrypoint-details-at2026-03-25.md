# Claim Verifier — Entrypoint Details

- recorded_at: `2026-03-25`

## Workflow

1. **claim 분해** — `python3 scripts/claim_verifier.py extract --input <file>`
   - 입력 텍스트에서 검증 가능한 claim 목록을 추출한다
   - 하나의 문장에 여러 주장이 섞여 있으면 최소 단위로 분리한다

2. **증거 수집** — `python3 scripts/claim_verifier.py verify --claims <claims.json> --repo <path>`
   - claim마다 코드/문서/파일 증거를 수집한다
   - 가능하면 파일 경로 + 라인 번호, 불가능하면 file-level evidence + 이유를 명시한다

3. **판정** — true / false / partial / unverifiable
   - 코드 증거와 문서 증거를 별도로 수집한다
   - unverifiable은 false와 구분하여 보존한다

4. **보고** — `python3 scripts/claim_verifier.py report --results <results.json>`
   - claim별 verdict + evidence + 후속 조치를 출력한다

## CLI

```bash
# claim 추출
python3 scripts/claim_verifier.py extract --input feedback.md

# 증거 수집 + 판정
python3 scripts/claim_verifier.py verify --claims claims.json --repo .

# 보고서 생성
python3 scripts/claim_verifier.py report --results results.json

# verdict 5열 표 (claim_id | verdict | evidence | reason | follow_up)
python3 scripts/claim_verifier.py table --results results.json

# 여러 파일/claim 일괄 검증
python3 scripts/claim_verifier.py batch --items f1.md f2.md --repo .
python3 scripts/claim_verifier.py batch --claims-json bundle.json --repo .

# 중간 산출물 lint
python3 scripts/claim_lint.py claims --input claims.json
python3 scripts/claim_lint.py results --input results.json
python3 scripts/claim_lint.py all --claims claims.json --results results.json
python3 scripts/claim_lint.py follow-up --input results.json

# 도움말
python3 scripts/claim_verifier.py --help
python3 scripts/claim_lint.py --help
```

## 판정 상태

| 상태 | 의미 | 후속 조치 |
|------|------|-----------|
| `true` | 코드/문서/파일 근거가 claim을 직접 지지 | 없음 |
| `false` | 반대 근거가 명확 | 무엇을 고칠지 명시 |
| `partial` | 일부만 충족 | 빠진 부분 명시 |
| `unverifiable` | 현재 근거로 판정 불가 | 추가 탐색 대상 명시 |

## Ecosystem 위치

claim-verifier는 공간 모델 #4 (관측/증거 → 사실 판정/claim verification) 역할을 한다.

- **입력**: 자연어 claim, 외부 피드백, checklist 항목
- **대조 대상**: repo 코드, 파일, 문서
- **출력**: claim별 verdict + line evidence

### 관련 skill

| skill | 관계 |
|-------|------|
| agent-task-packet | 실행 계약(done_definition, checklist)을 claim으로 변환하여 검증 |
| agent-tool-benchmark | claim-verifier의 정성 판정을 정량 메트릭으로 보완 |
| doc-code-sync-checker | consistency claim의 pairwise drift 검증 위임 대상. 시작점이 규칙 집합 |
| artifact-lifecycle-manager | 1차 stale candidate 탐지 → claim-heavy reference의 2차 semantic recheck를 이 skill이 맡음 |
