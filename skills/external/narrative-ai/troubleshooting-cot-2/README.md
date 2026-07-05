# Troubleshooting-CoT Skill v3.3

Git 히스토리와 AST 분석 기반 Chain-of-Thought 트러블슈팅. 현재 코드를 추측하지 말고, Git 이력에서 증거를 꺼내라.

## 요구사항

- Git, Python 3.8+
- (선택) Node.js, pylint, eslint

## 구조

```
SKILL.md                          # 메인 프로세스 (Phase 0-5)
DESIGN_DECISION.md                # 설계 의도, 제약, 비목표 정의서

scripts/
  ★ 핵심 (Core)
  semantic_diff.py                # Phase 2: AST 비교 → 삭제/수정/리네이밍 분류
  bisect_runner.py                # Phase 3-1: Git bisect 자동화

  보조 (Fallback/Auxiliary)
  commit_analyzer.py              # Phase 1: 커밋 스코어링 (LLM 폴백)
  syntax_checker.py               # Phase 3-0: 문법 검증 (린터 폴백)
  pattern_archiver.py             # Phase 4: 패턴 저장
  pattern_detector.py             # Phase 5-1: 사후 패턴 분석
  bridge.py                       # Phase 5-4: 연계 스킬 오케스트레이터

references/
  GEMINI_PROMPTS.md               # LLM 프롬프트 템플릿
  HYPOTHESIS_GUIDE.md             # 가설 검증 방법론
  PATTERN_LIBRARY.md              # 패턴 라이브러리
```
