# Codex CLI 인증/모델 이슈 전달 메모

## 핵심 정리
- Codex CLI는 로그인만 되어 있으면 수동으로 `codex` 입력해서 사용 가능.
- 이번 실패는 Codex 자체 불가가 아니라, Claude가 호출한 `codex exec` 컨텍스트에서 기본 모델(`gpt-5.3-codex`) 권한 오류가 발생한 케이스.
- 프로젝트 `codex.toml`에는 모델 설정이 없고 `notify`만 존재하므로, 모델 선택은 전역 기본값/계정 권한의 영향을 받음.
- 자동 실행(Claude가 호출)에서는 모델을 명시하는 방식이 안정적:
  - 권한 확인 후 가능하면: `codex exec -m gpt-5.3-codex "..."`
  - 권한이 없으면: `codex exec -m o3 "..."`
- `Interrupted` 메시지는 실행 중단 상태이므로 continue/allow가 필요.

## 운영 권장
1. `codex login`으로 인증 상태를 고정한다.
2. 자동 실행 경로는 `codex exec -m <모델>`을 강제한다.
3. 모델 권한 확인 전에는 `o3`를 기본 fallback으로 사용한다.
