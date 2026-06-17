#!/usr/bin/env python3
"""agent-task-packet 성과 측정 메트릭.

오케스트레이션(packet_builder.py)과 분리된 측정 전용 모듈.
packet 실행 결과를 agent-tool-benchmark 메트릭 관점으로 평가한다.

사용:
    from packet_eval_metrics import (
        response_coverage, turn_budget_score,
        resolve_readiness, safety_audit,
    )
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_CHECK_CATEGORIES = {"f2p", "p2p", "new", "smoke", "regression"}


# ---------------------------------------------------------------------------
# Response Milestone Coverage (ToolSandbox 3-Milestone AND)
# ---------------------------------------------------------------------------

def response_coverage(data):
    """done_definition의 required_checks + deliverables 커버리지 계산.

    ToolSandbox Response milestone 대응: done_definition의 몇 %가
    required_checks 또는 deliverables의 done_index로 machine-verifiable한지 측정.

    Returns: float (0.0 ~ 1.0). done_definition이 비어있으면 0.0.
    """
    defs = data.get("done_definition", [])
    if not defs:
        return 0.0
    n = len(defs)
    covered = set()
    for check in data.get("required_checks", []):
        if isinstance(check, dict) and "done_index" in check:
            idx = check["done_index"]
            if isinstance(idx, int) and 0 <= idx < n:
                covered.add(idx)
    for d in data.get("deliverables", []):
        if isinstance(d, dict) and "done_index" in d:
            idx = d["done_index"]
            if isinstance(idx, int) and 0 <= idx < n:
                covered.add(idx)
    return len(covered) / n


# ---------------------------------------------------------------------------
# SR@k (MINT): Turn Budget Score
# ---------------------------------------------------------------------------

def turn_budget_score(data):
    """SR@k turn budget 준비도 (0.0 ~ 1.0).

    MINT SR@k는 "k턴 안에 성공했는가"를 측정한다.
    k를 정의하려면 timeout_minutes(시간 기반)와 stop_conditions(범위 기반)가 필요.
    - timeout_minutes 설정 → +0.5
    - stop_conditions 비어있지 않음 → +0.5
    둘 다 없으면 0.0 — k가 정의되지 않아 SR@k 측정 불가.
    """
    score = 0.0
    if data.get("timeout_minutes") is not None:
        score += 0.5
    if data.get("stop_conditions") and len(data["stop_conditions"]) > 0:
        score += 0.5
    return score


def safety_audit(data):
    """운영 안전 필드 감사. warnings 리스트 반환.

    null timeout은 유효한 값(무제한)이지만, 운영 관점에서는
    무한 실행·범위 초과 위험을 경고한다.
    """
    warnings = []
    if data.get("timeout_minutes") is None:
        warnings.append(
            "timeout_minutes가 null — worker가 무한 실행될 위험."
            " SR@k 측정을 위해 turn budget 설정을 권장한다"
        )
    sc = data.get("stop_conditions", [])
    if not sc or (isinstance(sc, list) and len(sc) == 0):
        warnings.append(
            "stop_conditions가 비어있음 — worker가 범위를 초과할 위험."
            " SR@k 측정을 위해 중단 조건 설정을 권장한다"
        )
    return warnings


# ---------------------------------------------------------------------------
# Resolve Rate (SWE-bench): F2P / P2P 구분 준비도
# ---------------------------------------------------------------------------

def resolve_readiness(data):
    """required_checks의 category 채택 비율 (0.0 ~ 1.0).

    SWE-bench Resolve Rate = F2P ∧ P2P.
    이를 측정하려면 각 check가 f2p/p2p/new/smoke/regression 중 하나로 분류되어야 한다.
    category가 하나도 없으면 0.0 — Resolve Rate 측정 불가.
    """
    checks = data.get("required_checks", [])
    if not checks:
        return 0.0
    categorized = sum(
        1 for c in checks
        if isinstance(c, dict) and c.get("category") in REQUIRED_CHECK_CATEGORIES
    )
    return categorized / len(checks)
