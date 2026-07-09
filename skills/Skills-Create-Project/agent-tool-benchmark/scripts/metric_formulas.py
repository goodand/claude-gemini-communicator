#!/usr/bin/env python3
"""
agent-tool-benchmark: 수식 3중 표현 (수도코드 / LaTeX / Python) + 교차 검증

8개 주요 벤치마크에서 추출한 9개 핵심 메트릭을 3가지 형식으로 표현하고,
Python 구현을 ground truth로 삼아 교차 검증한다.

벤치마크 출처 (8개, metric registry에 대응하는 것만):
  - BFCL (Berkeley Function Calling Leaderboard)
  - ToolEval / ToolBench (OpenBMB, ICLR 2024)
  - T-Eval (Open-Compass, ACL 2024)
  - TaskBench (Microsoft JARVIS, NeurIPS 2023)
  - ToolSandbox (Apple, 2024)
  - SWE-bench (Princeton, ICLR 2024)
  - API-Bank (Alibaba, ACL 2023)
  - MINT (ICLR 2024)

조사만 수행 (metric 미구현):
  - AgentBench (THU, ICLR 2024) — 8개 환경별 normalized score, 범용 수식화 부적합
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field, asdict
from typing import Any


# ─────────────────────────────────────────────
# 1. Metric Registry — 3중 표현 구조
# ─────────────────────────────────────────────

@dataclass
class MetricFormula:
    """하나의 메트릭에 대한 3중 표현."""
    name: str
    source_benchmark: str
    description_ko: str

    # 3중 표현
    pseudocode: str
    latex: str
    # python 구현은 아래 함수로 제공

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────
# 2. Python 구현 (ground truth)
# ─────────────────────────────────────────────

def ast_accuracy(predictions: list[bool]) -> float:
    """BFCL AST Accuracy — 샘플별 AST 매칭 성공 여부의 평균.

    Args:
        predictions: 각 샘플의 AST 매칭 성공 여부 (True/False)
    Returns:
        0.0 ~ 1.0 사이의 정확도
    """
    if not predictions:
        return 0.0
    return sum(1.0 for p in predictions if p) / len(predictions)


def pass_rate(judgments: list[str]) -> float:
    """ToolEval Pass Rate — ChatGPT judge 판정의 가중 평균.

    Args:
        judgments: 각 샘플의 판정 ("pass", "unsure", "fail")
    Returns:
        0.0 ~ 1.0 사이의 pass rate
    """
    if not judgments:
        return 0.0
    score_map = {"pass": 1.0, "unsure": 0.5, "fail": 0.0}
    return sum(score_map.get(j.lower(), 0.0) for j in judgments) / len(judgments)


def f1_score(predicted: set, ground_truth: set) -> float:
    """T-Eval / TaskBench F1 Score — 집합 기반 precision-recall 조화 평균.

    Args:
        predicted: 예측된 항목 집합
        ground_truth: 정답 항목 집합
    Returns:
        0.0 ~ 1.0 사이의 F1 score
    """
    if not predicted and not ground_truth:
        return 1.0
    if not predicted or not ground_truth:
        return 0.0
    tp = len(predicted & ground_truth)
    precision = tp / len(predicted)
    recall = tp / len(ground_truth)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def milestone_and_score(
    action_score: float,
    state_score: float,
    response_score: float,
) -> float:
    """ToolSandbox 3-Milestone AND — 세 milestone의 곱.

    Args:
        action_score: tool call 정확도 (0.0~1.0)
        state_score: 상태 변화 정확도 (0 또는 1)
        response_score: 최종 응답 정확도 (0 또는 1)
    Returns:
        0.0 또는 action_score (AND 논리)
    """
    return action_score * state_score * response_score


def resolve_rate(
    results: list[dict],
) -> float:
    """SWE-bench Resolve Rate — F2P 통과 ∧ P2P 유지 비율.

    Args:
        results: [{"f2p_pass": bool, "p2p_pass": bool}, ...]
    Returns:
        0.0 ~ 1.0 사이의 resolve rate
    """
    if not results:
        return 0.0
    resolved = sum(
        1.0 for r in results if r.get("f2p_pass") and r.get("p2p_pass")
    )
    return resolved / len(results)


def graph_edit_distance_score(
    pred_edges: set[tuple],
    gt_edges: set[tuple],
) -> float:
    """TaskBench Parameter Prediction — 정규화된 GED 기반 점수.

    간소화: GED를 symmetric difference 크기로 근사.

    Args:
        pred_edges: 예측 그래프의 edge 집합 {(src, dst), ...}
        gt_edges: 정답 그래프의 edge 집합
    Returns:
        0.0 ~ 1.0 사이의 점수 (1.0 = 완전 일치)
    """
    if not pred_edges and not gt_edges:
        return 1.0
    sym_diff = len(pred_edges.symmetric_difference(gt_edges))
    max_edges = max(len(pred_edges) + len(gt_edges), 1)
    return 1.0 - sym_diff / max_edges


def multi_turn_success_rate(
    results: list[dict],
    max_turns: int,
) -> float:
    """MINT SR@k — k턴 이내 정답 도달 비율.

    Args:
        results: [{"correct": bool, "turns_used": int}, ...]
        max_turns: 허용 최대 턴 수 (k)
    Returns:
        0.0 ~ 1.0 사이의 success rate
    """
    if not results:
        return 0.0
    success = sum(
        1.0
        for r in results
        if r.get("correct") and r.get("turns_used", max_turns + 1) <= max_turns
    )
    return success / len(results)


def tool_call_action_score(
    predicted_calls: list[str],
    gt_calls: list[str],
) -> float:
    """ToolSandbox Action Score — 매칭된 호출 비율.

    Args:
        predicted_calls: 예측된 tool call 이름 리스트
        gt_calls: 정답 tool call 이름 리스트
    Returns:
        0.0 ~ 1.0 사이의 점수
    """
    pred_set = set(predicted_calls)
    gt_set = set(gt_calls)
    matched = len(pred_set & gt_set)
    denominator = max(len(pred_set), len(gt_set))
    if denominator == 0:
        return 1.0
    return matched / denominator


def api_bank_level1(
    predictions: list[dict],
    ground_truths: list[dict],
) -> float:
    """API-Bank Level-1 Accuracy — API name + args exact match.

    Args:
        predictions: [{"api_name": str, "args": dict}, ...]
        ground_truths: 동일 구조
    Returns:
        0.0 ~ 1.0 사이의 정확도
    """
    if not predictions:
        return 0.0
    correct = sum(
        1.0
        for p, g in zip(predictions, ground_truths)
        if p.get("api_name") == g.get("api_name")
        and p.get("args") == g.get("args")
    )
    return correct / len(predictions)


# ─────────────────────────────────────────────
# 3. 3중 표현 레지스트리
# ─────────────────────────────────────────────

METRIC_REGISTRY: list[MetricFormula] = [
    MetricFormula(
        name="AST Accuracy",
        source_benchmark="BFCL",
        description_ko="AST 파싱 후 function name + argument 매칭 성공 비율",
        pseudocode="""\
