#!/usr/bin/env python3
"""Check whether a knowledge base is reflected in a consistency checklist.

v0.1 목적:
- knowledge_base 전체와 checklist 전체를 직접 semantic judge 하지 않는다
- KB canonical unit vs consistency checklist item을 비교한다
- anchor/keyword + section-level comparison으로 candidate gap을 찾는다
- 최종 truth 대신 human review queue를 남긴다
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


BACKTICK_RE = re.compile(r"`([^`]+)`")
ASCII_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.:/-]{1,}")
KOREAN_TOKEN_RE = re.compile(r"[가-힣]{2,}")
CHECKLIST_LINE_RE = re.compile(r"^\s*- \[[ xX]\]\s+(.*)$")
BULLET_LINE_RE = re.compile(r"^(\s*)- (?!\[[ xX]\])(.*)$")
INTERNAL_LINK_RE = re.compile(r"^\[[^\]]+\]\(#.+\)$")
CHECKLIST_LABEL_RE = re.compile(r"^\*\*[A-Z]-\d+\*\*:\s*")
STOPWORDS = {
    "checklist",
    "knowledge",
    "base",
    "unit",
    "item",
    "comparison",
    "compare",
    "section",
    "level",
    "current",
    "target",
    "output",
    "input",
    "rule",
    "rules",
    "contract",
    "contracts",
    "ratio",
    "report",
    "json",
    "markdown",
    "human",
    "review",
    "queue",
    "한다",
    "있다",
    "정의",
    "구현",
    "출력",
    "비교",
    "현재",
    "항목",
    "단위",
    "계산",
    "시작",
}
NEGATION_MARKERS = (
    "아니라",
    "단정하지 않는다",
    "숨기지 않는다",
    "not ",
    "not final truth",
)
GUARDRAIL_HINTS = (
    "candidate detector",
    "candidate traceability gap detector",
    "heuristic",
    "human review",
    "section-level comparison",
    "anchor/keyword",
    "최종 truth",
    "v0.1",
)
ADVANCED_EXPANSION_HINTS = (
    "ast parser",
    "ast",
    "semantic graph",
    "full semantic graph",
    "full graph",
    "graph parser",
)
SUPPORT_METADATA_KEYS = {
    "canonical_role",
    "canonical_slice",
    "source_of_truth_for",
    "source_research_kb",
    "source_research_files",
}
SUPPORT_SECTION_PREFIXES = (
    "key_idea:",
    "execution_conditions:",
    "taxonomy:",
)
SUMMARY_PARENT_HINTS = (
    "아래 3개다.",
    "아래 4개다.",
    "아래 두 층이다.",
    "아래 두 층이 더 적합하다.",
    "아래 두 개다.",
    "아래 5개다.",
    "아래 네 개다.",
    "아래처럼 둔다.",
    "핵심은 아래다.",
)
PHRASE_ALIASES = {
    "consistency checklist item": {"consistency checklist item", "checklist item"},
    "kb canonical unit": {"kb canonical unit", "canonical unit"},
    "human review queue": {"human review queue", "human review needed", "ambiguity"},
    "artifact_vs_object": {"artifact_vs_object", "artifact-level", "object-level"},
    "traceability matrix": {"traceability matrix", "per-unit table"},
    "source of truth": {"source of truth", "source-of-truth"},
}
KB_METADATA_KEYS = {
    "ver",
    "generated_at",
    "updated_at",
    "canonical_role",
    "canonical_slice",
    "source_of_truth_for",
    "source_research_kb",
    "format",
    "generation_method",
    "total_urls",
    "paper_like_urls",
    "other_urls",
}
IGNORED_KB_SECTIONS = {
    "document map",
    "table of contents",
    "paper-like urls",
    "other research references urls",
}
SUPPORT_KB_SECTIONS = {
    "profile",
    "measurement alignment",
    "current implementation status",
}
METRIC_CONTRACT_PATH = (
    Path(__file__).resolve().parent.parent
    / "knowledge_bases"
    / "kb-to-consistency-metric-formula-contract-at2026-03-16-19-02.json"
)
REQUIRED_METRIC_SPEC_FIELDS = (
    "class",
    "semantic",
    "formula",
    "current_execution_note",
    "interpretation",
)


@dataclass
class ArtifactUnit:
    uid: str
    section: str
    text: str
    normalized: str
    explicit_tokens: list[str]
    keyword_tokens: list[str]
    kind: str = "canonical"


@dataclass
class Mapping:
    kb_unit_id: str
    checklist_item_id: str
    score: int
    evidence: list[str] = field(default_factory=list)


@dataclass
class BulletEntry:
    section: str
    indent: int
    content: str
    has_children: bool = False


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def _extract_explicit_tokens(text: str) -> list[str]:
    return [token.strip().lower() for token in BACKTICK_RE.findall(text) if token.strip()]


def _extract_keyword_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for token in ASCII_TOKEN_RE.findall(text):
        normalized = token.lower()
        if normalized not in STOPWORDS:
            tokens.append(normalized)
    for token in KOREAN_TOKEN_RE.findall(text):
        if token not in STOPWORDS:
            tokens.append(token)
    # preserve order while deduplicating
    return list(dict.fromkeys(tokens))


def _extract_phrase_tokens(text: str) -> list[str]:
    lowered = _normalize_text(text)
    tokens: list[str] = []
    for alias_group in PHRASE_ALIASES.values():
        if any(alias in lowered for alias in alias_group):
            tokens.extend(sorted(alias_group))
    return list(dict.fromkeys(tokens))


def _build_unit(uid: str, section: str, content: str, kind: str = "canonical") -> ArtifactUnit:
    if kind == "checklist_item":
        content = CHECKLIST_LABEL_RE.sub("", content).strip()
    explicit_tokens = _extract_explicit_tokens(content)
    keyword_tokens = _extract_keyword_tokens(content)
    for token in explicit_tokens:
        keyword_tokens.extend(_extract_keyword_tokens(token))
    keyword_tokens.extend(_extract_phrase_tokens(content))
    keyword_tokens = list(dict.fromkeys(keyword_tokens))
    return ArtifactUnit(
        uid=uid,
        section=section,
        text=content,
        normalized=_normalize_text(content),
        explicit_tokens=explicit_tokens,
        keyword_tokens=keyword_tokens,
        kind=kind,
    )


def _classify_kb_bullet(section: str, content: str, indent: int, has_children: bool) -> str:
    normalized_section = section.lower()
    stripped = content.strip()

    if normalized_section == "root":
        key = stripped.split(":", 1)[0].strip().lower()
        if key in SUPPORT_METADATA_KEYS:
            return "support"
        if key in KB_METADATA_KEYS:
            return "metadata"

    if normalized_section in IGNORED_KB_SECTIONS:
        if normalized_section == "table of contents" and INTERNAL_LINK_RE.match(stripped):
            return "toc"
        if any(stripped.lower().startswith(prefix) for prefix in SUPPORT_SECTION_PREFIXES):
            return "support"
        if normalized_section != "document map":
            return "reference_inventory"
        return "document_map"

    if INTERNAL_LINK_RE.match(stripped):
        return "toc"

    if normalized_section in SUPPORT_KB_SECTIONS:
        return "support"

    if normalized_section == "current implementation target":
        return "support"

    if has_children and any(stripped.endswith(hint) for hint in SUMMARY_PARENT_HINTS):
        return "support"

    if indent > 0 and normalized_section == "current implementation target":
        return "support"

    return "canonical"


def _parse_kb_bullets(path: Path) -> list[BulletEntry]:
    text = path.read_text(encoding="utf-8")
    entries: list[BulletEntry] = []
    section = "ROOT"

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue

        match = BULLET_LINE_RE.match(line)
        if not match:
            continue
        indent = len(match.group(1))
        content = match.group(2).strip()
        if not content:
            continue
        entries.append(BulletEntry(section=section, indent=indent, content=content))

    for idx, entry in enumerate(entries[:-1]):
        next_entry = entries[idx + 1]
        if next_entry.indent > entry.indent:
            entry.has_children = True

    return entries


def _extract_kb_units(path: Path) -> tuple[list[ArtifactUnit], list[ArtifactUnit], list[ArtifactUnit]]:
    units: list[ArtifactUnit] = []
    support_units: list[ArtifactUnit] = []
    ignored_units: list[ArtifactUnit] = []
    counter = 0
    support_counter = 0
    ignored_counter = 0

    for entry in _parse_kb_bullets(path):
        kind = _classify_kb_bullet(entry.section, entry.content, entry.indent, entry.has_children)
        if kind == "support":
            support_counter += 1
            support_units.append(_build_unit(f"KBS{support_counter:03d}", entry.section, entry.content, kind))
            continue
        if kind != "canonical":
            ignored_counter += 1
            ignored_units.append(_build_unit(f"KBI{ignored_counter:03d}", entry.section, entry.content, kind))
            continue

        counter += 1
        units.append(_build_unit(f"KB{counter:03d}", entry.section, entry.content))

    return units, support_units, ignored_units


def _detect_kb_profile(
    path: Path,
    kb_units: list[ArtifactUnit],
    support_kb_units: list[ArtifactUnit],
    ignored_kb_units: list[ArtifactUnit],
) -> str:
    parsed_sections = {entry.section.lower() for entry in _parse_kb_bullets(path)}
    has_canonical_sections = bool(
        {"canonical design takeaways", "current implementation target"} & parsed_sections
    )
    has_reference_inventory = any(unit.kind == "reference_inventory" for unit in ignored_kb_units)

    if kb_units and has_canonical_sections:
        return "hybrid_kb" if has_reference_inventory else "canonical_design_kb"
    if not kb_units and support_kb_units and has_reference_inventory:
        return "research_index_kb"
    if kb_units:
        return "canonical_design_kb"
    return "unknown_kb"


def _extract_checklist_units(path: Path) -> list[ArtifactUnit]:
    text = path.read_text(encoding="utf-8")
    units: list[ArtifactUnit] = []
    section = "ROOT"
    counter = 0

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue

        match = CHECKLIST_LINE_RE.match(line)
        if not match:
            continue
        content = match.group(1).strip()
        if not content:
            continue

        counter += 1
        units.append(_build_unit(f"CL{counter:03d}", section, content, "checklist_item"))

    return units


def _score_match(kb_unit: ArtifactUnit, checklist_item: ArtifactUnit) -> tuple[int, list[str]]:
    evidence: list[str] = []
    score = 0

    explicit_overlap = sorted(set(kb_unit.explicit_tokens) & set(checklist_item.explicit_tokens))
    if explicit_overlap:
        score += 10 + len(explicit_overlap)
        evidence.extend([f"explicit:{token}" for token in explicit_overlap])

    keyword_overlap = sorted(set(kb_unit.keyword_tokens) & set(checklist_item.keyword_tokens))
    if keyword_overlap:
        score += min(len(keyword_overlap), 4)
        evidence.extend([f"keyword:{token}" for token in keyword_overlap[:4]])

    if kb_unit.normalized in checklist_item.normalized or checklist_item.normalized in kb_unit.normalized:
        score += 2
        evidence.append("substring")

    return score, evidence


def _find_best_mapping(kb_units: list[ArtifactUnit], checklist_item: ArtifactUnit) -> tuple[ArtifactUnit | None, int, list[str]]:
    best_unit: ArtifactUnit | None = None
    best_score = 0
    best_evidence: list[str] = []

    for kb_unit in kb_units:
        score, evidence = _score_match(kb_unit, checklist_item)
        if score > best_score:
            best_unit = kb_unit
            best_score = score
            best_evidence = evidence

    return best_unit, best_score, best_evidence


def _is_guardrail_unit(kb_unit: ArtifactUnit) -> bool:
    text = kb_unit.normalized
    return any(marker in text for marker in NEGATION_MARKERS) or any(hint in text for hint in GUARDRAIL_HINTS)


def _is_scope_inflation(checklist_item: ArtifactUnit, kb_text: str) -> bool:
    item_text = checklist_item.normalized
    if not any(hint in item_text for hint in ADVANCED_EXPANSION_HINTS):
        return False
    return any(hint in kb_text for hint in ("section-level comparison", "anchor/keyword", "v0.1"))


def _violates_guardrail(kb_unit: ArtifactUnit, checklist_item: ArtifactUnit) -> bool:
    kb_text = kb_unit.normalized
    item_text = checklist_item.normalized

    if "semantic judge" in kb_text and "semantic judge" in item_text:
        if ("아니라" in kb_text or "candidate" in kb_text) and not any(
            token in item_text for token in ("candidate", "heuristic", "human review", "queue")
        ):
            return True

    if "최종 truth" in kb_text and any(token in item_text for token in ("semantic judge", "최종 truth", "단정", "자동")):
        return True

    if "section-level comparison" in kb_text and _is_scope_inflation(checklist_item, kb_text):
        return True

    return False


def _serialize_unit(unit: ArtifactUnit) -> dict:
    return {
        "id": unit.uid,
        "section": unit.section,
        "text": unit.text,
        "explicit_tokens": unit.explicit_tokens,
        "keyword_tokens": unit.keyword_tokens,
        "kind": unit.kind,
    }


def _load_metric_specs() -> dict[str, dict[str, str]]:
    if not METRIC_CONTRACT_PATH.is_file():
        raise ValueError(f"Missing metric contract file: {METRIC_CONTRACT_PATH}")

    payload = json.loads(METRIC_CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError("Metric contract must be a non-empty JSON object.")

    for metric_name, spec in payload.items():
        if not isinstance(spec, dict):
            raise ValueError(f"Metric spec for '{metric_name}' must be an object.")
        missing = [field for field in REQUIRED_METRIC_SPEC_FIELDS if not spec.get(field)]
        if missing:
            raise ValueError(
                f"Metric spec for '{metric_name}' is missing required fields: {', '.join(missing)}"
            )
    return payload


def _validate_metric_specs(metrics: dict[str, float | None], metric_specs: dict[str, dict[str, str]]) -> None:
    metric_keys = set(metrics)
    spec_keys = set(metric_specs)
    if metric_keys != spec_keys:
        missing_specs = sorted(metric_keys - spec_keys)
        extra_specs = sorted(spec_keys - metric_keys)
        detail = []
        if missing_specs:
            detail.append(f"missing specs: {', '.join(missing_specs)}")
        if extra_specs:
            detail.append(f"unused specs: {', '.join(extra_specs)}")
        raise ValueError("Metric/spec mismatch: " + "; ".join(detail))


def _build_payload(
    kb_profile: str,
    kb_units: list[ArtifactUnit],
    checklist_items: list[ArtifactUnit],
    support_kb_units: list[ArtifactUnit],
    ignored_kb_units: list[ArtifactUnit],
) -> dict:
    metric_specs = _load_metric_specs()
    mapping_pool = kb_units + support_kb_units
    kb_text = "\n".join(unit.normalized for unit in mapping_pool)
    warnings: list[str] = []
    verdicts: dict[str, list[dict]] = {
        "covered": [],
        "missing_from_checklist": [],
        "unsupported_in_checklist": [],
        "scope_inflation": [],
        "boundary_loss": [],
    }
    mappings: list[dict] = []
    human_review_queue: list[dict] = []
    matched_kb_unit_ids: set[str] = set()
    matched_support_unit_ids: set[str] = set()
    guardrail_violated_ids: set[str] = set()

    for checklist_item in checklist_items:
        best_unit, score, evidence = _find_best_mapping(mapping_pool, checklist_item)
        if best_unit is not None and score > 0:
            if _violates_guardrail(best_unit, checklist_item):
                verdict_entry = {
                    "kb_unit_id": best_unit.uid,
                    "kb_unit": best_unit.text,
                    "checklist_item_id": checklist_item.uid,
                    "checklist_item": checklist_item.text,
                    "reason": "guardrail contradiction",
                }
                verdicts["boundary_loss"].append(verdict_entry)
                human_review_queue.append(
                    {
                        "reason": "guardrail contradiction",
                        "kb_unit_id": best_unit.uid,
                        "checklist_item_id": checklist_item.uid,
                        "kb_unit": best_unit.text,
                        "checklist_item": checklist_item.text,
                    }
                )
                guardrail_violated_ids.add(best_unit.uid)
                continue

            if best_unit.kind == "canonical":
                matched_kb_unit_ids.add(best_unit.uid)
            elif best_unit.kind == "support":
                matched_support_unit_ids.add(best_unit.uid)
            mapping = Mapping(
                kb_unit_id=best_unit.uid,
                checklist_item_id=checklist_item.uid,
                score=score,
                evidence=evidence,
            )
            mappings.append(asdict(mapping))
            verdicts["covered"].append(
                {
                    "kb_unit_id": best_unit.uid,
                    "kb_unit": best_unit.text,
                    "checklist_item_id": checklist_item.uid,
                    "checklist_item": checklist_item.text,
                    "score": score,
                    "kb_unit_kind": best_unit.kind,
                }
            )
            if score <= 2:
                human_review_queue.append(
                    {
                        "reason": "low-confidence mapping",
                        "kb_unit_id": best_unit.uid,
                        "checklist_item_id": checklist_item.uid,
                        "kb_unit": best_unit.text,
                        "checklist_item": checklist_item.text,
                    }
                )
            continue

        if _is_scope_inflation(checklist_item, kb_text):
            verdicts["scope_inflation"].append(
                {
                    "checklist_item_id": checklist_item.uid,
                    "checklist_item": checklist_item.text,
                    "reason": "advanced requirement beyond KB baseline",
                }
            )
            human_review_queue.append(
                {
                    "reason": "scope inflation candidate",
                    "checklist_item_id": checklist_item.uid,
                    "checklist_item": checklist_item.text,
                }
            )
        else:
            verdicts["unsupported_in_checklist"].append(
                {
                    "checklist_item_id": checklist_item.uid,
                    "checklist_item": checklist_item.text,
                    "reason": "no KB support found",
                }
            )

    for kb_unit in kb_units:
        if kb_unit.uid in matched_kb_unit_ids or kb_unit.uid in guardrail_violated_ids:
            continue
        verdicts["missing_from_checklist"].append(
            {
                "kb_unit_id": kb_unit.uid,
                "kb_unit": kb_unit.text,
                "section": kb_unit.section,
                "reason": "no checklist item matched this KB unit",
            }
        )

    total_kb_units = len(kb_units)
    total_checklist_items = len(checklist_items)
    guardrail_units = [unit for unit in kb_units if _is_guardrail_unit(unit)]
    preserved_guardrails = [
        unit
        for unit in guardrail_units
        if (unit.uid in matched_kb_unit_ids or unit.uid in matched_support_unit_ids)
        and unit.uid not in guardrail_violated_ids
    ]
    traceable_items = len(mappings)

    coverage_ratio = round(len(matched_kb_unit_ids) / total_kb_units, 4) if total_kb_units else None
    if total_kb_units == 0:
        warnings.append(
            "KB canonical unit이 없습니다. 이 결과에서는 coverage_ratio를 해석하지 말고 "
            "KB를 canonical takeaway 중심으로 다시 정리해야 합니다."
        )
    if kb_profile == "research_index_kb":
        warnings.append(
            "현재 KB profile은 research_index_kb입니다. 이 pair는 reference inventory 중심이므로 "
            "canonical KB를 먼저 만든 뒤 checklist와 비교하는 것이 맞습니다."
        )

    metrics = {
        "coverage_ratio": coverage_ratio,
        "unsupported_item_ratio": round(
            len(verdicts["unsupported_in_checklist"]) / total_checklist_items,
            4,
        ) if total_checklist_items else 0.0,
        "traceability_ratio": round(traceable_items / total_checklist_items, 4) if total_checklist_items else 1.0,
        "boundary_preservation_ratio": round(
            len(preserved_guardrails) / len(guardrail_units),
            4,
        ) if guardrail_units else 1.0,
    }
    _validate_metric_specs(metrics, metric_specs)
    ignored_counts: dict[str, int] = {}
    for unit in ignored_kb_units:
        ignored_counts[unit.kind] = ignored_counts.get(unit.kind, 0) + 1
    support_counts: dict[str, int] = {}
    for unit in support_kb_units:
        support_counts[unit.kind] = support_counts.get(unit.kind, 0) + 1

    return {
        "kb_profile": kb_profile,
        "kb_units": [_serialize_unit(unit) for unit in kb_units],
        "support_kb_units": [_serialize_unit(unit) for unit in support_kb_units],
        "support_counts": support_counts,
        "ignored_kb_units": [_serialize_unit(unit) for unit in ignored_kb_units],
        "ignored_counts": ignored_counts,
        "checklist_items": [_serialize_unit(unit) for unit in checklist_items],
        "mappings": mappings,
        "metrics": metrics,
        "metric_specs": metric_specs,
        "warnings": warnings,
        "verdicts": verdicts,
        "human_review_queue": human_review_queue,
    }


def _render_markdown(payload: dict, kb_path: Path, checklist_path: Path) -> str:
    metrics = payload["metrics"]
    verdicts = payload["verdicts"]
    coverage_display = metrics["coverage_ratio"] if metrics["coverage_ratio"] is not None else "n/a"
    lines = [
        "# KB-To-Consistency Coverage Report",
        "",
        f"- kb: `{kb_path}`",
        f"- checklist: `{checklist_path}`",
        f"- kb_profile: `{payload['kb_profile']}`",
        "",
        "## Metrics",
        "",
    ]
    metric_specs = payload["metric_specs"]
    ordered_metric_names = (
        "coverage_ratio",
        "unsupported_item_ratio",
        "traceability_ratio",
        "boundary_preservation_ratio",
    )
    for metric_name in ordered_metric_names:
        value = coverage_display if metric_name == "coverage_ratio" else metrics[metric_name]
        spec = metric_specs[metric_name]
        lines.extend([
            f"- {metric_name}: `{value}`",
            f"  - class: `{spec['class']}`",
            f"  - formula: `{spec['formula']}`",
            f"  - semantic: {spec['semantic']}",
            f"  - execution_note: {spec['current_execution_note']}",
            f"  - interpretation: {spec['interpretation']}",
        ])
    lines.append("")
    if payload["warnings"]:
        lines.extend([
            "## Warnings",
            "",
        ])
        for warning in payload["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")
    lines.extend([
        "## Support KB Units",
        "",
    ])
    if not payload["support_kb_units"]:
        lines.append("- 없음")
    else:
        for kind, count in sorted(payload["support_counts"].items()):
            lines.append(f"- {kind}: `{count}`")
    lines.extend([
        "",
        "## Ignored KB Units",
        "",
    ])
    if not payload["ignored_kb_units"]:
        lines.append("- 없음")
    else:
        for kind, count in sorted(payload["ignored_counts"].items()):
            lines.append(f"- {kind}: `{count}`")
    lines.append("")

    for key in (
        "missing_from_checklist",
        "unsupported_in_checklist",
        "scope_inflation",
        "boundary_loss",
    ):
        lines.append(f"## {key}")
        items = verdicts.get(key, [])
        if not items:
            lines.append("")
            lines.append("- 없음")
            lines.append("")
            continue
        lines.append("")
        for item in items:
            label = item.get("kb_unit") or item.get("checklist_item") or item.get("reason", "item")
            lines.append(f"- {label}")
        lines.append("")

    lines.append("## Human Review Queue")
    lines.append("")
    if not payload["human_review_queue"]:
        lines.append("- 없음")
    else:
        for item in payload["human_review_queue"]:
            label = item.get("kb_unit") or item.get("checklist_item") or item.get("reason", "item")
            lines.append(f"- {item.get('reason', 'review')}: {label}")
    lines.append("")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether a knowledge base is reflected in a consistency checklist."
    )
    parser.add_argument("--kb", required=True, help="Knowledge base markdown file.")
    parser.add_argument("--checklist", required=True, help="Consistency checklist markdown file.")
    parser.add_argument("--output-json", help="Write machine-readable JSON output.")
    parser.add_argument("--output-md", help="Write human-readable markdown report.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    kb_path = Path(args.kb)
    checklist_path = Path(args.checklist)

    if not kb_path.is_file():
        print(f"[ERROR] Missing KB file: {kb_path}", file=sys.stderr)
        return 1
    if not checklist_path.is_file():
        print(f"[ERROR] Missing checklist file: {checklist_path}", file=sys.stderr)
        return 1

    kb_units, support_kb_units, ignored_kb_units = _extract_kb_units(kb_path)
    kb_profile = _detect_kb_profile(kb_path, kb_units, support_kb_units, ignored_kb_units)
    checklist_items = _extract_checklist_units(checklist_path)
    payload = _build_payload(kb_profile, kb_units, checklist_items, support_kb_units, ignored_kb_units)

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    markdown_report = _render_markdown(payload, kb_path, checklist_path)
    if args.output_md:
        output_path = Path(args.output_md)
        output_path.write_text(markdown_report, encoding="utf-8")

    print(
        "[INFO] "
        f"kb_units={len(payload['kb_units'])} "
        f"checklist_items={len(payload['checklist_items'])} "
        f"covered={len(payload['verdicts']['covered'])} "
        f"missing={len(payload['verdicts']['missing_from_checklist'])} "
        f"unsupported={len(payload['verdicts']['unsupported_in_checklist'])} "
        f"scope_inflation={len(payload['verdicts']['scope_inflation'])} "
        f"boundary_loss={len(payload['verdicts']['boundary_loss'])}"
    )
    for warning in payload["warnings"]:
        print(f"[WARN] {warning}", file=sys.stderr)

    if not args.output_json:
        print(json.dumps(payload["metrics"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
