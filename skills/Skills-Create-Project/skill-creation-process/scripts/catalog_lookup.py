#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CATALOG_DIR = Path(__file__).resolve().parents[1] / "references" / "catalog"
MANIFEST_PATH = CATALOG_DIR / "manifest.json"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON payload must be object: {path}")
    return payload


def _load_catalogs() -> dict[str, dict[str, object]]:
    manifest = _load_json(MANIFEST_PATH)
    catalogs = {"manifest": manifest}
    catalog_files = manifest.get("catalogs")
    if not isinstance(catalog_files, dict):
        raise ValueError("manifest.catalogs must be object")
    for catalog_name, relative_name in catalog_files.items():
        if not isinstance(relative_name, str):
            raise ValueError(f"manifest.catalogs.{catalog_name} must be str")
        catalogs[catalog_name] = _load_json(CATALOG_DIR / relative_name)
    return catalogs


def _items_by_key(catalog: dict[str, object]) -> dict[str, dict[str, object]]:
    items = catalog.get("items")
    if not isinstance(items, list):
        raise ValueError("catalog.items must be list")
    indexed: dict[str, dict[str, object]] = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("catalog item must be object")
        key = item.get("key")
        if not isinstance(key, str):
            raise ValueError("catalog item key must be str")
        indexed[key] = item
    return indexed


def _match_query(item: dict[str, object], query: str) -> bool:
    lowered = query.lower()
    for value in item.values():
        if isinstance(value, str) and lowered in value.lower():
            return True
        if isinstance(value, list):
            for nested in value:
                if isinstance(nested, str) and lowered in nested.lower():
                    return True
    return False


def _catalog_name_for_key(key: str) -> str:
    if key.startswith("TASK-"):
        return "tasks"
    if key.startswith("ISSUE-"):
        return "issues"
    if key.startswith("SKILL-"):
        return "skills"
    if key.startswith("LINK-"):
        return "links"
    if key.startswith("JOIN-"):
        return "joins"
    raise ValueError(f"Unsupported key namespace: {key}")


