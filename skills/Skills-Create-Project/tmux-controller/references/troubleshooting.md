# TMux-Controller Troubleshooting Cases

## CASE-001: wait 패턴이 echo된 명령 문자열에 먼저 매칭

- **증상**: `wait --pattern "Report|failed"` 실행 시 Codex 출력이 아니라 셸 echo가 먼저 매칭
- **원인**: tmux `send-keys`로 보낸 명령이 셸에서 echo됨. `capture-pane`이 echo를 먼저 캡처
- **해결법**: wait 패턴을 출력 전용 문자열로 한정 (예: `"Session ID:"`, `"PASSED"` 등)
- **예방책**: 명령 텍스트에 포함되지 않는 고유한 출력 패턴 사용. 프롬프트 문자열(`$`)도 주의

## CASE-002: stale tmux 세션 누적

- **증상**: `tmux list-sessions`에 24시간 이상 미접속 세션 누적
- **원인**: 이전 실험에서 세션 미종료
- **해결법**: `tmux_verify.py --cleanup-stale --force`
- **예방책**: 실험 종료 시 반드시 `tmux_helper.py kill <session>` 실행

## CASE-003: Codex CLI 옵션 변경 (--approval-mode → --full-auto)

- **증상**: `codex --approval-mode full-auto` 실행 시 `unexpected argument` 에러
- **원인**: Codex CLI v0.114.0+에서 옵션명 변경
- **해결법**: `codex exec --full-auto`로 실행. 비대화형은 반드시 `exec` 서브커맨드
- **예방책**: `codex exec --help`로 현재 옵션 확인 후 사용

## CASE-004: Codex 한글 경로 UTF-8 header 에러

- **증상**: `failed to connect to websocket: UTF-8 encoding error` — `x-codex-turn-metadata` header
- **원인**: macOS HFS+ NFD 분해된 한글이 HTTP header value에서 인코딩 실패
- **해결법**: 무시 가능. Codex가 자동 재연결 후 정상 동작 (경고만 발생)
- **예방책**: 가능하면 ASCII 경로 사용. Codex 자체 버그이므로 치명적이지 않음

## CASE-005: Codex sandbox 네트워크 차단

- **증상**: tmux 세션에서 실행한 Codex가 API 호출/pip install 실패
- **원인**: `CODEX_SANDBOX_NETWORK_DISABLED=1` — 기본 네트워크 차단
- **해결법**: 네트워크 작업은 Claude/사용자가 수행. Codex=로컬 작업만
- **예방책**: 분업 원칙 준수: Codex=코딩/검증, Claude=API/오케스트레이션

---

## 케이스 추가 템플릿

```markdown
## CASE-XXX: [짧은 제목]

- **증상**: [에러 메시지 또는 관찰된 동작]
- **원인**: [근본 원인]
- **해결법**: [구체적 해결 방법]
- **예방책**: [재발 방지 방법]
```
