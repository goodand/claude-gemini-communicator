#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from base64 import b64decode
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("agent_graph_ir.py")


VALID_SPEC = {
    "spec_version": "1.0.0",
    "agent_id": "desktop_screenshot_skill_agent",
    "title": "App Screenshot -> AI -> Action Loop",
    "variables": [
        {
            "name": "target_app",
            "meaning": "사용자가 지정한 대상 앱",
            "type": "string",
            "scope_id": "root",
            "unit": None,
        },
        {
            "name": "task_progress",
            "meaning": "전체 작업 진행률",
            "type": "float",
            "scope_id": "loop.exec",
            "unit": "ratio",
        },
    ],
    "nodes": [
        {"id": "n_observe", "kind": "observe", "label": "Capture Window", "tool": "capture_window", "scope_id": "root", "metadata": {}},
        {"id": "n_route_grounding", "kind": "router", "label": "Choose Grounding Path", "tool": None, "scope_id": "router.grounding", "metadata": {}},
        {"id": "n_ground_accessibility", "kind": "ground", "label": "Ground via UI Tree", "tool": "uia_grounder", "scope_id": "loop.exec", "metadata": {}},
        {"id": "n_ground_vision", "kind": "ground", "label": "Ground via Screenshot/OCR", "tool": "vision_grounder", "scope_id": "loop.exec", "metadata": {}},
        {"id": "n_plan", "kind": "plan", "label": "Plan Next Action", "tool": "llm_planner", "scope_id": "loop.exec", "metadata": {}},
        {"id": "n_act", "kind": "action", "label": "Execute Mouse/Keyboard", "tool": "desktop_executor", "scope_id": "loop.exec", "metadata": {}},
        {"id": "n_reflect", "kind": "reflect", "label": "Reflect / Verify Progress", "tool": "llm_reflector", "scope_id": "loop.exec", "metadata": {}},
        {"id": "n_stop_success", "kind": "stop", "label": "Success", "tool": None, "scope_id": "root", "metadata": {"terminal": True}},
        {"id": "n_stop_fail", "kind": "stop", "label": "Escalate", "tool": None, "scope_id": "root", "metadata": {"terminal": True}},
    ],
    "edges": [
        {"id": "e1", "src": "n_observe", "dst": "n_route_grounding", "scope_id": "root", "route_id": None, "condition_id": None},
        {"id": "e2", "src": "n_route_grounding", "dst": "n_ground_accessibility", "scope_id": "router.grounding", "route_id": "route_accessibility", "condition_id": "cond_route_accessibility"},
        {"id": "e3", "src": "n_route_grounding", "dst": "n_ground_vision", "scope_id": "router.grounding", "route_id": "route_vision", "condition_id": "cond_route_vision"},
        {"id": "e4", "src": "n_ground_accessibility", "dst": "n_plan", "scope_id": "loop.exec", "route_id": None, "condition_id": None},
        {"id": "e5", "src": "n_ground_vision", "dst": "n_plan", "scope_id": "loop.exec", "route_id": None, "condition_id": "cond_grounded"},
        {"id": "e6", "src": "n_plan", "dst": "n_act", "scope_id": "loop.exec", "route_id": None, "condition_id": None},
        {"id": "e7", "src": "n_act", "dst": "n_reflect", "scope_id": "loop.exec", "route_id": None, "condition_id": None},
        {"id": "e8", "src": "n_reflect", "dst": "n_observe", "scope_id": "loop.exec", "route_id": None, "condition_id": "cond_continue"},
        {"id": "e9", "src": "n_reflect", "dst": "n_stop_success", "scope_id": "loop.exec", "route_id": None, "condition_id": "cond_done"},
        {"id": "e10", "src": "n_reflect", "dst": "n_stop_fail", "scope_id": "loop.exec", "route_id": None, "condition_id": "cond_abort"},
    ],
    "scopes": [
        {"id": "root", "kind": "root", "parent_scope_id": None, "router": None, "loop": None},
        {
            "id": "router.grounding",
            "kind": "router",
            "parent_scope_id": "root",
            "router": {"router_id": "r_grounding", "selection_policy": "first_true", "default_route_id": "route_vision"},
            "loop": None,
        },
        {
            "id": "loop.exec",
            "kind": "loop",
            "parent_scope_id": "root",
            "router": None,
            "loop": {"loop_id": "loop_exec", "max_iterations": 12, "break_condition_id": "cond_done", "timeout_ms": 90000},
        },
    ],
    "conditions": {
        "cond_app_supported": {"kind": "binary", "op": "in", "left": {"kind": "var", "name": "target_app"}, "right": {"kind": "const", "value": ["notepad", "calculator", "chrome"]}},
        "cond_has_ui_tree": {"kind": "binary", "op": "eq", "left": {"kind": "var", "name": "obs.ui_tree_available"}, "right": {"kind": "const", "value": True}},
        "cond_route_accessibility": {"kind": "nary", "op": "and", "args": [{"kind": "ref", "id": "cond_app_supported"}, {"kind": "ref", "id": "cond_has_ui_tree"}]},
        "cond_route_vision": {"kind": "unary", "op": "not", "arg": {"kind": "ref", "id": "cond_route_accessibility"}},
        "cond_grounded": {"kind": "binary", "op": "gte", "left": {"kind": "var", "name": "grounding_confidence"}, "right": {"kind": "const", "value": 0.85}},
        "cond_done": {"kind": "binary", "op": "gte", "left": {"kind": "var", "name": "task_progress"}, "right": {"kind": "const", "value": 0.99}},
        "cond_abort": {"kind": "binary", "op": "eq", "left": {"kind": "var", "name": "stop_reason"}, "right": {"kind": "const", "value": "user_cancelled"}},
        "cond_continue": {"kind": "nary", "op": "and", "args": [{"kind": "unary", "op": "not", "arg": {"kind": "ref", "id": "cond_done"}}, {"kind": "unary", "op": "not", "arg": {"kind": "ref", "id": "cond_abort"}}]},
    },
    "formulae": {
        "efficiency_score": {
            "ast": {
                "kind": "nary",
                "op": "add",
                "args": [
                    {"kind": "nary", "op": "mul", "args": [{"kind": "const", "value": 0.5}, {"kind": "var", "name": "task_progress"}]},
                    {"kind": "nary", "op": "mul", "args": [{"kind": "const", "value": 0.3}, {"kind": "var", "name": "grounding_confidence"}]},
                    {"kind": "nary", "op": "mul", "args": [{"kind": "const", "value": 0.2}, {"kind": "var", "name": "action_success_rate"}]},
                ],
            },
            "latex": "S_{eff}=0.5p+0.3g+0.2a",
        }
    },
    "router_decisions": [
        {
            "router_id": "r_grounding",
            "routes": [
                {"route_id": "route_accessibility", "condition_id": "cond_route_accessibility"},
                {"route_id": "route_vision", "condition_id": "cond_route_vision"},
            ],
            "selection_policy": "first_true",
        }
    ],
    "validation_rules": [
        {"id": "VR001", "severity": "error", "message": "모든 node_id는 unique여야 한다."}
    ],
}


