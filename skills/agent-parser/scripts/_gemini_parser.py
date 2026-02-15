#!/usr/bin/env python3
"""Gemini JSON 파서: Gemini headless JSON 출력을 구조화 요약으로 변환."""

import json


def to_int(value) -> int:
    """숫자형 필드를 안전하게 int로 변환."""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def parse_gemini_json(raw_text: str) -> dict | None:
    """Gemini JSON을 파싱하여 필요한 필드만 추출."""
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 실패: {e.msg} (line {e.lineno}, col {e.colno})")
        return None

    if not isinstance(payload, dict):
        print("[ERROR] JSON 루트가 객체(dict)가 아닙니다.")
        return None

    stats = payload.get("stats") if isinstance(payload.get("stats"), dict) else {}
    models_raw = stats.get("models") if isinstance(stats.get("models"), dict) else {}
    tools_raw = stats.get("tools") if isinstance(stats.get("tools"), dict) else {}
    files_raw = stats.get("files") if isinstance(stats.get("files"), dict) else {}

    models = []
    for model_name, model_data in models_raw.items():
        if not isinstance(model_data, dict):
            continue
        api = model_data.get("api") if isinstance(model_data.get("api"), dict) else {}
        tokens = model_data.get("tokens") if isinstance(model_data.get("tokens"), dict) else {}

        models.append(
            {
                "name": model_name,
                "api": {
                    "total_requests": to_int(api.get("totalRequests")),
                    "total_errors": to_int(api.get("totalErrors")),
                    "total_latency_ms": to_int(api.get("totalLatencyMs")),
                },
                "tokens": {
                    "input": to_int(tokens.get("input")),
                    "prompt": to_int(tokens.get("prompt")),
                    "candidates": to_int(tokens.get("candidates")),
                    "total": to_int(tokens.get("total")),
                    "cached": to_int(tokens.get("cached")),
                    "thoughts": to_int(tokens.get("thoughts")),
                    "tool": to_int(tokens.get("tool")),
                },
            }
        )

    tools_by_name_raw = tools_raw.get("byName") if isinstance(tools_raw.get("byName"), dict) else {}
    tools_by_name = []
    for tool_name, tool_data in tools_by_name_raw.items():
        if not isinstance(tool_data, dict):
            continue
        decisions = tool_data.get("decisions") if isinstance(tool_data.get("decisions"), dict) else {}
        tools_by_name.append(
            {
                "name": tool_name,
                "count": to_int(tool_data.get("count")),
                "success": to_int(tool_data.get("success")),
                "fail": to_int(tool_data.get("fail")),
                "duration_ms": to_int(tool_data.get("durationMs")),
                "decisions": {
                    "accept": to_int(decisions.get("accept")),
                    "reject": to_int(decisions.get("reject")),
                    "modify": to_int(decisions.get("modify")),
                    "auto_accept": to_int(decisions.get("auto_accept")),
                },
            }
        )

    total_decisions = (
        tools_raw.get("totalDecisions") if isinstance(tools_raw.get("totalDecisions"), dict) else {}
    )
    error_value = payload.get("error")
    if isinstance(error_value, (dict, list)):
        error_parsed = error_value
    elif error_value is None:
        error_parsed = None
    else:
        error_parsed = str(error_value)

    return {
        "session_id": payload.get("session_id"),
        "response": payload.get("response"),
        "models": models,
        "tools": {
            "total_calls": to_int(tools_raw.get("totalCalls")),
            "total_success": to_int(tools_raw.get("totalSuccess")),
            "total_fail": to_int(tools_raw.get("totalFail")),
            "total_duration_ms": to_int(tools_raw.get("totalDurationMs")),
            "total_decisions": {
                "accept": to_int(total_decisions.get("accept")),
                "reject": to_int(total_decisions.get("reject")),
                "modify": to_int(total_decisions.get("modify")),
                "auto_accept": to_int(total_decisions.get("auto_accept")),
            },
            "by_name": tools_by_name,
        },
        "files": {
            "total_lines_added": to_int(files_raw.get("totalLinesAdded")),
            "total_lines_removed": to_int(files_raw.get("totalLinesRemoved")),
        },
        "error": error_parsed,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약 생성."""
    lines = []
    lines.append("# Gemini JSON 요약")
    lines.append("")
    lines.append(f"- session_id: {parsed.get('session_id') or '(없음)'}")
    lines.append(f"- error: {json.dumps(parsed.get('error'), ensure_ascii=False) if parsed.get('error') is not None else '(없음)'}")
    lines.append("")

    lines.append("## 최종 응답(response)")
    response = parsed.get("response")
    lines.append(response if isinstance(response, str) and response else "(없음)")
    lines.append("")

    lines.append("## 모델 통계")
    models = parsed.get("models", [])
    if models:
        for idx, model in enumerate(models, start=1):
            api = model.get("api", {})
            tokens = model.get("tokens", {})
            lines.append(
                f"{idx}. {model.get('name')} | requests={api.get('total_requests', 0)}, "
                f"errors={api.get('total_errors', 0)}, latency_ms={api.get('total_latency_ms', 0)}"
            )
            lines.append(
                "   "
                f"tokens(input={tokens.get('input', 0)}, prompt={tokens.get('prompt', 0)}, "
                f"candidates={tokens.get('candidates', 0)}, total={tokens.get('total', 0)}, "
                f"cached={tokens.get('cached', 0)}, thoughts={tokens.get('thoughts', 0)}, "
                f"tool={tokens.get('tool', 0)})"
            )
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## 도구 사용 통계")
    tools = parsed.get("tools", {})
    lines.append(
        f"- totals: calls={tools.get('total_calls', 0)}, success={tools.get('total_success', 0)}, "
        f"fail={tools.get('total_fail', 0)}, duration_ms={tools.get('total_duration_ms', 0)}"
    )
    decisions = tools.get("total_decisions", {})
    lines.append(
        f"- decisions: accept={decisions.get('accept', 0)}, reject={decisions.get('reject', 0)}, "
        f"modify={decisions.get('modify', 0)}, auto_accept={decisions.get('auto_accept', 0)}"
    )
    by_name = tools.get("by_name", [])
    if by_name:
        lines.append("- by_name:")
        for idx, tool in enumerate(by_name, start=1):
            lines.append(
                f"  {idx}. {tool.get('name')} | count={tool.get('count', 0)}, success={tool.get('success', 0)}, "
                f"fail={tool.get('fail', 0)}, duration_ms={tool.get('duration_ms', 0)}"
            )
    else:
        lines.append("- by_name: (없음)")
    lines.append("")

    files = parsed.get("files", {})
    lines.append("## 파일 변경 통계")
    lines.append(
        f"- lines_added={files.get('total_lines_added', 0)}, lines_removed={files.get('total_lines_removed', 0)}"
    )

    return "\n".join(lines).rstrip() + "\n"
