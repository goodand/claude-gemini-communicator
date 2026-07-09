# Rule Taxonomy — 검증 규칙 분류 체계

validate 함수에서 발견되는 검증 규칙을 7종으로 분류하고, 각 종류별 edge case 생성 전략을 정의한다.

## 1. required_field — 필수 필드 존재 여부

**탐지 패턴**: `REQUIRED_FIELDS - set(data.keys())`, `if "field" not in data`

**edge case 전략**:
| 케이스 | 입력 | 기대 |
|--------|------|------|
| 필수 필드 전부 누락 | `{}` | FAIL |
| 필수 필드 하나만 누락 | 각 필드를 하나씩 제거 | FAIL |
| 필수 필드 전부 존재 | 정상 입력 | PASS |
| 필수 필드 값이 null | `{"field": null}` | FAIL or WARN |
| 필수 필드 값이 빈 문자열 | `{"field": ""}` | FAIL or WARN |

---

## 2. forbidden_field — 금지 필드 부재 여부

**탐지 패턴**: `FORBIDDEN_FIELDS`, `if f in data: errors.append`

**edge case 전략**:
| 케이스 | 입력 | 기대 |
|--------|------|------|
| 금지 필드 하나 포함 | 정상 + `{"status": "running"}` | FAIL |
| 금지 필드 전부 포함 | 정상 + 모든 금지 필드 | FAIL |
| 금지 필드 이름 유사 | `{"status_hint": "ok"}` | PASS (선택 필드) |

---

## 3. string_length — 문자열 길이 제약

**탐지 패턴**: `len(str(data["field"])) < N`, `len(...strip()) < N`

**edge case 전략**:
| 케이스 | 입력 | 기대 |
|--------|------|------|
| 경계값 미달 (N-1자) | `"a" * (N-1)` | FAIL |
| 정확히 경계값 (N자) | `"a" * N` | PASS |
| 경계값 초과 | `"a" * (N+1)` | PASS |
| 공백만 | `"   "` | FAIL (strip 후 0자) |
| 빈 문자열 | `""` | FAIL |
| 숫자 타입 | `12345` | PASS or FAIL (str() 변환) |

---

## 4. enum_value — 열거형 값 제약

**탐지 패턴**: `if data["field"] not in VALID_SET`, `VALID_STATUSES`, `VALID_PRIORITIES`

**edge case 전략**:
| 케이스 | 입력 | 기대 |
|--------|------|------|
| 유효 값 각각 | 모든 VALID 값 순회 | PASS |
| 대소문자 변형 | `"Running"` vs `"running"` | FAIL (case-sensitive) |
| 빈 문자열 | `""` | FAIL |
| null | `null` | FAIL |
| 유사하지만 다른 값 | `"completed"` vs `"complete"` | FAIL |

---

## 5. path_safety — 경로 안전성 제약

**탐지 패턴**: `".." in`, `startswith("/")`, `islink()`, `_normalize_path`

**edge case 전략**:
| 케이스 | 입력 | 기대 |
|--------|------|------|
| path traversal | `"../secret"` | FAIL |
| 절대경로 | `"/etc/passwd"` | FAIL |
| symlink (실제 fixture) | run 단계에서 생성한 symlink 상대경로 | FAIL |
| 정상 상대경로 | `"src/auth/"` | PASS |
| trailing slash 유무 | `"src/auth"` vs `"src/auth/"` | 둘 다 PASS |
| 빈 문자열 | `""` | FAIL |
| 빈 배열 | `[]` | FAIL |
| 중복 경로 | `["src/", "src/"]` | FAIL or WARN |
| 한국어 경로 | `"소스/"` | PASS (정책에 따라) |
| 매우 긴 경로 | `"a/" * 100` | PASS (길이 제한 없으면) |

---

## 6. list_constraint — 배열 제약

**탐지 패턴**: `not isinstance(x, list)`, `len(x) == 0`, `if not x:`

**edge case 전략**:
| 케이스 | 입력 | 기대 |
|--------|------|------|
| 빈 배열 | `[]` | FAIL (최소 1개 필요) |
| 문자열 (타입 오류) | `"not_a_list"` | FAIL |
| 숫자 (타입 오류) | `123` | FAIL |
| null | `null` | FAIL |
| 단일 항목 | `["one"]` | PASS |
| 항목 내부 타입 오류 | `[123, null, ""]` | WARN or FAIL |

---

## 7. cross_field — 필드 간 관계 제약

**탐지 패턴**: `if "A" in data and "B" in data`, `subset`, `overlap`, `retry_count < max_retries`

**edge case 전략**:
| 케이스 | 입력 | 기대 |
|--------|------|------|
| locked ⊆ allowed 위반 | locked에 allowed에 없는 경로 | FAIL |
| allowed ∩ forbidden 겹침 | 같은 경로를 양쪽에 | FAIL |
| retry_count = max_retries | 경계값 | FAIL (초과) |
| retry_count = max_retries - 1 | 경계값 미만 | PASS |
| depends_on 존재하지 않는 ID | `["DISPATCH-9999"]` | WARN |

---

## 실전에서 발견된 버그와 해당 규칙 종류

| 버그 | 스킬 | 규칙 종류 | CASE |
|------|------|-----------|------|
| 빈 why 통과 | agent-task-packet | string_length | CASE-001 |
| `..` path traversal 통과 | codex-worktree-dispatch | path_safety | CASE-001 |
| symlink 미검출 | codex-worktree-dispatch | path_safety | CASE-003 |
| symlink placeholder 거짓 양성 | edge-case-generator | path_safety | CASE-005 |
| retry 초과 시 상태 오염 | codex-worktree-dispatch | cross_field | CASE-002 |
| JSON 입력 시 dict.strip() | workflow-bridge-eval | (타입 불일치) | CASE-001 |
| tmux 서버 없을 때 True | codex-tmux-orchestrator | (래퍼 반환값) | CASE-001 |
