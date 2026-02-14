# Gemini Code Assist Review Guidelines

## Language
- 리뷰 댓글은 한국어로 작성

## Project Context
Claude Code Hooks 기반 Claude↔Gemini 협업 평가 시스템.
- `scripts/a2a_bridge.py`: 핵심 모듈 (Gemini SDK/CLI 호출, 에러 감지)
- `scripts/hook_*.py`: Claude Code Hook 스크립트
- `scripts/config.json`: 설정 파일

## Focus Areas
- **보안**: API 키 노출, .env 파일 커밋 여부, 환경변수 하드코딩
- **에러 처리**: try/except 누락, 예외 무시, graceful degradation
- **동시성**: 파일 잠금(fcntl) 누락, race condition
- **코드 스타일**: PEP 8, 일관된 네이밍, 불필요한 복잡성

## Ignore
- `gemini_feedback.md`: 자동 생성 파일, 리뷰 불필요
- `plans/`: 설계 문서, 코드 리뷰 대상 아님
- `.cooldown_state.json`, `.error_history.json`: 런타임 생성 파일
