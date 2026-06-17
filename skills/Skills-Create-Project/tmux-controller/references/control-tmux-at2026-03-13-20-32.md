# tmux 제어용 에이전트 Skills·모듈 GitHub 저장소 심층 조사

## Executive summary

이번 조사는 **GitHub 저장소만**을 대상으로, 대화형/자동화 에이전트가 **tmux 세션·윈도우·팬을 생성/분할하고, 키 입력(send-keys), 출력 캡처(capture-pane), 리사이즈/줌, attach/detach, 스크립팅(원시 tmux 명령 포함)**을 수행할 수 있도록 “Skill/Plugin/Agent Module” 형태로 제공하는 구현체를 선별·분석했다. 결론적으로, 현재 생태계는 크게 세 갈래로 수렴한다: (1) **MCP 서버**로 tmux를 “도구”로 노출하는 방식(클라이언트: Claude Desktop/CLI 등), (2) 특정 에이전트 런타임/프레임워크에 **Skill/플러그인**으로 붙는 방식(예: Pi Agent식 SKILL.md, Claude Code 플러그인), (3) 다수 에이전트 세션을 사람이 관리하기 쉽게 만드는 **세션 매니저(TUI/CLI)** 방식이다. citeturn42view1turn19view0turn35view4turn29search0

실무 관점에서 “가장 바로 쓰기 좋은” 축은 두 가지다. 첫째, **Agent Deck(asheshgoplani/agent-deck)**은 AI 코딩 에이전트를 위한 **tmux 기반 세션 매니저**로, 설치/업데이트/릴리즈 주기가 매우 활발하고(릴리즈 다수, 2026-03 기준 최신 릴리즈 표기), tmux 세션을 자체 네임스페이스로 운용하며(기존 tmux 환경을 건드리지 않는다고 명시) 운영 안정성 이슈(예: **stale tmux socket 자동 복구**)까지 PR로 드러난다. citeturn35view0turn35view3turn39view0turn37view0  
둘째, “에이전트가 직접 tmux를 조종”해야 한다면, **MCP 기반 tmux 서버**(예: bnomei/tmux-mcp, k8ika0s/mcp-tmux, nickgnd/tmux-mcp)가 가장 범용적이다. 이 중 **k8ika0s/mcp-tmux**는 **SSH alias 기반 remote-first**, destructive call에 `confirm=true` 요구, 로그/감사 로깅 등 **안전장치와 관측성(Observability)**를 강하게 전면에 둔다. citeturn19view0turn18view0

보안 측면의 핵심은 단순하고 강력하다: tmux를 제어한다는 것은 사실상 “터미널을 제어”하는 것이며, 일부 구현은 **임의 명령 실행(또는 raw tmux command)**을 허용한다. 특히 **persistent-shell-mcp(TNTisdial/persistent-shell-mcp)**는 “AI가 임의 셸 명령을 실행할 수 있으니 격리된 테스트 환경에서만 사용”하라는 강력한 경고를 설치 섹션에 명시한다. 따라서 운영 환경에서는 (a) 별도 tmux 소켓으로 **격리**, (b) 원격 호스트는 **최소권한 SSH 계정**, (c) destructive 작업은 **명시적 승인(confirm)**, (d) 출력 캡처/로그에 포함될 수 있는 **비밀정보(토큰, 키) 취급 기준**이 필수다. citeturn22view3turn42view3turn29search0turn19view0

## 조사 범위와 평가 기준

범위는 “GitHub 저장소”로 한정했다. (공식 웹사이트, 블로그, 패키지 레지스트리 문서 등은 참고하지 않음) 판단 근거는 저장소 내 **README/문서/SKILL.md, 예제 코드, 이슈·PR**에 명시된 동작과 인터페이스(도구 목록, 명령, API, 구성 파일)였다. citeturn42view3turn35view4turn29search0turn33view0turn39view0

