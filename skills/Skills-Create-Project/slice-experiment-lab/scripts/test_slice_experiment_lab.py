#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("slice_experiment_lab.py")


CONTRACT_ARTIFACT = {
    "status": "ok",
    "contract_family": "slice_seed_candidates_contract",
}
VALID_ARTIFACT = {
    "status": "valid",
    "contract_family": "slice_seed_candidates_validation",
}
INVALID_ARTIFACT = {
    "status": "invalid",
    "contract_family": "slice_seed_candidates_validation",
}


class SliceExperimentLabTest(unittest.TestCase):
    def test_help_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("emit-experiment-bundle-contract", result.stdout)
        self.assertIn("evaluate-experiment-bundle", result.stdout)
        self.assertIn("gate-strict-warning-policy", result.stdout)
        self.assertIn("suggest-triad-names", result.stdout)
        self.assertIn("capture-quick-validate", result.stdout)
        self.assertIn("capture-smoke-command", result.stdout)
        self.assertNotIn("bridge-quick-validate-artifact", result.stdout)
        self.assertNotIn("bridge-captured-smoke-to-bundle", result.stdout)

    def test_emit_contract_stdout_json(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "emit-experiment-bundle-contract"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["contract_family"], "slice_experiment_bundle_contract")
        self.assertIn("quick_validate_status", payload["required_fields"])
        self.assertNotIn("next_slice_candidate", payload["required_fields"])

    def test_evaluate_bundle_ready_for_next_slice(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            contract = tmp / "contract.json"
            valid = tmp / "valid.json"
            invalid = tmp / "invalid.json"
            bundle = tmp / "bundle.json"
            contract.write_text(json.dumps(CONTRACT_ARTIFACT), encoding="utf-8")
            valid.write_text(json.dumps(VALID_ARTIFACT), encoding="utf-8")
            invalid.write_text(json.dumps(INVALID_ARTIFACT), encoding="utf-8")
            bundle.write_text(
                json.dumps(
                    {
                        "skill_name": "dependency-slice-planner",
                        "current_slice": "slice_seed_candidates_contract",
                        "contract_artifact": str(contract),
                        "valid_artifact": str(valid),
                        "invalid_artifact": str(invalid),
                        "quick_validate_status": "passed",
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "evaluate-experiment-bundle", "--input-bundle", str(bundle)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["bundle_status"], "valid")
            self.assertEqual(payload["workflow_status"], "ready_for_next_slice")
            self.assertNotIn("recommended_next_slice", payload)
            self.assertNotIn("recommended_action", payload)

    def test_evaluate_bundle_hold_when_quick_validate_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            contract = tmp / "contract.json"
            valid = tmp / "valid.json"
            invalid = tmp / "invalid.json"
            bundle = tmp / "bundle.json"
            contract.write_text(json.dumps(CONTRACT_ARTIFACT), encoding="utf-8")
            valid.write_text(json.dumps(VALID_ARTIFACT), encoding="utf-8")
            invalid.write_text(json.dumps(INVALID_ARTIFACT), encoding="utf-8")
            bundle.write_text(
                json.dumps(
                    {
                        "skill_name": "dependency-slice-planner",
                        "current_slice": "slice_seed_candidates_contract",
                        "contract_artifact": str(contract),
                        "valid_artifact": str(valid),
                        "invalid_artifact": str(invalid),
                        "quick_validate_status": "failed",
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "evaluate-experiment-bundle", "--input-bundle", str(bundle)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["bundle_status"], "valid")
            self.assertEqual(payload["workflow_status"], "hold_current_slice")

    def test_evaluate_bundle_invalid_when_contract_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            valid = tmp / "valid.json"
            invalid = tmp / "invalid.json"
            bundle = tmp / "bundle.json"
            valid.write_text(json.dumps(VALID_ARTIFACT), encoding="utf-8")
            invalid.write_text(json.dumps(INVALID_ARTIFACT), encoding="utf-8")
            bundle.write_text(
                json.dumps(
                    {
                        "skill_name": "dependency-slice-planner",
                        "current_slice": "slice_seed_candidates_contract",
                        "contract_artifact": str(tmp / "missing.json"),
                        "valid_artifact": str(valid),
                        "invalid_artifact": str(invalid),
                        "quick_validate_status": "passed",
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "evaluate-experiment-bundle", "--input-bundle", str(bundle)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["bundle_status"], "invalid")
            self.assertEqual(payload["workflow_status"], "hold_current_slice")

    def test_gate_strict_warning_policy_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            capture = tmp / "quick-validate.json"
            output_json = tmp / "gate.json"
            output_md = tmp / "gate.md"
            capture.write_text(
                json.dumps(
                    {
                        "status": "passed",
                        "contract_family": "quick_validate_capture",
                        "warnings": [],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "gate-strict-warning-policy",
                    "--input-artifact",
                    str(capture),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["decision"], "pass")
            self.assertEqual(payload["warning_count"], 0)
            self.assertEqual(payload["error_count"], 0)
            self.assertNotIn("recommended_action", payload)
            self.assertIn("strict warning policy gate", output_md.read_text(encoding="utf-8"))

    def test_gate_strict_warning_policy_hold_on_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            capture = tmp / "quick-validate.json"
            capture.write_text(
                json.dumps(
                    {
                        "status": "passed",
                        "contract_family": "quick_validate_capture",
                        "warnings": ["SKILL.md line count is close to threshold"],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "gate-strict-warning-policy",
                    "--input-artifact",
                    str(capture),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(payload["decision"], "hold")
            self.assertEqual(payload["workflow_status"], "hold_current_slice")
            self.assertIn("warnings present under strict policy", payload["reasons"][0])

    def test_gate_strict_warning_policy_invalid_on_failed_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            capture = tmp / "quick-validate.json"
            capture.write_text(
                json.dumps(
                    {
                        "status": "failed",
                        "contract_family": "quick_validate_capture",
                        "warnings": [],
                        "errors": ["SKILL.md missing frontmatter"],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "gate-strict-warning-policy",
                    "--input-artifact",
                    str(capture),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(payload["decision"], "invalid")
            self.assertEqual(payload["workflow_status"], "hold_current_slice")
            self.assertIn("quick_validate capture status is failed", payload["reasons"])

    def test_emit_and_evaluate_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            contract = tmp / "contract.json"
            valid = tmp / "valid.json"
            invalid = tmp / "invalid.json"
            bundle = tmp / "bundle.json"
            output_contract_json = tmp / "out_contract.json"
            output_contract_md = tmp / "out_contract.md"
            output_eval_json = tmp / "out_eval.json"
            output_eval_md = tmp / "out_eval.md"
            contract.write_text(json.dumps(CONTRACT_ARTIFACT), encoding="utf-8")
            valid.write_text(json.dumps(VALID_ARTIFACT), encoding="utf-8")
            invalid.write_text(json.dumps(INVALID_ARTIFACT), encoding="utf-8")
            bundle.write_text(
                json.dumps(
                    {
                        "skill_name": "dependency-slice-planner",
                        "current_slice": "slice_seed_candidates_contract",
                        "contract_artifact": str(contract),
                        "valid_artifact": str(valid),
                        "invalid_artifact": str(invalid),
                        "quick_validate_status": "passed",
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-experiment-bundle-contract",
                    "--output-json",
                    str(output_contract_json),
                    "--output-md",
                    str(output_contract_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "evaluate-experiment-bundle",
                    "--input-bundle",
                    str(bundle),
                    "--output-json",
                    str(output_eval_json),
                    "--output-md",
                    str(output_eval_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            contract_payload = json.loads(output_contract_json.read_text(encoding="utf-8"))
            eval_payload = json.loads(output_eval_json.read_text(encoding="utf-8"))
            self.assertEqual(contract_payload["contract_family"], "slice_experiment_bundle_contract")
            self.assertEqual(eval_payload["workflow_status"], "ready_for_next_slice")
            self.assertIn("experiment_bundle contract", output_contract_md.read_text(encoding="utf-8"))
            self.assertIn("experiment_bundle evaluation", output_eval_md.read_text(encoding="utf-8"))

    def test_suggest_triad_names(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "suggest-triad-names",
                "--slice",
                "static_dependency_overlay_contract",
                "--timestamp",
                "2026-03-19-00-57",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        artifacts = payload["artifacts"]
        self.assertIn("static_dependency_overlay_contract-contract-smoke-at2026-03-19-00-57.json", artifacts["contract_json"])
        self.assertIn("invalid-validation", artifacts["invalid_json"])

    def test_capture_quick_validate(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "capture-quick-validate",
                "--skill-dir",
                "slice-experiment-lab",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["contract_family"], "quick_validate_capture")
        self.assertIn(payload["status"], {"passed", "failed"})
        self.assertIn("Validation", payload["final_stdout"])

    def test_capture_smoke_command_valid(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "capture-smoke-command",
                "--expected-status",
                "valid",
                "--label",
                "seed-valid",
                "--",
                sys.executable,
                "dependency-slice-planner/scripts/dependency_slice_planner.py",
                "validate-slice-seed-candidates",
                "--input-candidates",
                "dependency-slice-planner/references/slice-seed-candidates-sample-at2026-03-19-00-22.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["parsed_stdout_status"], "valid")

    def test_capture_smoke_command_invalid(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "capture-smoke-command",
                "--expected-status",
                "invalid",
                "--label",
                "seed-invalid",
                "--",
                sys.executable,
                "dependency-slice-planner/scripts/dependency_slice_planner.py",
                "validate-slice-seed-candidates",
                "--input-candidates",
                "dependency-slice-planner/references/slice-seed-candidates-invalid-sample-at2026-03-19-00-22.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "invalid")
        self.assertEqual(payload["parsed_stdout_status"], "invalid")


if __name__ == "__main__":
    unittest.main()
