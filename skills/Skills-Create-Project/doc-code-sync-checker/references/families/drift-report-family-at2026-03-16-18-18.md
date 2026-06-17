# Drift Report Family

## Output Contract

- `missing_in_code`
- `missing_in_doc`
- `mismatch`

## Report Style

- compare 결과는 JSON artifact로 남긴다
- report는 사람이 읽을 수 있는 drift 요약과 후속 액션 1줄을 붙인다
- `unverifiable`은 필요 시 별도 설명으로 두되, v0.1 핵심 bucket은 위 3개를 유지한다

## Mapping

- reference seed: `references/sync-checklist.md`
- script: `scripts/doc_code_sync.py compare`, `scripts/doc_code_sync.py report`
- canonical KB: `doc-code-sync-canonical-design-at2026-03-16-18-18.md`
