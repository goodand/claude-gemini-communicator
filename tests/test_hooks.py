"""Hook 단위 테스트 모음.

- 대상:
  - src/hooks/hook_auto_task.py (main)
  - src/hooks/hook_stop.py (extract_last_assistant_text, handle_plan_detection, handle_error_detection)
  - src/hooks/hook_pre_tool.py (위험 명령 감지)

규칙: pytest, Gemini/외부 호출 전부 mock, stdin은 monkeypatch, capsys로 stdout 캡처
"""

import io
import json

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# hook_auto_task: main
# ─────────────────────────────────────────────────────────────────────────────


def _mock_config_auto_task(**overrides):
    """hook_auto_task용 기본 config 생성 헬퍼."""
    base = {
        "watch_extensions": [".md", ".txt", ".py"],
        "exclude_files": [],
        "code_extensions": [".py", ".js"],
        "evaluation_prompt": "이 문서를 평가해줘.",
        "code_evaluation_prompt": "이 코드를 리뷰해줘.",
        "async_mode": False,
        "a2a_schema_enabled": False,
        "gemini_cmd": "/usr/local/bin/gemini",
        "gemini_timeout": 5,
    }
    base.update(overrides)
    return base


def test_hook_auto_task_skip_wrong_tool(monkeypatch, capsys):
    # Write/Edit 이외의 tool은 즉시 종료 (stdout 없음)
    from src.hooks import hook_auto_task

    monkeypatch.setattr(hook_auto_task, "load_env", lambda: None)
    monkeypatch.setattr(hook_auto_task, "load_config", lambda: _mock_config_auto_task())

    hook_input = {"tool_name": "Bash", "tool_input": {"file_path": "note.md"}}
    monkeypatch.setattr(hook_auto_task.sys, "stdin", io.StringIO(json.dumps(hook_input)))

    with pytest.raises(SystemExit):
        hook_auto_task.main()

    out = capsys.readouterr().out
    assert out == ""


def test_hook_auto_task_skip_non_matching_ext(monkeypatch, capsys):
    # watch_extensions에 매칭되지 않으면 종료
    from src.hooks import hook_auto_task

    monkeypatch.setattr(hook_auto_task, "load_env", lambda: None)
    monkeypatch.setattr(hook_auto_task, "load_config", lambda: _mock_config_auto_task(watch_extensions=[".md"]))

    hook_input = {"tool_name": "Write", "tool_input": {"file_path": "note.txt"}}
    monkeypatch.setattr(hook_auto_task.sys, "stdin", io.StringIO(json.dumps(hook_input)))

    with pytest.raises(SystemExit):
        hook_auto_task.main()

    out = capsys.readouterr().out
    assert out == ""


def test_hook_auto_task_kill_switch_disabled(monkeypatch, capsys):
    # auto_hooks_enabled=False면 확장자/쿨다운/평가 로직 전에 조기 종료
    from src.hooks import hook_auto_task

    monkeypatch.setattr(hook_auto_task, "load_env", lambda: None)
    monkeypatch.setattr(
        hook_auto_task,
        "load_config",
        lambda: _mock_config_auto_task(auto_hooks_enabled=False, watch_extensions=[".md"]),
    )
    monkeypatch.setattr(hook_auto_task, "check_cooldown", lambda fp, cfg: True)

    def _fail_if_reached(*a, **k):
        raise AssertionError("kill-switch가 무시되고 평가 경로에 도달함")

    monkeypatch.setattr(hook_auto_task, "resolve_target", _fail_if_reached)

    hook_input = {"tool_name": "Write", "tool_input": {"file_path": "doc.md"}}
    monkeypatch.setattr(hook_auto_task.sys, "stdin", io.StringIO(json.dumps(hook_input)))

    with pytest.raises(SystemExit) as e:
        hook_auto_task.main()

    assert e.value.code == 0
    assert capsys.readouterr().out == ""


class _FakeProvider:
    """provider 레지스트리 seam용 가짜 — call/call_async가 고정 응답을 돌려주고 prompt를 기록."""

    def __init__(self, respond=lambda prompt: "RAW_FEEDBACK"):
        self.respond = respond
        self.seen_prompts = []

    def call(self, content, prompt, config, file_path=None):
        self.seen_prompts.append(prompt)
        return self.respond(prompt)

    def call_async(self, content, prompt, config, file_path=None, source=None):
        self.seen_prompts.append(prompt)
        return "PENDING"


