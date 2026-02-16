# 아키텍처 분석 — 의존성 맵 + 주요 Hub 식별

> 생성: CTO(Claude) | 분석 기반: Gemini(CSO) 코드베이스 분석 + Claude 정밀 검증
> 날짜: 2026-02-16

---

## 1. 모듈 의존성 그래프

```mermaid
flowchart TB
    subgraph HOOKS["Hook Scripts"]
        HAT[hook_auto_task.py]
        HS[hook_stop.py]
        HPT[hook_pre_tool.py]
    end

    subgraph CORE["Core - scripts/"]
        A2A["a2a_bridge.py\n836줄 - MEGA HUB"]
        AR[async_runner.py]
        CLI["cli.py\n953줄"]
        CJP[codex_json_parser.py]
        GJP[gemini_json_parser.py]
        TP[transcript_parser.py]
    end

    subgraph S1["Skill 1: gemini-reviewer"]
        GR_C[_common.py]
        GR_E[evaluate.py]
        GR_N[codex_notify.py]
    end

    subgraph S2["Skill 2: agent-parser"]
        AP_C[_common.py]
        AP_P[parse.py]
        AP_CP[_codex_parser.py]
        AP_GP[_gemini_parser.py]
        AP_TP[_transcript_parser.py]
    end

    subgraph S3["Skill 3: cross-agent-bridge"]
        CB_C[_common.py]
        CB_CFG[_config.py]
        CB_D[_doctor.py]
        CB_A2A[_a2a_protocol.py]
        CB_GC[_gemini_client.py]
        CB_B[bridge.py]
    end

    HAT -->|"9 functions"| A2A
    HS -->|"11 functions"| A2A
    HPT -->|"load_config"| A2A
    AR -->|"call_gemini"| A2A
    CLI -->|"12 functions"| A2A
    CLI -->|"check_command"| HPT

    GR_E --> GR_C
    GR_N --> GR_C
    GR_N -.->|"dynamic import"| GR_E

    AP_P --> AP_C
    AP_P --> AP_CP
    AP_P --> AP_GP
    AP_P --> AP_TP

    CB_B --> CB_C
    CB_B --> CB_CFG
    CB_B --> CB_D
    CB_B --> CB_GC
    CB_D --> CB_CFG

    style A2A fill:#ff6b6b,stroke:#c0392b,color:#fff,stroke-width:3px
    style CLI fill:#ff9f43,stroke:#e67e22,color:#fff
```

### Hub 랭킹

| 순위 | 모듈 | 의존자 수 | 줄 수 | 역할 |
|---|---|---|---|---|
| **1** | `a2a_bridge.py` | **5개** (3 hooks + cli + async_runner) | 836 | Gemini SDK/CLI, 쿨다운, A2A, 에러감지 — 모든 것 |
| **2** | `cli.py` | 0 (최종 소비자) | 953 | doctor, status, test 등 관리 도구 |
| **3** | `_config.py` (bridge) | 2개 (bridge, _doctor) | 116 | 설정 로딩/검증 |

---

## 2. 코드 중복 분석

```mermaid
flowchart LR
    subgraph DUP1["save_feedback — 7곳 중복"]
        SF1["a2a_bridge.py:107"]
        SF2["gemini-reviewer/_common.py"]
        SF3["agent-parser/_common.py"]
        SF4["cross-agent-bridge/_common.py"]
        SF5["codex_json_parser.py"]
        SF6["gemini_json_parser.py"]
        SF7["transcript_parser.py"]
    end

    subgraph DUP2["파서 100% 중복"]
        P1["scripts/codex_json_parser.py"] ---|"동일"| P2["agent-parser/_codex_parser.py"]
        P3["scripts/gemini_json_parser.py"] ---|"동일"| P4["agent-parser/_gemini_parser.py"]
        P5["scripts/transcript_parser.py"] ---|"동일"| P6["agent-parser/_transcript_parser.py"]
    end

    subgraph DUP3["Gemini 호출 로직 3중복"]
        G1["a2a_bridge.py:_call_gemini_sdk"]
        G2["gemini-reviewer/evaluate.py:call_gemini_sdk"]
        G3["cross-agent-bridge/_gemini_client.py:_call_sdk"]
    end

    style DUP1 fill:#ffe0e0,stroke:#c0392b
    style DUP2 fill:#fff3e0,stroke:#e67e22
    style DUP3 fill:#e0e0ff,stroke:#2980b9
```

### 중복 상세

