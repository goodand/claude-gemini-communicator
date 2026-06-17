#!/usr/bin/env python3
"""execution-contract-mapper v0.1 vertical slices.

Usage:
    python3 execution_contract_mapper.py map-rule-schema --checklist <file>
    python3 execution_contract_mapper.py emit-schema-contract --rule-schema <file>
    python3 execution_contract_mapper.py emit-cli-contract
    python3 execution_contract_mapper.py emit-contract-diff-basis --rule-schema <file> --schema-contract <file> --cli-contract <file>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))
CHECKBOX_RE = re.compile(r"^- \[ \] (.+)$")
SECTION_RE = re.compile(r"^##\s+(.+)$")
SOURCE_RE = re.compile(r"^>\s*source of truth:\s*(.+)$", re.IGNORECASE)


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def _slug(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"^[a-z]\.\s*", "", lowered)
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "item"


def _section_key(section_title: str) -> str:
    return _slug(re.sub(r"^[A-Z]\.\s*", "", section_title))


def _relative_or_str(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def parse_checklist(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = ""
    source_of_truth = ""
    current_section = ""
    rules: list[dict[str, object]] = []

    for lineno, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue

        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
            continue

        source_match = SOURCE_RE.match(stripped)
        if source_match:
            source_of_truth = source_match.group(1).strip()
            continue

        section_match = SECTION_RE.match(stripped)
        if section_match:
            current_section = section_match.group(1).strip()
            continue

        item_match = CHECKBOX_RE.match(stripped)
        if not item_match or not current_section:
            continue

        expectation = item_match.group(1).strip()
        section_key = _section_key(current_section)
        name = f"{section_key}__{_slug(expectation)}"
        evidence = f"{path.name}:{lineno} :: {current_section} :: {expectation}"
        rules.append(
            {
                "kind": "rule_schema",
                "name": name,
                "source": _relative_or_str(path),
                "value": {
                    "expectation": expectation,
                    "section": current_section,
                    "checklist_role": "consistency_evaluation",
                },
                "evidence": evidence,
            }
        )

    if not rules:
        _err(f"체크리스트에서 rule_schema item을 찾지 못했습니다: {path}")

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "rule_schema",
        "input_checklist": _relative_or_str(path),
        "source_of_truth": source_of_truth,
        "title": title,
        "rule_count": len(rules),
        "rules": rules,
    }


def render_markdown(payload: dict[str, object]) -> str:
    rules = payload["rules"]
    lines = [
        "# execution-contract-mapper rule_schema summary",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- input_checklist: `{payload['input_checklist']}`",
        f"- source_of_truth: `{payload['source_of_truth']}`",
        f"- rule_count: `{payload['rule_count']}`",
        "",
        "## Rules",
        "",
    ]

    for rule in rules:
        value = rule["value"]
        lines.extend(
            [
                f"- `{rule['name']}`",
                f"  - kind: `{rule['kind']}`",
                f"  - section: `{value['section']}`",
                f"  - expectation: {value['expectation']}",
                f"  - evidence: `{rule['evidence']}`",
            ]
        )

    return "\n".join(lines) + "\n"


def build_rule_schema_contract(input_artifact: Path, payload: dict[str, object]) -> dict[str, object]:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "ExecutionContractMapperRuleSchemaArtifact",
        "type": "object",
        "required": [
            "status",
            "generated_at",
            "contract_family",
            "input_checklist",
            "source_of_truth",
            "title",
            "rule_count",
            "rules",
        ],
        "properties": {
            "status": {"type": "string", "const": "ok"},
            "generated_at": {"type": "string", "format": "date-time"},
            "contract_family": {"type": "string", "const": "rule_schema"},
            "input_checklist": {"type": "string", "minLength": 1},
            "source_of_truth": {"type": "string", "minLength": 1},
            "title": {"type": "string", "minLength": 1},
            "rule_count": {"type": "integer", "minimum": 1},
            "source_kb": {"type": "string"},
            "rules": {
                "type": "array",
                "minItems": max(1, int(payload["rule_count"])),
                "items": {
                    "type": "object",
                    "required": ["kind", "name", "source", "value", "evidence"],
                    "properties": {
                        "kind": {"type": "string", "const": "rule_schema"},
                        "name": {"type": "string", "minLength": 1},
                        "source": {"type": "string", "minLength": 1},
                        "evidence": {"type": "string", "minLength": 1},
                        "value": {
                            "type": "object",
                            "required": ["expectation", "section", "checklist_role"],
                            "properties": {
                                "expectation": {"type": "string", "minLength": 1},
                                "section": {"type": "string", "minLength": 1},
                                "checklist_role": {"type": "string", "const": "consistency_evaluation"},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    }
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "schema_contract",
        "source_contract_family": "rule_schema",
        "input_artifact": _relative_or_str(input_artifact),
        "schema_name": "ExecutionContractMapperRuleSchemaArtifact",
        "field_count": len(schema["properties"]),
        "schema": schema,
    }


def render_schema_contract_markdown(payload: dict[str, object]) -> str:
    schema = payload["schema"]
    required = schema["required"]
    properties = schema["properties"]
    lines = [
        "# execution-contract-mapper schema_contract summary",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- input_artifact: `{payload['input_artifact']}`",
        f"- source_contract_family: `{payload['source_contract_family']}`",
        f"- schema_name: `{payload['schema_name']}`",
        f"- field_count: `{payload['field_count']}`",
        "",
        "## Required Fields",
        "",
    ]
    for name in required:
        lines.append(f"- `{name}`")

    lines.extend(["", "## Property Types", ""])
    for name, spec in properties.items():
        kind = spec.get("type", "n/a")
        if "const" in spec:
            lines.append(f"- `{name}`: `{kind}` (`const={spec['const']}`)")
        else:
            lines.append(f"- `{name}`: `{kind}`")

    return "\n".join(lines) + "\n"


def _normalize_default(value: object) -> object:
    if value is argparse.SUPPRESS:
        return None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _action_to_contract(action: argparse.Action) -> dict[str, object]:
    kind = "option" if action.option_strings else "argument"
    choices = None
    if action.choices is not None:
        choices = [str(choice) for choice in action.choices]
    return {
        "dest": action.dest,
        "kind": kind,
        "option_strings": list(action.option_strings),
        "required": bool(getattr(action, "required", False)),
        "default": _normalize_default(getattr(action, "default", None)),
        "help": action.help or "",
        "nargs": action.nargs,
        "choices": choices,
    }


def build_cli_contract(script_path: Path, parser: argparse.ArgumentParser) -> dict[str, object]:
    subcommands: list[dict[str, object]] = []
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, subparser in action.choices.items():
            arguments = []
            for sub_action in subparser._actions:
                if isinstance(sub_action, argparse._HelpAction):
                    continue
                arguments.append(_action_to_contract(sub_action))

            subcommands.append(
                {
                    "name": name,
                    "help": subparser.description or subparser.format_usage().strip(),
                    "usage": subparser.format_usage().strip(),
                    "arguments": arguments,
                }
            )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "cli_contract",
        "script": _relative_or_str(script_path),
        "description": parser.description or "",
        "usage": parser.format_usage().strip(),
        "exit_codes": {
            "0": "success",
            "1": "argument or execution error",
        },
        "subcommand_count": len(subcommands),
        "subcommands": subcommands,
    }


def render_cli_contract_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# execution-contract-mapper cli_contract summary",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- script: `{payload['script']}`",
        f"- usage: `{payload['usage']}`",
        f"- subcommand_count: `{payload['subcommand_count']}`",
        "",
        "## Exit Codes",
        "",
    ]
    for code, meaning in payload["exit_codes"].items():
        lines.append(f"- `{code}`: {meaning}")

    lines.extend(["", "## Subcommands", ""])
    for subcommand in payload["subcommands"]:
        lines.append(f"- `{subcommand['name']}`")
        lines.append(f"  - usage: `{subcommand['usage']}`")
        for argument in subcommand["arguments"]:
            label = argument["dest"]
            lines.append(
                f"  - arg `{label}`: `{argument['kind']}` required=`{argument['required']}` option_strings=`{argument['option_strings']}`"
            )

    return "\n".join(lines) + "\n"


def build_contract_diff_basis(
    rule_schema_path: Path,
    rule_schema: dict[str, object],
    schema_contract_path: Path,
    schema_contract: dict[str, object],
    cli_contract_path: Path,
    cli_contract: dict[str, object],
) -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "contract_diff_basis",
        "inputs": {
            "rule_schema": _relative_or_str(rule_schema_path),
            "schema_contract": _relative_or_str(schema_contract_path),
            "cli_contract": _relative_or_str(cli_contract_path),
        },
        "supported_contract_families": ["rule_schema", "schema_contract", "cli_contract"],
        "compare_order": ["rule_schema", "schema_contract", "cli_contract"],
        "basis_count": 3,
        "recommended_diff_buckets": [
            "missing_contract_unit",
            "extra_contract_unit",
            "contract_value_changed",
            "requiredness_changed",
            "cli_argument_surface_changed",
        ],
        "downstream_consumers": [
            "baseline-diff-lab",
            "evidence-trace-auditor",
            "codebase-doc-alignment",
        ],
        "diff_bases": [
            {
                "contract_family": "rule_schema",
                "unit_name": "rule",
                "unit_count": rule_schema.get("rule_count", 0),
                "identity_keys": ["name"],
                "compare_fields": [
                    "kind",
                    "value.expectation",
                    "value.section",
                    "value.checklist_role",
                ],
                "evidence_fields": ["source", "evidence"],
                "candidate_buckets": [
                    "missing_contract_unit",
                    "extra_contract_unit",
                    "contract_value_changed",
                ],
            },
            {
                "contract_family": "schema_contract",
                "unit_name": "schema_property",
                "unit_count": schema_contract.get("field_count", 0),
                "identity_keys": ["property_name"],
                "compare_fields": [
                    "type",
                    "const",
                    "format",
                    "minLength",
                    "minimum",
                    "required_membership",
                ],
                "evidence_fields": ["input_artifact", "schema_name"],
                "candidate_buckets": [
                    "missing_contract_unit",
                    "extra_contract_unit",
                    "requiredness_changed",
                    "contract_value_changed",
                ],
            },
            {
                "contract_family": "cli_contract",
                "unit_name": "cli_subcommand_or_argument",
                "unit_count": cli_contract.get("subcommand_count", 0),
                "identity_keys": ["subcommand.name", "argument.dest"],
                "compare_fields": [
                    "usage",
                    "required",
                    "option_strings",
                    "choices",
                    "nargs",
                    "help",
                ],
                "evidence_fields": ["script", "usage"],
                "candidate_buckets": [
                    "missing_contract_unit",
                    "extra_contract_unit",
                    "cli_argument_surface_changed",
                    "contract_value_changed",
                ],
            },
        ],
    }


def render_contract_diff_basis_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# execution-contract-mapper contract_diff_basis summary",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- rule_schema: `{payload['inputs']['rule_schema']}`",
        f"- schema_contract: `{payload['inputs']['schema_contract']}`",
        f"- cli_contract: `{payload['inputs']['cli_contract']}`",
        f"- basis_count: `{payload['basis_count']}`",
        "",
        "## Recommended Diff Buckets",
        "",
    ]
    for bucket in payload["recommended_diff_buckets"]:
        lines.append(f"- `{bucket}`")

    lines.extend(["", "## Diff Bases", ""])
    for basis in payload["diff_bases"]:
        lines.append(f"- `{basis['contract_family']}`")
        lines.append(f"  - unit_name: `{basis['unit_name']}`")
        lines.append(f"  - unit_count: `{basis['unit_count']}`")
        lines.append(f"  - identity_keys: `{basis['identity_keys']}`")
        lines.append(f"  - compare_fields: `{basis['compare_fields']}`")
        lines.append(f"  - candidate_buckets: `{basis['candidate_buckets']}`")

    return "\n".join(lines) + "\n"


def cmd_map_rule_schema(args: argparse.Namespace) -> int:
    checklist_path = Path(args.checklist)
    if not checklist_path.is_file():
        _err(f"체크리스트 파일이 없습니다: {checklist_path}")

    payload = parse_checklist(checklist_path)
    if args.source_kb:
        payload["source_kb"] = args.source_kb

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_emit_schema_contract(args: argparse.Namespace) -> int:
    input_path = Path(args.rule_schema)
    if not input_path.is_file():
        _err(f"rule_schema artifact가 없습니다: {input_path}")

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if payload.get("contract_family") != "rule_schema":
        _err("입력 artifact의 contract_family가 rule_schema가 아닙니다.")

    contract = build_rule_schema_contract(input_path, payload)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(contract, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_schema_contract_markdown(contract), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_emit_cli_contract(args: argparse.Namespace) -> int:
    parser = build_parser()
    contract = build_cli_contract(Path(__file__), parser)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(contract, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_cli_contract_markdown(contract), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_emit_contract_diff_basis(args: argparse.Namespace) -> int:
    rule_schema_path = Path(args.rule_schema)
    schema_contract_path = Path(args.schema_contract)
    cli_contract_path = Path(args.cli_contract)

    for path, label in (
        (rule_schema_path, "rule_schema"),
        (schema_contract_path, "schema_contract"),
        (cli_contract_path, "cli_contract"),
    ):
        if not path.is_file():
            _err(f"{label} artifact가 없습니다: {path}")

    rule_schema = json.loads(rule_schema_path.read_text(encoding="utf-8"))
    schema_contract = json.loads(schema_contract_path.read_text(encoding="utf-8"))
    cli_contract = json.loads(cli_contract_path.read_text(encoding="utf-8"))

    if rule_schema.get("contract_family") != "rule_schema":
        _err("입력 artifact의 contract_family가 rule_schema가 아닙니다.")
    if schema_contract.get("contract_family") != "schema_contract":
        _err("입력 artifact의 contract_family가 schema_contract가 아닙니다.")
    if cli_contract.get("contract_family") != "cli_contract":
        _err("입력 artifact의 contract_family가 cli_contract가 아닙니다.")

    payload = build_contract_diff_basis(
        rule_schema_path,
        rule_schema,
        schema_contract_path,
        schema_contract,
        cli_contract_path,
        cli_contract,
    )

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_contract_diff_basis_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Map consistency checklist items into rule_schema artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    map_parser = subparsers.add_parser(
        "map-rule-schema",
        help="Convert consistency checklist checkbox items into machine-readable rule_schema objects.",
    )
    map_parser.add_argument("--checklist", required=True, help="Path to consistency checklist markdown file.")
    map_parser.add_argument("--source-kb", help="Optional source KB path for metadata.")
    map_parser.add_argument("--output-json", help="Optional output path for machine-readable artifact.")
    map_parser.add_argument("--output-md", help="Optional output path for markdown summary.")
    map_parser.set_defaults(func=cmd_map_rule_schema)

    schema_parser = subparsers.add_parser(
        "emit-schema-contract",
        help="Emit a JSON Schema contract for a rule_schema artifact.",
    )
    schema_parser.add_argument("--rule-schema", required=True, help="Path to rule_schema JSON artifact.")
    schema_parser.add_argument("--output-json", help="Optional output path for schema contract JSON.")
    schema_parser.add_argument("--output-md", help="Optional output path for schema contract markdown summary.")
    schema_parser.set_defaults(func=cmd_emit_schema_contract)

    cli_parser = subparsers.add_parser(
        "emit-cli-contract",
        help="Emit a machine-readable CLI contract for this mapper script.",
    )
    cli_parser.add_argument("--output-json", help="Optional output path for CLI contract JSON.")
    cli_parser.add_argument("--output-md", help="Optional output path for CLI contract markdown summary.")
    cli_parser.set_defaults(func=cmd_emit_cli_contract)

    diff_parser = subparsers.add_parser(
        "emit-contract-diff-basis",
        help="Emit a machine-readable diff basis from stable contract artifacts.",
    )
    diff_parser.add_argument("--rule-schema", required=True, help="Path to rule_schema JSON artifact.")
    diff_parser.add_argument("--schema-contract", required=True, help="Path to schema_contract JSON artifact.")
    diff_parser.add_argument("--cli-contract", required=True, help="Path to cli_contract JSON artifact.")
    diff_parser.add_argument("--output-json", help="Optional output path for contract diff basis JSON.")
    diff_parser.add_argument("--output-md", help="Optional output path for contract diff basis markdown summary.")
    diff_parser.set_defaults(func=cmd_emit_contract_diff_basis)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
