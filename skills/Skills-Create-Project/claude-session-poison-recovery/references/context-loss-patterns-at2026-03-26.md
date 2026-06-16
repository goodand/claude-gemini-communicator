# Context Loss Patterns

Compaction / resume 후 Claude가 plan context를 잃는 패턴과 대응 전략.

## Pattern 1: Plan Amnesia (계획 망각)

- **증상**: Claude가 합의된 다음 단계 대신 엉뚱한 작업을 제안
- **실제 사례**: "너가 지금 계획을 잃은 것 같은데" — 3-step 계획(체크리스트→Env Gate→Step 0)을 잊고 코드 구현을 시도
- **원인**: compaction summary가 plan state를 누락. 특히 multi-step 계획의 "현재 어디까지 했는지"가 빠짐
- **복원**: HANDOFF 문서 → active plan/checklist 순으로 읽기
- **예방**: 계획 확정 시 외부 파일(HANDOFF, plan 문서)에 "현재 단계" 마커를 명시적으로 기록

## Pattern 2: Role Boundary Confusion (역할 경계 혼동)

- **증상**: CTO가 코드를 직접 구현하려 하거나, Codex 세션을 Claude subagent로 착각
- **실제 사례**: CEO가 "너는 CTO고 코드의 구현은 Codex가 진행해야 한다" 정정
- **원인**: compaction이 팀 구조/역할 분담 정보를 요약에서 삭제
- **복원**: MEMORY.md의 팀 구조 섹션 재확인
- **예방**: MEMORY.md에 역할 표를 유지하고, HANDOFF에 "이 세션의 역할 분담" 명시

## Pattern 3: Metric Naming Regression (지표명 회귀)

- **증상**: 정식 지표명(HitRate@10) 대신 비공식 명칭(DocHit@10) 사용
- **실제 사례**: post-impl 체크리스트에서 DocHit@10 사용 → CEO가 HitRate@10으로 수정
- **원인**: metric_formula_contract.md의 naming rule이 compaction summary에 포함되지 않음
- **복원**: metric_formula_contract.md §7 naming rules 재참조
- **예방**: contract 문서 경로를 HANDOFF에 명시

## Pattern 4: Document Drift Blindness (문서 drift 미감지)

- **증상**: 하나의 문서를 수정했지만 연관 문서에 전파하지 않음
- **실제 사례**: plan에서 `text` 필드 추가 후 pre-impl 체크리스트에 반영 안 됨 (3회 반복)
- **원인**: compaction이 "어떤 문서들이 서로 연결되어 있는지" 관계 정보를 유실
- **복원**: plan/checklist/spec 간 SoT reference 맵을 재구성
- **예방**: 문서 수정 시 영향받는 문서 목록을 먼저 나열 → 전부 갱신 후 완료 선언

## Pattern 5: Environment Fact Misidentification (환경 사실 오인)

- **증상**: system python 버전을 workspace python으로 착각
- **실제 사례**: 3.13.6(system)을 workspace로 보고 → 실제는 3.11.14(.venv)
- **원인**: compaction summary에 환경 정보가 부정확하게 요약됨
- **복원**: 환경 관련은 반드시 실행 결과(`python --version`, `uv --version`) 기반 판단
- **예방**: SPEC 문서에 pinned version 기록, pyproject.toml에 requires-python 명시

## Restoration Source Priority

| 우선순위 | 소스 | 신뢰도 | 커버 범위 |
|---------|------|--------|----------|
| 1 | git log / diff | 최고 (ground truth) | 코드 변경 이력 |
| 2 | HANDOFF 문서 | 높음 (세션 단위 스냅샷) | plan state, 결정사항, 다음 단계 |
| 3 | MEMORY.md | 중간 (프로젝트 수준) | 팀 구조, phase, 장기 결정 |
| 4 | Active plans/checklists | 중간 (최신 수정일 기준) | 현재 작업 맥락 |
| 5 | Session JSONL transcript | 낮음 (비용 높음) | compaction summary, 전체 대화 |

## Anti-patterns

- compaction 후 "기억나는 대로" 진행 → **항상 외부 소스로 검증**
- HANDOFF 없이 resume → **blind resume는 Pattern 1-3을 거의 확실히 유발**
- 환경 정보를 context에서 추론 → **반드시 실행 결과 기반**
- 단일 문서만 수정하고 완료 선언 → **영향 문서 전파 체크 필수**
