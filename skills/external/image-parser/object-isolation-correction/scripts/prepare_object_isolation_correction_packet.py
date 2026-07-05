#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


IssueType = Literal[
    "background_residue",
    "missing_object_part",
    "merged_objects",
    "wrong_target_selected",
    "overcrop",
    "undercrop",
    "transparent_cutout_needed",
    "split_decision_needed",
    "text_grounding_needed",
    "edge_artifact",
]


ALL_ISSUES: tuple[str, ...] = (
    "background_residue",
    "missing_object_part",
    "merged_objects",
    "wrong_target_selected",
    "overcrop",
    "undercrop",
    "transparent_cutout_needed",
    "split_decision_needed",
    "text_grounding_needed",
    "edge_artifact",
)


@dataclass(frozen=True)
class CorrectionPacket:
    source_image: str
    current_result: str | None
    issues: list[str]
    target_description: str | None
    route: str
    route_reason: str
    recommended_next_tools: list[str]
    recommended_actions: list[str]
    imagegen_prompt: str | None
    notes: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a bounded object-isolation correction packet that chooses "
            "between imagesorcery-first, imagegen-first, or hybrid."
        )
    )
    parser.add_argument("--source-image", required=True, help="Absolute path to the source image.")
    parser.add_argument("--current-result", help="Absolute path to the current isolation result, if it exists.")
    parser.add_argument(
        "--issue",
        action="append",
        required=True,
        choices=ALL_ISSUES,
        help="Repeatable issue label describing the current isolation problem.",
    )
    parser.add_argument(
        "--target-description",
        help="Short description of the exact object or component to keep.",
    )
    parser.add_argument(
        "--route",
        choices=["auto", "imagesorcery-first", "imagegen-first", "hybrid"],
        default="auto",
        help="Force a correction route or let the script choose automatically.",
    )
    parser.add_argument("--output-md", required=True, help="Markdown packet output path.")
    parser.add_argument("--output-json", help="Optional JSON sidecar output path.")
    return parser.parse_args()


def choose_route(issues: set[str], forced_route: str) -> tuple[str, str]:
    if forced_route != "auto":
        return forced_route, "Route was explicitly forced by the caller."

    if issues & {"merged_objects", "wrong_target_selected", "split_decision_needed", "text_grounding_needed"}:
        return (
            "imagesorcery-first",
            "The main problem is target selection, split choice, or deterministic boundary recovery.",
        )
    if issues & {"missing_object_part", "edge_artifact"}:
        return (
            "imagegen-first",
            "The main problem is visual damage in the current isolation result rather than object discovery.",
        )
    if issues & {"background_residue", "transparent_cutout_needed", "overcrop", "undercrop"}:
        return (
            "hybrid",
            "Deterministic masking is still useful, but the final result may need model-assisted cleanup.",
        )
    return (
        "imagesorcery-first",
        "Defaulting to deterministic object-boundary correction because the issue set does not clearly demand repair-first generation.",
    )


def build_recommended_actions(route: str, issues: set[str], target_description: str | None) -> tuple[list[str], list[str], str | None, list[str]]:
    tools: list[str] = []
    actions: list[str] = []
    notes: list[str] = []
    imagegen_prompt: str | None = None

    if route in {"imagesorcery-first", "hybrid"}:
        tools.extend(["imagesorcery-mcp.detect/find", "imagesorcery-mcp.fill", "imagesorcery-mcp.crop"])
        if issues & {"merged_objects", "wrong_target_selected", "split_decision_needed"}:
            actions.append(
                "Run `find` or `detect(return_geometry=true)` to recover the intended object boundary before any final crop."
            )
        if issues & {"background_residue", "transparent_cutout_needed"}:
            actions.append(
                "Use `fill` with a mask or polygon and `invert_areas=true` plus transparent output to isolate the target region."
            )
        if issues & {"overcrop", "undercrop"}:
            actions.append(
                "Use the corrected bbox or polygon to rebuild the crop before any model-assisted cleanup."
            )
        if issues & {"text_grounding_needed"}:
            actions.append(
                "Confirm whether OCR evidence is needed after the corrected boundary is chosen."
            )
            notes.append("If the boundary becomes acceptable and the remaining blocker is text, hand off to macos-ocr-evidence.")

    if route in {"imagegen-first", "hybrid"}:
        tools.append("imagegen")
        prompt_target = target_description or "the intended primary object"
        imagegen_prompt = (
            f"Use the provided image as the source. Keep only {prompt_target}. "
            "Repair missing or damaged edges, remove surrounding residue, and deliver a clean transparent-background cutout. "
            "Do not change the object identity, text, or core visual structure unless the current isolation result is visibly damaged."
        )
        actions.append(
            "Prepare a bounded multimodal edit prompt that preserves object identity while cleaning the current cutout."
        )

    if not target_description:
        notes.append("Target description was not provided; object identity may stay ambiguous across retries.")

    if not actions:
        actions.append("Inspect the source image and state the target object more explicitly before retrying correction.")

    return tools, actions, imagegen_prompt, notes


def build_packet(args: argparse.Namespace) -> CorrectionPacket:
    source_image = Path(args.source_image).resolve()
    if not source_image.is_file():
        raise SystemExit(f"Source image not found: {source_image}")

    current_result = None
    if args.current_result:
        current_result = str(Path(args.current_result).resolve())

    issues = list(dict.fromkeys(args.issue))
    route, route_reason = choose_route(set(issues), args.route)
    tools, actions, imagegen_prompt, notes = build_recommended_actions(
        route,
        set(issues),
        args.target_description,
    )
    return CorrectionPacket(
        source_image=str(source_image),
        current_result=current_result,
        issues=issues,
        target_description=args.target_description,
        route=route,
        route_reason=route_reason,
        recommended_next_tools=tools,
        recommended_actions=actions,
        imagegen_prompt=imagegen_prompt,
        notes=notes,
    )


def render_markdown(packet: CorrectionPacket) -> str:
    lines: list[str] = [
        "# Object Isolation Correction Packet",
        "",
        "## Inputs",
        "",
        f"- source_image: `{packet.source_image}`",
        f"- current_result: `{packet.current_result or 'n/a'}`",
        f"- issues: `{', '.join(packet.issues)}`",
        f"- target_description: `{packet.target_description or 'n/a'}`",
        "",
        "## Route",
        "",
        f"- chosen_route: `{packet.route}`",
        f"- reason: {packet.route_reason}",
        "",
        "## Recommended Next Tools",
        "",
    ]
    for tool in packet.recommended_next_tools:
        lines.append(f"- `{tool}`")

    lines.extend(["", "## Recommended Actions", ""])
    for action in packet.recommended_actions:
        lines.append(f"- {action}")

    lines.extend(["", "## imagegen Prompt", ""])
    if packet.imagegen_prompt:
        lines.append(f"> {packet.imagegen_prompt}")
    else:
        lines.append("> n/a")

    lines.extend(["", "## Notes", ""])
    if packet.notes:
        for note in packet.notes:
            lines.append(f"- {note}")
    else:
        lines.append("- n/a")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    packet = build_packet(args)

    output_md = Path(args.output_md).resolve()
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(packet), encoding="utf-8")

    if args.output_json:
        output_json = Path(args.output_json).resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(asdict(packet), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
