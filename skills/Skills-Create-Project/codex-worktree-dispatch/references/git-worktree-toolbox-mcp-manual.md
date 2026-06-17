# git-worktree-toolbox MCP Manual

작성일: 2026-03-15

## 설치 상태

Codex MCP에 `git-worktree-toolbox`를 stdio 서버로 등록했다.

등록값:

```text
name: git-worktree-toolbox
command: npx
args: -y git-worktree-toolbox@latest
transport: stdio
```

확인 명령:

```bash
codex mcp list
codex mcp get git-worktree-toolbox
```

삭제 명령:

```bash
codex mcp remove git-worktree-toolbox
```

## 의미

- Codex가 필요할 때 `npx -y git-worktree-toolbox@latest`를 통해 MCP 서버를 띄운다.
- 첫 실행 시 npm에서 패키지를 내려받을 수 있다.
- 로컬 CLI 이름은 `gwtree`다.

## 현재 결론

2026-03-16 기준 실제 end-to-end 테스트 결과는 다음과 같다.

- Codex MCP 등록: 성공
- 패키지 다운로드 및 CLI 실행: 성공
- Codex에서 MCP handshake 후 tool 호출: 실패

즉, 현재 상태는 "등록은 되지만 Codex에서 바로 실사용 가능한 MCP"는 아니다.

## Codex에서 쓰는 방법

Codex 대화에서 worktree 작업을 직접 요청하면 된다.

예시:

- `현재 repo의 git worktree 목록 보여줘`
- `feature/login 작업용 worktree 하나 만들어줘`
- `auth-fix worktree의 변경사항 요약해줘`
- `사용 안 하는 worktree 정리 가능한지 dry-run으로 봐줘`
- `이 worktree에 대응하는 MR 링크 만들어줘`

Codex가 MCP를 사용해 처리할 수 있는 대표 작업:

- worktree 목록 조회
- 새 worktree + branch 생성
- 특정 worktree로 이동 또는 열기
- 변경사항 요약 및 push
- archive / clean
- doctor 진단
- 다른 worktree의 변경사항 grab
- worktree별 AI agent prompt resume

## CLI 메뉴얼

패키지 도움말 기준 버전: `0.5.1`

기본:

```bash
npx -y git-worktree-toolbox@latest --help
```

핵심 명령:

```bash
gwtree list --all
gwtree create "task description"
gwtree changes <worktree_identifier>
gwtree archive <worktree_identifier>
gwtree clean --git_repo_path . --yes
gwtree doctor --git_repo_path .
gwtree mr <worktree_identifier>
gwtree grab <worktree_identifier>
gwtree prompt --worktree_identifier <worktree_identifier>
```

## 명령별 요약

### `list`

- 저장소별 worktree 목록 조회
- `--all`로 전체 저장소 범위 조회

```bash
gwtree list --all
```

### `create` / `new`

- 새 branch와 matching worktree 생성
- 기본 base branch 외에 `--base_branch` 지정 가능
- `--branch_name`으로 이름 고정 가능
- `--git_repo_path` 생략 시 현재 저장소 기준

```bash
gwtree create "login page fix"
gwtree create "login page fix" --base_branch main
gwtree create "login page fix" --branch_name feat/login-fix --git_repo_path .
```

### `go`

- 특정 worktree를 editor/terminal로 연다
- 기본 editor는 `cursor`

```bash
gwtree go auth-fix
gwtree go auth-fix --editor code
```

### `changes`

- 특정 worktree의 변경사항 조회
- `--push_changes`로 push까지 진행 가능

```bash
gwtree changes auth-fix
gwtree changes auth-fix --push_changes
```

### `archive` / `rm`

- worktree를 archive 처리
- `--has_branch_removal` 사용 시 branch도 제거

```bash
gwtree archive auth-fix
gwtree archive auth-fix --has_branch_removal
```

### `clean`

- base branch 대비 변경 없는 worktree를 한 번에 정리
- 기본은 dry-run 성격이고 실제 수행은 `--yes`