선정 기준은 다음을 충족하는 정도로 가중치를 뒀다.  
첫째, “에이전트 친화적 인터페이스”가 명시되어야 했다(예: MCP tool 목록/리소스 URI, Skill CLI, 플러그인 커맨드). 둘째, tmux에서 최소한 **세션/팬 단위 제어 + 출력 관측(캡처/모니터/리소스)**가 가능해야 했다. 셋째, 유지보수 신호(최근 커밋, 릴리즈, 이슈/PR 활동, 경고문·안전장치 유무)를 함께 평가했다. citeturn7view5turn19view0turn29search0turn37view0turn22view3

## 저장소 비교 표

아래 표의 별(stars)·마지막 커밋 날짜는 GitHub UI에 표시된 정보를 기반으로 하며, 시점에 따라 변동될 수 있다(본 조사는 2026-03-13 KST 기준). citeturn35view0turn37view0turn28view0turn18view0turn8view0

| name | URL | 주 언어 | 라이선스 | 마지막 커밋 | ⭐ | 요약 | 지원 에이전트/프레임워크 | tmux 제어 범위 | 설치 | 사용 예시 | 주요 파일 | 성숙도/메인터넌스 |
|---|---|---|---|---|---:|---|---|---|---|---|---|---|
| agent-deck | https://github.com/asheshgoplani/agent-deck | Go | MIT | 2026-03-03 | ~1.5k | AI 코딩 에이전트를 위한 **tmux 기반 TUI/CLI 세션 매니저** | “Claude Code Skill” 설치 옵션 명시, MCP 관리/세션 포킹 등 세션 운영 중심 citeturn35view4 | 세션 생성/삭제/attach, 포크(대화 컨텍스트 상속) 등 “관리” 중심(낮은 수준의 tmux 명령 API라기보다 운영 UX) citeturn35view3turn36view1 | `curl …/install.sh \| bash`, `brew install …`, `go install …` citeturn35view4 | `agent-deck add . -c claude`, `agent-deck session fork …`, `agent-deck mcp attach …` citeturn35view4 | `README.md`, `install.sh`, `cmd/agent-deck`, `skills/` citeturn36view0turn35view4 | 릴리즈가 매우 활발(최신 릴리즈 2026-03-11 표기). tmux 안정성 이슈(예: stale socket 자동 복구) PR로 확인: https://github.com/asheshgoplani/agent-deck/pull/282 citeturn35view0turn39view0 |
| Pi Agent tmux skill (Dwsy/agent 내) | https://github.com/Dwsy/agent | TypeScript (repo 기준) | MIT | 2026-02-20 | 25 | 에이전트 시스템(Pi Agent) 내 **tmux 원격 제어 Skill**(CLI/TUI+TS API) citeturn27view0turn29search0 | Pi Agent의 “Skills” 아키텍처(SKILL.md 주입형) citeturn27view0turn29search0 | 세션 생성/리스트/상태/종료, send/capture, attach 커맨드 출력, sync/cleanup. 별도 tmux 소켓(`/tmp/pi-tmux-sockets/pi.sock`)·세션 메타 저장(파일) citeturn29search0 | Bun 기반: `bun ~/.pi/agent/skills/tmux/lib.ts …` citeturn29search0 | `create`, `send`, `capture`, `attach`, `kill` 등 CLI + `TmuxManager` TS API citeturn29search0 | `skills/tmux/SKILL.md`, `skills/tmux/lib.ts`, `scripts/wait-for-text.sh` citeturn29search0turn26search3turn26search6 | 최근 커밋 2026-02-20. tmux 관련 이슈/PR은 표면적으로 드러나지 않지만, Skill 문서에 안전 모드(리터럴 send)·복구(sync) 규칙이 상세 citeturn28view0turn29search0 |
| mcp-tmux | https://github.com/k8ika0s/mcp-tmux | JavaScript | AGPL-3.0 | 2025-12-14 | 1 | **remote-first**(SSH alias+세션) tmux MCP 서버. 안전장치/관측성 강조 citeturn17view6 | MCP 클라이언트(Claude Desktop/CLI 스타일) + “ChatGPT/Supergateway” 언급 citeturn17view6turn19view0 | 세션/윈도우/팬 관리, send_keys, capture, layout 저장/복구, sync panes, kill(확인 필요), raw tmux command, tail/pattern task, 로그/감사 로깅 citeturn19view0 | `npm install && npm run build`, `MCP_TMUX_HOST=… npx @k8ika0s/mcp-tmux` citeturn17view3 | 권장 호출 체인: `tmux_open_session → … → tmux_send_keys → tmux_capture_pane`, 협업 attach 예시 포함 citeturn19view0 | `README.md`, `src/`, `tests/`, `server.json` citeturn17view2 | 커밋 2025-12-14. PR 머지 기록 다수(예: #30/#29 등)로 원격 SSH quoting/파서 하드닝 흔적 citeturn18view0 |
| tmux-mcp | https://github.com/nickgnd/tmux-mcp | (주로) TypeScript/Node | MIT | 2025-08-24 | ~230 | tmux MCP 서버. “세션/팬 탐색+캡처+명령 실행+생성/분할/삭제” 제공 citeturn7view5turn8view0 | Claude Desktop 구성 예시를 README에 직접 제공 citeturn7view5 | list/find session, list windows/panes, capture, execute, create session/window, split pane(크기 옵션), kill session/window/pane citeturn7view5 | Claude Desktop: `npx -y tmux-mcp` 구성. shell-type 옵션 제공 citeturn7view5 | `tmux://pane/{paneId}`, 도구 목록 기반으로 에이전트가 탐색→실행→결과 조회 citeturn7view5 | `README.md` 중심 citeturn7view5 | 커밋 2025-08-24. 이슈가 실제 사용 요구/배포 이슈를 반영: https://github.com/nickgnd/tmux-mcp/issues/23, https://github.com/nickgnd/tmux-mcp/issues/2 citeturn10view0turn10view1 |
| tmux-mcp-rs | https://github.com/bnomei/tmux-mcp | Rust | MIT | 2026-02-23 | 1 | “세션 생성·팬 분할·명령 실행·캡처”에 더해 **buffer 기반 탐색/슬라이스** 등 고급 워크플로 포함 citeturn42view3turn42view2turn6view0 | 여러 MCP 클라이언트 예시(Claude Code/Codex CLI/OpenCode/Amp)를 README에 병기 citeturn42view1 | create-session/window/split, send-keys/capture-pane, cancel/EOF, sync panes, buffer list/show/save/delete/search/subsearch, pane swap/join/break, layout select, rename, zoom/resize, clients/metadata 리소스 citeturn42view2turn42view3 | `cargo install tmux-mcp-rs` 또는 `brew install …/tmux-mcp-rs` citeturn42view3 | (격리 예시) `tmux -S /tmp/ai-agent.sock … new-session -d …` + `TMUX_MCP_SOCKET=… tmux-mcp-rs` citeturn42view3 | `README.md`, `skills/`, `tests/`, `specs/…` citeturn42view4 | 커밋 2026-02-23. 통합 테스트가 “임시 소켓의 격리된 tmux 서버”를 사용해 기존 tmux와 충돌 회피를 명시 citeturn42view5turn6view0 |
| agent-manager-skill | https://github.com/fractalmind-ai/agent-manager-skill | Python | MIT | 2026-02-20 | 18 | tmux+Python으로 **에이전트 라이프사이클(start/stop/monitor)** + cron 스케줄링 citeturn31view1turn31view4turn32view0 | “openskills install” 전제로 `.agent/skills/` 또는 `.claude/skills/` 배치 citeturn31view4 | 개별 에이전트를 tmux로 띄우고 monitor로 캡처, stop으로 종료. 선택적으로 단일 tmux 세션에 window로 모으기 citeturn31view6 | `npx --yes openskills install fractalmind-ai/agent-manager-skill` citeturn31view4 | `python3 …/scripts/main.py start …; monitor … --follow; stop …` citeturn31view6 | `README.md`, `agent-manager/SKILL.md`, `examples/…`, `SECURITY.md` citeturn31view1turn31view6 | 이슈가 “운영 중 starvation” 같은 실제 장애 맥락을 담음: https://github.com/fractalmind-ai/agent-manager-skill/issues/111 citeturn34view0 |
| persistent-shell-mcp (npm: tmux-mcp-server) | https://github.com/TNTisdial/persistent-shell-mcp | JavaScript | MIT | 2025-07-02 | 1 | tmux 세션을 “workspace”로 써서 **지속 셸 실행**을 MCP 도구로 제공 citeturn22view2turn22view3turn23view0 | MCP 클라이언트 구성(`"mcpServers": …`) 제공 citeturn22view3 | 워크스페이스=tmux 세션. `execute_command`, `start_process`(장기/인터랙티브), 출력 조회/중단(Ctrl+C) 등 citeturn22view3turn22view5 | `npm install -g tmux-mcp-server` 또는 소스 설치 citeturn22view3 | `execute_command({command:"…", workspace_id:"…"})`, `start_process({…, target_window:"ui"})` citeturn22view3 | `src/server.js`, `src/tmux-manager.js`, `EXAMPLES.md` citeturn22view2turn22view3 | “민감 데이터/프로덕션 금지” 보안 경고를 설치 섹션에 명시 citeturn22view3 |
| rinadelph/tmux-mcp | https://github.com/rinadelph/tmux-mcp | Python | MIT | 2025-08-20 | 2 | MCP stdio 서버 + GUI(Tkinter) + uv 기반 구현까지 포함한 “종합 tmux 제어 시스템” citeturn15view0turn16view0 | Claude Desktop 및 MCP 호환 클라이언트 “통합”을 README에서 강조 citeturn14view2turn15view0 | `list_tmux_sessions`, 세션 메시지 전송, AI 에이전트 launch, 타이머/자동 사이클, Ctrl+C 등(윈도우/팬 저수준 도구보다는 “세션 단위 오케스트레이션” 성격) citeturn15view0 | `pip install -r requirements.txt` 또는 `uv sync`, `claude mcp add … python …/tmux_mcp_server.py` citeturn14view4turn14view5 | JSON-RPC `tools/call` 예시와 리소스 URI(`tmux://sessions` 등) 제공 citeturn15view0 | `tmux_mcp_server.py`, `tmux_messenger*.py`, `claude_desktop_config.json` citeturn14view2turn15view0 | 이슈/PR 0 표기, 커밋 2025-08-20. 기능 폭은 넓지만 유지보수 신호는 제한적 citeturn16view0turn15view0 |
| tmux-mcp-server | https://github.com/lox/tmux-mcp-server | Go | (미표기) | 2025-06-16 | 6 | Go로 만든 간단한 tmux MCP 서버(세션 시작/명령 전송/화면 캡처) citeturn20view3turn21view0 | MCP 서버(stdio)로 “세션 관리 도구” 제공 citeturn20view3 | `start_session`, `send_commands`(특수키 토큰 지원), `view_session`, `list_sessions`, `join_session`, `close_session` citeturn20view3 | `go run ./cmd/tmux-mcp-server` citeturn20view3 | vim 편집 예제(키 시퀀스 전송) 제공 citeturn20view4 | `AGENT.md`, `cmd/…`, `internal/…`, `README.md` citeturn20view3 | 이슈 0, PR 2 표기. (라이선스 파일이 표에 보이지 않아 “미표기”로 처리) citeturn21view0turn20view3 |
| t-pane | https://github.com/cni-locates-rumen/t-pane | JavaScript | (미표기) | 2025-06-28 | 2 | Claude가 tmux 팬에서 명령 실행·출력 캡처를 하도록 하는 MCP 서버(디렉터리 인지) citeturn24view3turn25view0 | Claude 구성 파일 경로/예시를 직접 제시(사실상 MCP client 대상) citeturn24view4 | 디렉터리별 팬 생성/관리, `execute_command`, `create_pane`(split), `capture_output`, `list_panes`, 프롬프트 감지/로깅 citeturn24view3turn24view4 | `npm install`, `npm run build`, config에 `dist/index.js` 지정 citeturn24view4 | JS 호출 예시(`execute_command({…})` 등) citeturn24view4 | `.t-pane/logs/`, `src/`, `CLAUDE.md`, `test.sh`, `README.md` citeturn24view3 | 단기간 커밋(2025-06-28). “다중 인스턴스 충돌” 같은 tmux 경합 문제를 커밋 로그에서 직접 다룸 citeturn25view0 |
| claude-tmux | https://github.com/buremba/claude-tmux | Shell | MIT | 2026-01-12 | 2 | Claude Code 플러그인: “tmux 환경 인지”로 백그라운드 윈도우/병렬 팬/세션 연속성 지원 citeturn40view3turn41view0 | Claude Code의 `/plugin` 워크플로를 전제로 한 플러그인 citeturn40view3 | 백그라운드 윈도우 작업, 병렬 팬, 출력 모니터링, 다음 세션 메시지 큐잉(자기-연속), asciinema 기록(`/record`) citeturn40view3 | `/plugin marketplace add …`, `/plugin install …` 또는 `git clone … ~/.claude/plugins/…` citeturn40view3 | 자연어 유스케이스 문장 + `/record` CLI 옵션 제공 citeturn40view3 | `.claude-plugin/`, `skills/`, `generate-demos.sh`, `README.md` citeturn40view6turn40view3 | 이슈/PR 0 표기. 커밋 2026-01-12로 비교적 최근이며 데모/기록 기능이 중심 citeturn41view0turn40view5 |
| tmux-mcp (POC) | https://github.com/jonrad/tmux-mcp | Python | (미표기) | 2025-02-21 | 7 | **POC** MCP 서버: “임의 tmux 명령 실행”만 제공(프로덕션 금지 경고) citeturn11view0turn13view0 | MCP client config 예시(uvx로 git 설치) citeturn11view0 | raw tmux command(임의 실행) → 강력하지만 위험. pane 읽기/키 전송 가능하다고 경고 citeturn11view0 | `uvx --from git+… tmux-mcp` citeturn11view0 | MCP client가 raw command를 호출하는 형태(도구 최소) citeturn11view0 | `server.py`, `pyproject.toml`, `README.md` citeturn11view0 | README에 “proof of concept, production 사용 금지”를 명시. 이슈 1 표기 citeturn11view0turn13view0 |

