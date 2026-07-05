# Skill Discovery Guide

이 저장소와 이 PC의 여러 위치에 흩어진 **agent skill**을 일관되게 찾기 위한 규칙과
도구입니다. Claude Code, Codex CLI, Gemini CLI가 모두 같은 규칙으로 skill을 찾도록
합니다.

## 1. skill이란

`SKILL.md`(YAML frontmatter의 `name` + `description`)를 루트에 가진 디렉토리 하나가
하나의 skill입니다. 하위에 `scripts/`, `references/`, `evals/`, `knowledge_bases/`
등을 둘 수 있습니다.

## 2. 발견 루트 (우선순위 순)

resolver는 아래 루트를 **위에서 아래로** 스캔하고, 같은 skill 이름이 여러 곳에
있으면 **먼저 나온 것(높은 우선순위)** 을 채택합니다.

| # | 루트 | 성격 |
|---|------|------|
| 1 | `$SKILLS_ROOT` (설정 시) | 명시적 오버라이드 |
| 2 | `<repo>/skills` | 이 저장소의 1차 skill (Skills-Create-Project 포함) |
| 3 | `<repo>/skills/external/<source>/` | 다른 프로젝트/환경에서 가져온 skill 미러 |
| 4 | `~/.claude/skills` | Claude Code 사용자 전역 skill |
| 5 | `~/.codex/skills` | Codex CLI skill (다수가 2·3의 심링크) |
| 6 | `~/skills` | 홈 공용 skill |
| 7 | `/Users/jaehyuntak/control` | control-plane 패턴/운영 자산 (§4) |
| 8 | `/Users/jaehyuntak/agent` | agent 작업공간 skill (§4) |
| 9 | `<project>/skills`, `<project>/.claude/skills`, `<project>/control` | 프로젝트별 skill·control-plane (§4) |

**알려진 프로젝트 root** (`$SKILL_PROJECTS_BASE` = `~/Desktop/Project_____현재_진행중인` 아래, `KNOWN_PROJECTS`로 관리):

