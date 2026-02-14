# Phase 4 설계안 v2: 실용적 에러 감지 + Code Assist

> v1 → Gemini 비판 반영: Over-Engineering 제거, 핵심 가치만 구현
> Reference Architecture는 장기 비전으로 보존, 당장은 현재 아키텍처 위에 증분 확장

---

## Gemini 비판 수용 사항

| 비판 | 대응 |
|---|---|
| Scheduler/Router/Adapter 클래스 분리 = 과설계 | **철회** — 기존 a2a_bridge.py 유지 |
| Memory 4계층 비현실적 | **Layer 1만** — 에러 이력 JSON 파일 하나 |
| SummaryMemory 비용 역전 | **삭제** — 필요해지면 그때 |
| ProceduralMemory 별도 프로젝트급 | **삭제** |
| debate/relay 모드 하드코딩 | **연기** — 현재 evaluate 모드만 |
| Race Condition | **file lock 추가** |
| 목표 불일치 | **코드 품질 향상에 집중** |

---

## 구현 범위 (최소한)

### 1. 에러 감지 — Stop Hook 확장

**변경 파일:** `scripts/hook_stop.py`, `scripts/a2a_bridge.py`

Stop Hook에 에러 스캔 분기를 직접 추가. 별도 클래스/파일 없음.

```
Claude 응답 완료
    → Stop Hook 발동
    → ① Plan 감지 (기존 로직 유지)
    → ② 에러 스캔 (신규):
        transcript_path에서 마지막 N줄 읽기
        에러 패턴 매칭 (Traceback, Error 등)
        에러 이력 확인 (같은 에러 반복?)
        임계값 초과 시에만 Gemini 분석
        "[SYSTEM ADVISORY]" prefix로 Claude에 주입
```

**핵심 설계 결정:**
- 증분 스캔 X → 단순히 **마지막 N줄**(tail) 읽기 (파일 전체 스캔 방지)
- 에러 해시: 가변 요소(경로, 숫자, 시간) 정규화 후 해싱
- 가중치: Critical(1회) / High(1회) / Medium(2회) / Low(3회)
- 전역 쿨다운: 에러 분석 간 최소 60초

**에러 이력 파일:** `scripts/.error_history.json`
```json
{
  "last_analysis_time": 0,
  "errors": {
    "hash123": {
      "preview": "ModuleNotFoundError: ...",
      "count": 2,
      "severity": "high",
      "analyzed": false
    }
  }
}
```

### 2. Gemini Code Assist — PR 리뷰 설정

**새 파일:** `.gemini/review.md`

리포지토리별 커스텀 리뷰 규칙 설정. 구현 5분.

### 3. Config 확장

**변경 파일:** `scripts/config.json`

```json
{
  "error_detection": {
    "enabled": true,
    "tail_lines": 50,
    "global_cooldown_seconds": 60,
    "thresholds": {"critical": 1, "high": 1, "medium": 2, "low": 3},
    "error_prompt": "다음 에러를 분석하고 원인과 수정 방법을 간결하게 제안해주세요.",
    "feedback_prefix": "[SYSTEM ADVISORY: Gemini Error Analysis]"
  }
}
```

---

## 변경 없는 것

| 항목 | 이유 |
|---|---|
| a2a_bridge.py 구조 | Router/Adapter 분리 철회, 기존 유지 |
| hook_auto_task.py | 변경 불필요 |
| Message dataclass | 과설계, A2A 스키마로 충분 |
| Scheduler 클래스 | 과설계, Hook 스크립트에서 직접 처리 |
| Memory 계층 | 에러 이력 JSON 하나로 충분 |
| debate/relay 모드 | 수요 발생 시 구현 |

---

## 구현 순서

1. `config.json`에 `error_detection` 추가
2. `a2a_bridge.py`에 에러 관련 함수 3개 추가
3. `hook_stop.py`에 에러 스캔 분기 추가
4. `.gemini/review.md` 생성
5. 테스트
6. 커밋 + 푸시
