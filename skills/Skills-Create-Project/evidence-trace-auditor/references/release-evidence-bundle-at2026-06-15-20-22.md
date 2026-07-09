# release-evidence-bundle rules

- generated_at: `2026-06-15T20:22:00+09:00`
- applies_to: remote release claim verification (tag push, PR merge, branch promotion)

## Purpose

리모트 릴리스가 "정상"이라고 주장하기 전에 수집해야 하는 machine-truth 증거 집합을 정의한다.
agent self-report나 human-facing 요약이 아닌 커맨드 출력·tracked artifact가 근거가 되어야 한다.

---

## 1. Release Evidence Bundle — 필수 수집 항목

| # | 항목 | 증거 출처 | 근거 형식 |
|---|------|-----------|-----------|
| 1 | **Validator output** | `release-gate` 스크립트 stdout/stderr | pass/fail 요약 + exit code |
| 2 | **pytest output** | `pytest` stdout (또는 JUnit XML) | 테스트 수/pass/fail/skip 카운트 |
| 3 | **`git diff --check`** | git stdout | 출력 없음 = 공백 오류 없음 (verified) |
| 4 | **tracked-file existence** | `git ls-files --error-unmatch <path>` | 0 exit = 파일이 index에 있음 |
| 5 | **stale markdown target scan** | grep/fd 커맨드 출력 | docs가 scope에 있을 때만 필수 |
| 6 | **PR URL** | `gh pr view --json url` 또는 PR 생성 커맨드 stdout | URL 문자열 |
| 7 | **Merge commit** | `git log -1 --format=%H origin/<branch>` | 40자 SHA |
| 8 | **Base commit** | `git merge-base HEAD origin/main` | 40자 SHA |

> 항목 5(stale scan)는 문서 변경이 릴리스 scope에 포함된 경우에만 필수다.
> 나머지 1–4, 6–8은 모든 릴리스에 필수다.

---

## 2. Clean Target Worktree 규칙

- 모든 증거는 **clean TARGET worktree**에서 수집해야 한다.
  - origin/main 또는 target base에서 체크아웃한 상태를 의미한다.
  - dirty local main(미커밋 변경, 스테이징 파일 혼재)에서 수집한 결과는 릴리스 증거로 인정하지 않는다.
- 증거 수집 전 `git status --short`가 깨끗한지 확인하거나,
  별도 worktree(`git worktree add`)에서 수집한다.
- local dirty 상태에서 수집한 pytest/validator 결과는 `residual_uncertainty`로 분류한다.

---

## 3. Trace Status 적용 (기존 vocabulary 재사용)

기존 `evidence-status-rules-at2026-03-17-02-36.md`의 세 상태를 릴리스 맥락에 적용한다.

- **`verified_evidence`**
  - 커맨드 출력이 실제로 존재하고
  - exit code가 0이며
  - 결과가 claim(pass/exist/no-drift)을 직접 지지할 때

- **`missing_evidence`**
  - 커맨드를 실행하지 않았거나
  - 커맨드 출력이 없거나
  - `git ls-files`가 아닌 `Path.exists()`만 사용한 파일 존재 확인

- **`residual_uncertainty`**
  - 커맨드 출력은 존재하지만 claim을 닫기에 불충분할 때
    (예: dirty worktree, 윈도우 절단 등)

---

## 4. 부정 증거 예시 (looks-pass-but-isn't)

아래 패턴은 겉으로는 pass처럼 보이지만 `verified_evidence`로 인정하지 않는다.

### 4-1. `Path.exists()` pass — untracked 파일

```
Path("/repo/docs/spec.md").exists()  # → True
git ls-files --error-unmatch docs/spec.md  # → exit 1 (untracked)
```

- 파일이 디스크에 있더라도 index에 없으면 릴리스에 포함되지 않는다.
- status: `missing_evidence` (tracked 여부를 증명하지 못했으므로)

### 4-2. 빈 gates 배열 — 0건 검사 실행

```json
{ "gates": [] }
```

- validator가 gates를 한 건도 실행하지 않았을 때 exit 0이 나올 수 있다.
- 0건 실행 = 0건 통과이므로 릴리스 정합성을 보장하지 않는다.
- status: `missing_evidence` (no-op validator 결과는 verified로 인정하지 않음)

### 4-3. `git log --max-count` 윈도우 절단

```bash
git log --max-count=300 --oneline
```

- 히스토리가 300건을 초과하면 그 이전 커밋은 조회되지 않는다.
- 필요한 커밋 subject가 윈도우 밖에 있으면 검사가 silently miss된다.
- status: `residual_uncertainty` (증거는 있으나 범위를 닫지 못함)
- 대안: `git log --all --grep="<subject>"` 또는 SHA 직접 지정

### 4-4. 마커/서브스트링 pass — 동작 미검증

```python
assert "PASSED" in log_text  # marker check
```

- 로그에 "PASSED" 문자열이 있어도 실제 로직이 동작했다는 보장이 아니다.
- 마커 통과 ≠ 동작 검증됨.
- status: `residual_uncertainty` (마커 외 artifact나 exit code 없을 때)

---

## 5. doc-code-sync handoff

릴리스 증거 수집 중 문서↔코드 드리프트가 발견되면
(예: docs의 메트릭 이름이 계약과 다르거나, source-of-truth 경로가 stale한 경우)
시맨틱 재점검을 위해 `doc-code-sync-checker` skill로 handoff한다.

- relative path: `../doc-code-sync-checker/SKILL.md`
- handoff 조건: 릴리스 증거 중 문서 항목이 `missing_evidence` 또는 `residual_uncertainty`로 분류될 때

---

## Notes

- 이 규칙은 `evidence-trace-auditor`의 skill-local rule이며 릴리스 맥락 전용이다.
- 기존 `applies_to` 목록(raw_smoke_report, test_result_evidence 등)과 병렬 관계이고 덮어쓰지 않는다.
- 일반 audit 판정 규칙은 `evidence-status-rules-at2026-03-17-02-36.md`를 따른다.

---

## (boundary) release scope vs generic artifact audit

- release-bound 파일 확인은 반드시 `git ls-files`(또는 target commit tree) 기준이다. 이것이 release 전용 규칙이다.
- 반면 `scripts/evidence_trace_auditor.py`의 generic artifact path ledger(`build-artifact-path-ledger`)는 `Path.exists()` 기준으로 `verified_evidence`를 매긴다. 이는 **non-release 일반 artifact 증거용**이며 의도된 동작이다.
- 따라서 release 검증에는 generic ledger의 `Path.exists()` 결과를 그대로 쓰면 안 된다 — untracked 파일이 false-pass로 잡힐 수 있다. release tracked-file 체크는 위 §1·§4의 `git ls-files` 계약을 별도로 적용한다.
- 요약: generic artifact ledger(Path.exists) ≠ release tracked-file 계약(git ls-files). 두 계약을 혼용하지 않는다.
