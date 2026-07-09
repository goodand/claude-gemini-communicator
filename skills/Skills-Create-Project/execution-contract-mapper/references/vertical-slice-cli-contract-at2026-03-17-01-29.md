# execution-contract-mapper vertical slice — cli_contract

## Purpose

- 세 번째 구현 slice로 `cli_contract`를 고정한다.
- `execution_contract_mapper.py`의 subcommand surface를 machine-readable contract로 내린다.

## Input

- source script:
  - `scripts/execution_contract_mapper.py`

## Output

- JSON artifact:
  - `references/cli-contract-smoke-at2026-03-17-01-29.json`
- Markdown summary:
  - `references/cli-contract-smoke-at2026-03-17-01-29.md`

## Contract Scope

- root usage
- exit code contract
- subcommand 목록
- 각 subcommand의 required/optional argument surface

## Current Result

- `subcommand_count >= 3`
- `map-rule-schema`, `emit-schema-contract`, `emit-cli-contract` surface 추출 확인

## Follow-up

- 다음 slice는 `contract_diff_basis`
