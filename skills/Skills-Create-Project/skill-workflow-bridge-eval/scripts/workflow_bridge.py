#!/usr/bin/env python3
"""skill-workflow-bridge-eval 통합 래퍼.

upstream skill 출력을 평가하고 다음 워크플로우 단계를 결정한다.
bridge_eval.json, retry_spec.json, handoff_packet.json을 생성한다.

Usage:
    python3 workflow_bridge.py classify --raw <output_file>
    python3 workflow_bridge.py evaluate --raw <output_file> [--contract <contract.json>]
    python3 workflow_bridge.py decide --eval <bridge_eval.json>
    python3 workflow_bridge.py retry-spec --eval <bridge_eval.json>
    python3 workflow_bridge.py handoff --eval <bridge_eval.json> [--next-skill <name>]
    python3 workflow_bridge.py run --raw <output_file> --contract <contract.json> [--output-dir <dir>]
    python3 workflow_bridge.py validate --artifact <file.json> --type <bridge_eval|retry_spec|handoff>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KST = timezone(timedelta(hours=9))

OUTPUT_TYPES = {"script_result", "structured_json", "natural_language", "mixed"}

DECISIONS = {
    "pass", "retry", "reroute", "loop",
    "stop", "escalate", "fanout", "fanin_hold",
}

FAILURE_TYPES = {
    "recoverable", "irrecoverable", "ambiguous",
    "external_blocked", "no_progress", "unsafe",
}

EVENTS = [
    "STEP_STARTED", "OUTPUT_CAPTURED", "CLASSIFICATION_COMPLETED",
    "NORMALIZATION_COMPLETED", "GRADE_COMPLETED",
    "DECISION_MADE", "HANDOFF_CREATED", "RETRY_SPEC_CREATED",
]

BRIDGE_EVAL_REQUIRED = {
    "run_id", "step_id", "skill_name", "output_type",
    "pass", "score", "confidence", "failure_type",
    "recommended_action", "unmet_conditions", "evidence",
    "next_step_ready",
}

RETRY_SPEC_REQUIRED = {
    "retryable", "retry_count", "max_retries", "failure_type",
    "unmet_conditions", "repair_instructions", "no_progress_signal",
}

HANDOFF_REQUIRED = {
    "ready", "decision", "next_skill", "normalized_summary",
    "key_outputs", "missing_items", "confidence", "source_artifacts",
}

# bridge_eval에서 금지 — packet 소유 필드
FORBIDDEN_IN_EVAL = {"goal", "done_definition", "allowed_paths", "constraints"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def _gen_id(prefix="RUN"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        if path.endswith(".json"):
            return json.load(f)
        return f.read()


def _save_json(path, data):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _log_event(events, event_type, detail=""):
    events.append({"event": event_type, "at": _now_iso(), "detail": detail})


# ---------------------------------------------------------------------------
# classify: 출력 유형 판정
# ---------------------------------------------------------------------------

def classify_output(raw_text):
    """출력 유형을 판정한다. (output_type, confidence, reasoning) 반환."""
    # _load가 JSON을 파싱하여 dict/list로 반환한 경우 즉시 structured_json
    if isinstance(raw_text, (dict, list)):
        return "structured_json", 0.95, "Already parsed JSON object"
    text = raw_text.strip()

    # JSON 시도
    try:
        parsed = json.loads(text)
        if isinstance(parsed, (dict, list)):
            return "structured_json", 0.95, "Valid JSON parsed"
    except (json.JSONDecodeError, ValueError):
        pass

    # exit code 패턴
    exit_pattern = re.search(r"exit\s*(code|status)\s*[=:]\s*\d+", text, re.IGNORECASE)
    stdout_pattern = re.search(r"(stdout|stderr)\s*[=:]", text, re.IGNORECASE)
    if exit_pattern or stdout_pattern:
        # JSON도 섞여있으면 mixed
        if "{" in text and "}" in text:
            return "mixed", 0.7, "Script output with embedded JSON"
        return "script_result", 0.85, "Exit code or stdout/stderr pattern detected"

    # 자연어 판정
    nl_indicators = 0
    if len(text.split()) > 20:
        nl_indicators += 1
    if re.search(r"[가-힣]{3,}", text):
        nl_indicators += 1
    if any(w in text.lower() for w in ["completed", "완료", "analyzed", "분석", "generated", "생성"]):
        nl_indicators += 1
    if re.search(r"^#+\s", text, re.MULTILINE):
        nl_indicators += 1

    # JSON 블록도 포함
    if nl_indicators >= 2 and "```" in text:
        return "mixed", 0.75, "Natural language with code blocks"

    if nl_indicators >= 2:
        return "natural_language", 0.8, "Multiple NL indicators"

    return "natural_language", 0.5, "Default classification (low confidence)"


def cmd_classify(args):
    raw = _load(args.raw)
    otype, conf, reason = classify_output(raw)
    result = {"output_type": otype, "confidence": conf, "reasoning": reason}
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# evaluate: extract + grade → bridge_eval.json
# ---------------------------------------------------------------------------

def extract_from_nl(text):
    """자연어에서 구조화된 정보를 추출한다."""
    extracted = {
        "task_completion_claim": "",
        "key_outputs": [],
        "missing_items": [],
        "open_questions": [],
        "evidence": [],
        "confidence": 0.5,
        "next_step_ready": False,
    }

    lines = text.split("\n")

    # completion claim 추출
    for line in lines:
        line_lower = line.lower().strip()
        if any(kw in line_lower for kw in ["completed", "완료", "done", "finished", "성공"]):
            extracted["task_completion_claim"] = line.strip()
            break

    # key outputs: 파일 경로, artifact 언급
    file_patterns = re.findall(r"[`'\"]?([a-zA-Z0-9_/\-]+\.\w{1,5})[`'\"]?", text)
    extracted["key_outputs"] = list(set(file_patterns))[:10]

    # evidence: 구체적 증거 (파일 존재, 테스트 통과 등)
    evidence_keywords = ["exists", "created", "passed", "생성", "존재", "통과", "test"]
    for line in lines:
        if any(kw in line.lower() for kw in evidence_keywords):
            cleaned = line.strip()
            if cleaned and len(cleaned) > 5:
                extracted["evidence"].append(cleaned)

    # missing items: "없", "누락", "missing", "TODO"
    missing_keywords = ["missing", "없", "누락", "todo", "필요", "needed", "not found"]
    for line in lines:
        if any(kw in line.lower() for kw in missing_keywords):
            cleaned = line.strip()
            if cleaned and len(cleaned) > 3:
                extracted["missing_items"].append(cleaned)

    # open questions
    for line in lines:
        if "?" in line or "질문" in line:
            cleaned = line.strip()
            if cleaned and len(cleaned) > 3:
                extracted["open_questions"].append(cleaned)

    # confidence 추정
    if extracted["evidence"] and not extracted["missing_items"]:
        extracted["confidence"] = 0.85
        extracted["next_step_ready"] = True
    elif extracted["evidence"] and extracted["missing_items"]:
        extracted["confidence"] = 0.5
    elif extracted["task_completion_claim"] and not extracted["evidence"]:
        extracted["confidence"] = 0.3  # claim만 있고 evidence 없음
    else:
        extracted["confidence"] = 0.2

    return extracted


def grade_output(extracted, contract=None):
    """추출 결과를 평가한다. (score, unmet_conditions, failure_type) 반환."""
    score = 0.0
    unmet = []
    max_score = 5.0

    # 1. completion claim 존재
    if extracted.get("task_completion_claim"):
        score += 1.0
    else:
        unmet.append("completion claim 없음")

    # 2. key outputs 존재
    if extracted.get("key_outputs"):
        score += 1.0
    else:
        unmet.append("key outputs 없음")

    # 3. evidence 존재
    if extracted.get("evidence"):
        score += 1.5
    else:
        unmet.append("evidence 부족 — artifact 존재 확인 필요")

    # 4. missing items 없음
    if not extracted.get("missing_items"):
        score += 1.0
    else:
        unmet.append(f"missing items 존재: {len(extracted['missing_items'])}개")

    # 5. contract 충족 (있으면)
    if contract:
        required = contract.get("required_fields", [])
        outputs = set(extracted.get("key_outputs", []))
        for req in required:
            if not any(req in o for o in outputs):
                unmet.append(f"contract 미충족: '{req}' 없음")
                score -= 0.5

    normalized = max(0.0, min(1.0, score / max_score))

    # failure type 판정
    if not unmet:
        ftype = None
    elif any("evidence" in u for u in unmet):
        ftype = "recoverable"
    elif len(unmet) >= 3:
        ftype = "irrecoverable"
    else:
        ftype = "recoverable"

    return normalized, unmet, ftype


def build_bridge_eval(raw_path, contract=None, run_id=None, step_id=None, skill_name=None):
    """raw output → bridge_eval.json 데이터 생성."""
    raw_text = _load(raw_path)
    otype, otype_conf, otype_reason = classify_output(raw_text)

    if otype in ("natural_language", "mixed"):
        text_for_nl = json.dumps(raw_text, ensure_ascii=False) if isinstance(raw_text, (dict, list)) else raw_text
        extracted = extract_from_nl(text_for_nl)
    elif otype == "structured_json":
        parsed = raw_text if isinstance(raw_text, (dict, list)) else json.loads(raw_text)
        extracted = {
            "task_completion_claim": "structured output",
            "key_outputs": list(parsed.keys()) if isinstance(parsed, dict) else [],
            "missing_items": [],
            "open_questions": [],
            "evidence": ["valid JSON structure"],
            "confidence": 0.9,
            "next_step_ready": True,
        }
    else:
        text_for_nl = json.dumps(raw_text, ensure_ascii=False) if isinstance(raw_text, (dict, list)) else raw_text
        extracted = extract_from_nl(text_for_nl)

    contract_data = None
    if contract and os.path.isfile(contract):
        contract_data = _load(contract)

    score, unmet, ftype = grade_output(extracted, contract_data)

    is_pass = len(unmet) == 0 and score >= 0.7
    next_ready = extracted.get("next_step_ready", False) and is_pass

    # recommended action
    if is_pass:
        action = "pass"
    elif ftype == "irrecoverable":
        action = "stop"
    elif ftype == "recoverable":
        action = "retry"
    else:
        action = "retry"

    return {
        "run_id": run_id or _gen_id("RUN"),
        "step_id": step_id or _gen_id("STEP"),
        "skill_name": skill_name or "unknown",
        "output_type": otype,
        "pass": is_pass,
        "score": round(score, 2),
        "confidence": round(extracted.get("confidence", 0.5), 2),
        "failure_type": ftype,
        "recommended_action": action,
        "unmet_conditions": unmet,
        "evidence": extracted.get("evidence", []),
        "next_step_ready": next_ready,
        "extracted": extracted,
    }


def cmd_evaluate(args):
    if not os.path.isfile(args.raw):
        print(f"[ERROR] 파일 없음: {args.raw}", file=sys.stderr)
        sys.exit(1)

    contract = getattr(args, "contract", None)
    run_id = getattr(args, "run_id", None)
    step_id = getattr(args, "step_id", None)
    skill_name = getattr(args, "skill_name", None)

    bridge = build_bridge_eval(args.raw, contract, run_id, step_id, skill_name)

    if args.output:
        _save_json(args.output, bridge)
        print(f"[OK] bridge_eval 생성: {args.output}")
    else:
        print(json.dumps(bridge, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# decide: bridge_eval → decision
# ---------------------------------------------------------------------------

def make_decision(bridge_eval):
    """bridge_eval에서 결정을 도출한다."""
    is_pass = bridge_eval.get("pass", False)
    score = bridge_eval.get("score", 0)
    ftype = bridge_eval.get("failure_type")
    unmet = bridge_eval.get("unmet_conditions", [])
    next_ready = bridge_eval.get("next_step_ready", False)

    # 무효 결정 방지
    if not next_ready and is_pass:
        is_pass = False  # next_step_ready=false → pass 불가

    if is_pass and next_ready:
        return "pass", "contract 충족, next_step_ready=true"

    if ftype == "irrecoverable":
        return "stop", f"irrecoverable failure: {unmet}"

    if ftype == "unsafe":
        return "stop", "unsafe output detected"

    if ftype == "ambiguous":
        return "escalate", f"ambiguous output: {unmet}"

    if ftype == "no_progress":
        return "stop", "no progress detected — loop 종료"

    if ftype == "external_blocked":
        return "reroute", "external dependency blocked"

    if ftype == "recoverable":
        return "retry", f"recoverable: {unmet}"

    # fallback
    if score < 0.3:
        return "stop", f"score too low: {score}"
    elif score < 0.7:
        return "retry", f"score below threshold: {score}"

    return "pass", "default pass"


def cmd_decide(args):
    bridge = _load(args.eval)
    decision, reason = make_decision(bridge)
    result = {"decision": decision, "reason": reason}
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# retry-spec: bridge_eval → retry_spec.json
# ---------------------------------------------------------------------------

def build_retry_spec(bridge_eval, retry_count=0, max_retries=3):
    """bridge_eval에서 retry spec을 생성한다. blind retry 금지."""
    unmet = bridge_eval.get("unmet_conditions", [])
    ftype = bridge_eval.get("failure_type", "recoverable")

    # repair instructions 생성 — blind retry 방지의 핵심
    instructions = []
    for condition in unmet:
        if "evidence" in condition.lower():
            instructions.append("각 claim에 대해 최소 1개의 구체적 evidence를 추가하세요 (파일 경로, 테스트 결과 등)")
        elif "missing" in condition.lower():
            instructions.append(f"누락 항목을 채우세요: {condition}")
        elif "contract" in condition.lower():
            instructions.append(f"계약 미충족 항목을 수정하세요: {condition}")
        elif "completion" in condition.lower():
            instructions.append("작업 완료 여부를 명시적으로 서술하세요")
        else:
            instructions.append(f"수정 필요: {condition}")

    if not instructions:
        instructions.append("이전 시도에서 부족했던 부분을 구체적으로 보완하세요")

    no_progress = retry_count >= 2 and len(unmet) > 0

    return {
        "retryable": ftype == "recoverable" and retry_count < max_retries,
        "retry_count": retry_count,
        "max_retries": max_retries,
        "failure_type": ftype,
        "unmet_conditions": unmet,
        "repair_instructions": instructions,
        "no_progress_signal": no_progress,
    }


def cmd_retry_spec(args):
    bridge = _load(args.eval)
    retry_count = getattr(args, "retry_count", 0) or 0
    max_retries = getattr(args, "max_retries", 3) or 3
    spec = build_retry_spec(bridge, retry_count, max_retries)

    if args.output:
        _save_json(args.output, spec)
        print(f"[OK] retry_spec 생성: {args.output}")
    else:
        print(json.dumps(spec, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# handoff: bridge_eval → handoff_packet.json
# ---------------------------------------------------------------------------

def build_handoff(bridge_eval, decision, next_skill=None):
    """canonical downstream input인 handoff_packet을 생성한다."""
    extracted = bridge_eval.get("extracted", {})
    is_ready = decision == "pass"

    return {
        "ready": is_ready,
        "decision": decision,
        "next_skill": next_skill,
        "normalized_summary": extracted.get("task_completion_claim", ""),
        "key_outputs": extracted.get("key_outputs", []),
        "missing_items": extracted.get("missing_items", []),
        "confidence": bridge_eval.get("confidence", 0),
        "source_artifacts": ["raw_output.md", "bridge_eval.json"],
    }


def cmd_handoff(args):
    bridge = _load(args.eval)
    decision, _ = make_decision(bridge)
    next_skill = getattr(args, "next_skill", None)
    packet = build_handoff(bridge, decision, next_skill)

    if args.output:
        _save_json(args.output, packet)
        print(f"[OK] handoff_packet 생성: {args.output}")
    else:
        print(json.dumps(packet, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# run: 전체 파이프라인
# ---------------------------------------------------------------------------

def cmd_run(args):
    """classify → evaluate → decide → retry-spec/handoff 일괄 실행."""
    if not os.path.isfile(args.raw):
        print(f"[ERROR] 파일 없음: {args.raw}", file=sys.stderr)
        sys.exit(1)

    out_dir = args.output_dir or ".bridge_eval"
    os.makedirs(out_dir, exist_ok=True)
    events = []

    # 1. classify
    _log_event(events, "STEP_STARTED", f"raw={args.raw}")
    _log_event(events, "OUTPUT_CAPTURED", args.raw)

    raw_text = _load(args.raw)
    otype, conf, reason = classify_output(raw_text)
    _log_event(events, "CLASSIFICATION_COMPLETED", f"type={otype} conf={conf}")

    # 2. evaluate
    contract = getattr(args, "contract", None)
    run_id = getattr(args, "run_id", None) or _gen_id("RUN")
    step_id = getattr(args, "step_id", None) or _gen_id("STEP")
    skill_name = getattr(args, "skill_name", None) or "unknown"

    bridge = build_bridge_eval(args.raw, contract, run_id, step_id, skill_name)
    bridge_path = os.path.join(out_dir, "bridge_eval.json")
    _save_json(bridge_path, bridge)
    _log_event(events, "GRADE_COMPLETED", f"score={bridge['score']} pass={bridge['pass']}")

    # 3. decide
    decision, reason = make_decision(bridge)
    _log_event(events, "DECISION_MADE", f"decision={decision} reason={reason}")

    # 4. retry-spec or handoff
    if decision in ("retry", "loop"):
        retry_count = getattr(args, "retry_count", 0) or 0
        spec = build_retry_spec(bridge, retry_count)
        spec_path = os.path.join(out_dir, "retry_spec.json")
        _save_json(spec_path, spec)
        _log_event(events, "RETRY_SPEC_CREATED", spec_path)

        # blind retry 방지 검증
        if not spec.get("repair_instructions"):
            print("[ERROR] blind retry 감지 — repair_instructions가 비어있음", file=sys.stderr)
            sys.exit(1)
    else:
        next_skill = getattr(args, "next_skill", None)
        packet = build_handoff(bridge, decision, next_skill)
        handoff_path = os.path.join(out_dir, "handoff_packet.json")
        _save_json(handoff_path, packet)
        _log_event(events, "HANDOFF_CREATED", handoff_path)

    # 5. raw output 보존
    raw_copy = os.path.join(out_dir, "raw_output.md")
    with open(raw_copy, "w", encoding="utf-8") as f:
        f.write(raw_text)

    # 6. event log 저장
    event_log = {
        "run_id": run_id,
        "step_id": step_id,
        "skill_name": skill_name,
        "workflow_mode": "sequential",
        "output_type": otype,
        "decision": decision,
        "decision_reason": reason,
        "score": bridge["score"],
        "confidence": bridge["confidence"],
        "events": events,
    }
    log_path = os.path.join(out_dir, "event_log.json")
    _save_json(log_path, event_log)

    # 결과 요약
    print(f"[OK] pipeline 완료: {out_dir}/")
    print(f"     output_type: {otype}")
    print(f"     score: {bridge['score']}")
    print(f"     decision: {decision}")
    print(f"     artifacts: bridge_eval.json, {'retry_spec.json' if decision in ('retry', 'loop') else 'handoff_packet.json'}, event_log.json")


# ---------------------------------------------------------------------------
# validate: artifact 검증
# ---------------------------------------------------------------------------

def cmd_validate(args):
    """artifact JSON 스키마 검증."""
    data = _load(args.artifact)
    atype = args.type
    errors = []

    # 금지 필드 체크
    for f in FORBIDDEN_IN_EVAL:
        if f in data:
            errors.append(f"금지 필드 포함: '{f}' — packet 소유 필드를 eval에 넣지 않는다")

    if atype == "bridge_eval":
        missing = BRIDGE_EVAL_REQUIRED - set(data.keys())
        if missing:
            errors.append(f"필수 필드 누락: {sorted(missing)}")
        if "recommended_action" in data and data["recommended_action"] not in DECISIONS:
            errors.append(f"잘못된 recommended_action: {data['recommended_action']}")
        if "failure_type" in data and data["failure_type"] is not None:
            if data["failure_type"] not in FAILURE_TYPES:
                errors.append(f"잘못된 failure_type: {data['failure_type']}")
        # next_step_ready=false인데 pass=true → 무효
        if data.get("pass") and not data.get("next_step_ready"):
            errors.append("pass=true인데 next_step_ready=false — 무효 상태")

    elif atype == "retry_spec":
        missing = RETRY_SPEC_REQUIRED - set(data.keys())
        if missing:
            errors.append(f"필수 필드 누락: {sorted(missing)}")
        # blind retry 방지
        if data.get("retryable") and not data.get("repair_instructions"):
            errors.append("retryable=true인데 repair_instructions 비어있음 — blind retry 금지")

    elif atype == "handoff":
        missing = HANDOFF_REQUIRED - set(data.keys())
        if missing:
            errors.append(f"필수 필드 누락: {sorted(missing)}")
        if "decision" in data and data["decision"] not in DECISIONS:
            errors.append(f"잘못된 decision: {data['decision']}")

    else:
        errors.append(f"알 수 없는 artifact type: {atype}")

    name = os.path.basename(args.artifact)
    if errors:
        for e in errors:
            print(f"[ERROR] {name}: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"[OK] {name}: 검증 통과")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="skill-workflow-bridge-eval 통합 래퍼",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # classify
    p_cls = sub.add_parser("classify", help="출력 유형 판정")
    p_cls.add_argument("--raw", required=True, help="raw output 파일")

    # evaluate
    p_eval = sub.add_parser("evaluate", help="extract + grade → bridge_eval")
    p_eval.add_argument("--raw", required=True, help="raw output 파일")
    p_eval.add_argument("--contract", help="downstream contract JSON")
    p_eval.add_argument("--run-id", help="run ID")
    p_eval.add_argument("--step-id", help="step ID")
    p_eval.add_argument("--skill-name", help="upstream skill name")
    p_eval.add_argument("--output", "-o", help="bridge_eval.json 출력 경로")

    # decide
    p_dec = sub.add_parser("decide", help="bridge_eval → decision")
    p_dec.add_argument("--eval", required=True, help="bridge_eval.json")

    # retry-spec
    p_retry = sub.add_parser("retry-spec", help="bridge_eval → retry_spec")
    p_retry.add_argument("--eval", required=True, help="bridge_eval.json")
    p_retry.add_argument("--retry-count", type=int, default=0, help="현재 retry 횟수")
    p_retry.add_argument("--max-retries", type=int, default=3, help="최대 retry")
    p_retry.add_argument("--output", "-o", help="retry_spec.json 출력 경로")

    # handoff
    p_hand = sub.add_parser("handoff", help="bridge_eval → handoff_packet")
    p_hand.add_argument("--eval", required=True, help="bridge_eval.json")
    p_hand.add_argument("--next-skill", help="다음 skill 이름")
    p_hand.add_argument("--output", "-o", help="handoff_packet.json 출력 경로")

    # run (full pipeline)
    p_run = sub.add_parser("run", help="전체 파이프라인 일괄 실행")
    p_run.add_argument("--raw", required=True, help="raw output 파일")
    p_run.add_argument("--contract", help="downstream contract JSON")
    p_run.add_argument("--run-id", help="run ID")
    p_run.add_argument("--step-id", help="step ID")
    p_run.add_argument("--skill-name", help="upstream skill name")
    p_run.add_argument("--next-skill", help="다음 skill 이름")
    p_run.add_argument("--retry-count", type=int, default=0)
    p_run.add_argument("--output-dir", default=".bridge_eval", help="출력 디렉토리")

    # validate
    p_val = sub.add_parser("validate", help="artifact JSON 검증")
    p_val.add_argument("--artifact", required=True, help="JSON 파일")
    p_val.add_argument("--type", required=True, choices=["bridge_eval", "retry_spec", "handoff"],
                       help="artifact 유형")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "classify": cmd_classify,
        "evaluate": cmd_evaluate,
        "decide": cmd_decide,
        "retry-spec": cmd_retry_spec,
        "handoff": cmd_handoff,
        "run": cmd_run,
        "validate": cmd_validate,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
