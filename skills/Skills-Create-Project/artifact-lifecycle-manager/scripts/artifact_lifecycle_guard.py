#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


MINUTE_TIMESTAMP_RE = re.compile(r"-at\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$")


@dataclass
class ArtifactInfo:
    label: str
    path: Path
    created_epoch: float | None
    modified_epoch: float
    has_minute_timestamp: bool

    @property
    def order_epoch(self) -> float:
        return self.created_epoch if self.created_epoch is not None else self.modified_epoch

    @property
    def order_key(self) -> tuple[float, float]:
        return (self.order_epoch, self.modified_epoch)


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def _collect_markdown_files(directory: Path, include_legacy: bool = False) -> list[Path]:
    files: list[Path] = []
    for path in directory.rglob("*.md"):
        if not include_legacy and "legacy" in path.parts:
            continue
        files.append(path)
    return sorted(files)


def _pick_stage_file(directory: Path, preferred_keyword: str | None, excluded_keywords: tuple[str, ...] = ()) -> Path | None:
    if not directory.is_dir():
        return None
    files = sorted(
        [path for path in directory.iterdir() if path.is_file() and path.suffix == ".md"],
        key=lambda path: path.stat().st_mtime,
    )
    if not files:
        return None
    filtered = [path for path in files if not any(keyword in path.name for keyword in excluded_keywords)]
    if preferred_keyword:
        preferred = [path for path in filtered if preferred_keyword in path.name]
        if preferred:
            return preferred[-1]
    return filtered[-1] if filtered else files[-1]


def _discover_chain(skill_dir: Path) -> list[tuple[str, Path]]:
    knowledge_base = _pick_stage_file(
        skill_dir / "knowledge_bases",
        preferred_keyword="knowledge_base",
        excluded_keywords=("issues",),
    )
    consistency = _pick_stage_file(
        skill_dir / "checklist-forconsistency-evaluation",
        preferred_keyword="consistency",
    )
    implementation = _pick_stage_file(
        skill_dir / "checklist-forimplementation",
        preferred_keyword="implementation",
    )

    chain: list[tuple[str, Path]] = []
    if knowledge_base is not None:
        chain.append(("knowledge_base", knowledge_base))
    if consistency is not None:
        chain.append(("consistency_checklist", consistency))
    if implementation is not None:
        chain.append(("implementation_checklist", implementation))
    return chain


def _build_info(label: str, path: Path) -> ArtifactInfo:
    stats = path.stat()
    created_epoch = getattr(stats, "st_birthtime", None)
    modified_epoch = stats.st_mtime
    return ArtifactInfo(
        label=label,
        path=path,
        created_epoch=created_epoch,
        modified_epoch=modified_epoch,
        has_minute_timestamp=bool(MINUTE_TIMESTAMP_RE.search(path.stem)),
    )