## 상위 저장소 활용 패턴

아래는 “tmux 제어” 관점에서 가장 실용도가 높은 상위 5개(Agent Deck, Pi Agent tmux Skill, mcp-tmux, nickgnd/tmux-mcp, tmux-mcp-rs)의 **설치/구성·핵심 호출·예시 워크플로**를 짧게 발췌한 것이다. (코드는 원문에서 필요한 최소만 요약/발췌) citeturn35view4turn29search0turn19view0turn7view5turn42view3

```mermaid
flowchart LR
  U[사용자] --> A[대화형 에이전트<br/>(Claude/Codex/커스텀)]
  A -->|Skill 호출 또는 MCP tools/call| T[tmux 제어 모듈<br/>(Skill/Plugin/MCP Server)]
  T -->|tmux 명령 실행| S[tmux server / socket<br/>(로컬 또는 SSH 원격)]
  S --> P[session/window/pane 상태 변화]
  P -->|capture-pane / state snapshot| O[관측 출력/메타데이터]
  O -->|tool 결과 or resource 읽기| A
  A -->|파괴적 작업은 confirm/승인| T
```
citeturn19view0turn42view3turn22view3

**Agent Deck (asheshgoplani/agent-deck)**  
설치와 시작이 빠르고, 세션 운영(추가/포크/MCP 부착 등)을 CLI/TUI로 제공한다. 특히 Claude Code 사용자는 “Claude Code Skill” 설치 절차(`/plugin marketplace add …`)를 README에 포함한다. citeturn35view4  
```bash
curl -fsSL https://raw.githubusercontent.com/asheshgoplani/agent-deck/main/install.sh | bash
agent-deck
agent-deck add . -c claude
agent-deck session fork my-proj
agent-deck mcp attach my-proj exa
```
citeturn35view4  
운영 안정성 측면에서는, tmux “기본 소켓이 stale 상태일 때 세션 시작이 실패”하던 문제를 자동 복구하도록 만든 PR #282가 공개되어 있다(리스크: 소켓/권한/다중 tmux 서버 환경). PR 요약에 실패 메시지(`server exited unexpectedly`)와 “stale socket quarantine 후 재시도” 전략이 명시된다. https://github.com/asheshgoplani/agent-deck/pull/282 citeturn39view0turn37view0