def _resolve_record(catalogs: dict[str, dict[str, object]], key: str) -> dict[str, object]:
    catalog_name = _catalog_name_for_key(key)
    catalog = catalogs[catalog_name]
    record = _items_by_key(catalog).get(key)
    if record is None:
        raise KeyError(key)

    tasks = _items_by_key(catalogs["tasks"])
    issues = _items_by_key(catalogs["issues"])
    skills = _items_by_key(catalogs["skills"])
    links_catalog = catalogs["links"].get("items")
    if not isinstance(links_catalog, list):
        raise ValueError("links.items must be list")

    resolved = dict(record)
    if key.startswith("TASK-"):
        primary = []
        for skill_key in record.get("primary_skill_keys", []):
            if isinstance(skill_key, str) and skill_key in skills:
                primary.append(skills[skill_key])
        support = []
        for skill_key in record.get("support_skill_keys", []):
            if isinstance(skill_key, str) and skill_key in skills:
                support.append(skills[skill_key])
        resolved["resolved_primary_skills"] = primary
        resolved["resolved_support_skills"] = support
    elif key.startswith("ISSUE-"):
        task_records = []
        for task_key in record.get("repeated_task_keys", []):
            if isinstance(task_key, str) and task_key in tasks:
                task_records.append(tasks[task_key])
        skill_records = []
        for skill_key in record.get("related_skill_keys", []):
            if isinstance(skill_key, str) and skill_key in skills:
                skill_records.append(skills[skill_key])
        resolved["resolved_tasks"] = task_records
        resolved["resolved_skills"] = skill_records
    elif key.startswith("SKILL-"):
        task_records = []
        for task in tasks.values():
            for field in ("primary_skill_keys", "support_skill_keys"):
                keys = task.get(field, [])
                if isinstance(keys, list) and key in keys:
                    task_records.append(task)
                    break
        resolved["related_tasks"] = task_records
    elif key.startswith("LINK-"):
        from_key = record.get("from_key")
        to_key = record.get("to_key")
        if isinstance(from_key, str):
            source_catalog = _catalog_name_for_key(from_key)
            resolved["from_record"] = _items_by_key(catalogs[source_catalog]).get(from_key)
        if isinstance(to_key, str):
            target_catalog = _catalog_name_for_key(to_key)
            resolved["to_record"] = _items_by_key(catalogs[target_catalog]).get(to_key)
    elif key.startswith("JOIN-"):
        issue_key = record.get("issue_key")
        task_keys = record.get("task_keys", [])
        issue_record = issues.get(issue_key) if isinstance(issue_key, str) else None
        resolved["resolved_issue"] = issue_record

        task_records = []
        for task_key in task_keys:
            if isinstance(task_key, str) and task_key in tasks:
                task_records.append(tasks[task_key])
        resolved["resolved_tasks"] = task_records

        skill_keys: list[str] = []
        if isinstance(issue_record, dict):
            for skill_key in issue_record.get("related_skill_keys", []):
                if isinstance(skill_key, str) and skill_key not in skill_keys:
                    skill_keys.append(skill_key)
        for task_record in task_records:
            for field in ("primary_skill_keys", "support_skill_keys"):
                keys = task_record.get(field, [])
                if not isinstance(keys, list):
                    continue
                for skill_key in keys:
                    if isinstance(skill_key, str) and skill_key not in skill_keys:
                        skill_keys.append(skill_key)
        resolved["resolved_skills"] = [skills[skill_key] for skill_key in skill_keys if skill_key in skills]

        derived_links = []
        for link in links_catalog:
            if not isinstance(link, dict):
                continue
            if isinstance(issue_key, str) and link.get("from_key") == issue_key:
                derived_links.append(link)
                continue
            if link.get("from_key") in task_keys:
                derived_links.append(link)
        resolved["derived_links"] = derived_links

    resolved["linked_edges"] = [
        link for link in links_catalog
        if isinstance(link, dict) and (link.get("from_key") == key or link.get("to_key") == key)
    ]
    return resolved


def cmd_list(args: argparse.Namespace) -> int:
    catalogs = _load_catalogs()
    catalog = catalogs[args.type]
    items = catalog.get("items")
    if not isinstance(items, list):
        raise ValueError("catalog.items must be list")
    print(json.dumps({"type": args.type, "count": len(items), "items": items}, indent=2, ensure_ascii=False))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    catalogs = _load_catalogs()
    try:
        payload = _resolve_record(catalogs, args.key)
    except KeyError:
        print(json.dumps({"status": "not_found", "key": args.key}, indent=2, ensure_ascii=False))
        return 1
    print(json.dumps({"status": "ok", "record": payload}, indent=2, ensure_ascii=False))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    catalogs = _load_catalogs()
    target_catalogs = ["tasks", "issues", "skills", "links", "joins"] if args.type == "all" else [args.type]
    matches: list[dict[str, object]] = []
    for catalog_name in target_catalogs:
        items = catalogs[catalog_name].get("items")
        if not isinstance(items, list):
            raise ValueError("catalog.items must be list")
        for item in items:
            if isinstance(item, dict) and _match_query(item, args.query):
                matches.append({"catalog": catalog_name, "item": item})
    print(json.dumps({"status": "ok", "query": args.query, "count": len(matches), "matches": matches}, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search namespaced task/issue/skill/link catalogs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List a catalog.")
    list_parser.add_argument("--type", choices=["tasks", "issues", "skills", "links", "joins"], required=True)
    list_parser.set_defaults(func=cmd_list)

    show_parser = subparsers.add_parser("show", help="Show one record by namespaced key.")
    show_parser.add_argument("--key", required=True, help="Namespaced key like TASK-01, ISSUE-03, SKILL-foo.")
    show_parser.set_defaults(func=cmd_show)

    search_parser = subparsers.add_parser("search", help="Search catalogs by key, label, title, or text.")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--type", choices=["tasks", "issues", "skills", "links", "joins", "all"], default="all")
    search_parser.set_defaults(func=cmd_search)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