FUNCTION ast_accuracy(predictions):
    N ← len(predictions)
    IF N = 0 THEN RETURN 0
    count ← 0
    FOR EACH p IN predictions:
        IF ast_match(p.predicted, p.ground_truth) THEN
            count ← count + 1
    RETURN count / N""",
        latex=r"$\text{AST\_Acc} = \frac{1}{N}\sum_{i=1}^{N}\mathbb{1}\!\left[\text{ast\_match}(\hat{y}_i, y_i)\right]$",
    ),
    MetricFormula(
        name="Pass Rate",
        source_benchmark="ToolEval (ToolBench)",
        description_ko="ChatGPT judge가 판정한 pass/unsure/fail의 가중 평균",
        pseudocode="""\
FUNCTION pass_rate(judgments):
    N ← len(judgments)
    IF N = 0 THEN RETURN 0
    total ← 0
    FOR EACH j IN judgments:
        IF j = "pass"   THEN total ← total + 1.0
        IF j = "unsure" THEN total ← total + 0.5
        IF j = "fail"   THEN total ← total + 0.0
    RETURN total / N""",
        latex=r"$\text{PR} = \frac{1}{N}\sum_{i=1}^{N}s_i, \quad s_i = \begin{cases}1.0 & \text{pass}\\0.5 & \text{unsure}\\0.0 & \text{fail}\end{cases}$",
    ),
    MetricFormula(
        name="F1 Score (Set-based)",
        source_benchmark="T-Eval / TaskBench",
        description_ko="예측 집합과 정답 집합 간 precision-recall 조화 평균",
        pseudocode="""\