**Pi Agent tmux Skill (Dwsy/agent 내부 skill)**  
이 구현은 “MCP 서버”라기보다 “에이전트 런타임에 주입되는 Skill”에 가깝다. 특이점은 **개인 tmux와 충돌을 줄이기 위해 전용 소켓(`/tmp/pi-tmux-sockets/pi.sock`)**을 잡고, 세션 메타를 JSON으로 유지(sessions.json)하며, send를 “리터럴 모드”로 안전하게 처리한다는 규칙을 문서화한 점이다. citeturn29search0  
```bash
bun ~/.pi/agent/skills/tmux/lib.ts create python "PYTHON_BASIC_REPL=1 python3 -q" task
bun ~/.pi/agent/skills/tmux/lib.ts send pi-task-python-* "print('Hello')"
bun ~/.pi/agent/skills/tmux/lib.ts capture pi-task-python-* 200
bun ~/.pi/agent/skills/tmux/lib.ts attach pi-task-python-*
```
citeturn29search0  
TypeScript API도 제공해, 에이전트 코드 내부에서 세션 생성→출력 캡처→패턴 대기(waitForText) 같은 “반복 가능한 상호작용”을 구성할 수 있다. citeturn29search0

**mcp-tmux (k8ika0s/mcp-tmux)**  
원격 환경에서 “LLM은 터미널을 실제로 보지 못한다”는 문제의식으로, **상태 스냅샷(`tmux_state`) 중심의 grounded control**과 **파괴적 도구의 confirm 요구**, 그리고 SSH alias 기반의 remote tmux 부트스트랩을 전면에 둔다. citeturn19view0turn17view2  
```bash
npm install
npm run build
MCP_TMUX_HOST=my-ssh-alias MCP_TMUX_SESSION=collab npx @k8ika0s/mcp-tmux
```
citeturn17view3turn19view0  
도구 호출의 “권장 순서”를 README에서 직접 제시한다(세션 열기→기본 컨텍스트→윈도우/팬 나열→키 전송→캡처). citeturn17view3turn19view0  
또한 도구 목록에 `tmux_split_pane`, `tmux_new_window`, `tmux_capture_layout`/`restore_layout`, `tmux_set_sync_panes`, `tmux_kill_* (confirm=true)` 등이 포함되어 “낮은 수준 tmux 조작+안전성”을 동시에 겨냥한다. citeturn19view0turn18view0

