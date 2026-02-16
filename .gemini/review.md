# Gemini Code Assist Review Guidelines

## Language
- 리뷰 댓글은 한국어로 작성

## Project Context
Claude Code Hooks 기반 Claude↔Gemini 협업 평가 시스템.
- `src/core/`: 핵심 모듈 (gemini_service, a2a_protocol, error_analyzer, cooldown)
- `src/hooks/`: Claude Code Hook 스크립트
- `config.json`: 설정 파일

## Focus Areas
- **보안**: API 키 노출, .env 파일 커밋 여부, 환경변수 하드코딩
- **에러 처리**: try/except 누락, 예외 무시, graceful degradation
- **동시성**: 파일 잠금(fcntl) 누락, race condition
- **코드 스타일**: PEP 8, 일관된 네이밍, 불필요한 복잡성

## Commit Convention
이 프로젝트는 `<type>(<scope>): <subject>` 형식의 커밋 메시지를 사용합니다.
- type: feat, fix, refactor, docs, test, chore, perf
- scope: hook, bridge, config, sdk, error, a2a

### Good Case (feat/refactor/perf)
커밋 body에 수도코드(`pseudo`)로 핵심 로직이 기술됩니다.
- 수도코드와 실제 구현이 일치하는지 확인하세요.
- 수도코드에 없는 edge case가 코드에서 처리되는지 확인하세요.

### Bad Case (fix)
커밋 body에 소크라테스식 근본 원인 분석이 포함됩니다:
- `Problem:` → `∵ Why-1:` → `∵ Why-2:` → `∵ Why-3:` → `∴ Fix:`
- Fix가 Why-3(근본 원인)을 실제로 해결하는지 확인하세요.
- 증상만 가린 임시 처리가 아닌지 검증하세요.

### Footer
- `Impact`, `Risk`, `Review-focus` 필드를 참고하여 리뷰 우선순위를 판단하세요.
- Impact/Risk가 `high`인 변경은 더 꼼꼼히 리뷰하세요.

## Ignore
- `gemini_feedback.md`: 자동 생성 파일, 리뷰 불필요
- `plans/`: 설계 문서, 코드 리뷰 대상 아님
- `.cooldown_state.json`, `.error_history.json`: 런타임 생성 파일
- `.gitmessage`: 커밋 템플릿, 리뷰 불필요