FUNCTION f1_score(predicted_set, gt_set):
    IF both empty THEN RETURN 1.0
    IF either empty THEN RETURN 0.0
    TP ← |predicted_set ∩ gt_set|
    P  ← TP / |predicted_set|
    R  ← TP / |gt_set|
    IF P + R = 0 THEN RETURN 0.0
    RETURN 2 * P * R / (P + R)""",
        latex=r"$F_1 = \frac{2PR}{P+R}, \quad P=\frac{|\hat{S}\cap S^*|}{|\hat{S}|}, \quad R=\frac{|\hat{S}\cap S^*|}{|S^*|}$",
    ),
    MetricFormula(
        name="3-Milestone AND Score",
        source_benchmark="ToolSandbox (Apple)",
        description_ko="Action × State × Response — 세 milestone 모두 통과해야 성공",
        pseudocode="""\
FUNCTION milestone_and(action, state, response):
    RETURN action * state * response

FUNCTION overall(instances):
    RETURN mean(milestone_and(i.action, i.state, i.response) FOR i IN instances)""",
        latex=r"$\text{Overall}_i = A_i \cdot S_i \cdot R_i, \quad \text{Overall} = \frac{1}{N}\sum_{i=1}^{N}\text{Overall}_i$",
    ),
    MetricFormula(
        name="Resolve Rate",
        source_benchmark="SWE-bench",
        description_ko="fail-to-pass 테스트 통과 ∧ pass-to-pass 테스트 유지 비율",
        pseudocode="""\
FUNCTION resolve_rate(results):
    N ← len(results)
    IF N = 0 THEN RETURN 0
    resolved ← 0
    FOR EACH r IN results:
        IF r.f2p_all_pass AND r.p2p_all_pass THEN
            resolved ← resolved + 1
    RETURN resolved / N""",
        latex=r"$\text{RR} = \frac{1}{N}\sum_{i=1}^{N}\mathbb{1}\!\left[F2P_i \subseteq \text{pass}_i \;\wedge\; P2P_i \subseteq \text{pass}_i\right]$",
    ),
    MetricFormula(
        name="GED-based Parameter Prediction",
        source_benchmark="TaskBench",
        description_ko="예측 그래프와 정답 그래프 간 정규화된 Graph Edit Distance 점수",
        pseudocode="""\
FUNCTION ged_score(pred_edges, gt_edges):
    IF both empty THEN RETURN 1.0
    sym_diff ← |pred_edges △ gt_edges|
    max_e ← max(|pred_edges| + |gt_edges|, 1)
    RETURN 1.0 - sym_diff / max_e""",
        latex=r"$\text{PP} = 1 - \frac{\text{GED}(\hat{G}, G^*)}{\max(|\hat{E}|+|E^*|,\;1)}$",
    ),
    MetricFormula(
        name="SR@k (Multi-Turn Success Rate)",
        source_benchmark="MINT",
        description_ko="k턴 이내에 정답에 도달한 비율",
        pseudocode="""\
FUNCTION sr_at_k(results, k):
    N ← len(results)
    IF N = 0 THEN RETURN 0
    success ← 0
    FOR EACH r IN results:
        IF r.correct AND r.turns_used ≤ k THEN
            success ← success + 1
    RETURN success / N""",
        latex=r"$\text{SR}@k = \frac{1}{N}\sum_{i=1}^{N}\mathbb{1}\!\left[\text{correct}_i \;\wedge\; t_i \le k\right]$",
    ),
    MetricFormula(
        name="Action Score (Tool Call Match)",
        source_benchmark="ToolSandbox (Apple)",
        description_ko="예측된 tool call과 정답 tool call의 매칭 비율",
        pseudocode="""\
FUNCTION action_score(pred_calls, gt_calls):
    matched ← |set(pred_calls) ∩ set(gt_calls)|
    denom ← max(|set(pred_calls)|, |set(gt_calls)|)
    IF denom = 0 THEN RETURN 1.0
    RETURN matched / denom""",
        latex=r"$\text{Action} = \frac{|\hat{C} \cap C^*|}{\max(|\hat{C}|,\;|C^*|)}$",
    ),
    MetricFormula(
        name="API-Bank Level-1 Accuracy",
        source_benchmark="API-Bank",
        description_ko="API name + arguments exact match 정확도",
        pseudocode="""\
