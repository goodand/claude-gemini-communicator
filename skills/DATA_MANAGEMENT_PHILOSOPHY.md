# Data Management Philosophy — 파일시스템이 증언하는 관리 철학

이 문서는 이 PC의 실제 디렉토리·심링크 구조(2026-07-06 전수 스캔)에서 **관찰된**
자료 관리 철학을 기록합니다. skill 발견([SKILL_DISCOVERY.md](SKILL_DISCOVERY.md))과
분류 체계([SKILL_TAXONOMY.md](SKILL_TAXONOMY.md))가 왜 그런 모양인지의 근거 층입니다.

## 1. Desktop 최상위 = PARA + 시간축 하이브리드

```
Desktop/
├── Project_____현재_진행중인/      P  활성 프로젝트 (모든 git repo·skill 정본의 집)
├── Area/                          A  지속 관심영역 (취미·건강·인간관계·AI·Obsidian·정체성/행정)
├── Archieve_____성취한 것들_관심이_없어진_것들/   Ar  졸업식장 (완료·관심소멸)
├── Date/                          T  시간축 — 일일/사건 로그 255+ (`<주제>-at2026-MM-DD.md`)
├── IMAGE/ · GRAPH/ · SVG/ · TABLE/ · Font/       R  자산을 '형식(type)'으로 분류
└── Date_symbolic → Date               시간축의 별칭 프로젝션
```

PARA(Projects/Areas/Resources/Archives)를 따르되 두 가지를 변형:
- **Resources를 주제가 아니라 자산 형식으로** 분해 (IMAGE/GRAPH/SVG/TABLE/Font)
- PARA에 없는 **시간축(Date)을 1급 시민으로** 추가 — 생애주기 축과 직교

## 2. 링크 지도 (방향이 곧 철학)

### Desktop 내부 — Date가 허브
```
Date_symbolic ──────────┐
Area/Date ──────────────┼──→ Date      # 하나의 시간축을 여러 컨텍스트에 프로젝션
개인_작업_개인_목표/Date ──┘
Area/Obsidian/Downloads ──→ ~/Downloads          # 수집 인입구
개인_작업_개인_목표/Image_Obsidian_link ──→ Area/Obsidian/.../Image_Obsidian   # 지식 이미지 브릿지
```

### 외부 → Desktop — 전부 단방향 유입 (35+ 심링크)
```
~/.codex/skills/*            ──→ Desktop/Project…/{claude-gemini-communicator,
                                                   my-image-parser, narrative-ai}
~/control/patterns/{catalog, catalog_lookup.py, *-patterns.md}
                             ──→ Desktop/Project…/communicator/…/skill-creation-process/
~/agent/project_agent_ops    ──→ ~/control/project_agent_ops (→ 내용 정본은 Desktop repo)
```

**역방향(Desktop → 외부 config) 링크는 없다.** 모든 화살표가 Desktop의 git-tracked
repo로 수렴한다.

## 3. 관찰된 원칙

1. **정본은 한 곳, 나머지는 전부 뷰(view).**
   복사 대신 심링크. 실행 계층(`~/.codex/skills`)도, 거버넌스 계층(`~/control`)조차
   정본을 소유하지 않고 참조만 한다. → resolver가 `repo/skills`를 우선순위 #1로 두는
   근거이자, "control은 크게 감싸되 실행은 외측에 위임"(SKILL_DISCOVERY §4)의
   파일시스템 버전.

2. **분류축의 직교 분리.**
   생애주기(P/A/Ar) × 시간(Date) × 형식(IMAGE/GRAPH/SVG/TABLE)을 한 폴더에 섞지 않고
   별도 축으로 둔다. 하나의 자료는 축마다 다른 좌표를 가질 뿐, 축들이 충돌하지 않는다.
   (ConceptGate의 "서로 다른 분류축을 같은 is-a 계층에 넣지 말라"와 동일한 원칙.)

3. **이름 = 계약.**
   메타데이터를 별도 DB가 아니라 이름에 인코딩한다:
   `<폴더>_____<정의>` (예: `Project_____현재_진행중인`),
   `<주제>-at2026-MM-DD.md` 타임스탬프, `SKILL-*`/`TASK-*` typed key.

4. **프로젝션으로 컨텍스트를 잇는다.**
   같은 실체(Date)를 필요한 곳마다 심링크로 투영해, 컨텍스트별 진입점을 주되
   중복 저장을 만들지 않는다.

## 4. 운영 함의 (도구가 지켜야 할 것)

- 어떤 도구도 뷰 위치(~/.codex, ~/control, /agent)에 정본을 새로 만들지 말 것 —
  정본은 Desktop의 repo에 만들고 뷰로 노출한다.
- 폴더 개명은 링크를 깨뜨린다 (실례: `Area_____지속적으로…` → `Area` 개명으로
  `Image_Obsidian_link`가 끊겼다가 2026-07-06 복구). 개명 시 인바운드 링크 스캔이
  필요하다: `find ~/Desktop -maxdepth 3 -type l ! -exec test -e {} \; -print`.
- macOS 한글 경로는 NFD로 분해될 수 있다 — 경로 비교는 NFC 정규화 후에
  (`resolve_skill.py`, `catalog_resolver_audit.py`가 이미 처리).
