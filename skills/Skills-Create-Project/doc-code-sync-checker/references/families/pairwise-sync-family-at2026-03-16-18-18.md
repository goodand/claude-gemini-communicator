# Pairwise Sync Family

## Scope

- v0.1 범위는 `reference 문서 1개 + code script 1개` pairwise checker다.
- repo-wide crawler, 대규모 semantic diff engine, 자동 수정기는 비목표다.

## Workflow Family

1. `extract-doc`로 문서 규칙 추출
2. `extract-code`로 코드 규칙 추출
3. `compare`에서 normalize 이후 drift 분류
4. `report`에서 사람이 읽는 보고 생성

## Mapping

- script: `scripts/doc_code_sync.py`
- checklist anchor: workflow / scope / scaffold
- canonical KB: `doc-code-sync-canonical-design-at2026-03-16-18-18.md`