| 중복 항목 | 발생 횟수 | 심각도 |
|---|---|---|
| `save_feedback()` | **7곳** | Critical |
| 파서 코드 (codex/gemini/claude) | **2벌** (scripts/ vs skills/) | High |
| Gemini SDK 호출 로직 | **3곳** | High |
| `read_input()` / `load_env()` | **4곳** | Medium |
| `load_config()` | **2곳** (a2a_bridge vs _config.py) | Medium |

---

## 3. 데이터 흐름도

```mermaid
flowchart LR
    subgraph INPUT["입력"]
        STDIN["stdin\n(Hook JSON)"]
        FILE["파일\n(.md/.py)"]
        TRANSCRIPT["transcript\n(JSONL)"]
    end

    subgraph HOOKS["Hook Layer"]
        H1["PostToolUse\nhook_auto_task.py"]
        H2["Stop\nhook_stop.py"]
        H3["PreToolUse\nhook_pre_tool.py"]
    end

    subgraph ENGINE["Engine Layer"]
        A2A_CORE["a2a_bridge.py"]
        SDK["Gemini SDK\ngoogle-genai"]
        CLI_G["Gemini CLI\nsubprocess"]
    end

    subgraph OUTPUT["출력"]
        STDOUT["stdout\n(Claude 주입)"]
        FEEDBACK["gemini_feedback.md\n(append-only)"]
        STATE[".cooldown_state.json\n.error_history.json"]
    end

    STDIN --> H1
    STDIN --> H2
    STDIN --> H3
    FILE --> H1
    TRANSCRIPT --> H2

    H1 --> A2A_CORE
    H2 --> A2A_CORE
    H3 -->|"차단/허용"| STDOUT

    A2A_CORE --> SDK
    A2A_CORE --> CLI_G
    SDK -->|"응답"| A2A_CORE
    CLI_G -->|"응답"| A2A_CORE

    A2A_CORE --> STDOUT
    A2A_CORE --> FEEDBACK
    A2A_CORE --> STATE
```

---

## 4. 핵심 문제점 (CTO 진단)

### Problem 1: God Object — `a2a_bridge.py`
- **836줄에 33개 함수** — 단일 책임 원칙 위반
- 쿨다운, 에러 감지, A2A 프로토콜, Gemini 호출, OAuth, 피드백 저장 — 모두 한 파일
- **5개 파일이 의존** → 변경 시 영향 범위 최대

### Problem 2: 이중 구조 (scripts/ vs skills/)
- Phase 6에서 skills/를 만들었지만 **scripts/를 정리하지 않음**
- hooks가 여전히 `a2a_bridge.py`에 의존 → skills/ 코드와 단절
- **결과**: 동일 로직이 2~3곳에 존재, 어디가 정본인지 불명확

### Problem 3: 역할 경계 불명확
- `cli.py`가 953줄 — doctor/status/stats/search/test/clear/codex 모든 것
- `bridge.py`도 doctor/parse 기능 보유 → cli.py와 기능 중복
- Hook scripts는 진입점인데 로직도 포함

### Problem 4: 설정 분산
- `config.json` → `a2a_bridge.load_config()` + `_config.py.load_config()` 2곳에서 로딩
- 환경변수 로딩도 `_load_env()` / `load_env()` 이름만 다르고 동일

---

## 5. 주요 Hub 시각화

```mermaid
graph TD
    A2A["a2a_bridge.py\n33 functions\n836 lines"]

    A2A --- COOL["쿨다운 관리\ncheck_cooldown\nload/save_cooldown_state"]
    A2A --- GEMINI["Gemini 호출\ncall_gemini\n_call_gemini_sdk\n_call_gemini_cli\n_call_gemini_with_api_key\n_call_gemini_with_oauth"]
    A2A --- A2APROT["A2A 프로토콜\nbuild_a2a_request\nparse_a2a_response\na2a_response_to_markdown\nbuild_a2a_evaluation_prompt"]
    A2A --- ERROR["에러 감지\nscan_transcript_for_errors\ncheck_error_and_analyze\nnormalize_error_text\nhash_error\nclassify_error_severity"]
    A2A --- UTIL["유틸리티\nload_config\nsave_feedback\nformat_hook_output\n_load_env\n_read_file_content"]
    A2A --- ASYNC["비동기\ncall_gemini_async"]

    style A2A fill:#ff6b6b,stroke:#c0392b,color:#fff,stroke-width:3px
    style COOL fill:#74b9ff,stroke:#0984e3
    style GEMINI fill:#a29bfe,stroke:#6c5ce7
    style A2APROT fill:#55efc4,stroke:#00b894
    style ERROR fill:#ffeaa7,stroke:#fdcb6e
    style UTIL fill:#dfe6e9,stroke:#b2bec3
    style ASYNC fill:#fab1a0,stroke:#e17055
```

이것이 분해(decompose)해야 할 6개 도메인입니다.