**tmux-mcp (nickgnd/tmux-mcp)**  
Claude Desktop에 “npx로 즉시 연결”하는 구성이 간결하다. 도구는 세션/윈도우/팬 탐색, 캡처, 생성/분할, 삭제 등 전형적인 tmux 제어 세트를 제공한다. citeturn7view5turn8view0  
```json
"mcpServers": {
  "tmux": {
    "command": "npx",
    "args": ["-y", "tmux-mcp"]
  }
}
```
citeturn7view5  
이슈 트래커에는 기능 요청(예: “Dedicated Terminal Interaction Commands”)과 배포/리스트 등록 관련 이슈가 보이며, “실사용 중 부족한 도구”가 어떤 것인지 신호를 준다. https://github.com/nickgnd/tmux-mcp/issues/23 citeturn10view0turn9view0

**tmux-mcp-rs (bnomei/tmux-mcp)**  
설치 옵션이 다양하고(cargo/brew), 여러 MCP 클라이언트용 Quick Start를 병기한다. 특히 “단순 send-keys/capture”를 넘어, **buffer 탐색(search/subsearch), pane 재배치(join/break/swap), zoom/resize, client 목록, 메타데이터 리소스** 등 tmux의 구조적 조작을 에이전트 워크플로로 끌어올린 점이 특징이다. citeturn42view3turn42view2turn42view5  
```bash
cargo install tmux-mcp-rs
# 또는
brew install bnomei/tmux-mcp/tmux-mcp-rs
```
citeturn42view3  
원격/격리 운용을 위해 `--socket` 또는 `TMUX_MCP_SOCKET`로 특정 tmux 서버 소켓에 붙는 방법을 문서화하며, “에이전트 전용 tmux 서버 생성” 예시도 제공한다. citeturn42view3  
또한 통합 테스트가 “임시 소켓의 격리된 tmux server”를 사용해 기존 세션에 영향을 주지 않는다고 명시해, 유지보수 관점에서 신뢰 신호를 준다. citeturn42view5turn6view0

