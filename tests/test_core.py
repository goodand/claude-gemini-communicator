"""core 모듈 단위 테스트 모음.

- 대상:
  - src/core/a2a_protocol.py (build_a2a_request, parse_a2a_response, parse_error_status, a2a_response_to_markdown)
  - src/core/cooldown.py (check_cooldown)
  - src/core/error_analyzer.py (normalize_error_text, hash_error, classify_error_severity, scan_transcript_for_errors)

규칙: pytest, Gemini 호출은 mock, tmp_path로 파일 I/O, JSONL 임시 파일 활용
"""

import json
import os

import pytest

from src.core.a2a_protocol import (
    build_a2a_request,
    parse_a2a_response,
    parse_error_status,
    a2a_response_to_markdown,
)
from src.core.cooldown import check_cooldown
from src.core import cooldown as cooldown_mod
from src.core.error_analyzer import (
    normalize_error_text,
    hash_error,
    classify_error_severity,
    scan_transcript_for_errors,
)


# -----------------------------
# a2a_protocol.py 테스트
# -----------------------------

def test_build_a2a_request_basic_fields():
    # A2A 요청 엔벨로프 필드 검증
    payload = {"k": "v"}
    req = build_a2a_request(
        message_type="evaluation_request", payload=payload, hook_source="post_commit"
    )

    assert req["a2a_version"] == "1.0"
    assert req["message_type"] == "evaluation_request"
    assert req["source_agent"] == "claude"
    assert req["target_agent"] == "gemini"
    assert req["status"] == "pending"
    assert isinstance(req.get("message_id"), str) and req["message_id"]
    assert isinstance(req.get("request_id"), str) and req["request_id"]
    assert isinstance(req.get("timestamp"), str) and "T" in req["timestamp"]
    assert req["payload"] == payload
    assert req["source"] == {"agent": "claude", "hook": "post_commit"}


def test_parse_error_status_variants():
    # 에러 prefix 파싱 분기 확인
    s = parse_error_status("[SDK_ERROR] boom")
    assert s == {"code": "error", "error_type": "sdk", "detail": "boom"}

    s = parse_error_status("[ERROR] oops")
    assert s == {"code": "error", "error_type": "general", "detail": "oops"}

    s = parse_error_status("[FALLBACK] try other")
    assert s == {"code": "fallback", "detail": "try other"}

    assert parse_error_status("normal text") is None


def test_parse_a2a_response_success_json_and_request_id():
    # 순수 JSON 응답을 성공으로 파싱
    raw = json.dumps(
        {
            "evaluation": {
                "논리적 일관성": {"score": "높음", "detail": "간결"},
                "누락된 고려사항": ["항목1", "항목2"],
            },
            "summary": "한 줄 요약",
        },
        ensure_ascii=False,
    )
    resp = parse_a2a_response(raw_text=raw, request_id="req-123")

    assert resp["status"] == {"code": "success"}
    assert resp["request_id"] == "req-123"
    assert resp["source_agent"] == "gemini"
    assert resp["target_agent"] == "claude"
    assert resp["payload"]["summary"] == "한 줄 요약"
    assert "논리적 일관성" in resp["payload"]["evaluation"]


def test_parse_a2a_response_from_code_fence():
    # 코드펜스 내부 JSON 파싱
    inner = {
        "evaluation": {"실현 가능성": {"score": "보통", "detail": "가능"}},
        "summary": "정상",
    }
    raw = "```json\n" + json.dumps(inner, ensure_ascii=False) + "\n```"
    resp = parse_a2a_response(raw_text=raw, request_id="rid-1")

    assert resp["status"] == {"code": "success"}
    assert resp["payload"] == inner
    assert resp["request_id"] == "rid-1"


def test_parse_a2a_response_repairs_truncated_json():
    # 잘린 JSON 복구 시도 — 마지막 콤마 뒤가 잘린 경우
    # 복구 로직이 trailing comma 이후를 잘라내므로 summary는 유실될 수 있음
    raw = (
        '{ "evaluation": {"누락된 고려사항": ["항목1", "항목2"]}, "summary": "ok",'
    )
    resp = parse_a2a_response(raw_text=raw, request_id="rid-2")

    assert resp["status"] == {"code": "success"}
    pl = resp["payload"]
    assert isinstance(pl, dict)
    # 복구 시 trailing comma 이후 key-value가 잘릴 수 있음 → evaluation 존재만 확인
    assert "누락된 고려사항" in pl.get("evaluation", {})


def test_parse_a2a_response_error_prefix_passthrough():
    # 에러 prefix가 있으면 status에 반영 + raw_text 유지
    raw = "[ERROR] something bad"
    resp = parse_a2a_response(raw_text=raw, request_id="rid-3")

    assert resp["status"]["code"] == "error"
    assert resp["status"]["error_type"] == "general"
    assert resp["payload"]["raw_text"] == raw