FUNCTION level1_accuracy(predictions, ground_truths):
    N ← len(predictions)
    IF N = 0 THEN RETURN 0
    correct ← 0
    FOR i ← 1 TO N:
        IF predictions[i].api_name = ground_truths[i].api_name
           AND predictions[i].args = ground_truths[i].args THEN
            correct ← correct + 1
    RETURN correct / N""",
        latex=r"$\text{L1\_Acc} = \frac{1}{N}\sum_{i=1}^{N}\mathbb{1}\!\left[\hat{a}_i = a_i^* \;\wedge\; \hat{\theta}_i = \theta_i^*\right]$",
    ),
]


# ─────────────────────────────────────────────
# 4. 교차 검증 (Cross-Validation)
# ─────────────────────────────────────────────

def cross_validate() -> list[dict]:
    """각 수식에 대해 Python 구현 결과를 고정 테스트 벡터로 검증한다.

    검증 전략:
      - 각 메트릭에 2~3개 테스트 케이스 (경계값 포함)
      - expected 값은 수도코드/LaTeX를 손으로 추적한 결과
      - Python 구현 결과와 비교하여 일치 여부 판정
    """
    results = []

    # --- 1. AST Accuracy ---
    cases_ast = [
        {"input": [True, True, True, False], "expected": 0.75},
        {"input": [], "expected": 0.0},
        {"input": [True], "expected": 1.0},
        {"input": [False, False], "expected": 0.0},
    ]
    for c in cases_ast:
        got = ast_accuracy(c["input"])
        results.append({
            "metric": "AST Accuracy",
            "input": str(c["input"]),
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    # --- 2. Pass Rate ---
    cases_pr = [
        {"input": ["pass", "pass", "fail", "unsure"], "expected": 0.625},
        {"input": [], "expected": 0.0},
        {"input": ["pass"], "expected": 1.0},
        {"input": ["fail", "fail"], "expected": 0.0},
    ]
    for c in cases_pr:
        got = pass_rate(c["input"])
        results.append({
            "metric": "Pass Rate",
            "input": str(c["input"]),
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    # --- 3. F1 Score ---
    cases_f1 = [
        {"pred": {"a", "b", "c"}, "gt": {"b", "c", "d"}, "expected": 2 / 3},
        {"pred": set(), "gt": set(), "expected": 1.0},
        {"pred": {"a"}, "gt": {"b"}, "expected": 0.0},
        {"pred": {"a", "b"}, "gt": {"a", "b"}, "expected": 1.0},
    ]
    for c in cases_f1:
        got = f1_score(c["pred"], c["gt"])
        results.append({
            "metric": "F1 Score",
            "input": f"pred={c['pred']}, gt={c['gt']}",
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    # --- 4. Milestone AND ---
    cases_ms = [
        {"a": 0.8, "s": 1.0, "r": 1.0, "expected": 0.8},
        {"a": 0.9, "s": 0.0, "r": 1.0, "expected": 0.0},
        {"a": 1.0, "s": 1.0, "r": 1.0, "expected": 1.0},
    ]
    for c in cases_ms:
        got = milestone_and_score(c["a"], c["s"], c["r"])
        results.append({
            "metric": "3-Milestone AND",
            "input": f"a={c['a']}, s={c['s']}, r={c['r']}",
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    # --- 5. Resolve Rate ---
    cases_rr = [
        {
            "input": [
                {"f2p_pass": True, "p2p_pass": True},
                {"f2p_pass": True, "p2p_pass": False},
                {"f2p_pass": False, "p2p_pass": True},
                {"f2p_pass": True, "p2p_pass": True},
            ],
            "expected": 0.5,
        },
        {"input": [], "expected": 0.0},
    ]
    for c in cases_rr:
        got = resolve_rate(c["input"])
        results.append({
            "metric": "Resolve Rate",
            "input": str(c["input"][:2]) + "...",
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    # --- 6. GED Score ---
    cases_ged = [
        {
            "pred": {("a", "b"), ("b", "c")},
            "gt": {("a", "b"), ("c", "d")},
            "expected": 1.0 - 2 / 4,  # sym_diff=2, max=4 → 0.5
        },
        {"pred": set(), "gt": set(), "expected": 1.0},
        {
            "pred": {("a", "b")},
            "gt": {("a", "b")},
            "expected": 1.0,
        },
    ]
    for c in cases_ged:
        got = graph_edit_distance_score(c["pred"], c["gt"])
        results.append({
            "metric": "GED Score",
            "input": f"pred={c['pred']}, gt={c['gt']}",
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    # --- 7. SR@k ---
    cases_sr = [
        {
            "input": [
                {"correct": True, "turns_used": 2},
                {"correct": True, "turns_used": 5},
                {"correct": False, "turns_used": 1},
                {"correct": True, "turns_used": 3},
            ],
            "k": 3,
            "expected": 0.5,  # 2/4 (turns 2,3 통과)
        },
        {"input": [], "k": 5, "expected": 0.0},
    ]
    for c in cases_sr:
        got = multi_turn_success_rate(c["input"], c["k"])
        results.append({
            "metric": "SR@k",
            "input": f"k={c['k']}, n={len(c['input'])}",
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    # --- 8. Action Score ---
    cases_as = [
        {"pred": ["a", "b", "c"], "gt": ["b", "c", "d"], "expected": 2 / 3},
        {"pred": [], "gt": [], "expected": 1.0},
        {"pred": ["a"], "gt": ["a"], "expected": 1.0},
    ]
    for c in cases_as:
        got = tool_call_action_score(c["pred"], c["gt"])
        results.append({
            "metric": "Action Score",
            "input": f"pred={c['pred']}, gt={c['gt']}",
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    # --- 9. API-Bank L1 ---
    cases_l1 = [
        {
            "pred": [
                {"api_name": "getWeather", "args": {"city": "Seoul"}},
                {"api_name": "getNews", "args": {"topic": "AI"}},
            ],
            "gt": [
                {"api_name": "getWeather", "args": {"city": "Seoul"}},
                {"api_name": "getNews", "args": {"topic": "tech"}},
            ],
            "expected": 0.5,
        },
    ]
    for c in cases_l1:
        got = api_bank_level1(c["pred"], c["gt"])
        results.append({
            "metric": "API-Bank L1",
            "input": "2 samples",
            "expected": c["expected"],
            "got": got,
            "pass": math.isclose(got, c["expected"], abs_tol=1e-9),
        })

    return results


# ─────────────────────────────────────────────
# 5. 출력 (3중 표현 보고서 + 검증 결과)
# ─────────────────────────────────────────────

def print_triple_report():
    """3중 표현 보고서를 stdout에 출력한다."""
    print("=" * 72)
    print("  Agent Tool-Use Benchmark — 수식 3중 표현 보고서")
    print("=" * 72)

    for i, m in enumerate(METRIC_REGISTRY, 1):
        print(f"\n{'─' * 72}")
        print(f"[{i}] {m.name}  ({m.source_benchmark})")
        print(f"    {m.description_ko}")
        print(f"\n  ■ 수도코드:")
        for line in m.pseudocode.split("\n"):
            print(f"    {line}")
        print(f"\n  ■ LaTeX:")
        print(f"    {m.latex}")
        print(f"\n  ■ Python: {m.name.lower().replace(' ', '_').replace('-', '_')}()")


def print_validation_report(results: list[dict]):
    """교차 검증 결과를 stdout에 출력한다."""
    print(f"\n{'=' * 72}")
    print("  교차 검증 결과")
    print(f"{'=' * 72}")

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    print(f"\n  총 {total}개 테스트 케이스 중 {passed}개 통과\n")

    for r in results:
        status = "✓ PASS" if r["pass"] else "✗ FAIL"
        print(f"  [{status}] {r['metric']}: expected={r['expected']}, got={r['got']}")

    if passed == total:
        print(f"\n  ✓ 3중 표현 교차 검증 완료: 수도코드 ↔ LaTeX ↔ Python 일관성 확인")
    else:
        print(f"\n  ✗ {total - passed}개 불일치 발견")


def export_registry_json(path: str | None = None) -> str:
    """레지스트리를 JSON으로 직렬화한다."""
    data = {
        "schema_version": "1",
        "metrics": [m.to_dict() for m in METRIC_REGISTRY],
    }
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)
    return output


# ─────────────────────────────────────────────
# 6. CLI
# ─────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metric_formulas",
        description="Agent tool-use benchmark 수식 3중 표현 + 교차 검증",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("report", help="3중 표현 보고서 + 교차 검증 출력 (기본값)")
    sub.add_parser("validate", help="교차 검증만 실행")

    export_p = sub.add_parser("export", help="metric registry를 JSON으로 내보내기")
    export_p.add_argument("output", nargs="?", default=None, help="출력 파일 경로")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    cmd = args.command or "report"

    if cmd == "validate":
        results = cross_validate()
        print_validation_report(results)
        sys.exit(0 if all(r["pass"] for r in results) else 1)
    elif cmd == "export":
        export_registry_json(args.output)
        if args.output:
            print(f"exported to {args.output}")
    else:
        print_triple_report()
        print()
        results = cross_validate()
        print_validation_report(results)
        sys.exit(0 if all(r["pass"] for r in results) else 1)


if __name__ == "__main__":
    main()
