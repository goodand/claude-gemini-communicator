#!/usr/bin/env python3
"""agent-task-packet 성과 측정 메트릭 테스트.

scripts/test_packet_builder.py (오케스트레이션)와 분리된 측정 전용 테스트.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# scripts/ 모듈 접근을 위한 path 설정
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from packet_builder import make_scaffold

from packet_eval_metrics import (
    REQUIRED_CHECK_CATEGORIES,
    resolve_readiness,
    response_coverage,
    safety_audit,
    turn_budget_score,
)


def _valid_packet(**overrides):
    packet = make_scaffold("EVAL-TEST-01", "Eval metric test")
    packet.update(
        {
            "goal": "Evaluate packet metrics for tool calling performance.",
            "why": "Measurement functions need isolated testing.",
            "allowed_paths": ["src/"],
            "context_files": ["docs/spec.md"],
            "done_definition": ["테스트 통과", "산출물 생성"],
            "required_checks": [
                {"type": "command", "value": "pytest tests/", "required": True}
            ],
            "deliverables": [
                {"path": "src/output.py", "type": "source", "required": True}
            ],
            "created_by": "eval-test",
        }
    )
    packet.update(overrides)
    return packet


class TestTurnBudgetScore(unittest.TestCase):
    """SR@k (MINT) — turn budget 정의 검증."""

    def test_full(self):
        p = _valid_packet(timeout_minutes=30, stop_conditions=["spec 외 작업"])
        self.assertEqual(turn_budget_score(p), 1.0)

    def test_timeout_only(self):
        p = _valid_packet(timeout_minutes=30, stop_conditions=[])
        self.assertEqual(turn_budget_score(p), 0.5)

    def test_stop_conditions_only(self):
        p = _valid_packet(timeout_minutes=None, stop_conditions=["범위 초과"])
        self.assertEqual(turn_budget_score(p), 0.5)

    def test_zero(self):
        p = _valid_packet(timeout_minutes=None, stop_conditions=[])
        self.assertEqual(turn_budget_score(p), 0.0)


class TestSafetyAudit(unittest.TestCase):
    """운영 안전 경고."""

    def test_warns_null_timeout(self):
        p = _valid_packet(timeout_minutes=None, stop_conditions=["x"])
        w = safety_audit(p)
        self.assertEqual(len(w), 1)
        self.assertIn("timeout_minutes", w[0])

    def test_warns_empty_stop_conditions(self):
        p = _valid_packet(timeout_minutes=30, stop_conditions=[])
        w = safety_audit(p)
        self.assertEqual(len(w), 1)
        self.assertIn("stop_conditions", w[0])

    def test_warns_both(self):
        p = _valid_packet(timeout_minutes=None, stop_conditions=[])
        w = safety_audit(p)
        self.assertEqual(len(w), 2)

    def test_clean(self):
        p = _valid_packet(timeout_minutes=60, stop_conditions=["범위 초과"])
        w = safety_audit(p)
        self.assertEqual(len(w), 0)


class TestResolveReadiness(unittest.TestCase):
    """Resolve Rate (SWE-bench) — category 채택 비율."""

    def test_full(self):
        p = _valid_packet(required_checks=[
            {"type": "command", "value": "pytest new.py", "required": True, "category": "f2p"},
            {"type": "command", "value": "pytest old.py", "required": True, "category": "p2p"},
        ])
        self.assertEqual(resolve_readiness(p), 1.0)

    def test_partial(self):
        p = _valid_packet(required_checks=[
            {"type": "command", "value": "pytest new.py", "required": True, "category": "f2p"},
            {"type": "command", "value": "pytest old.py", "required": True},
        ])
        self.assertEqual(resolve_readiness(p), 0.5)

    def test_zero(self):
        p = _valid_packet(required_checks=[
            {"type": "command", "value": "pytest", "required": True},
        ])
        self.assertEqual(resolve_readiness(p), 0.0)

    def test_empty_checks(self):
        p = _valid_packet(required_checks=[])
        self.assertEqual(resolve_readiness(p), 0.0)

    def test_all_categories_valid(self):
        for cat in sorted(REQUIRED_CHECK_CATEGORIES):
            p = _valid_packet(required_checks=[
                {"type": "command", "value": "pytest", "required": True, "category": cat},
            ])
            self.assertEqual(resolve_readiness(p), 1.0, f"category '{cat}' should be valid")


class TestResponseCoverage(unittest.TestCase):
    """Response Milestone — done_index 커버리지."""

    def test_full_coverage(self):
        p = _valid_packet(
            done_definition=["조건1", "조건2"],
            required_checks=[
                {"type": "command", "value": "pytest", "required": True, "done_index": 0},
            ],
            deliverables=[
                {"path": "out.py", "type": "source", "required": True, "done_index": 1},
            ],
        )
        self.assertEqual(response_coverage(p), 1.0)

    def test_partial_coverage(self):
        p = _valid_packet(
            done_definition=["조건1", "조건2"],
            required_checks=[
                {"type": "command", "value": "pytest", "required": True, "done_index": 0},
            ],
            deliverables=[],
        )
        self.assertEqual(response_coverage(p), 0.5)

    def test_zero_coverage(self):
        p = _valid_packet(
            done_definition=["조건1"],
            required_checks=[{"type": "command", "value": "pytest", "required": True}],
        )
        self.assertEqual(response_coverage(p), 0.0)


if __name__ == "__main__":
    unittest.main()