```bash
gwtree clean --git_repo_path .
gwtree clean --git_repo_path . --yes
```

### `doctor` / `init`

- worktree 메타데이터 검사
- 누락된 metadata 초기화

```bash
gwtree doctor --git_repo_path .
```

### `mr`

- 해당 worktree 기준 merge request 링크 생성

```bash
gwtree mr auth-fix
```

### `grab`

- 다른 worktree의 변경을 현재 worktree로 가져온다
- 기본은 dry-run 성격, 실제 수행은 `--avoid_dry_run`

```bash
gwtree grab auth-fix
gwtree grab auth-fix --avoid_dry_run
```

### `prompt` / `chat`

- worktree 기준 AI agent 세션 resume
- `--setup`으로 글로벌 AI agent prompt 설정 파일(`~/.gwtree/ai-agent.yaml`) 초기화
- `--cursor`, `--claude`, `--yolo` 옵션 지원

```bash
gwtree prompt --setup --claude
gwtree prompt --worktree_identifier auth-fix
gwtree prompt --worktree_identifier auth-fix --prompt "continue from last context"
```

## 운영 메모

- `archive --has_branch_removal`은 branch 삭제가 포함되므로 주의.
- `clean --yes`는 실제 삭제를 수행한다.
- `prompt --setup`은 `~/.gwtree/ai-agent.yaml`를 만든다.
- `go`는 로컬 editor 실행을 수반할 수 있다.
- MCP로 붙어 있어도, 필요하면 같은 패키지를 CLI로 직접 실행해 동작을 확인할 수 있다.

## E2E 테스트 결과

테스트 날짜: 2026-03-16

테스트 절차:

1. `/tmp/gwtree-mcp-test.tkkv7D` 임시 git 저장소 생성
2. 초기 empty commit 생성
3. `feat/test-worktree` branch로 worktree 추가
4. `codex exec`에서 `git-worktree-toolbox` MCP 사용을 강제 요청

테스트 저장소의 실제 worktree 상태:

```text
worktree /private/tmp/gwtree-mcp-test.tkkv7D
branch refs/heads/main

worktree /private/tmp/gwtree-mcp-test.tkkv7D-feature
branch refs/heads/feat/test-worktree
```

Codex 실행 결과:

- `mcp: git-worktree-toolbox starting`
- 이후 handshake 실패
- Codex가 MCP 대신 shell fallback으로 `git worktree list --porcelain` 수행
- 최종 응답에 `MCP call succeeded: no.` 명시

실패 로그 핵심:

```text
ERROR rmcp::transport::async_rw: Error reading from stream: serde error expected value at line 1 column 1
mcp: git-worktree-toolbox failed: MCP client for `git-worktree-toolbox` failed to start: MCP startup failed: handshaking with MCP server failed: connection closed: initialize response
```

추정 원인:

- 패키지 내부 `dist/stdio.js`가 MCP stdio 서버 시작 후 `console.info(...)`로 일반 텍스트를 stdout에 출력한다.
- Codex는 MCP JSON-RPC frame만 기대하므로 startup banner가 먼저 나오면 handshake가 깨진다.
- 확인한 배너 문자열:

```text
Git Worktree Toolbox 0.5.1 MCP Server running on stdio
```

따라서 현재 버전은 Codex stdio MCP 호환성 문제가 있다고 보는 것이 맞다.

## 이번 세팅에서 확인한 것

- `codex mcp list`에 `git-worktree-toolbox`가 표시됨
- `codex mcp get git-worktree-toolbox`에서 `command=npx`, `args=-y git-worktree-toolbox@latest` 확인
- `npx -y git-worktree-toolbox@latest --help` 실행 시 `gwtree` CLI와 도구 목록 확인
- `codex exec` 기반 실제 MCP 테스트에서는 handshake 실패 확인

## 참고

- GitHub: <https://github.com/ben-rogerson/git-worktree-toolbox>
- OpenAI Codex MCP 문서: <https://developers.openai.com/resources/docs-mcp>