## 호환성 및 보안 고려사항

호환성에서 먼저 확인해야 할 것은 “도구가 전제하는 실행 환경”이다. 예를 들어 **agent-deck**은 macOS/Linux/Windows(WSL) 지원을 명시하고, 설치 스크립트·Homebrew·go install을 제공한다. citeturn35view4 반면 **t-pane**은 “tmux 세션 내부에서 실행해야 완전한 기능을 쓴다”는 식의 실행 조건을 README에 포함한다(“Not running inside a tmux session” 트러블슈팅 포함). citeturn24view4 또한 **claude-tmux**는 요구사항에 tmux 버전(v3.0+)과 `jq`/`bash` 등을 명시한다. citeturn40view3turn40view1

보안은 “권한 모델”과 “명령 표면적”으로 나눠 보는 것이 실용적이다. tmux 제어 도구는 대체로 **현재 사용자 권한**으로 로컬/원격에서 터미널 명령을 실행할 가능성이 높으며, 구현에 따라 사실상 “임의 셸 명령 실행”을 제공한다. 그 극단이 **persistent-shell-mcp**로, 설치 섹션에 “AI assistants가 임의 셸 명령을 실행할 수 있으니 격리된 테스트 환경에서만 사용, 민감 데이터/프로덕션 금지”를 강하게 경고한다. citeturn22view3 또한 **jonrad/tmux-mcp**는 POC로서 “임의 tmux 명령 실행”과 pane 읽기/키 전송 가능성을 경고하며 프로덕션 사용 금지를 명시한다. citeturn11view0turn13view0

