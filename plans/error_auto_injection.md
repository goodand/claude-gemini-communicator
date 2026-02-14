# Linter/Error 자동 주입 설계안 v2

> v1 → Gemini 비판적 피드백 + Hook 실험 결과 반영 + Gemini Code Assist 통합

## 목적

Claude Code 개발 워크플로우에서 에러/경고를 자동 감지하여 Gemini에 전달하고,
디버깅 제안을 Claude에 다시 주입하는 기능.

## 실험 결과 (v1에서 확인된 제약)

### PostToolUse Hook 실제 스키마 (실험으로 확인)

```json
{
  "session_id": "...",
  "transcript_path": "...",
  "cwd": "...",
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "tool_input": {"command": "...", "description": "..."},
  "tool_response": {
    "stdout": "...",
    "stderr": "...",
    "interrupted": false,
    "isImage": false,
    "noOutputExpected": false
  },
  "tool_use_id": "..."
}
```

- `tool_response` 필드 존재 확인 (v1의 `tool_output` → 실제는 `tool_response`)
- `exit_code` 필드 없음 — stderr/stdout 내용으로 에러 판별 필요
- **치명적 제약: PostToolUse Hook은 Bash 실패(exit code != 0) 시 발동하지 않음**

### Gemini 피드백 반영 사항

1. ~~PostToolUse Hook에서 Bash 에러 감지~~ → **불가능** (Hook 미발동)
2. 에러 루프 방지: Lazy Analysis 도입 필요
3. min_stderr_length 기준 부적절 → 에러 패턴 매칭으로 전환
4. Claude 인지 부조화 → 제어 장치 필요

## 수정된 설계안

### 아키텍처: 3계층 품질 게이트

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: 실시간 (개발 중)                                │
│ PostToolUse Hook (Write/Edit) → Gemini SDK 평가          │
│ Stop Hook (Plan 감지) → Gemini SDK 평가                   │
│ → .md 파일 변경 시 자동 품질 평가                         │
├─────────────────────────────────────────────────────────┤
│ Layer 2: 에러 분석 (Stop Hook 확장)                      │
│ Stop Hook → 최근 transcript 스캔 → 에러 패턴 감지        │
│ → 반복 에러 또는 Claude 해결 실패 시에만 Gemini 분석     │
│ → Lazy Analysis (지연 분석) 전략                          │
├─────────────────────────────────────────────────────────┤
│ Layer 3: PR 리뷰 (GitHub)                                │
│ git push → PR 생성 → Gemini Code Assist 자동 리뷰        │
│ → 코드 품질, 보안, 스타일 가이드 검사                     │
│ → /gemini review 수동 트리거 가능                         │
└─────────────────────────────────────────────────────────┘
```

### Layer 2: Stop Hook 기반 에러 분석 (새로운 접근)

**PostToolUse 대신 Stop Hook을 확장하는 이유:**
- PostToolUse Hook은 Bash 실패 시 발동하지 않음 (실험 확인)
- Stop Hook은 Claude 응답 완료 시 항상 발동됨
- transcript 파일에서 최근 Bash 에러 이력을 읽을 수 있음

```
Claude 응답 완료 → Stop Hook 발동
    → transcript_path에서 최근 N개 메시지 스캔
    → Bash 에러 패턴 감지 (Traceback, Error, exit code != 0)
    → 에러 반복 횟수 확인 (Lazy Analysis)
    → 2회 이상 반복 OR Claude가 해결 실패한 경우에만 Gemini 호출
    → Gemini 디버깅 제안 → Claude에 주입
```

**Lazy Analysis 전략 (Gemini 피드백 반영):**
- 모든 에러에 즉시 반응하지 않음
- 에러 이력 파일(`.error_history.json`)에 에러 해시 저장
- 동일 에러 2회 이상 반복 시에만 Gemini 분석 트리거
- 전역 쿨다운 (에러 분석 간 최소 N초 간격)

**에러 패턴 매칭 (min_stderr_length 대체):**
```python
ERROR_PATTERNS = [
    r"Traceback \(most recent call last\)",
    r"Error:|ERROR:|error:",
    r"SyntaxError:|TypeError:|ValueError:",
    r"ModuleNotFoundError:|ImportError:",
    r"FAILED|FAIL",
    r"exit code [1-9]",
]
```

### Layer 3: Gemini Code Assist (GitHub PR 리뷰)

**이미 설치 완료된 GitHub Marketplace 앱 활용:**

| 기능 | 설명 |
|---|---|
| 자동 PR 요약 | PR 생성 시 변경사항 자동 요약 |
| 코드 리뷰 | 심각도별 (Critical/High/Medium/Low) 피드백 |
| 코드 수정 제안 | GitHub에서 직접 커밋 가능한 suggestion |
| 수동 트리거 | `/gemini review`, `/gemini summary` 명령어 |
| 스타일 가이드 | 리포지토리별 커스텀 규칙 설정 가능 |

**일일 한도:** 무료 33개 PR (충분)

**커스텀 설정 (`.gemini/review.md` 또는 리포 설정):**
- 프로젝트별 코딩 스타일 규칙
- 보안 체크리스트 (API 키 노출, SQL 인젝션 등)
- 한국어 리뷰 설정

## 구현 범위

### 수정 파일
| 파일 | 변경 내용 |
|---|---|
| `scripts/hook_stop.py` | 에러 분석 분기 추가 (Plan 감지 + 에러 감지) |
| `scripts/a2a_bridge.py` | `scan_transcript_errors()`, `check_error_history()` 추가 |
| `scripts/config.json` | `error_detection` 섹션 추가 |

### 새 파일
| 파일 | 설명 |
|---|---|
| `scripts/.error_history.json` | 런타임 생성 — 에러 해시 + 발생 횟수 |

### Gemini Code Assist 설정 (선택)
| 파일 | 설명 |
|---|---|
| `.gemini/review.md` (리포 루트) | 커스텀 리뷰 가이드라인 |

## 구현 순서

1. `hook_stop.py`에 transcript 스캔 로직 추가
2. `a2a_bridge.py`에 에러 스캔/이력 관리 함수 추가
3. `config.json`에 `error_detection` 설정 추가
4. Lazy Analysis 테스트 (에러 반복 → Gemini 분석 트리거)
5. Gemini Code Assist 커스텀 리뷰 규칙 설정 (`.gemini/review.md`)

## 검증 방법

```bash
# 1. Stop Hook에서 에러 스캔 테스트 (transcript에 Bash 에러가 있는 경우)
# transcript 파일에 에러 포함된 메시지 추가 후:
echo '{}' | python3 scripts/hook_stop.py

# 2. Lazy Analysis 테스트
# 동일 에러 2회 반복 후 Gemini 분석 트리거 확인

# 3. Gemini Code Assist 테스트
# PR 생성 후 자동 리뷰 확인
git checkout -b test/error-detection
git push -u origin test/error-detection
gh pr create --title "test" --body "test"
# → Gemini Code Assist 리뷰 댓글 확인

# 4. 수동 트리거
# PR 댓글에 /gemini review 입력
```

## 롤백

`config.json`에서 `"error_detection": {"enabled": false}`로 비활성화 가능.
Gemini Code Assist는 GitHub Marketplace에서 앱 제거로 비활성화.
