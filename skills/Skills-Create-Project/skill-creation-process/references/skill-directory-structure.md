# Skill 필수 디렉토리 구조

## 표준 구조 (모든 Skill 공통)

```
<skill-name>/
├── SKILL.md                        # Layer 0: 진입점 (~45줄)
├── scripts/                        # Layer 1: 실행 도구
│   └── <script>.py
│   └── test_<script>.py            # TDD 파일 (권장)
├── references/                     # Layer 2: 실제 task 수행용 reference
│   ├── <reference-docs>.md         # 필드 정의, 예시, 체크리스트 등
│   └── troubleshooting.md          # ★ 필수: Codex 실험 중 발견된 버그·오류 기록
├── knowledge_bases/                # Skill 구체화/조사 자산 (선택 권장)
│   └── <knowledge-base>.md         # GitHub 조사, 논문/URL KB, 설계 근거
├── checklist-forconsistency-evaluation/   # 정합성 평가용 checklist
│   └── <consistency-checklist>.md
├── checklist-forimplementation/    # 구현용 checklist
│   └── <implementation-checklist>.md
├── legacy/                         # 다운그레이드/이전 버전 보관 (선택)
│   └── .gitkeep
└── evals/
    └── evals.json                  # 검증 기준
```

## 디렉토리 역할 분리

- `references/`: 가장 넓은 문서 층. 조사 원자료, task 수행용 문서, 실험 후 보강 문서를 포함
- `knowledge_bases/`: `references/`를 구조화·정리한 중간 지식층. checklist와 codebase의 입력
- `checklist-forconsistency-evaluation/`: knowledge_base를 읽고 만든 정합성 판정 기준
- `checklist-forimplementation/`: consistency checklist를 구현 항목과 테스트 계획으로 내린 문서
- `scripts/test_*.py` 또는 `tests/test_*.py`: 구현 파일 작성 전/직후 함께 두는 TDD 파일
- `legacy/`: 이전 버전 스크립트/문서/명세를 잠시 보관해 다운그레이드나 비교가 필요할 때 사용
- active artifact rename/delete/duplicate cleanup이 필요하면 `(→ references/artifact-lifecycle-bridge-at2026-03-16-23-58.md)` 기준으로 lifecycle audit를 먼저 한다

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

`quick_validate.py`는 `scripts/` 또는 구현 파일이 있는데 TDD 파일(`scripts/test_*.py`, `tests/test_*.py`)이 없으면 경고한다.
`--strict`에서는 실패로 승격할 수 있다.

`skill-creation-process/scripts/verify_artifact_order.py`는 `knowledge_base -> consistency checklist -> implementation checklist`
생성 순서와 분 단위 파일명을 메타데이터 기준으로 검사한다.

active tree에서 같은 내용의 예전 artifact를 정리하거나 legacy backup 필요 여부를 판단할 때는
`artifact-lifecycle-manager`를 쓰는 쪽이 맞다. `(→ references/artifact-lifecycle-bridge-at2026-03-16-23-58.md)`
