#!/usr/bin/env python3
"""Tests for agent task packet builder — standard/extended profile 포함."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
import unittest

from packet_builder import (
    DISPATCH_STATUSES, DISPATCH_TRANSITIONS,
    EXTENDED_FIELDS, FORBIDDEN_FIELDS,
    _detect_profile, cmd_new, make_scaffold, render_prompt,
    response_coverage, validate_dispatch, validate_dispatch_transition,
    validate_packet,
)


def _valid_packet(**overrides):
    packet = make_scaffold("TASK-UNIT-01", "Smoke validation task")
    packet.update(
        {
            "goal": "Create a reliable packet with clear scope and done conditions.",
            "why": "Subagents need bounded handoff to avoid scope drift.",
            "allowed_paths": ["agent-task-packet/SKILL.md"],
            "context_files": ["agent-task-packet/references/packet-fields.md"],
            "done_definition": ["Create packet file", "Run packet_builder validate"],
            "required_checks": [
                {"type": "command", "value": "python3 -m py_compile scripts/packet_builder.py", "required": True}
            ],
            "deliverables": [
                {"path": "agent-task-packet/SKILL.md", "type": "doc", "required": True}
            ],
            "created_by": "agent-test",
            "updated_at": "2026-03-19T22:24:00+09:00",
            "created_at": "2026-03-19T22:24:00+09:00",
        }
    )
    packet.update(overrides)
    return packet


def _valid_extended_packet(**overrides):
    packet = make_scaffold("TASK-EXT-01", "Extended profile task", profile="extended")
    packet.update(
        {
            "goal": "Validate extended profile fields work correctly.",
            "why": "Extended profile needs regression-free validation path.",
            "allowed_paths": ["src/"],
            "context_files": ["docs/spec.md"],
            "done_definition": ["Extended fields validate without error"],
            "required_checks": [
                {"type": "command", "value": "python3 -m pytest", "required": True}
            ],
            "deliverables": [
                {"path": "src/module.py", "type": "source", "required": True}
            ],
            "created_by": "agent-test",
            "repo_root": ".",
            "source_of_truth": "docs/spec.md",
            "env_requirements": {"python": ">=3.9"},
            "stop_conditions": ["spec 범위 초과 시"],
            "timeout_minutes": 60,
        }
    )
    packet.update(overrides)
    return packet


# ──────────────────────────────────────────────────────────
# Standard Packet Tests (v0.1 zero-regression)
# ──────────────────────────────────────────────────────────

class TestStandardPacket(unittest.TestCase):
    def test_validate_accepts_minimal_valid_packet(self):
        errors, warnings = validate_packet(_valid_packet())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_validate_rejects_empty_why_and_task_id(self):
        errors, _ = validate_packet(_valid_packet(why="   ", task_id="   "))
        self.assertIn("why가 너무 짧다 (최소 5자) — 이 작업이 필요한 이유를 명시해야 한다", errors)
        self.assertIn("task_id가 비어있다", errors)

    def test_validate_rejects_forbidden_fields(self):
        for field in ("status", "session_id", "pid", "log_path",
                       "worktree_path", "branch", "locked_paths", "dispatch_id"):
            packet = _valid_packet()
            packet[field] = "should-fail"
            errors, _ = validate_packet(packet)
            self.assertTrue(any(field in e for e in errors), f"'{field}' should be rejected")

    def test_validate_rejects_heartbeat_path_runtime_field(self):
        """heartbeat_path는 dispatch/runtime 소유 — packet에서 금지 (instruction acceptance)."""
        packet = _valid_packet()
        packet["heartbeat_path"] = ".codex/dispatch/TASK-UNIT-01.heartbeat"
        errors, _ = validate_packet(packet)
        self.assertTrue(any("heartbeat_path" in e for e in errors))

    def test_structured_required_checks_validate_and_preserve(self):
        """구조화 required_checks(type/target/operator/expected/required/evidence_path)는
        에러 없이 검증되고 JSON round-trip에서 필드가 보존된다."""
        check = {
            "type": "command",
            "target": "scripts/packet_builder.py",
            "operator": "exit_code_eq",
            "expected": 0,
            "required": True,
            "evidence_path": "logs/smoke/packet_validate.txt",
        }
        packet = _valid_packet(required_checks=[check])
        errors, _ = validate_packet(packet)
        self.assertEqual(errors, [])
        roundtrip = json.loads(json.dumps(packet))
        rc = roundtrip["required_checks"][0]
        for key in ("type", "target", "operator", "expected", "required", "evidence_path"):
            self.assertIn(key, rc)

    def test_render_prompt_surfaces_structured_check_fields(self):
        """render_prompt는 구조화 check의 target/operator/expected/evidence_path를 잃지 않는다."""
        check = {
            "type": "command",
            "target": "scripts/packet_builder.py",
            "operator": "exit_code_eq",
            "expected": 0,
            "required": True,
            "evidence_path": "logs/smoke/packet_validate.txt",
        }
        output = render_prompt(_valid_packet(required_checks=[check]))
        self.assertIn("target=scripts/packet_builder.py", output)
        self.assertIn("operator=exit_code_eq", output)
        self.assertIn("expected=0", output)
        self.assertIn("evidence_path=logs/smoke/packet_validate.txt", output)

    def test_validate_rejects_missing_required(self):
        packet = _valid_packet()
        del packet["goal"]
        errors, _ = validate_packet(packet)
        self.assertTrue(any("필수 필드 누락" in e for e in errors))

    def test_validate_rejects_empty_allowed_paths(self):
        errors, _ = validate_packet(_valid_packet(allowed_paths=[]))
        self.assertTrue(any("allowed_paths" in e for e in errors))

    def test_validate_rejects_short_goal(self):
        errors, _ = validate_packet(_valid_packet(goal="short"))
        self.assertTrue(any("goal이 너무 짧다" in e for e in errors))

    def test_done_definition_must_be_nonempty(self):
        errors, _ = validate_packet(_valid_packet(done_definition=[]))
        self.assertTrue(any("done_definition" in e for e in errors))

    def test_done_definition_rejects_object_elements(self):
        """done_definition은 string[]로 고정 — object[]는 거부."""
        errors, _ = validate_packet(_valid_packet(
            done_definition=[{"criterion": "tests pass", "verifiable": True}]
        ))
        self.assertTrue(any("문자열이어야" in e for e in errors))

    def test_done_definition_rejects_mixed_types(self):
        errors, _ = validate_packet(_valid_packet(
            done_definition=["valid string", 42]
        ))
        self.assertTrue(any("문자열이어야" in e for e in errors))

    def test_packet_version_must_be_0_1(self):
        """packet_version은 항상 0.1 — 다른 값은 거부."""
        errors, _ = validate_packet(_valid_packet(packet_version="0.2"))
        self.assertTrue(any("packet_version" in e for e in errors))

    def test_packet_version_rejects_arbitrary(self):
        errors, _ = validate_packet(_valid_packet(packet_version="99.9"))
        self.assertTrue(any("packet_version" in e for e in errors))

    def test_render_prompt_standard(self):
        output = render_prompt(_valid_packet())
        self.assertIn("## Goal", output)
        self.assertIn("## Scope", output)
        self.assertIn("## Done Definition", output)
        self.assertIn("TASK-UNIT-01", output)

    def test_standard_accepts_timeout_minutes(self):
        """timeout_minutes는 core optional — standard에서도 사용 가능."""
        errors, warnings = validate_packet(_valid_packet(timeout_minutes=60))
        self.assertEqual(errors, [])

    def test_standard_accepts_stop_conditions(self):
        """stop_conditions는 core optional — standard에서도 사용 가능."""
        errors, warnings = validate_packet(_valid_packet(stop_conditions=["범위 초과 시 중단"]))
        self.assertEqual(errors, [])

    def test_standard_rejects_bad_timeout_type(self):
        """timeout_minutes 타입 검증은 profile 무관하게 항상 실행."""
        errors, _ = validate_packet(_valid_packet(timeout_minutes="not-int"))
        self.assertTrue(any("timeout_minutes" in e for e in errors))

    def test_standard_rejects_bad_stop_conditions_type(self):
        """stop_conditions 타입 검증은 profile 무관하게 항상 실행."""
        errors, _ = validate_packet(_valid_packet(stop_conditions="not-list"))
        self.assertTrue(any("stop_conditions" in e for e in errors))

    def test_timeout_and_stop_conditions_dont_trigger_extended(self):
        """이 두 필드만 있으면 standard로 판별 — extended로 오판하면 안 됨."""
        packet = _valid_packet(timeout_minutes=30, stop_conditions=["x"])
        self.assertEqual(_detect_profile(packet), "standard")

    def test_cmd_new_creates_standard_packet(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            args = argparse.Namespace(
                task_id="TASK-CLI-01", title="CLI smoke",
                dir=tmpdir, force=False, profile="standard",
            )
            cmd_new(args)
            data = json.loads((Path(tmpdir) / "TASK-CLI-01.json").read_text())
            self.assertEqual(data["packet_version"], "0.1")
            self.assertEqual(data["packet_profile"], "standard")
            self.assertNotIn("repo_root", data)
            # core optional 안전 필드 기본값 포함 확인
            self.assertIsNone(data["timeout_minutes"])
            self.assertEqual(data["stop_conditions"], [])

    def test_standard_rejects_extended_fields(self):
        """standard profile에 extended 필드 존재 시 에러."""
        packet = _valid_packet()
        packet["repo_root"] = "."
        errors, _ = validate_packet(packet)
        self.assertTrue(any("extended 필드 존재" in e for e in errors))


# ──────────────────────────────────────────────────────────
# Extended Packet Tests (v0.2 opt-in)
# ──────────────────────────────────────────────────────────

class TestExtendedPacket(unittest.TestCase):
    def test_scaffold_extended_has_profile_fields(self):
        packet = make_scaffold("TASK-EXT-99", "ext test", profile="extended")
        self.assertEqual(packet["packet_profile"], "extended")
        self.assertEqual(packet["packet_version"], "0.1")  # version은 항상 0.1, profile로 구분
        self.assertIn("repo_root", packet)
        self.assertIn("env_requirements", packet)
        self.assertIn("timeout_minutes", packet)  # core optional — standard/extended 모두 기본값 포함
        self.assertIn("stop_conditions", packet)

    def test_scaffold_standard_has_no_extended_fields(self):
        packet = make_scaffold("TASK-STD-99", "std test", profile="standard")
        self.assertEqual(packet["packet_profile"], "standard")
        self.assertNotIn("repo_root", packet)

    def test_validate_extended_accepts_valid(self):
        errors, warnings = validate_packet(_valid_extended_packet())
        self.assertEqual(errors, [])

    def test_validate_extended_auto_detects_profile(self):
        packet = _valid_extended_packet()
        self.assertEqual(_detect_profile(packet), "extended")

    def test_validate_standard_auto_detects_profile(self):
        self.assertEqual(_detect_profile(_valid_packet()), "standard")

    def test_validate_extended_rejects_bad_timeout(self):
        errors, _ = validate_packet(_valid_extended_packet(timeout_minutes="not-int"))
        self.assertTrue(any("timeout_minutes" in e for e in errors))

    def test_validate_extended_rejects_bad_env_requirements(self):
        errors, _ = validate_packet(_valid_extended_packet(env_requirements="not-dict"))
        self.assertTrue(any("env_requirements" in e for e in errors))

    def test_validate_extended_rejects_bad_stop_conditions(self):
        errors, _ = validate_packet(_valid_extended_packet(stop_conditions="not-list"))
        self.assertTrue(any("stop_conditions" in e for e in errors))

    def test_validate_extended_rejects_bad_packet_profile(self):
        errors, _ = validate_packet(_valid_extended_packet(packet_profile="invalid"))
        self.assertTrue(any("packet_profile" in e for e in errors))

    def test_validate_extended_still_checks_core_fields(self):
        """Extended packet도 core 필수 필드 누락을 잡아야 한다."""
        packet = _valid_extended_packet()
        del packet["goal"]
        errors, _ = validate_packet(packet)
        self.assertTrue(any("필수 필드 누락" in e for e in errors))

    def test_validate_extended_still_rejects_forbidden(self):
        """Extended profile이어도 runtime/dispatch 필드는 금지."""
        packet = _valid_extended_packet()
        packet["status"] = "running"
        errors, _ = validate_packet(packet)
        self.assertTrue(any("status" in e for e in errors))

    def test_render_prompt_extended_ignores_extra_fields(self):
        """render_prompt는 extended 필드를 무시해도 정상 동작."""
        output = render_prompt(_valid_extended_packet())
        self.assertIn("## Goal", output)
        self.assertIn("TASK-EXT-01", output)
        self.assertNotIn("repo_root", output)
        self.assertNotIn("timeout_minutes", output)

    def test_cmd_new_creates_extended_packet(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            args = argparse.Namespace(
                task_id="TASK-CLI-EXT-01", title="Extended CLI smoke",
                dir=tmpdir, force=False, profile="extended",
            )
            cmd_new(args)
            data = json.loads((Path(tmpdir) / "TASK-CLI-EXT-01.json").read_text())
            self.assertEqual(data["packet_version"], "0.1")  # version 항상 0.1
            self.assertEqual(data["packet_profile"], "extended")
            self.assertIn("repo_root", data)

    def test_extended_does_not_own_runtime_state(self):
        """Extended field에 runtime/state ownership이 없음을 확인."""
        runtime_fields = {"status", "session_id", "pid", "heartbeat", "log_path"}
        self.assertTrue(runtime_fields <= FORBIDDEN_FIELDS)
        self.assertEqual(runtime_fields & EXTENDED_FIELDS, set())


# ──────────────────────────────────────────────────────────
# Profile Detection Tests
# ──────────────────────────────────────────────────────────

class TestProfileDetection(unittest.TestCase):
    def test_explicit_standard(self):
        self.assertEqual(_detect_profile({"packet_profile": "standard"}), "standard")

    def test_explicit_extended(self):
        self.assertEqual(_detect_profile({"packet_profile": "extended"}), "extended")

    def test_no_implicit_detection_without_profile_field(self):
        """packet_profile 없이 extended 필드만 있으면 standard로 판별."""
        self.assertEqual(_detect_profile({"repo_root": "."}), "standard")
        self.assertEqual(_detect_profile({"source_of_truth": "spec.md"}), "standard")

    def test_implicit_standard_no_extended_fields(self):
        self.assertEqual(_detect_profile({"task_id": "X"}), "standard")

    def test_unknown_field_warns_not_errors(self):
        packet = _valid_packet()
        packet["totally_unknown_field"] = "value"
        errors, warnings = validate_packet(packet)
        self.assertEqual(errors, [])
        self.assertTrue(any("알 수 없는 필드" in w for w in warnings))


# ──────────────────────────────────────────────────────────
# Response Milestone Tests (ToolSandbox 3-Milestone AND)
# ──────────────────────────────────────────────────────────

class TestResponseMilestone(unittest.TestCase):
    """done_definition ↔ required_checks ↔ deliverables traceability."""

    def test_done_index_valid_no_error(self):
        """done_index가 범위 내이면 에러 없음."""
        packet = _valid_packet(
            done_definition=["조건 A", "조건 B"],
            required_checks=[
                {"type": "command", "value": "pytest", "required": True, "done_index": 0},
                {"type": "file_exists", "value": "out.md", "required": True, "done_index": 1},
            ],
        )
        errors, warnings = validate_packet(packet)
        self.assertEqual(errors, [])
        # 100% 커버리지 → 커버리지 경고 없음
        self.assertFalse(any("커버리지" in w for w in warnings))

    def test_done_index_out_of_range_errors(self):
        """done_index가 done_definition 범위 밖이면 에러."""
        packet = _valid_packet(
            required_checks=[
                {"type": "command", "value": "pytest", "required": True, "done_index": 99}
            ],
        )
        errors, _ = validate_packet(packet)
        self.assertTrue(any("done_index" in e for e in errors))

    def test_deliverables_done_index_out_of_range(self):
        """deliverables의 done_index도 범위 검증."""
        packet = _valid_packet(
            deliverables=[
                {"path": "out.py", "type": "source", "required": True, "done_index": -1}
            ],
        )
        errors, _ = validate_packet(packet)
        self.assertTrue(any("done_index" in e for e in errors))

    def test_partial_coverage_warns(self):
        """done_index를 일부만 사용하면 커버리지 경고."""
        packet = _valid_packet(
            done_definition=["조건 1", "조건 2"],
            required_checks=[
                {"type": "command", "value": "pytest", "required": True, "done_index": 0}
            ],
        )
        _, warnings = validate_packet(packet)
        self.assertTrue(any("커버리지" in w for w in warnings))

    def test_no_done_index_no_coverage_warning(self):
        """done_index가 하나도 없으면 커버리지 경고 안 함 (미채택 상태)."""
        packet = _valid_packet()
        _, warnings = validate_packet(packet)
        self.assertFalse(any("커버리지" in w for w in warnings))

    def test_response_coverage_full(self):
        """모든 done_definition에 done_index가 매핑되면 1.0."""
        packet = _valid_packet(
            done_definition=["조건 A", "조건 B"],
            required_checks=[
                {"type": "command", "value": "pytest", "required": True, "done_index": 0}
            ],
            deliverables=[
                {"path": "out.py", "type": "source", "required": True, "done_index": 1}
            ],
        )
        self.assertAlmostEqual(response_coverage(packet), 1.0)

    def test_response_coverage_zero(self):
        """done_index 없으면 커버리지 0."""
        self.assertAlmostEqual(response_coverage(_valid_packet()), 0.0)

    def test_response_coverage_partial(self):
        """done_definition 3개 중 1개만 커버 → 1/3."""
        packet = _valid_packet(
            done_definition=["A", "B", "C"],
            required_checks=[
                {"type": "command", "value": "pytest", "required": True, "done_index": 1}
            ],
        )
        self.assertAlmostEqual(response_coverage(packet), 1.0 / 3)


# ──────────────────────────────────────────────────────────
# Action Milestone Tests (ToolSandbox 3-Milestone AND)
# ──────────────────────────────────────────────────────────

class TestActionMilestone(unittest.TestCase):
    """Tool permissions + path constraint validation."""

    def test_must_not_modify_subset_of_forbidden(self):
        """must_not_modify ⊆ forbidden_paths 위반 시 에러."""
        packet = _valid_packet(
            forbidden_paths=[],
            constraints={
                "must_not_modify": ["src/config.py"],
                "must_run_tests": False,
                "must_not_use_network": True,
                "notes": "",
            },
        )
        errors, _ = validate_packet(packet)
        self.assertTrue(any("must_not_modify ⊆ forbidden_paths" in e for e in errors))

    def test_must_not_modify_valid_subset(self):
        """must_not_modify ⊆ forbidden_paths 만족 시 에러 없음."""
        packet = _valid_packet(
            forbidden_paths=["src/config.py"],
            constraints={
                "must_not_modify": ["src/config.py"],
                "must_run_tests": True,
                "must_not_use_network": True,
                "notes": "",
            },
        )
        errors, _ = validate_packet(packet)
        self.assertFalse(any("must_not_modify" in e for e in errors))

    def test_allowed_tools_requires_extended(self):
        """standard profile에서 allowed_tools 사용 시 에러."""
        packet = _valid_packet(
            constraints={
                "must_not_modify": [],
                "must_run_tests": False,
                "must_not_use_network": True,
                "notes": "",
                "allowed_tools": ["Read", "Edit"],
            },
        )
        errors, _ = validate_packet(packet)
        self.assertTrue(any("standard profile" in e and "allowed_tools" in e for e in errors))

    def test_allowed_tools_accepted_in_extended(self):
        """extended profile에서 allowed_tools 정상 수용."""
        packet = _valid_extended_packet()
        packet["constraints"]["allowed_tools"] = ["Read", "Edit", "Bash"]
        errors, _ = validate_packet(packet)
        self.assertFalse(any("allowed_tools" in e for e in errors))

    def test_forbidden_tools_bad_type_rejected(self):
        """forbidden_tools 타입 오류 시 에러."""
        packet = _valid_extended_packet()
        packet["constraints"]["forbidden_tools"] = "Agent"  # string, not list
        errors, _ = validate_packet(packet)
        self.assertTrue(any("forbidden_tools" in e for e in errors))

    def test_both_tools_warns_whitelist_priority(self):
        """allowed + forbidden 동시 지정 시 경고."""
        packet = _valid_extended_packet()
        packet["constraints"]["allowed_tools"] = ["Read", "Edit"]
        packet["constraints"]["forbidden_tools"] = ["Agent"]
        _, warnings = validate_packet(packet)
        self.assertTrue(any("화이트리스트" in w for w in warnings))

    def test_allowed_forbidden_paths_overlap_error(self):
        """allowed_paths와 forbidden_paths 겹침 시 에러."""
        packet = _valid_packet(
            allowed_paths=["src/", "src/config.py"],
            forbidden_paths=["src/config.py"],
        )
        errors, _ = validate_packet(packet)
        self.assertTrue(any("겹침" in e for e in errors))


# ──────────────────────────────────────────────────────────
# State Milestone Tests (ToolSandbox 3-Milestone AND)
# ──────────────────────────────────────────────────────────

def _valid_dispatch(**overrides):
    """유효한 dispatch fixture."""
    d = {
        "dispatch_version": "0.1",
        "dispatch_id": "DISPATCH-TEST-01",
        "task_id": "TASK-TEST-01",
        "packet_path": ".codex/packets/TASK-TEST-01.json",
        "branch": "feat/task-test-01",
        "worktree_path": ".worktrees/task-test-01",
        "assigned_agent": "codex",
        "status": "ready",
        "locked_paths": ["src/"],
        "history": [
            {"from": None, "to": "queued", "at": "2026-03-25T00:00:00+09:00",
             "by": "claude", "reason": "생성"},
            {"from": "queued", "to": "ready", "at": "2026-03-25T00:01:00+09:00",
             "by": "claude", "reason": "의존성 충족"},
        ],
        "created_at": "2026-03-25T00:00:00+09:00",
        "created_by": "claude",
        "updated_at": "2026-03-25T00:01:00+09:00",
    }
    d.update(overrides)
    return d


class TestStateMilestone(unittest.TestCase):
    """Dispatch status transition validation."""

    # -- transition function --
    def test_valid_transition_queued_to_ready(self):
        valid, _ = validate_dispatch_transition("queued", "ready")
        self.assertTrue(valid)

    def test_invalid_transition_queued_to_complete(self):
        valid, reason = validate_dispatch_transition("queued", "complete")
        self.assertFalse(valid)
        self.assertIn("전이 불가", reason)

    def test_terminal_status_no_transition(self):
        valid, reason = validate_dispatch_transition("merged", "running")
        self.assertFalse(valid)
        self.assertIn("terminal", reason)

    def test_retry_transition_valid(self):
        valid, _ = validate_dispatch_transition("failed", "running")
        self.assertTrue(valid)

    def test_unknown_status_rejected(self):
        valid, _ = validate_dispatch_transition("queued", "magic")
        self.assertFalse(valid)

    # -- full dispatch validation --
    def test_validate_dispatch_valid(self):
        errors, _ = validate_dispatch(_valid_dispatch())
        self.assertEqual(errors, [])

    def test_validate_dispatch_invalid_transition_in_history(self):
        d = _valid_dispatch(
            status="complete",
            history=[
                {"from": None, "to": "queued", "at": "...", "by": "c", "reason": "생성"},
                {"from": "queued", "to": "complete", "at": "...", "by": "c", "reason": "skip"},
            ],
        )
        errors, _ = validate_dispatch(d)
        self.assertTrue(any("전이 불가" in e for e in errors))

    def test_validate_dispatch_history_status_mismatch(self):
        d = _valid_dispatch(
            status="running",
            history=[
                {"from": None, "to": "queued", "at": "...", "by": "c", "reason": "생성"},
            ],
        )
        errors, _ = validate_dispatch(d)
        self.assertTrue(any("불일치" in e for e in errors))

    def test_validate_dispatch_rejects_packet_fields(self):
        d = _valid_dispatch(goal="이건 여기 있으면 안 됨")
        errors, _ = validate_dispatch(d)
        self.assertTrue(any("금지 필드" in e for e in errors))

    def test_all_statuses_have_transitions(self):
        """모든 status가 DISPATCH_TRANSITIONS에 정의됨."""
        for s in DISPATCH_STATUSES:
            self.assertIn(s, DISPATCH_TRANSITIONS)


if __name__ == "__main__":
    unittest.main()
