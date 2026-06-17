#!/usr/bin/env python3
"""agent-tool-benchmark metric 교차 검증 테스트.

metric_formulas.py의 Python 구현이 수도코드/LaTeX와 일관적인지
고정 테스트 벡터로 검증한다.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from metric_formulas import (
    ast_accuracy,
    pass_rate,
    f1_score,
    milestone_and_score,
    resolve_rate,
    graph_edit_distance_score,
    multi_turn_success_rate,
    tool_call_action_score,
    api_bank_level1,
    cross_validate,
    METRIC_REGISTRY,
)


class TestASTAccuracy(unittest.TestCase):
    def test_normal(self):
        self.assertAlmostEqual(ast_accuracy([True, True, True, False]), 0.75)

    def test_empty(self):
        self.assertAlmostEqual(ast_accuracy([]), 0.0)

    def test_all_pass(self):
        self.assertAlmostEqual(ast_accuracy([True]), 1.0)

    def test_all_fail(self):
        self.assertAlmostEqual(ast_accuracy([False, False]), 0.0)


class TestPassRate(unittest.TestCase):
    def test_mixed(self):
        self.assertAlmostEqual(pass_rate(["pass", "pass", "fail", "unsure"]), 0.625)

    def test_empty(self):
        self.assertAlmostEqual(pass_rate([]), 0.0)

    def test_all_pass(self):
        self.assertAlmostEqual(pass_rate(["pass"]), 1.0)

    def test_all_fail(self):
        self.assertAlmostEqual(pass_rate(["fail", "fail"]), 0.0)

    def test_case_insensitive(self):
        self.assertAlmostEqual(pass_rate(["PASS", "Unsure"]), 0.75)


class TestF1Score(unittest.TestCase):
    def test_partial_overlap(self):
        self.assertAlmostEqual(f1_score({"a", "b", "c"}, {"b", "c", "d"}), 2 / 3)

    def test_both_empty(self):
        self.assertAlmostEqual(f1_score(set(), set()), 1.0)

    def test_no_overlap(self):
        self.assertAlmostEqual(f1_score({"a"}, {"b"}), 0.0)

    def test_perfect(self):
        self.assertAlmostEqual(f1_score({"a", "b"}, {"a", "b"}), 1.0)

    def test_pred_empty(self):
        self.assertAlmostEqual(f1_score(set(), {"a"}), 0.0)


class TestMilestoneAND(unittest.TestCase):
    def test_partial(self):
        self.assertAlmostEqual(milestone_and_score(0.8, 1.0, 1.0), 0.8)

    def test_zero_state(self):
        self.assertAlmostEqual(milestone_and_score(0.9, 0.0, 1.0), 0.0)

    def test_perfect(self):
        self.assertAlmostEqual(milestone_and_score(1.0, 1.0, 1.0), 1.0)


class TestResolveRate(unittest.TestCase):
    def test_mixed(self):
        results = [
            {"f2p_pass": True, "p2p_pass": True},
            {"f2p_pass": True, "p2p_pass": False},
            {"f2p_pass": False, "p2p_pass": True},
            {"f2p_pass": True, "p2p_pass": True},
        ]
        self.assertAlmostEqual(resolve_rate(results), 0.5)

    def test_empty(self):
        self.assertAlmostEqual(resolve_rate([]), 0.0)

    def test_all_resolved(self):
        results = [{"f2p_pass": True, "p2p_pass": True}]
        self.assertAlmostEqual(resolve_rate(results), 1.0)


class TestGEDScore(unittest.TestCase):
    def test_partial(self):
        pred = {("a", "b"), ("b", "c")}
        gt = {("a", "b"), ("c", "d")}
        self.assertAlmostEqual(graph_edit_distance_score(pred, gt), 0.5)

    def test_both_empty(self):
        self.assertAlmostEqual(graph_edit_distance_score(set(), set()), 1.0)

    def test_perfect(self):
        edges = {("a", "b")}
        self.assertAlmostEqual(graph_edit_distance_score(edges, edges), 1.0)

    def test_no_overlap(self):
        pred = {("a", "b")}
        gt = {("c", "d")}
        self.assertAlmostEqual(graph_edit_distance_score(pred, gt), 0.0)


class TestSRatK(unittest.TestCase):
    def test_k3(self):
        results = [
            {"correct": True, "turns_used": 2},
            {"correct": True, "turns_used": 5},
            {"correct": False, "turns_used": 1},
            {"correct": True, "turns_used": 3},
        ]
        self.assertAlmostEqual(multi_turn_success_rate(results, 3), 0.5)

    def test_empty(self):
        self.assertAlmostEqual(multi_turn_success_rate([], 5), 0.0)

    def test_all_within_k(self):
        results = [{"correct": True, "turns_used": 1}]
        self.assertAlmostEqual(multi_turn_success_rate(results, 5), 1.0)


class TestActionScore(unittest.TestCase):
    def test_partial(self):
        self.assertAlmostEqual(
            tool_call_action_score(["a", "b", "c"], ["b", "c", "d"]), 2 / 3
        )

    def test_both_empty(self):
        self.assertAlmostEqual(tool_call_action_score([], []), 1.0)

    def test_perfect(self):
        self.assertAlmostEqual(tool_call_action_score(["a"], ["a"]), 1.0)


class TestAPIBankL1(unittest.TestCase):
    def test_half_correct(self):
        pred = [
            {"api_name": "getWeather", "args": {"city": "Seoul"}},
            {"api_name": "getNews", "args": {"topic": "AI"}},
        ]
        gt = [
            {"api_name": "getWeather", "args": {"city": "Seoul"}},
            {"api_name": "getNews", "args": {"topic": "tech"}},
        ]
        self.assertAlmostEqual(api_bank_level1(pred, gt), 0.5)

    def test_empty(self):
        self.assertAlmostEqual(api_bank_level1([], []), 0.0)


class TestCrossValidate(unittest.TestCase):
    def test_all_pass(self):
        results = cross_validate()
        failed = [r for r in results if not r["pass"]]
        self.assertEqual(failed, [], f"Failed: {failed}")

    def test_count(self):
        results = cross_validate()
        self.assertEqual(len(results), 26)


class TestMetricRegistry(unittest.TestCase):
    def test_registry_count(self):
        self.assertEqual(len(METRIC_REGISTRY), 9)

    def test_all_have_triple(self):
        for m in METRIC_REGISTRY:
            self.assertTrue(m.pseudocode, f"{m.name} missing pseudocode")
            self.assertTrue(m.latex, f"{m.name} missing latex")
            self.assertTrue(m.source_benchmark, f"{m.name} missing source")


if __name__ == "__main__":
    unittest.main()
