# Progressive Context Injection

스킬의 계층 구조는 **Agent에게 컨텍스트를 점진적으로 주입하는 전략**이다.
Agent의 컨텍스트 윈도우는 유한하므로, 처음부터 모든 정보를 로드하지 않는다.

## 3-Layer 구조

```
Layer 0: SKILL.md (진입점, ~45줄)
  │  Agent가 첫 번째로 읽는 파일
  │  "언제 쓰는가" + "어떤 순서로 하는가"만 담는다
  │  각 단계에서 필요한 깊은 정보는 → 링크로 가리킨다
  │
  ├─→ Layer 1: scripts/ (실행 가능한 도구)
  │     Agent가 워크플로우 단계를 실행할 때만 진입
  │     --help로 사용법 파악 → 실행 → exit code로 결과 판단
  │     스크립트 내부 로직은 Agent가 읽을 필요 없음
  │
  ├─→ Layer 2: references/ (깊은 컨텍스트)
  │     Agent가 판단이 필요할 때만 진입
  │     cheatsheet, 스키마, 사례 조사, troubleshooting
  │     SKILL.md에서 "(→ references/X.md)" 형식으로 가리킴
  │
  └─→ Layer 2: evals/ (검증 기준)
        Agent가 자기 작업을 평가할 때만 진입
        기대 출력, assertions
```

## 링크 표현 규칙

SKILL.md에서 하위 레이어를 가리킬 때:

```markdown
# Workflow 단계에서 스크립트를 가리킴
4. **실행** — `scripts/worktree_manager.py spawn`으로 생성

# Notes에서 troubleshooting을 가리킴
- Codex sandbox에서 spawn 불가 (→ `references/troubleshooting.md` CASE-003)

# Workflow 단계에서 reference를 가리킴
1. **검색 전략** — 목적별 검색 방법 선택 (→ `references/cheatsheet.md` 검색 팁)
```

## 왜 이렇게 하는가

| 문제 | 해결 |
|------|------|
| SKILL.md에 모든 정보 → Agent 컨텍스트 낭비 | Layer 0은 45줄 이하, 나머지는 링크 |
| Agent가 불필요한 reference까지 읽음 | 링크에 "(→ file CASE-003)" 같은 앵커로 정확한 위치 안내 |
| 스크립트 소스를 Agent가 해석 | `--help`와 exit code만으로 소통, 내부 구현은 불투명 |
| 같은 함정을 반복 | Notes에 핵심 규칙, troubleshooting에 상세 케이스 — 2단계 분리 |
| 새 Agent가 전체 맥락 없이 시작 | Layer 0만 읽으면 "무엇을 어떤 순서로" 알 수 있음 |

## Line Limit Handling

- `quick_validate`에서 SKILL.md line-count warning이 나오면, 기본 대응은 압축이 아니라 split이다.
- 먼저 `Workflow`, `Scripts`, `References`, `Notes` 중 자연스러운 경계가 있는지 찾는다.
- 경계가 있으면 해당 블록을 별도 파일로 옮기고, `SKILL.md`에는 짧은 설명과 링크만 남긴다.
- 분리한 파일은 내용을 억지로 재요약하지 말고, 원래 있던 내용을 최대한 보존한다.
- 압축은 split해도 entrypoint가 여전히 과밀할 때만 2차 선택지로 쓴다.

## PCI Anti-pattern

- SKILL.md에 커맨드 예시 10줄 나열 → **references/cheatsheet.md로 이동**
- scripts/ 사용법을 SKILL.md에 상세 설명 → **`--help`로 위임**
- troubleshooting 전체를 SKILL.md Notes에 기재 → **Notes=규칙 1줄, references/troubleshooting.md=상세 케이스**
- reference 링크 없이 "자세한 내용은 참고" → **"(→ `references/X.md` 섹션명)" 정확한 포인터**
- 의존성 방향 역전 (references → SKILL.md 참조) → **Layer 0→1→2 단방향만 허용**
- line limit 초과 시 문장을 억지로 잘라 entrypoint 의미를 흐림 → **먼저 split point를 찾고 별도 파일 + 링크로 해결**
