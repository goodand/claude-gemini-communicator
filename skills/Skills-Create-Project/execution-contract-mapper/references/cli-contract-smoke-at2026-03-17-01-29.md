# execution-contract-mapper cli_contract summary

- generated_at: `2026-03-17T01:30:54+09:00`
- script: `execution-contract-mapper/scripts/execution_contract_mapper.py`
- usage: `usage: execution_contract_mapper.py [-h]
                                    {map-rule-schema,emit-schema-contract,emit-cli-contract} ...`
- subcommand_count: `3`

## Exit Codes

- `0`: success
- `1`: argument or execution error

## Subcommands

- `map-rule-schema`
  - usage: `usage: execution_contract_mapper.py map-rule-schema [-h] --checklist CHECKLIST
                                                    [--source-kb SOURCE_KB]
                                                    [--output-json OUTPUT_JSON]
                                                    [--output-md OUTPUT_MD]`
  - arg `checklist`: `option` required=`True` option_strings=`['--checklist']`
  - arg `source_kb`: `option` required=`False` option_strings=`['--source-kb']`
  - arg `output_json`: `option` required=`False` option_strings=`['--output-json']`
  - arg `output_md`: `option` required=`False` option_strings=`['--output-md']`
- `emit-schema-contract`
  - usage: `usage: execution_contract_mapper.py emit-schema-contract [-h]
                                                         --rule-schema RULE_SCHEMA
                                                         [--output-json OUTPUT_JSON]
                                                         [--output-md OUTPUT_MD]`
  - arg `rule_schema`: `option` required=`True` option_strings=`['--rule-schema']`
  - arg `output_json`: `option` required=`False` option_strings=`['--output-json']`
  - arg `output_md`: `option` required=`False` option_strings=`['--output-md']`
- `emit-cli-contract`
  - usage: `usage: execution_contract_mapper.py emit-cli-contract [-h]
                                                      [--output-json OUTPUT_JSON]
                                                      [--output-md OUTPUT_MD]`
  - arg `output_json`: `option` required=`False` option_strings=`['--output-json']`
  - arg `output_md`: `option` required=`False` option_strings=`['--output-md']`