운영 안전장치로는 세 가지 패턴이 확인된다.  
첫째, 파괴적 작업의 명시적 승인. **mcp-tmux**는 kill 계열 도구에 `confirm=true`를 요구한다고 README에서 강조한다. citeturn19view0  
둘째, **격리된 tmux 소켓**(별도 tmux 서버) 운용. **tmux-mcp-rs**는 `--socket`/`TMUX_MCP_SOCKET`로 특정 소켓을 지정하고, “에이전트 전용 tmux 서버” 예시를 제공한다. citeturn42view3turn42view1 Pi Agent tmux Skill 역시 `/tmp/pi-tmux-sockets/pi.sock`를 “개인 tmux와 충돌 방지” 목적으로 고정한다. citeturn29search0  
셋째, 관측성과 레이스 컨디션 완화. **mcp-tmux**는 `tmux_state` 스냅샷과 tail/task, 로그/감사 로깅을 제공하고, **tmux-mcp-rs**는 “ID-first targeting” 및 “연속 출력 캡처/인터럽트(send-cancel/send-eof)” 같은 워크플로 테스트를 문서에 포함해(도구 조합을 명시) 경합·혼선을 줄이려는 설계를 드러낸다. citeturn19view0turn42view2

## 추천 및 선택 가이드

**가장 추천: “운영형 세션 관리 + 다중 에이전트 워크스테이션”이 목적이면 Agent Deck**이 우선순위가 높다. (a) 별점/릴리즈 규모가 압도적이고, (b) 설치/업데이트 루트가 다중이며, (c) tmux 세션을 자체 프리픽스로 관리해 기존 환경을 오염시키지 않는다고 명시하고, (d) 실제 tmux 장애 케이스(기본 소켓 stale) 자동 복구 PR이 공개되어 “현장에서 부딪히는 문제”가 개발 이력에 남아 있다. citeturn35view0turn35view3turn35view4turn39view0

