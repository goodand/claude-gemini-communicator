"""shared 모듈 단위 테스트 모음.

- 대상:
  - src/shared/config.py (load_config, load_env, validate_config)
  - src/shared/feedback.py (save_feedback)
  - src/shared/hook_io.py (format_hook_output, read_file_content)

규칙: pytest, 외부 API 호출 금지, tmp_path 사용, 한국어 주석
"""

import json
import os

import pytest

from src.shared import config as config_mod
from src.shared.config import load_config, load_env, validate_config
from src.shared import feedback as feedback_mod
from src.shared.feedback import save_feedback
from src.shared.hook_io import format_hook_output, read_file_content


# ─────────────────────────────────────────────────────────────────────────────
# config.py 테스트
# ─────────────────────────────────────────────────────────────────────────────

def test_load_config_from_custom_path(tmp_path):
    # 임시 config.json 로드
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"gemini_timeout": 42}), encoding="utf-8")

    result = load_config(config_path=cfg_file)
    assert result["gemini_timeout"] == 42


def test_load_config_default_path():
    # 기본 경로(scripts/config.json) 로드 검증
    result = load_config()
    assert isinstance(result, dict)
    assert "gemini_cmd" in result
    assert "watch_extensions" in result


def test_load_env_sets_new_vars(tmp_path, monkeypatch):
    # .env 파일에서 새 환경변수를 설정
    env_file = tmp_path / ".env"
    env_file.write_text('NEW_VAR=hello\nQUOTED="world"\n# 주석\n', encoding="utf-8")
    monkeypatch.setattr(config_mod, "ENV_PATH", env_file)

    # 기존 환경변수에 없는 키만 설정
    monkeypatch.delenv("NEW_VAR", raising=False)
    monkeypatch.delenv("QUOTED", raising=False)

    load_env()
    assert os.environ["NEW_VAR"] == "hello"
    assert os.environ["QUOTED"] == "world"


def test_load_env_does_not_overwrite_existing(tmp_path, monkeypatch):
    # 이미 존재하는 환경변수는 덮어쓰지 않음
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=new_value\n", encoding="utf-8")
    monkeypatch.setattr(config_mod, "ENV_PATH", env_file)
    monkeypatch.setenv("EXISTING", "original")

    load_env()
    assert os.environ["EXISTING"] == "original"


def test_load_env_missing_file(tmp_path, monkeypatch):
    # .env 파일이 없으면 에러 없이 반환
    monkeypatch.setattr(config_mod, "ENV_PATH", tmp_path / "nonexistent")
    load_env()  # 예외 없이 통과


def test_load_env_skips_comments_and_empty_lines(tmp_path, monkeypatch):
    # 주석, 빈 줄, = 없는 줄은 무시
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\n\nNO_EQUALS\nVALID=ok\n", encoding="utf-8")
    monkeypatch.setattr(config_mod, "ENV_PATH", env_file)
    monkeypatch.delenv("VALID", raising=False)

    load_env()
    assert os.environ.get("VALID") == "ok"
    assert "NO_EQUALS" not in os.environ


def test_validate_config_all_ok():
    # 정상 config는 이슈 없음
    config = {
        "gemini_cmd": "/usr/local/bin/gemini",
        "gemini_timeout": 90,
        "watch_extensions": [".md"],
        "evaluation_prompt": "평가해줘",
    }
    assert validate_config(config) == []


def test_validate_config_missing_required():
    # 필수 필드 누락 감지
    issues = validate_config({})
    assert len(issues) >= 4
    assert all(level == "error" for level, _ in issues)


def test_validate_config_type_error():
    # 타입 오류 감지
    config = {
        "gemini_cmd": 123,  # str이어야 함
        "gemini_timeout": "slow",  # int/float이어야 함
        "watch_extensions": ".md",  # list여야 함
        "evaluation_prompt": "ok",
    }
    issues = validate_config(config)
    error_msgs = [msg for level, msg in issues if level == "error"]
    assert any("gemini_cmd" in m for m in error_msgs)
    assert any("gemini_timeout" in m for m in error_msgs)
    assert any("watch_extensions" in m for m in error_msgs)


