#!/usr/bin/env python3
"""Conservative cross-skill dependency auditor.

v1 범위:
- consumer declaration file 존재 확인
- provider skill 존재 확인
- provider contract path 존재 확인
- last_synced_at ISO 8601 파싱
- provider contract mtime > last_synced_at 인 stale_dependency 탐지

의도적으로 하지 않는 것:
- consumer 내부 semantic drift 탐지
- SKILL.md Notes fallback 파싱
- consumed_facts 의미 검사
"""
from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DECLARATION_REL = Path("references") / "cross_skill_dependencies.yaml"


@dataclass
class AuditEntry:
    consumer: str
    provider: str | None
    contract: str | None
    status: str
    detail: str
    last_synced_at: str | None = None
    provider_mtime: str | None = None


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value[0] in {'"', "'"}:
        return ast.literal_eval(value)
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    return value


def _parse_declaration_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    root_seen = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "cross_skill_dependencies:":
            root_seen = True
            continue
        if not root_seen:
            continue

        if stripped.startswith("- provider:"):
            if current:
                entries.append(current)
            current = {"provider": _parse_scalar(stripped.split(":", 1)[1])}
            continue

        if current is None:
            continue

        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        if key in {"contract", "consumed_facts", "last_synced_at"}:
            current[key] = _parse_scalar(value)

    if current:
        entries.append(current)

    return entries


def _iter_skill_dirs(skills_root: Path) -> list[Path]:
    return sorted(
        path for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def _isoformat_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat()


def _parse_timestamp(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _audit_consumer_skill(consumer_dir: Path, *, require_declaration: bool = False) -> list[AuditEntry]:
    consumer = consumer_dir.name
    decl_path = consumer_dir / DECLARATION_REL
    if not decl_path.is_file():
        if require_declaration:
            return [
                AuditEntry(
                    consumer=consumer,
                    provider=None,
                    contract=None,
                    status="missing_declaration",
                    detail=f"declaration file not found: {DECLARATION_REL}",
                )
            ]
        return []

    parsed = _parse_declaration_file(decl_path)
    if not parsed:
        return [
            AuditEntry(
                consumer=consumer,
                provider=None,
                contract=None,
                status="invalid_declaration",
                detail="cross_skill_dependencies entries not found",
            )
        ]

    rows: list[AuditEntry] = []
    for item in parsed:
        provider = item.get("provider")
        contract = item.get("contract")
        last_synced_at = item.get("last_synced_at")

        if not isinstance(provider, str) or not provider:
            rows.append(
                AuditEntry(
                    consumer=consumer,
                    provider=None,
                    contract=contract if isinstance(contract, str) else None,
                    status="invalid_declaration",
                    detail="provider missing or invalid",
                    last_synced_at=last_synced_at if isinstance(last_synced_at, str) else None,
                )
            )
            continue

        provider_dir = consumer_dir.parent / provider
        if not provider_dir.is_dir():
            rows.append(
                AuditEntry(
                    consumer=consumer,
                    provider=provider,
                    contract=contract if isinstance(contract, str) else None,
                    status="missing_provider",
                    detail=f"provider skill not found: {provider}",
                    last_synced_at=last_synced_at if isinstance(last_synced_at, str) else None,
                )
            )
            continue

        if not isinstance(contract, str) or not contract:
            rows.append(
                AuditEntry(
                    consumer=consumer,
                    provider=provider,
                    contract=None,
                    status="invalid_declaration",
                    detail="contract missing or invalid",
                    last_synced_at=last_synced_at if isinstance(last_synced_at, str) else None,
                )
            )
            continue

        contract_path = (provider_dir / contract).resolve()
        if not contract_path.is_file():
            rows.append(
                AuditEntry(
                    consumer=consumer,
                    provider=provider,
                    contract=contract,
                    status="missing_contract",
                    detail=f"provider contract not found: {contract}",
                    last_synced_at=last_synced_at if isinstance(last_synced_at, str) else None,
                )
            )
            continue

        if not isinstance(last_synced_at, str) or not last_synced_at:
            rows.append(
                AuditEntry(
                    consumer=consumer,
                    provider=provider,
                    contract=contract,
                    status="invalid_timestamp",
                    detail="last_synced_at missing or invalid",
                    last_synced_at=None,
                    provider_mtime=_isoformat_mtime(contract_path),
                )
            )
            continue

        synced_dt = _parse_timestamp(last_synced_at)
        if synced_dt is None:
            rows.append(
                AuditEntry(
                    consumer=consumer,
                    provider=provider,
                    contract=contract,
                    status="invalid_timestamp",
                    detail="last_synced_at is not valid ISO 8601",
                    last_synced_at=last_synced_at,
                    provider_mtime=_isoformat_mtime(contract_path),
                )
            )
            continue

        provider_dt = datetime.fromtimestamp(contract_path.stat().st_mtime).astimezone()
        if provider_dt > synced_dt.astimezone():
            rows.append(
                AuditEntry(
                    consumer=consumer,
                    provider=provider,
                    contract=contract,
                    status="stale_dependency",
                    detail="provider contract is newer than last_synced_at",
                    last_synced_at=last_synced_at,
                    provider_mtime=provider_dt.isoformat(),
                )
            )
            continue

        rows.append(
            AuditEntry(
                consumer=consumer,
                provider=provider,
                contract=contract,
                status="ok",
                detail="dependency declaration is present and not stale",
                last_synced_at=last_synced_at,
                provider_mtime=provider_dt.isoformat(),
            )
        )

    return rows


def run_audit(skills_root: Path, *, skill: str | None = None) -> list[AuditEntry]:
    if skill:
        return _audit_consumer_skill(skills_root / skill, require_declaration=True)

    rows: list[AuditEntry] = []
    for skill_dir in _iter_skill_dirs(skills_root):
        rows.extend(_audit_consumer_skill(skill_dir, require_declaration=False))
    return rows


def _format_text(rows: list[AuditEntry]) -> str:
    lines = [
        "| consumer | provider | status | contract | detail |",
        "|----------|----------|--------|----------|--------|",
    ]
    for row in rows:
        lines.append(
            "| {consumer} | {provider} | {status} | {contract} | {detail} |".format(
                consumer=row.consumer,
                provider=row.provider or "",
                status=row.status,
                contract=row.contract or "",
                detail=row.detail,
            )
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="audit conservative cross-skill dependency declarations")
    parser.add_argument("--skills-root", default=".", help="Skills-Create-Project root")
    parser.add_argument("--skill", default=None, help="single consumer skill directory name")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true", help="exit 1 on any non-ok status")
    args = parser.parse_args()

    skills_root = Path(args.skills_root).resolve()
    rows = run_audit(skills_root, skill=args.skill)

    if args.format == "json":
        print(json.dumps([asdict(row) for row in rows], indent=2, ensure_ascii=False))
    else:
        print(_format_text(rows))

    if args.strict and any(row.status != "ok" for row in rows):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
