#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


DOCUMENT_EXTS = {".md", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
SCRIPT_EXTS = {".py", ".sh", ".js", ".ts", ".tsx", ".jsx", ".rb", ".go", ".rs"}

INDEX_DOC = "references/indexes/kb-checklist-pipeline-branch-index-at2026-03-16-23-11.md"
DOC_BRANCH_DOC = "references/families/document-output-branch-at2026-03-16-23-11.md"
IMPL_BRANCH_DOC = "references/families/implementation-output-branch-at2026-03-16-23-11.md"
CANONICAL_KB = "knowledge_bases/kb-checklist-pipeline-canonical-design-at2026-03-16-23-11.md"
CONSISTENCY = "checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-11.md"
IMPLEMENTATION = "checklist-forimplementation/implementation-checklist-at2026-03-16-23-11.md"
BASELINE_DIFF_BRIDGE = "references/families/baseline-diff-bridge-at2026-03-16-23-17.md"
BASELINE_DIFF_METRICIZE = "../baseline-diff-lab/scripts/metricize_smoke_report.py"
EXECUTION_EVIDENCE_PATTERN = "../skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md"
EXECUTION_EVIDENCE_PLANNER = "../skill-creation-process/scripts/execution_evidence_planner.py"


def _execution_evidence_handoff() -> dict[str, object]:
    return {
        "target_skill": "evidence-trace-auditor",
        "pattern_doc": EXECUTION_EVIDENCE_PATTERN,
        "planner_script": EXECUTION_EVIDENCE_PLANNER,
        "sequence": [
            "preserve raw smoke artifact",
            "build evidence ledger",
            "audit support against contract_diff_basis",
            "record troubleshooting and residual uncertainty",
        ],
    }


def _baseline_diff_handoff() -> dict[str, object]:
    return {
        "target_skill": "baseline-diff-lab",
        "bridge_doc": BASELINE_DIFF_BRIDGE,
        "requires_metricize_when": "upstream artifact is raw smoke report without metrics dict",
        "metricize_script": BASELINE_DIFF_METRICIZE,
        "sequence": [
            "metricize raw smoke report if needed",
            "plan baseline diff artifacts",
            "compute before/after diff",
        ],
    }


def classify_artifact(target: str, artifact_kind: str) -> str:
    if artifact_kind != "auto":
        return artifact_kind

    suffix = Path(target).suffix.lower()
    if suffix in DOCUMENT_EXTS:
        return "document_output"
    if suffix in SCRIPT_EXTS:
        return "script_output"
    return "implementation_output"


def plan(branch: str) -> dict[str, object]:
    base_read_order = [INDEX_DOC, CANONICAL_KB, CONSISTENCY, IMPLEMENTATION]
    if branch == "document_output":
        return {
            "branch": branch,
            "tdd_required": False,
            "read_order": [INDEX_DOC, DOC_BRANCH_DOC, CANONICAL_KB, CONSISTENCY, IMPLEMENTATION],
            "execution_evidence_handoff": None,
            "baseline_diff_handoff": None,
            "next_actions": [
                "문서 산출물 작성",
                "필요하면 evidence/reference 추가",
            ],
        }
    if branch == "script_output":
        return {
            "branch": branch,
            "tdd_required": True,
            "read_order": [INDEX_DOC, IMPL_BRANCH_DOC, CANONICAL_KB, CONSISTENCY, IMPLEMENTATION],
            "execution_evidence_handoff": _execution_evidence_handoff(),
            "baseline_diff_handoff": _baseline_diff_handoff(),
            "next_actions": [
                "TDD 파일 생성",
                "script 구현",
                "smoke test 실행",
                "raw smoke artifact 저장",
                "evidence ledger/support audit 계산",
                "debug 메모 작성",
                "raw smoke면 metricize 후 before/after diff 작성",
            ],
        }
    return {
        "branch": "implementation_output",
        "tdd_required": True,
        "read_order": [INDEX_DOC, IMPL_BRANCH_DOC, CANONICAL_KB, CONSISTENCY, IMPLEMENTATION],
        "execution_evidence_handoff": _execution_evidence_handoff(),
        "baseline_diff_handoff": _baseline_diff_handoff(),
        "next_actions": [
            "검증 파일 생성",
            "구현물 생성",
            "raw smoke artifact 저장",
            "evidence ledger/support audit 계산",
            "debug 메모 작성",
            "raw smoke면 metricize 후 before/after diff 작성",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="kb-checklist-pipeline branch router")
    parser.add_argument("--target", required=True, help="planned output path or filename")
    parser.add_argument(
        "--artifact-kind",
        default="auto",
        choices=["auto", "document_output", "script_output", "implementation_output"],
        help="artifact branch override",
    )
    args = parser.parse_args()

    branch = classify_artifact(args.target, args.artifact_kind)
    payload = {
        "target": args.target,
        "artifact_kind": branch,
    }
    payload.update(plan(branch))
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