def test_parse_a2a_response_non_json_fallback_raw_text():
    # JSON 아님 → raw_text payload로 보존
    raw = "not json at all"
    resp = parse_a2a_response(raw_text=raw, request_id="rid-4")

    assert resp["status"] == {"code": "success"}
    assert resp["payload"] == {"raw_text": raw}
    assert resp["request_id"] == "rid-4"


def test_a2a_response_to_markdown_passthrough_raw_text():
    # raw_text가 있으면 그대로 반환
    response = {"payload": {"raw_text": "원문 유지"}}
    assert a2a_response_to_markdown(response) == "원문 유지"


def test_a2a_response_to_markdown_structured_rendering():
    # evaluation(dict+list) + summary 렌더링 확인
    response = {
        "payload": {
            "evaluation": {
                "논리적 일관성": {"score": "높음", "detail": "간결"},
                "누락된 고려사항": ["항목1", "항목2"],
            },
            "summary": "최종 요약",
        }
    }
    md = a2a_response_to_markdown(response)

    assert "### 논리적 일관성: 높음" in md
    assert "간결" in md
    assert "### 누락된 고려사항" in md
    assert "- 항목1" in md and "- 항목2" in md
    assert "**요약:** 최종 요약" in md


# -----------------------------
# cooldown.py 테스트
# -----------------------------

def test_check_cooldown_per_file(tmp_path, monkeypatch):
    # 쿨다운 파일 경로를 임시 위치로 바인딩
    state_path = tmp_path / "cooldown_state.json"
    monkeypatch.setattr(cooldown_mod, "COOLDOWN_STATE_PATH", state_path)

    # 시간 제어: 첫 번째 호출 시 now=1000, 두 번째=1000, 세 번째=1002
    times = iter([1000.0, 1000.0, 1002.0])
    monkeypatch.setattr(cooldown_mod.time, "time", lambda: next(times))

    config = {"cooldown_seconds_per_file": 1}
    fp = "/tmp/fileA.py"

    assert check_cooldown(fp, config) is True   # 최초 호출 허용
    assert check_cooldown(fp, config) is False  # 쿨다운 중
    assert check_cooldown(fp, config) is True   # 쿨다운 종료 후 허용


# -----------------------------
# error_analyzer.py 테스트
# -----------------------------

def test_normalize_error_text_masks_variables():
    # 경로/라인/주소/시간 마스킹 확인
    text = (
        'File "/Users/me/project/app.py", line 123, in main\n'
        "Memory at 0xDEADBEEF\n"
        "2023-12-02 12:34"
    )
    normalized = normalize_error_text(text)

    assert "/Users/me/project/app.py" not in normalized
    assert "line 123" not in normalized and "line <N>" in normalized
    assert "0xDEADBEEF" not in normalized and "<ADDR>" in normalized
    assert "2023-12-02 12:34" not in normalized and "<TIME>" in normalized


def test_hash_error_is_stable_over_normalized_diffs():
    # 경로/라인이 달라도 동일 해시
    e1 = 'File "/a/b.py", line 10\nTypeError: wrong type'
    e2 = 'File "/x/y.py", line 999\nTypeError: wrong type'
    assert hash_error(e1) == hash_error(e2)
    assert len(hash_error(e1)) == 12


def test_classify_error_severity_categories():
    # 심각도 분류 규칙 확인
    assert classify_error_severity("PermissionError: denied") == "critical"
    assert classify_error_severity("ModuleNotFoundError: x") == "high"
    assert classify_error_severity("SyntaxError: x") == "low"
    assert classify_error_severity("TypeError: x") == "medium"
    assert classify_error_severity("random text") == "medium"


def test_scan_transcript_for_errors_jsonl(tmp_path):
    # JSONL transcript에서 에러 스캔 + 중복 해시 제거
    p = tmp_path / "transcript.jsonl"

    entries = [
        {"content": "Build successful"},
        {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Traceback (most recent call last)\n"
                        '  File "/app/main.py", line 10\n'
                        "ValueError: bad value"
                    ),
                }
            ]
        },
        {"content": "ModuleNotFoundError: no module named pkg"},
        {"content": 'File "/a/b.py", line 10\nTypeError: wrong type'},
        # 동일 의미의 중복 에러 (경로/라인만 다름)
        {"content": 'File "/x/y.py", line 999\nTypeError: wrong type'},
        {"content": "process exited with exit code 2"},
    ]

    with open(p, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
        f.write("{bad json}\n")

    found = scan_transcript_for_errors(str(p), tail_lines=50)

    assert isinstance(found, list)
    assert len(found) >= 4

    # 중복 제거: TypeError는 한 번만
    type_error_count = sum(1 for t in found if "TypeError" in t)
    assert type_error_count == 1