VALID_RUN = {
    "summary": {
        "trace_id": "tr_01JXYZ",
        "session_id": "sess_2026-03-13_demo",
        "status": "success",
        "stop_reason": "task_completed",
        "latency_ms": 8210,
        "raw_action_count": 6,
        "final_action_count": 5,
        "selected_routes": [{"router_id": "r_grounding", "selected_route": "route_vision"}],
        "loop_iterations": {"loop_exec": 4},
        "metadata": {"target_app": "Calculator"},
    },
    "trace": [
        {
            "step_id": "s1",
            "node_id": "n_observe",
            "scope_instance_id": "root#0",
            "iteration_id": 0,
            "timestamp": "2026-03-13T09:00:00Z",
            "input": {"target_app": "Calculator"},
            "output": {
                "artifact_ref": "artifact://screens/1.png",
                "file_path": "/tmp/1.png",
                "sha256": "deadbeef" * 8,
                "width": 1440,
                "height": 900,
                "mime_type": "image/png",
                "capture_mode": "window",
                "ui_tree_available": False,
            },
            "metadata": {},
            "tool_call": {"tool_name": "capture_window", "latency_ms": 140, "input": {}, "output": {}},
        },
        {
            "step_id": "s2",
            "node_id": "n_route_grounding",
            "scope_instance_id": "router.grounding#0",
            "iteration_id": 0,
            "timestamp": "2026-03-13T09:00:00.150Z",
            "selected_route": "route_vision",
            "input": {},
            "output": {},
            "metadata": {},
        },
        {
            "step_id": "s3",
            "node_id": "n_ground_vision",
            "scope_instance_id": "loop.exec#0",
            "iteration_id": 1,
            "timestamp": "2026-03-13T09:00:00.300Z",
            "input": {},
            "output": {"grounding_confidence": 0.88},
            "metadata": {},
        },
        {
            "step_id": "s4",
            "node_id": "n_plan",
            "scope_instance_id": "loop.exec#0",
            "iteration_id": 1,
            "timestamp": "2026-03-13T09:00:00.450Z",
            "input": {},
            "output": {"action": "click"},
            "metadata": {},
        },
        {
            "step_id": "s5",
            "node_id": "n_act",
            "scope_instance_id": "loop.exec#0",
            "iteration_id": 1,
            "timestamp": "2026-03-13T09:00:00.700Z",
            "input": {},
            "output": {"action_success": True},
            "metadata": {},
            "tool_call": {"tool_name": "desktop_executor", "latency_ms": 92, "input": {}, "output": {}},
        },
        {
            "step_id": "s6",
            "node_id": "n_reflect",
            "scope_instance_id": "loop.exec#0",
            "iteration_id": 1,
            "timestamp": "2026-03-13T09:00:01.000Z",
            "stop_reason": "task_completed",
            "input": {},
            "output": {"task_progress": 1.0, "continue": False},
            "metadata": {},
        },
    ],
}