- `my-image-parser/` — `skills/`(정본은 [my-image-parser repo](https://github.com/goodand/my-image-parser)) + `control/`
- `narrative-ai/` — `.claude/skills/` + `control/`
- `vscode-markdown-review-surface/` — `skills/` + `control/`
- `my-second-identity/` — `skills/` (repair-rag-artifact-contract, trace-claude-session-memory 등)

새 프로젝트를 추가하려면 `resolve_skill.py`의 `KNOWN_PROJECTS`에 이름만 넣으면 된다
(`SKILL_PROJECTS_BASE`가 다른 경우 환경변수로 베이스를 지정).

`external/`의 소스 버킷:

- `external/image-parser/` — `my-image-parser` 프로젝트 skill (정본은 그 repo)
- `external/narrative-ai/` — `narrative-ai` 프로젝트 skill (iOS/Xcode/merge-audit 등)
- `external/codex/` — `~/.codex/skills`의 실체 skill (m5-ssh-codex-operator 등)
- `external/home/` — `~/.claude/skills`·`~/skills`의 공용 skill

> `external/`는 **미러**입니다. 각 skill의 원 소유 repo가 정본이며, 이 미러는
> 배포·검색·오프라인 참조용입니다. `.env` 등 시크릿은 미러에서 제외됩니다.
>
> **정본 우선순위**: `claude-gemini-communicator`(이 repo)가 가장 최신·일관된
> 메커니즘으로 제작한 정본입니다. external 미러가 repo 정본과 이름이 겹치면
> **repo 정본이 우선**하며, 정본보다 오래된 external 스냅샷은
> `external/_stale/`로 격리합니다(resolver 발견 대상에서 제외 — `external/_stale/README.md` 참조).

## 3. resolver 사용법

```bash
# 모든 루트에서 skill 인벤토리 (이름·경로·소스·중복)
python3 skills/resolve_skill.py list

# 특정 skill의 실제 경로 찾기 (우선순위 승자)
python3 skills/resolve_skill.py find m5-ssh-codex-operator

# 이름으로 SKILL.md 경로만 출력 (스크립트 연동용)
python3 skills/resolve_skill.py path taskmaster

# 이름 중복(같은 skill이 여러 루트에 존재) 진단
python3 skills/resolve_skill.py conflicts

# JSON 출력 (에이전트 소비용)
python3 skills/resolve_skill.py list --json
```

환경변수:

- `SKILLS_ROOT` — 최우선 루트를 하나 추가 (콜론으로 여러 개)
- `SKILL_DISCOVERY_EXTRA` — 추가 루트를 콜론 구분으로 append

## 4. control / agent 디렉토리 패턴

### 설계 원칙: 큰 control(안) + 실행은 밖(외측)

`/control`은 이 아키텍처에서 **가장 크고 상위인 거버넌스 계층**입니다 — "무엇을·왜·
언제" 를 지배하는 의사결정·후보관리·기록의 두뇌. 그러나 **실제로 실행(execute)되는
능력(skill)은 의도적으로 control 바깥(외측)에 둡니다**: `repo/skills`(정본),
`~/.claude/skills`, `~/.codex/skills`, `/agent/skills`.

따라서 resolver 우선순위에서 **실행 정본은 `repo/skills`(#1)** 이고 control은
후순위입니다. 이는 "control이 크니까 먼저 실행된다"가 아니라 **control이 크게
감싸되 실행은 밖으로 위임한다** 는 설계의 직접적 결과입니다:

```
        ┌─────────────────  /control  (큰 거버넌스: 결정·후보·기록) ─────────────────┐
        │  project_agent_ops · project_domain · team · user_decisions              │
        │        │ 승격(skill_candidates → skill)                                   │
        └────────┼────────────────────────────────────────────────────────────────┘
                 ▼   실행은 외측(outer)으로 분리 · resolver #1 = repo/skills
        repo/skills · ~/.claude/skills · ~/.codex/skills · /agent/skills   ← 실제 execute
```

`/control`(그리고 프로젝트별 `<project>/control`)은 skill이 아니라 **control-plane
운영 자산**을 담는 규약입니다. resolver는 여기서 skill 디렉토리(`SKILL.md` 보유)만
골라냅니다(대개 없음 — 실행물은 외측에 있으므로). 관례 구조:

```
control/
├── patterns/                  # 재사용 패턴 카탈로그 (catalog/, *.md, catalog_lookup.py)
├── project_agent_ops/         # 에이전트 운영 자산
│   └── resources/skill_candidates/   # skill 승격 후보
├── project_domain/            # 도메인 지식
│   ├── archive/ registry/ resources/
├── team/                      # 팀/역할 정의
│   └── archive/ registry/ resources/
└── user_decisions/            # 사용자 결정 로그
    └── archive/ registry/ resources/
```

`archive / registry / resources` 3분할이 각 하위 도메인의 공통 형태입니다:
- `registry/` — 현재 유효한 SSOT 항목
- `resources/` — 작업 산출물·후보 (예: `skill_candidates/`)
- `archive/` — 폐기·과거 버전

`agent/`는 작업공간으로 `agent/skills/`(실 skill 또는 서브모듈)와
`agent/project_agent_ops`(→ `control/project_agent_ops` 심링크)를 둡니다.

에이전트가 "이 skill 어디 있어?"를 물으면: **먼저 `resolve_skill.py find <name>`**,
없으면 `control/*/resources/skill_candidates/`(아직 승격 안 된 후보)를 확인하세요.

## 5. 새 skill 추가 시

1. 원 소유 위치(프로젝트 repo 또는 `~/.claude/skills`)에 skill을 만든다.
2. 공유가 필요하면 `external/<source>/`에 미러(시크릿 제외)한다.
3. `resolve_skill.py list`로 이름 충돌이 없는지 확인한다.
