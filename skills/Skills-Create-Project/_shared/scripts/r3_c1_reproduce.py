#!/usr/bin/env python3
"""R3/C1 audit-test reproduction harness (machine evidence, not prose).

Builds an ISOLATED temp bundle from the C1 *runnable* closure (exact pathspecs —
6 skills files + 11 template JSONs), runs the audit + regression test against the
bundle, and emits a sha256 closure manifest. Re-runnable, self-cleaning.

This proves CLOSURE COMPLETENESS (current local files reproduce the result). It is
NOT a durability proof — the closure files are untracked; durability needs a commit
binding both repos (see the manifest's `cross_repo` note).

Usage:
    python3 r3_c1_reproduce.py [--skills-root SR] [--msi-root MSI] [--manifest OUT.json]
Exit: 0 if bundle reproduces (audit all in_sync + tests pass), 1 otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))

# --- C1 RUNNABLE closure: EXACT pathspecs (NO directory adds) ---
SKILLS_FILES = [
    "_shared/scripts/audit_contract_sync.py",
    "_shared/scripts/test_audit_contract_sync.py",
    "agent-task-packet/scripts/packet_builder.py",
    "agent-task-packet/references/contracts/packet_contract_v0_1.json",
    "codex-worktree-dispatch/scripts/dispatch_manager.py",
    "codex-worktree-dispatch/references/contracts/dispatch_contract_v0_1.json",
]
TEMPLATE_FILES = [  # my-second-identity/template/*.json — EXACT 11, not `git add template/`
    "dispatch_state_extended_template.json",
    "dispatch_state_standard_template.json",
    "dispatch_template.json",
    "task_packet_extended_template.json",
    "task_packet_standard_template.json",
    "task_packet_template.json",
    "task_progress_state_template.json",
    "task_state_extended_template.json",
    "task_state_standard_template.json",
    "task_state_template.json",
    "template_manifest.json",
]
ROLE = {
    "_shared/scripts/audit_contract_sync.py": "C1 auditor (implementation)",
    "_shared/scripts/test_audit_contract_sync.py": "C1 regression test (14 cases)",
    "agent-task-packet/scripts/packet_builder.py": "BUILDER_PY (packet projection source)",
    "agent-task-packet/references/contracts/packet_contract_v0_1.json": "PACKET_REGISTRY",
    "codex-worktree-dispatch/scripts/dispatch_manager.py": "DISPATCH_MANAGER_PY (operational tables)",
    "codex-worktree-dispatch/references/contracts/dispatch_contract_v0_1.json": "DISPATCH_REGISTRY (canonical)",
}


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills-root", default=None,
                    help="Skills-Create-Project root (default: auto-derived from script location)")
    ap.add_argument("--msi-root", default=None,
                    help="[deprecated] my-second-identity repo root; use --template-root instead")
    ap.add_argument("--template-root", default=None,
                    help="template directory (default: {skills-root}/_shared/templates/)")
    ap.add_argument("--manifest", default=None, help="write closure manifest JSON here")
    args = ap.parse_args()
    sr = Path(args.skills_root) if args.skills_root else Path(__file__).resolve().parents[2]
    template_dir = (Path(args.template_root) if args.template_root
                    else Path(args.msi_root) / "template" if args.msi_root
                    else sr / "_shared" / "templates")

    closure = []
    for f in SKILLS_FILES:
        p = sr / f
        closure.append({"repo": "claude-gemini-communicator", "path": f, "abs": str(p),
                        "sha256": _sha(p) if p.is_file() else None, "role": ROLE[f], "used_in_verification": True})
    for f in TEMPLATE_FILES:
        p = template_dir / f
        closure.append({"repo": "skills-internal", "path": f"_shared/templates/{f}", "abs": str(p),
                        "sha256": _sha(p) if p.is_file() else None,
                        "role": "audit template input / template_manifest_inventory dir scan", "used_in_verification": True})

    print(f"# R3/C1 reproduction — {datetime.now(KST).isoformat(timespec='seconds')}")
    print("## sha256 closure (exact pathspecs)")
    for e in closure:
        print(f"  {e['sha256'] or 'MISSING':64.64}  {e['repo']:26}  {e['path']}")

    # --- build isolated bundle (templates now self-contained in _shared/templates/) ---
    root = Path(tempfile.mkdtemp()) / "closure"
    dst_sr = root / "claude-gemini-communicator" / "skills" / "Skills-Create-Project"
    ok = True
    for f in SKILLS_FILES:
        (dst_sr / f).parent.mkdir(parents=True, exist_ok=True)
        if (sr / f).is_file():
            shutil.copy2(sr / f, dst_sr / f)
        else:
            ok = False
    (dst_sr / "_shared" / "templates").mkdir(parents=True, exist_ok=True)
    for f in TEMPLATE_FILES:
        if (template_dir / f).is_file():
            shutil.copy2(template_dir / f, dst_sr / "_shared" / "templates" / f)
        else:
            ok = False

    nfiles = sum(1 for _ in root.rglob("*") if _.is_file())
    print(f"## isolated bundle: {nfiles} files (expect 17), tmp={root}")

    audit = subprocess.run([sys.executable, str(dst_sr / "_shared/scripts/audit_contract_sync.py"),
                            "--skills-root", str(dst_sr), "--format", "text"], capture_output=True, text=True)
    in_sync = audit.stdout.count("| in_sync |")
    print(f"## audit: exit={audit.returncode}, in_sync_rows={in_sync} (expect 17 / 17)")
    test = subprocess.run([sys.executable, str(dst_sr / "_shared/scripts/test_audit_contract_sync.py")],
                          capture_output=True, text=True)
    test_tail = (test.stderr or test.stdout).strip().splitlines()[-1:] or [""]
    print(f"## test: exit={test.returncode}, last='{test_tail[0]}'")

    shutil.rmtree(root.parent, ignore_errors=True)

    reproduced = ok and audit.returncode == 0 and in_sync == 17 and test.returncode == 0
    manifest = {
        "artifact": "C1 audit/test RUNNABLE closure (not R3 semantic/document closure)",
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "cross_repo": ("NOT ATOMIC — closure spans 2 repos (claude-gemini-communicator + my-second-identity); "
                       "all files untracked. Durable only if BOTH repos commit these exact paths and the "
                       "commit SHAs are recorded as a pair here. No commit binds them yet."),
        "reproduction": {"bundle_files": nfiles, "audit_exit": audit.returncode,
                         "audit_in_sync_rows": in_sync, "test_exit": test.returncode,
                         "reproduced": reproduced},
        "closure": closure,
        "decision_archive": {"repo": "my-second-identity", "branch": "docs/r3-decision-archive",
                             "note": "decision docs only (R3 note + handoff + closure report); NOT this runnable closure"},
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"## manifest written: {args.manifest}")
    print(f"## REPRODUCED={reproduced}")
    return 0 if reproduced else 1


if __name__ == "__main__":
    raise SystemExit(main())