**에이전트가 “tmux를 도구로 직접 조종(세션/윈도우/팬 단위)”해야 한다면, MCP 서버 계열이 정공법**이다. 이때 선택은 “원격/안전” vs “tmux 기능 폭”으로 갈린다.  
remote-first·안전장치(`confirm=true`, 로그/감사)·상태 스냅샷 중심이면 **mcp-tmux(k8ika0s/mcp-tmux)**가 개념적으로 가장 뚜렷하다. citeturn19view0turn18view0  
tmux 조작 기능 폭(버퍼 탐색, pane 재배치, zoom/resize 등)과 격리 소켓 운용 패턴이 중요하면 **tmux-mcp-rs(bnomei/tmux-mcp)**가 강하다. citeturn42view2turn42view3turn6view0  
간결한 Claude Desktop 구성과 전형적 tmux 조작 세트가 목적이면 **nickgnd/tmux-mcp**가 빠른 선택이다(이슈에서도 기능 확장 요구가 관찰됨). citeturn7view5turn10view0turn8view0

**“특정 에이전트 런타임에 Skill로 붙여 쓰고 싶다”면** Pi Agent tmux Skill(Dwsy/agent)이나 agent-manager-skill(fractalmind-ai/agent-manager-skill)이 적합하다. 전자는 tmux 제어를 “세션 메타+전용 소켓+CLI/TUI+TS API”로 패키징했고, 후자는 “여러 에이전트를 tmux에 띄우고 cron으로 생명주기를 운영”하는 데 집중한다. citeturn29search0turn31view6turn31view4

마지막으로, 아래는 “실사용/버그 신호”가 드러난 대표 이슈·PR 링크다(요구사항 충족을 위해 GitHub URL을 직접 표기).  
- Agent Deck: stale tmux socket 자동 복구 PR #282 — https://github.com/asheshgoplani/agent-deck/pull/282 citeturn39view0  
- nickgnd/tmux-mcp: 기능 요청 이슈 #23 — https://github.com/nickgnd/tmux-mcp/issues/23 citeturn10view0  
- nickgnd/tmux-mcp: 배포/리스트 관련 이슈 #2 — https://github.com/nickgnd/tmux-mcp/issues/2 citeturn10view1  
- agent-manager-skill: 운영 중 heartbeat starvation 이슈 #111 — https://github.com/fractalmind-ai/agent-manager-skill/issues/111 citeturn34view0