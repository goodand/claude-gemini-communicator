# external/_stale — 구버전 스냅샷 (정본 아님)

여기 있는 skill들은 다른 프로젝트에서 미러했으나, **`claude-gemini-communicator`
의 정본(`repo/skills/` 최상위)이 더 최신·완전**한 것으로 확인되어 구버전으로
격리한 스냅샷입니다.

- **정본 위치**: `skills/<name>/` (communicator가 가장 일관된 메커니즘으로 제작한 최신본)
- **여기(_stale)**: 과거 narrative-ai 스냅샷. 내용 비교/이력 참조용으로만 보관.
- resolver(`resolve_skill.py`)는 `_stale`을 우선순위에서 배제하지 않지만
  `repo/skills`가 항상 우선하므로 실제 채택되지 않습니다. 참조 시 정본을 쓰세요.

## 격리된 항목 (narrative-ai, 2026-07-06)

| skill | 정본 파일수 | _stale 파일수 |
|-------|-----------|-------------|
| class-hierarchy-classifier | 6 | 5 |
| codebase-architecture-mapper | 18 | 13 |
| depsolve-analyzer | 30 | 19 |
| graph-structure-classifier | 6 | 6 |
| runtime-flow-tracer-web-preview | 12 | 12 |
| skill-path-resolver | 9 | 7 |
| super-skill-creator | 24 | 16 |
| troubleshooting-cot-2 | 15 | 14 |

각 항목의 정본은 `skills/<name>/`에 있습니다.
