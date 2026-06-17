# Template Identity Rule

- scope: template / reference 파일의 신분(canonical, local support, legacy alias, runtime evidence)을 명확히 구분하는 규칙
- source: 2026-03-26~27 세션에서 local support가 canonical처럼 읽혀서 규범이 분산되는 문제

## 문제 정의

template이나 보조 파일이 실제 canonical처럼 읽히면:
1. 규범 정보가 canonical에도 있고 local support에도 있어서 어디가 source of truth인지 모호
2. legacy alias를 현행 파일로 착각하고 거기에 새 필드를 추가
3. runtime evidence를 template로 착각하고 규범으로 참조

## 4가지 신분

### 1. Canonical Template
- machine registry의 projection
- `$schema_notes`에 canonical 규범 정보(enum, field set, transition)를 반영
- **규범 정보의 owner가 아니라 projection** — 독자적으로 enum/field를 정의하지 않음
- 예: `task_packet_standard_template.json`, `dispatch_state_extended_template.json`

### 2. Local Support Template
- canonical template보다 풍부한 예시, 설명, 주석 포함
- **규범을 local support에만 두면 안 됨** → canonical 또는 registry로 승격
- 학습 보조, 빠른 시작 가이드 역할
- 예: `task_packet_template.json`

### 3. Legacy Alias
- 이전 이름/구조에서 새 canonical을 가리키는 thin stub
- 본문: `_comment: "LEGACY ALIAS"` + `canonical_files` 포인터만
- 새 코드에서 import/참조 금지
- 예: `task_state_extended_template.json` → `dispatch_state_extended_template.json`

### 4. Runtime Evidence
- 실행 결과, smoke output, audit report
- `runs/`, `logs/`, `reports/` 디렉토리에 격리
- template 디렉토리에 섞지 않는다

## Manifest Contract

신분 판별의 유일한 1순위 소스. 파일 내부 메타는 2순위 fallback.

### Canonical manifest
- **파일명**: `template_manifest.json` (유일한 manifest — 복수 기준 금지)
- **위치**: template 디렉토리 루트 (예: `my-second-identity/template/template_manifest.json`)
- **필수 필드**:

| 필드 | 타입 | 설명 |
|------|------|------|
| `manifest_version` | string | 현재 `"0.1"` |
| `canonical` | string[] | canonical template 파일명 목록 |
| `local_support` | string[] | local support template 파일명 목록 |
| `legacy_alias` | string[] | legacy alias 파일명 목록 |

```json
{
  "manifest_version": "0.1",
  "canonical": ["task_packet_standard_template.json", "..."],
  "local_support": ["task_packet_template.json"],
  "legacy_alias": ["task_state_standard_template.json", "..."]
}
```

### Manifest 관리 규칙

- **owner**: template 디렉토리를 소유하는 프로젝트/skill. 현재는 `my-second-identity`
- **갱신 시점**: template 파일 추가/삭제/이름변경 시 반드시 manifest를 같이 갱신
- **갱신 순서**: manifest(owner) 먼저 → template 파일 추가/삭제 → consumer(task_template_reference.md 등 mirror) 갱신
- **검증**: manifest의 배열에 있는 파일이 실제 존재하는지, 실제 파일이 manifest에 등록돼 있는지 양방향 확인
- **금지**: manifest 없이 template 파일을 추가하는 것. 미등록 파일은 "분류 오류"로 판정

### Mirror 문서

- `task_template_reference.md`는 이 manifest의 human-readable mirror (owner가 아님)
- mirror는 manifest 변경 후에만 갱신. mirror를 먼저 수정하면 owner 개념이 약해진다

## 판별 규칙

1순위: `template_manifest.json` → 2순위: 파일 내부 메타

```
template_manifest.json의 canonical 배열에 있음?
  → Yes: canonical template
template_manifest.json의 legacy_alias 배열에 있음?
  → Yes: legacy alias
template_manifest.json의 local_support 배열에 있음?
  → Yes: local support
runs/, logs/, reports/ 디렉토리에 있음?
  → Yes: runtime evidence
위 모두 아님?
  → 분류 오류 — manifest에 먼저 등록할 것
```

**핵심**: `template_manifest.json`이 유일한 판별 소스. 파일 내부 `$schema_notes`는 사람이 읽는 보조 정보일 뿐 판별 기준이 아니다.

## 신분별 규칙

| 신분 | 규범 정의 | 수정 가능 | sync audit 대상 |
|------|-----------|-----------|----------------|
| canonical | registry 반영만 (재정의 금지) | registry 변경 후에만 | strict |
| local support | 예시만 (규범 금지) | 자유 | warning |
| legacy alias | 불가 | pointer만 갱신 | skip |
| runtime evidence | 불가 | 자동 생성 | skip |

## 실전 교훈

1. `task_packet_template.json`(local support)에 `forbidden_runtime_fields`, `enums`가 있었는데 canonical extended에는 없음 → 규범이 local support에만 존재하는 문제
2. `task_state_template.json`이 phase model + metric registry + dispatch 필드를 모두 소유 → 정체성 혼란 → legacy alias로 전환
3. `task_state_extended_template.json`이 legacy alias인데 한동안 현행 파일처럼 사용됨