def test_hook_auto_task_sync_mode_saves_feedback(monkeypatch, capsys):
    # 동기 모드에서 provider 호출 결과를 저장 후 포맷하여 출력
    from src.hooks import hook_auto_task

    monkeypatch.setattr(hook_auto_task, "load_env", lambda: None)
    monkeypatch.setattr(hook_auto_task, "check_cooldown", lambda fp, cfg: True)

    saved = {}

    def fake_save_feedback(feedback, source, file_path=None, request_id=None, **kwargs):
        saved["feedback"] = feedback
        saved["source"] = source
        saved["file_path"] = file_path
        saved["request_id"] = request_id

    monkeypatch.setattr(hook_auto_task, "save_feedback", fake_save_feedback)
    monkeypatch.setattr(hook_auto_task, "get_provider", lambda agent: _FakeProvider())
    monkeypatch.setattr(
        hook_auto_task,
        "load_config",
        lambda: _mock_config_auto_task(async_mode=False, a2a_schema_enabled=False, watch_extensions=[".md"]),
    )

    hook_input = {"tool_name": "Write", "tool_input": {"file_path": "doc.md"}}
    monkeypatch.setattr(hook_auto_task.sys, "stdin", io.StringIO(json.dumps(hook_input)))

    hook_auto_task.main()

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert "RAW_FEEDBACK" in payload["hookSpecificOutput"]["additionalContext"]
    assert saved["feedback"] == "RAW_FEEDBACK"
    assert saved["file_path"] == "doc.md"
    assert saved["request_id"]


def test_hook_auto_task_uses_code_prompt_for_code_ext(monkeypatch):
    # 코드 확장자 파일이면 code_evaluation_prompt 사용
    from src.hooks import hook_auto_task

    monkeypatch.setattr(hook_auto_task, "load_env", lambda: None)
    monkeypatch.setattr(hook_auto_task, "check_cooldown", lambda fp, cfg: True)

    fake = _FakeProvider(respond=lambda prompt: "OK")
    monkeypatch.setattr(hook_auto_task, "get_provider", lambda agent: fake)
    monkeypatch.setattr(
        hook_auto_task,
        "load_config",
        lambda: _mock_config_auto_task(watch_extensions=[".py", ".md"], a2a_schema_enabled=False),
    )

    hook_input = {"tool_name": "Write", "tool_input": {"file_path": "main.py"}}
    monkeypatch.setattr(hook_auto_task.sys, "stdin", io.StringIO(json.dumps(hook_input)))
    monkeypatch.setattr(hook_auto_task, "save_feedback", lambda *a, **k: None)
    hook_auto_task.main()

    assert any("이 코드를 리뷰해줘." in p for p in fake.seen_prompts)


# ─────────────────────────────────────────────────────────────────────────────
# hook_pre_tool: check_command + main
# ─────────────────────────────────────────────────────────────────────────────


def _mock_config_pre_tool(**overrides):
    base = {"pre_tool_guard": {"enabled": True}, "gemini_cmd": "/usr/local/bin/gemini", "gemini_timeout": 5}
    base.update(overrides)
    return base


def test_pre_tool_check_command_block_rm_rf():
    # rm -rf 같은 치명적 명령은 block
    from src.hooks.hook_pre_tool import check_command

    res = check_command("rm -rf /", _mock_config_pre_tool())
    assert res and res["severity"] == "block"


def test_pre_tool_check_command_contextual_sql():
    # DROP TABLE은 DB 콘텍스트가 있을 때만 차단
    from src.hooks.hook_pre_tool import check_command

    assert check_command("DROP TABLE users;", _mock_config_pre_tool()) is None
    res = check_command("psql -c 'DROP TABLE users;'", _mock_config_pre_tool())
    assert res and res["severity"] == "block"


def test_pre_tool_check_command_warn_examples():
    # 경고 패턴은 warn으로 반환
    from src.hooks.hook_pre_tool import check_command

    assert check_command("git branch -D feature/tmp", _mock_config_pre_tool())["severity"] == "warn"
    assert check_command("chmod 777 app.py", _mock_config_pre_tool())["severity"] == "warn"
    assert check_command("pip install requests", _mock_config_pre_tool())["severity"] == "warn"


def test_pre_tool_check_command_quote_heredoc_suppression():
    # 따옴표/heredoc 내부의 위험 키워드는 오탐 방지
    from src.hooks.hook_pre_tool import check_command

    assert check_command('echo "rm -rf /"', _mock_config_pre_tool()) is None


