# Smoke Archive Layout Rule

- scope: `workspace-artifact-production-process`에서 multi-file smoke/test 실행의 raw archive 경로와 최소 보관 파일 구성을 고정한다.
- purpose: human-readable smoke report, raw stdout/stderr capture, generated artifacts를 섞지 않고 per-run traceability를 유지한다.

## Canonical Layout

- archive root: `logs/smoke/<command>/<timestamp>/`
- case leaf: `<archive-root>/<case>/`
- `<case>`는 `input_mode`, `fixture_name`, `variant_name` 같은 실행 구분자를 쓴다.
- 하나의 smoke report에서 여러 실행을 돌리면 case leaf를 나누고, report는 공통 `archive_dir`를 링크한다.

## Canonical Files

For JSON-summary CLI smokes:
- `stdout.json` — stdout으로 나온 structured summary
- `stderr.log` — raw stderr capture
- `warnings.log` — warning-only view

Rules:
- warning이 없더라도 `warnings.log`는 빈 파일로 생성해 clean path를 명시한다.
- command가 자체 summary file을 만들면 archive leaf에 함께 복사해도 된다.
- generated artifacts(`graph.dot`, `nodes.csv`, `rels.csv`, `graph.cypher` 등)는 필요 시 archive leaf로 복사하거나 smoke report에서 원본 경로를 링크한다.

## Boundary

- `tmp/`는 작업/실험 중간 산출물 경로다. 장기 보관용 raw archive root로 쓰지 않는다.
- `references/*-smoke-*.json` 또는 smoke report MD는 사람 읽기용/entry report 계층이다.
- `logs/smoke/...`는 per-run raw evidence archive 계층이다.
- `references/troubleshooting.md`는 lesson/case 설명 계층이며 raw stdout/stderr 저장소가 아니다.
- `references/fixtures/`는 sample input/output bundle 계층이며 per-run smoke archive 경로가 아니다.

## Smoke Report Requirements

- smoke report는 `archive_dir`를 명시한다.
- 각 실행 case마다 대표 `stdout.json`, `stderr.log`, `warnings.log` 링크를 남긴다.
- clean path면 `warnings.log`가 비어 있어야 한다는 해석을 같이 적는다.
- fallback path면 warning interpretation과 canonical replacement 여부를 같이 적는다.

## Escalation

- 같은 archive layout이 반복되면 smoke template이나 script helper로 승격한다.
- 공통 warning 패턴이 반복되면 `troubleshooting.md` 또는 validator/code rule로 승격한다.