def _format_epoch(epoch: float | None) -> str:
    if epoch is None:
        return "N/A"
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def _check_order(skill_dir: Path) -> dict[str, object]:
    discovered = _discover_chain(skill_dir)
    errors: list[str] = []
    artifacts: list[dict[str, object]] = []

    if len(discovered) < 2:
        errors.append("need at least knowledge_base and one checklist artifact")
        return {"status": "failed", "errors": errors, "artifacts": artifacts}

    infos = [_build_info(label, path) for label, path in discovered]

    for info in infos:
        artifacts.append(
            {
                "label": info.label,
                "path": str(info.path),
                "created": _format_epoch(info.created_epoch),
                "modified": _format_epoch(info.modified_epoch),
                "minute_timestamp": info.has_minute_timestamp,
            }
        )
        if not info.has_minute_timestamp:
            errors.append(f"{info.label}: minute-level timestamp missing -> {info.path.name}")

    for previous, current in zip(infos, infos[1:]):
        if previous.order_key > current.order_key:
            errors.append(
                f"metadata order violated: {previous.label} must be earlier than {current.label}"
            )

    return {
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "artifacts": artifacts,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scan_duplicates(skill_dir: Path, include_legacy: bool) -> dict[str, object]:
    files = _collect_markdown_files(skill_dir, include_legacy=include_legacy)
    groups: dict[str, list[str]] = {}
    for path in files:
        digest = _sha256(path)
        groups.setdefault(digest, []).append(str(path))

    duplicates = [
        {"hash": digest, "paths": sorted(paths)}
        for digest, paths in groups.items()
        if len(paths) > 1
    ]
    return {
        "status": "passed" if not duplicates else "failed",
        "include_legacy": include_legacy,
        "duplicate_groups": duplicates,
    }


# ---------------------------------------------------------------------------
# Stale candidate detection
# ---------------------------------------------------------------------------

STALE_SCOPE_MAP: dict[str, list[str]] = {
    "references": ["references"],
    "knowledge_bases": ["knowledge_bases"],
    "checklists": [
        "checklist-forconsistency-evaluation",
        "checklist-forimplementation",
    ],
}

RULE_BEARING_PATH_KEYWORDS = ("vertical-slice", "fields", "contract", "rule")
INFORMATIONAL_NAME_KEYWORDS = (
    "index",
    "catalog",
    "examples",
    "template_reference",
    "template-reference",
)


def _collect_reference_candidates(
    skill_dir: Path,
    include_legacy: bool = False,
    scope: list[str] | None = None,
) -> list[Path]:
    """Collect candidate documents for stale checking."""
    if scope is None:
        scope = list(STALE_SCOPE_MAP.keys())

    scope_dirs: list[str] = []
    for s in scope:
        if s in STALE_SCOPE_MAP:
            scope_dirs.extend(STALE_SCOPE_MAP[s])
        else:
            scope_dirs.append(s)

    candidates: list[Path] = []
    for dir_name in scope_dirs:
        d = skill_dir / dir_name
        if not d.is_dir():
            continue
        for path in d.rglob("*.md"):
            if not include_legacy and "legacy" in path.parts:
                continue
            candidates.append(path)
    return sorted(candidates)


def _extract_target_paths(doc_path: Path, skill_dir: Path) -> list[Path]:
    """Extract target paths referenced in a document.

    Sources:
    - markdown links: [text](relative/path.py)
    - inline code paths: `scripts/foo.py`
    - keyword prefixes: source of truth:, files:
    - bare paths: scripts/..., references/..., knowledge_bases/..., checklist-for.../...
    """
    text = doc_path.read_text(encoding="utf-8", errors="replace")
    raw: set[str] = set()

    # Markdown links
    for m in re.finditer(r"\]\(([^)\s]+\.\w{1,5})\)", text):
        p = m.group(1)
        if not p.startswith(("http://", "https://", "#")):
            raw.add(p)

    # Inline code paths (must contain /)
    for m in re.finditer(r"`([^`\s]+/[^`\s]+\.\w{1,5})`", text):
        raw.add(m.group(1))

    # Keyword prefixes
    for m in re.finditer(
        r"(?:source\s+of\s+truth|files)\s*:\s*([\w./-]+\.\w{1,5})",
        text,
        re.IGNORECASE,
    ):
        raw.add(m.group(1))

    # Bare paths with known directory prefixes
    for m in re.finditer(
        r"(?:^|[\s,;|])((?:scripts|references|knowledge_bases|checklist-for[\w-]*)/[\w./-]+\.\w{1,5})",
        text,
        re.MULTILINE,
    ):
        raw.add(m.group(1))

    # Resolve: ../ relative to doc parent, others relative to skill_dir
    resolved: list[Path] = []
    for p in raw:
        if p.startswith("..") or p.startswith("./"):
            full = (doc_path.parent / p).resolve()
        else:
            full = (skill_dir / p).resolve()
        resolved.append(full)

    return sorted(set(resolved))


def _classify_semantic_owner(doc_path: Path, text: str = "") -> tuple[str, str]:
    """Classify document kind and semantic recheck owner.

    Returns (semantic_owner, recheck_owner):
    - ("rule_bearing", "doc-code-sync-checker")
    - ("claim_heavy", "claim-verifier")
    - ("informational", "manual-review")
    """
    path_str = str(doc_path)
    name = doc_path.name.lower()

    if "checklist-for" in path_str:
        return ("rule_bearing", "doc-code-sync-checker")

    for kw in RULE_BEARING_PATH_KEYWORDS:
        if kw in name:
            return ("rule_bearing", "doc-code-sync-checker")

    for kw in INFORMATIONAL_NAME_KEYWORDS:
        if kw in name:
            return ("informational", "manual-review")

    return ("claim_heavy", "claim-verifier")


def _expected_review_record(doc_path: Path, skill_dir: Path) -> tuple[str, Path | None]:
    """Return expected review record location for a document."""
    rel = _relative_str(doc_path, skill_dir)
    if rel.startswith("references/"):
        return ("frontmatter", None)
    if rel.startswith("knowledge_bases/"):
        return ("sidecar", skill_dir / "knowledge_bases" / ".freshness_audit.yaml")
    if rel.startswith("checklist-for"):
        return ("sidecar", doc_path.parent / ".freshness_audit.yaml")
    return ("none", None)


def _has_review_record(doc_path: Path, skill_dir: Path) -> tuple[str, bool]:
    """Check whether a freshness review record is present.

    This is advisory metadata only and does not affect stale status.
    """
    expected, sidecar = _expected_review_record(doc_path, skill_dir)
    if expected == "frontmatter":
        text = doc_path.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---"):
            return (expected, "freshness_review:" in text)
        return (expected, False)

    if expected == "sidecar" and sidecar is not None and sidecar.is_file():
        text = sidecar.read_text(encoding="utf-8", errors="replace")
        patterns = [
            rf'file:\s*"{re.escape(doc_path.name)}"',
            rf"file:\s*'{re.escape(doc_path.name)}'",
            rf"file:\s*{re.escape(doc_path.name)}",
        ]
        return (expected, any(re.search(pattern, text) for pattern in patterns))

    return (expected, False)


def _relative_str(path: Path, base: Path) -> str:
    """Return path relative to base, or absolute if not under base."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _scan_stale_candidates(
    skill_dir: Path,
    include_legacy: bool = False,
    scope: list[str] | None = None,
) -> dict[str, object]:
    """Scan for stale candidate documents.

    Statuses:
    - fresh: all targets exist and doc is newer
    - candidate_stale: at least one target is newer than doc
    - needs_mapping: no target paths found in document
    - missing_target: at least one target path does not exist
    - skipped: excluded by scope/legacy filter
    """
    candidates = _collect_reference_candidates(skill_dir, include_legacy, scope)
    entries: list[dict[str, object]] = []
    summary = {
        "fresh": 0,
        "candidate_stale": 0,
        "needs_mapping": 0,
        "missing_target": 0,
        "skipped": 0,
    }

    for doc_path in candidates:
        text = doc_path.read_text(encoding="utf-8", errors="replace")
        targets = _extract_target_paths(doc_path, skill_dir)
        semantic_owner, recheck_owner = _classify_semantic_owner(doc_path, text)
        review_record_expected, review_record_present = _has_review_record(doc_path, skill_dir)
        doc_mtime = doc_path.stat().st_mtime

        if not targets:
            status = "needs_mapping"
            reasons = ["no target paths found in document"]
            target_info: list[dict[str, object]] = []
        else:
            target_info = []
            missing: list[Path] = []
            newer: list[Path] = []

            for t in targets:
                if not t.exists():
                    missing.append(t)
                    target_info.append({
                        "path": _relative_str(t, skill_dir),
                        "modified": None,
                        "exists": False,
                    })
                else:
                    t_mtime = t.stat().st_mtime
                    target_info.append({
                        "path": _relative_str(t, skill_dir),
                        "modified": _format_epoch(t_mtime),
                        "exists": True,
                    })
                    if t_mtime > doc_mtime:
                        newer.append(t)

            reasons = []
            if missing:
                status = "missing_target"
                for m in missing:
                    reasons.append(f"target not found: {_relative_str(m, skill_dir)}")
            elif newer:
                status = "candidate_stale"
                for n in newer:
                    reasons.append(f"target newer than document: {_relative_str(n, skill_dir)}")
            else:
                status = "fresh"

        summary[status] += 1
        entries.append({
            "doc_path": _relative_str(doc_path, skill_dir),
            "doc_kind": semantic_owner,
            "semantic_owner": semantic_owner,
            "recheck_owner": recheck_owner,
            "status": status,
            "reasons": reasons,
            "targets": target_info,
            "doc_modified": _format_epoch(doc_mtime),
            "review_record_expected": review_record_expected,
            "review_record_present": review_record_present,
        })

    return {
        "skill_dir": str(skill_dir),
        "total": len(entries),
        "summary": summary,
        "entries": entries,
    }


# ---------------------------------------------------------------------------
# Audit (combined)
# ---------------------------------------------------------------------------

def _audit(
    skill_dir: Path,
    include_legacy: bool = False,
    *,
    include_stale: bool = False,
    fail_on_candidate: bool = False,
    scope: list[str] | None = None,
) -> dict[str, object]:
    order_result = _check_order(skill_dir)
    duplicate_result = _scan_duplicates(skill_dir, include_legacy=include_legacy)
    status = "passed"
    if order_result["status"] != "passed" or duplicate_result["status"] != "passed":
        status = "failed"

    result: dict[str, object] = {
        "status": status,
        "skill_dir": str(skill_dir),
        "order": order_result,
        "duplicates": duplicate_result,
    }

    if include_stale:
        stale_result = _scan_stale_candidates(
            skill_dir, include_legacy=include_legacy, scope=scope,
        )
        result["stale_candidates"] = stale_result
        if fail_on_candidate and stale_result["summary"]["candidate_stale"] > 0:
            result["status"] = "failed"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard skill artifact lifecycle rules")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_order = subparsers.add_parser("check-order", help="check metadata order and timestamp naming")
    check_order.add_argument("--skill-dir", default=".", help="target skill directory")

    scan_duplicates = subparsers.add_parser("scan-duplicates", help="scan same-content markdown duplicates")
    scan_duplicates.add_argument("--skill-dir", default=".", help="target skill directory")
    scan_duplicates.add_argument("--include-legacy", action="store_true", help="include legacy files in duplicate scan")

    audit = subparsers.add_parser("audit", help="run order and duplicate checks together")
    audit.add_argument("--skill-dir", default=".", help="target skill directory")
    audit.add_argument("--include-legacy", action="store_true", help="include legacy files in duplicate scan")
    audit.add_argument("--include-stale", action="store_true", help="include stale candidate scan")
    audit.add_argument("--fail-on-candidate", action="store_true", help="exit 1 if candidate_stale found")
    audit.add_argument("--scope", default=None, help="comma-separated: references,knowledge_bases,checklists")

    p_stale = subparsers.add_parser("scan-stale-candidates", help="scan stale candidate documents")
    p_stale.add_argument("--skill-dir", default=".", help="target skill directory")
    p_stale.add_argument("--include-legacy", action="store_true", help="include legacy/ files")
    p_stale.add_argument("--fail-on-candidate", action="store_true", help="exit 1 if candidate_stale found")
    p_stale.add_argument("--scope", default=None, help="comma-separated: references,knowledge_bases,checklists")

    args = parser.parse_args()
    skill_dir = Path(args.skill_dir)
    if not skill_dir.is_absolute():
        skill_dir = Path(os.getcwd()) / skill_dir
    skill_dir = skill_dir.resolve()

    if args.command == "check-order":
        payload = _check_order(skill_dir)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if payload["status"] == "passed" else 1

    elif args.command == "scan-duplicates":
        payload = _scan_duplicates(skill_dir, include_legacy=args.include_legacy)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if payload["status"] == "passed" else 1

    elif args.command == "scan-stale-candidates":
        scope = args.scope.split(",") if args.scope else None
        payload = _scan_stale_candidates(
            skill_dir, include_legacy=args.include_legacy, scope=scope,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        if args.fail_on_candidate and payload["summary"]["candidate_stale"] > 0:
            return 1
        return 0

    else:  # audit
        scope = args.scope.split(",") if args.scope else None
        payload = _audit(
            skill_dir,
            include_legacy=args.include_legacy,
            include_stale=args.include_stale,
            fail_on_candidate=args.fail_on_candidate,
            scope=scope,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