def test_validate_config_sdk_warnings():
    # SDK 설정 경고
    config = {
        "gemini_cmd": "/usr/local/bin/gemini",
        "gemini_timeout": 90,
        "watch_extensions": [".md"],
        "evaluation_prompt": "ok",
        "sdk": {"temperature": 5.0},  # model 미설정 + temperature 범위 초과
    }
    issues = validate_config(config)
    warn_msgs = [msg for level, msg in issues if level == "warn"]
    assert any("model" in m for m in warn_msgs)
    assert any("temperature" in m for m in warn_msgs)


# ─────────────────────────────────────────────────────────────────────────────
# feedback.py 테스트
# ─────────────────────────────────────────────────────────────────────────────

def test_save_feedback_creates_file_and_appends(tmp_path, monkeypatch):
    # 피드백 파일 생성 + append 확인
    fb_path = tmp_path / "plans" / "gemini" / "gemini_feedback.md"
    monkeypatch.setattr(feedback_mod, "FEEDBACK_PATH", fb_path)

    save_feedback("첫 번째 피드백", source="TestSource")
    assert fb_path.exists()
    content = fb_path.read_text(encoding="utf-8")
    assert "첫 번째 피드백" in content
    assert "TestSource" in content

    # 두 번째 호출은 append
    save_feedback("두 번째", source="TestSource2")
    content = fb_path.read_text(encoding="utf-8")
    assert "첫 번째 피드백" in content
    assert "두 번째" in content


def test_save_feedback_includes_file_path_and_request_id(tmp_path, monkeypatch):
    # file_path와 request_id가 헤더에 포함
    fb_path = tmp_path / "feedback.md"
    monkeypatch.setattr(feedback_mod, "FEEDBACK_PATH", fb_path)

    save_feedback("내용", source="Hook", file_path="doc.md", request_id="req-abc")
    content = fb_path.read_text(encoding="utf-8")
    assert "대상: `doc.md`" in content
    assert "request_id: req-abc" in content


def test_save_feedback_without_optional_fields(tmp_path, monkeypatch):
    # file_path, request_id 없이도 정상 동작
    fb_path = tmp_path / "feedback.md"
    monkeypatch.setattr(feedback_mod, "FEEDBACK_PATH", fb_path)

    save_feedback("내용만", source="Minimal")
    content = fb_path.read_text(encoding="utf-8")
    assert "내용만" in content
    assert "대상:" not in content
    assert "request_id:" not in content


# ─────────────────────────────────────────────────────────────────────────────
# hook_io.py 테스트
# ─────────────────────────────────────────────────────────────────────────────

def test_format_hook_output_short_feedback():
    # 500자 이하 피드백은 그대로 포함
    result = format_hook_output("짧은 피드백")
    parsed = json.loads(result)
    assert "[Gemini 평가] 짧은 피드백" == parsed["hookSpecificOutput"]["additionalContext"]


def test_format_hook_output_long_feedback_truncated():
    # 500자 초과 피드백은 잘림
    long_text = "가" * 600
    result = format_hook_output(long_text)
    parsed = json.loads(result)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    # prefix "[Gemini 평가] " + 500자
    assert len(ctx) < len(long_text) + 20


def test_format_hook_output_valid_json():
    # 출력이 유효한 JSON
    result = format_hook_output("test")
    parsed = json.loads(result)
    assert "hookSpecificOutput" in parsed


def test_read_file_content_normal(tmp_path):
    # 정상 파일 읽기
    f = tmp_path / "test.txt"
    f.write_text("hello world", encoding="utf-8")
    assert read_file_content(str(f)) == "hello world"


def test_read_file_content_truncation(tmp_path):
    # max_chars 초과 시 잘림
    f = tmp_path / "big.txt"
    f.write_text("x" * 1000, encoding="utf-8")
    result = read_file_content(str(f), max_chars=100)
    assert "truncated" in result
    assert result.startswith("x" * 100)


def test_read_file_content_missing_file():
    # 파일 없으면 에러 메시지
    result = read_file_content("/nonexistent/file.txt")
    assert "파일을 찾을 수 없습니다" in result