def test_pre_tool_main_block_output(monkeypatch, capsys):
    # main은 block 판정 시 JSON을 stdout에 출력
    from src.hooks import hook_pre_tool

    monkeypatch.setattr(hook_pre_tool, "load_env", lambda: None)
    monkeypatch.setattr(hook_pre_tool, "load_config", lambda: _mock_config_pre_tool())

    hook_input = {"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}}
    monkeypatch.setattr(hook_pre_tool.sys, "stdin", io.StringIO(json.dumps(hook_input)))

    hook_pre_tool.main()

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["decision"] == "block"
    assert "위험 명령" in payload["reason"]


# ─────────────────────────────────────────────────────────────────────────────
# hook_stop: extract_last_assistant_text / handle_plan_detection / handle_error_detection
# ─────────────────────────────────────────────────────────────────────────────

from src.hooks.hook_stop import (
    extract_last_assistant_text,
    handle_plan_detection,
    handle_error_detection,
)


def _mock_config_stop(**overrides):
    base = {
        "plan_detection_prompt": "이 텍스트는 계획입니까?",
        "evaluation_prompt": "평가해줘",
        "async_mode": False,
        "a2a_schema_enabled": False,
        "error_detection": {"enabled": True, "tail_lines": 50},
        "gemini_cmd": "/usr/local/bin/gemini",
        "gemini_timeout": 5,
        "min_content_length": 10,
    }
    base.update(overrides)
    return base


def test_stop_extract_last_assistant_text_from_transcript(tmp_path):
    # transcript JSONL의 마지막 assistant 텍스트를 추출
    lines = [
        json.dumps({"role": "user", "content": "hi"}),
        json.dumps({
            "role": "assistant",
            "content": [{"type": "text", "text": "first"}],
        }),
        json.dumps({
            "role": "assistant",
            "content": [
                {"type": "text", "text": "second"},
                {"type": "text", "text": "line"},
            ],
        }),
    ]
    tpath = tmp_path / "transcript.jsonl"
    tpath.write_text("\n".join(lines), encoding="utf-8")

    stop_input = {"transcript_path": str(tpath)}
    result = extract_last_assistant_text(stop_input)
    assert result == "second\nline"


def test_stop_extract_last_assistant_text_fallbacks():
    # transcript 없으면 message → content 순으로 사용
    assert extract_last_assistant_text({"message": "MSG"}) == "MSG"
    content_list = [{"type": "text", "text": "A"}, {"type": "text", "text": "B"}]
    assert extract_last_assistant_text({"content": content_list}) == "A\nB"
    assert extract_last_assistant_text({}) == ""


def test_stop_handle_plan_detection_min_length_gate(monkeypatch):
    # 최소 길이 미만이면 감지 스킵
    cfg = _mock_config_stop(min_content_length=100)
    assert handle_plan_detection("short", cfg) is None


def test_stop_handle_plan_detection_yes_sync(monkeypatch):
    # 예로 분류되면 동기 평가 후 저장
    cfg = _mock_config_stop(async_mode=False, a2a_schema_enabled=False)

    called = {"classified": False, "evaluated": False, "saved": False}

    def respond(prompt):
        if "계획" in prompt or "분류" in prompt:
            called["classified"] = True
            return "예"
        called["evaluated"] = True
        return "EVAL_RESULT"

    def fake_save(feedback, source, file_path=None, request_id=None, **kwargs):
        called["saved"] = True

    monkeypatch.setattr("src.hooks.hook_stop.get_provider", lambda agent: _FakeProvider(respond=respond))
    monkeypatch.setattr("src.hooks.hook_stop.save_feedback", fake_save)

    res = handle_plan_detection("A" * 200, cfg)
    assert called["classified"] and called["evaluated"] and called["saved"]
    assert res == "EVAL_RESULT"


def test_stop_main_kill_switch_disabled(monkeypatch, capsys):
    # auto_hooks_enabled=False면 plan/error 감지 진입 전에 조기 종료
    from src.hooks import hook_stop

    monkeypatch.setattr(hook_stop, "load_env", lambda: None)
    monkeypatch.setattr(
        hook_stop, "load_config", lambda: _mock_config_stop(auto_hooks_enabled=False)
    )

    def _fail_if_reached(*a, **k):
        raise AssertionError("kill-switch가 무시되고 감지 경로에 도달함")

    monkeypatch.setattr(hook_stop, "handle_plan_detection", _fail_if_reached)
    monkeypatch.setattr(hook_stop, "handle_error_detection", _fail_if_reached)

    monkeypatch.setattr(hook_stop.sys, "stdin", io.StringIO("{}"))

    with pytest.raises(SystemExit) as e:
        hook_stop.main()

    assert e.value.code == 0
    assert capsys.readouterr().out == ""


def test_stop_handle_error_detection_flows(monkeypatch, tmp_path):
    # 에러 감지 설정/흐름 검증
    cfg_disabled = _mock_config_stop(error_detection={"enabled": False})
    assert handle_error_detection({}, cfg_disabled) is None

    cfg_enabled = _mock_config_stop(error_detection={"enabled": True, "tail_lines": 5})

    # transcript 미제공 → None
    assert handle_error_detection({}, cfg_enabled) is None

    # transcript 제공 + 에러 없음 → None
    tpath = tmp_path / "t.jsonl"
    tpath.write_text("{}\n{}\n", encoding="utf-8")
    monkeypatch.setattr("src.hooks.hook_stop.scan_transcript_for_errors", lambda path, tail: [])
    assert handle_error_detection({"transcript_path": str(tpath)}, cfg_enabled) is None

    # 에러 존재 → check_error_and_analyze 결과 반환
    monkeypatch.setattr("src.hooks.hook_stop.scan_transcript_for_errors", lambda path, tail: ["Error: boom"])
    monkeypatch.setattr("src.hooks.hook_stop.check_error_and_analyze", lambda errs, config: "ANALYZED")
    assert handle_error_detection({"transcript_path": str(tpath)}, cfg_enabled) == "ANALYZED"
