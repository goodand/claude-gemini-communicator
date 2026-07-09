# Skill 필수 디렉토리 구조

## 표준 구조 (모든 Skill 공통)

```
<skill-name>/
├── SKILL.md                        # Layer 0: 진입점 (~45줄)
├── scripts/                        # Layer 1: 실행 도구
│   └── <script>.py
├── references/                     # Layer 2: 실제 task 수행용 reference
│   ├── <reference-docs>.md         # 필드 정의, 예시, 체크리스트 등
│   └── troubleshooting.md          # ★ 필수: Codex 실험 중 발견된 버그·오류 기록
├── knowledge_bases/                # Skill 구체화/조사 자산 (선택 권장)
│   └── <knowledge-base>.md         # GitHub 조사, 논문/URL KB, 설계 근거
├── legacy/                         # 다운그레이드/이전 버전 보관 (선택)
│   └── .gitkeep
└── evals/
    └── evals.json                  # 검증 기준
```

## 디렉토리 역할 분리

- `references/`: skill이 실제로 사용될 때 다른 agent가 task를 수행하는 데 읽는 문서
- `knowledge_bases/`: skill을 만들거나 구체화할 때 모은 조사 자료, URL KB, 설계 근거
- `legacy/`: 이전 버전 스크립트/문서/명세를 잠시 보관해 다운그레이드나 비교가 필요할 때 사용

## `references/troubleshooting.md` 필수 규칙

모든 skill에 **반드시** 포함. Codex/Agent가 실험·실행하면서 겪은 실수·에러·오류를 기록하는 보편적 구조.

### 기록 대상:
- Codex 실전 테스트(Phase 5-2)에서 발견된 버그
- Agent가 skill 사용 중 반복하는 실수 패턴
- 예상과 다른 동작, edge case, 환경 제약(sandbox 등)

### 케이스 형식:
```markdown
## CASE-001: <한 줄 제목>

**증상**: 무엇이 발생했는가
**원인**: 왜 발생했는가
**해결**: 어떻게 고쳤는가
**교훈**: 재발 방지를 위해 무엇을 기억할 것인가
```

### SKILL.md와의 연결:
- SKILL.md Notes에 해결된 규칙 1줄 추가
- 상세는 `(→ references/troubleshooting.md CASE-XXX)` 포인터

### 아직 실험 전인 skill:
- 빈 템플릿(`# Troubleshooting — <skill-name>`)으로 생성
- Phase 5-2 실전 테스트 후 케이스 추가

## 린터 검사

`quick_validate.py`가 `references/troubleshooting.md` 존재를 검사한다.
없으면: `[WARN] references/troubleshooting.md 없음. Codex 실험 중 발견된 버그·오류를 기록하는 필수 파일입니다.`