class AgentGraphIrCLITest(unittest.TestCase):
    @staticmethod
    def _write_png(path: Path) -> None:
        path.write_bytes(
            b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7ZP9sAAAAASUVORK5CYII="
            )
        )

    def _write_json(self, tmpdir: str, name: str, payload: dict) -> Path:
        path = Path(tmpdir) / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_help_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("emit-json-schema", result.stdout)
        self.assertIn("validate-spec", result.stdout)
        self.assertIn("emit-trace-json", result.stdout)
        self.assertIn("plan-capture", result.stdout)
        self.assertIn("emit-observe-event", result.stdout)
        self.assertIn("emit-observe-events-from-screenshot-output", result.stdout)
        self.assertIn("run-screenshot-bridge", result.stdout)

    def test_emit_json_schema(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "emit-json-schema"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_name"], "AgentSpec")
        self.assertIn("agent_id", payload["schema"]["properties"])

    def test_validate_spec_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = self._write_json(tmpdir, "spec.json", VALID_SPEC)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "validate-spec", "--input", str(spec_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["issue_count"], 0)

    def test_validate_spec_detects_duplicate_node_and_router_edges(self) -> None:
        broken_spec = json.loads(json.dumps(VALID_SPEC))
        broken_spec["nodes"].append(broken_spec["nodes"][0])
        broken_spec["edges"] = broken_spec["edges"][:1]

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = self._write_json(tmpdir, "broken_spec.json", broken_spec)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "validate-spec", "--input", str(spec_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("VR001", codes)
            self.assertIn("VR013", codes)

    def test_validate_spec_detects_illegal_sibling_scope_jump(self) -> None:
        broken_spec = json.loads(json.dumps(VALID_SPEC))
        broken_spec["scopes"].append(
            {
                "id": "loop.review",
                "kind": "loop",
                "parent_scope_id": "root",
                "router": None,
                "loop": {"loop_id": "loop_review", "max_iterations": 2, "break_condition_id": "cond_done", "timeout_ms": 5000},
            }
        )
        broken_spec["nodes"].append(
            {
                "id": "n_review",
                "kind": "plan",
                "label": "Review State",
                "tool": "reviewer",
                "scope_id": "loop.review",
                "metadata": {},
            }
        )
        broken_spec["edges"].append(
            {
                "id": "e11",
                "src": "n_act",
                "dst": "n_review",
                "scope_id": "loop.exec",
                "route_id": None,
                "condition_id": None,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = self._write_json(tmpdir, "broken_scope_spec.json", broken_spec)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "validate-spec", "--input", str(spec_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("VR023", codes)

    def test_plan_capture_prefers_tool_specific_then_window_then_desktop(self) -> None:
        request = {
            "target_app": "Calculator",
            "window_name": "Calculator",
            "tool_name": "playwright_screenshot",
            "prefer_tool_specific": True,
            "allow_desktop_fallback": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            request_path = self._write_json(tmpdir, "capture_request.json", request)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "plan-capture", "--input", str(request_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            route_ids = [route["route_id"] for route in payload["routes"]]
            self.assertEqual(route_ids[0], "route_tool_specific")
            self.assertIn("route_window_capture", route_ids)
            self.assertEqual(route_ids[-1], "route_desktop_fallback")

    def test_render_dot_and_mermaid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = self._write_json(tmpdir, "spec.json", VALID_SPEC)

            dot_result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "render-dot", "--input", str(spec_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("digraph AgentGraphIR", dot_result.stdout)
            self.assertIn("n_observe -> n_route_grounding", dot_result.stdout)

            mermaid_result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "render-mermaid", "--input", str(spec_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("flowchart LR", mermaid_result.stdout)
            self.assertIn('subgraph scope_root["root"]', mermaid_result.stdout)
            self.assertIn('subgraph scope_router_grounding["router.grounding"]', mermaid_result.stdout)
            self.assertIn("n_route_grounding -->|route_vision| n_ground_vision", mermaid_result.stdout)

    def test_validate_run_and_emit_trace_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = self._write_json(tmpdir, "spec.json", VALID_SPEC)
            run_path = self._write_json(tmpdir, "run.json", VALID_RUN)

            validate_result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "validate-run", "--spec", str(spec_path), "--run", str(run_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            validate_payload = json.loads(validate_result.stdout)
            self.assertEqual(validate_payload["issue_count"], 0)

            trace_result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "emit-trace-json", "--spec", str(spec_path), "--run", str(run_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            trace_payload = json.loads(trace_result.stdout)
            self.assertEqual(trace_payload["trace_id"], "tr_01JXYZ")
            self.assertEqual(trace_payload["run_summary"]["status"], "success")
            self.assertEqual(trace_payload["scores"][0]["name"], "task_completed")
            self.assertGreaterEqual(len(trace_payload["observations"]), 2)
            observation_by_id = {obs["id"]: obs for obs in trace_payload["observations"]}
            self.assertIn("scope::loop.exec#0", observation_by_id)
            self.assertEqual(observation_by_id["s3"]["parent_id"], "scope::loop.exec#0")

    def test_emit_observe_event_includes_artifact_fields(self) -> None:
        request = {
            "target_app": "Calculator",
            "window_name": "Calculator",
            "prefer_tool_specific": False,
            "allow_desktop_fallback": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            request_path = self._write_json(tmpdir, "capture_request.json", request)
            artifact_path = Path(tmpdir) / "capture.png"
            self._write_png(artifact_path)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-observe-event",
                    "--request",
                    str(request_path),
                    "--artifact",
                    str(artifact_path),
                    "--step-id",
                    "s_capture",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["step_id"], "s_capture")
            self.assertEqual(payload["output"]["artifact_ref"], "artifact://screens/capture.png")
            self.assertEqual(payload["output"]["width"], 1)
            self.assertEqual(payload["output"]["height"], 1)
            self.assertEqual(payload["output"]["capture_mode"], "window")
            self.assertEqual(payload["metadata"]["capture_route_id"], "route_window_capture")

    def test_emit_observe_events_from_screenshot_output_handles_multiple_paths(self) -> None:
        request = {
            "target_app": "Calculator",
            "window_name": "Calculator",
            "prefer_tool_specific": False,
            "allow_desktop_fallback": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            request_path = self._write_json(tmpdir, "capture_request.json", request)
            artifact_one = Path(tmpdir) / "capture-1.png"
            artifact_two = Path(tmpdir) / "capture-2.png"
            self._write_png(artifact_one)
            self._write_png(artifact_two)
            stdout_file = Path(tmpdir) / "paths.txt"
            stdout_file.write_text(f"{artifact_one}\n{artifact_two}\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-observe-events-from-screenshot-output",
                    "--request",
                    str(request_path),
                    "--stdout-file",
                    str(stdout_file),
                    "--step-prefix",
                    "s_capture",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["event_count"], 2)
            first_event, second_event = payload["events"]
            self.assertEqual(first_event["step_id"], "s_capture_001")
            self.assertEqual(second_event["step_id"], "s_capture_002")
            self.assertEqual(first_event["tool_call"]["tool_name"], "openai_curated_screenshot_skill")
            self.assertEqual(first_event["metadata"]["capture_output_count"], 2)
            self.assertEqual(second_event["output"]["capture_mode"], "window")

    def test_run_screenshot_bridge_emits_partial_run(self) -> None:
        request = {
            "target_app": "Calculator",
            "window_name": "Calculator",
            "prefer_tool_specific": False,
            "allow_desktop_fallback": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            request_path = self._write_json(tmpdir, "capture_request.json", request)
            spec_path = self._write_json(tmpdir, "spec.json", VALID_SPEC)
            artifact_one = Path(tmpdir) / "capture-1.png"
            artifact_two = Path(tmpdir) / "capture-2.png"
            self._write_png(artifact_one)
            self._write_png(artifact_two)

            emitter_script = Path(tmpdir) / "emit_paths.py"
            emitter_script.write_text(
                "import sys\nfor arg in sys.argv[1:]:\n    print(arg)\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "run-screenshot-bridge",
                    "--request",
                    str(request_path),
                    "--trace-id",
                    "tr_capture",
                    "--session-id",
                    "sess_capture",
                    "--command",
                    sys.executable,
                    str(emitter_script),
                    str(artifact_one),
                    str(artifact_two),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["returncode"], 0)
            self.assertIn("capture-1.png", payload["stdout"])
            self.assertEqual(payload["run"]["summary"]["trace_id"], "tr_capture")
            self.assertEqual(payload["run"]["summary"]["status"], "partial")
            self.assertEqual(len(payload["run"]["trace"]), 2)

            run_path = self._write_json(tmpdir, "capture_run.json", payload["run"])
            validate_result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "validate-run", "--spec", str(spec_path), "--run", str(run_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            validate_payload = json.loads(validate_result.stdout)
            self.assertEqual(validate_payload["issue_count"], 0)

    def test_validate_run_detects_missing_stop_reason(self) -> None:
        broken_run = json.loads(json.dumps(VALID_RUN))
        broken_run["summary"]["stop_reason"] = None
        broken_run["trace"][-1]["stop_reason"] = None

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = self._write_json(tmpdir, "spec.json", VALID_SPEC)
            run_path = self._write_json(tmpdir, "run.json", broken_run)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "validate-run", "--spec", str(spec_path), "--run", str(run_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RR006", codes)

    def test_validate_run_detects_missing_observe_artifact_fields(self) -> None:
        broken_run = json.loads(json.dumps(VALID_RUN))
        broken_run["trace"][0]["output"] = {"artifact_ref": "artifact://screens/1.png"}

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = self._write_json(tmpdir, "spec.json", VALID_SPEC)
            run_path = self._write_json(tmpdir, "run.json", broken_run)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "validate-run", "--spec", str(spec_path), "--run", str(run_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RR009", codes)


if __name__ == "__main__":
    unittest.main()
