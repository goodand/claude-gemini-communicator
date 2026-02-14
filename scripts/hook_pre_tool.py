"""PreToolUse Hook: 위험한 명령 실행 전 사전 경고/차단합니다.

stdin으로 Claude PreToolUse Hook JSON을 수신하고,
Bash 명령이 위험 패턴에 매칭되면 차단(block) 판정을 반환합니다.
"""

import json
import os
import re
import sys

try:
    from a2a_bridge import load_config
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from a2a_bridge import load_config


# ── 위험 명령 패턴 (severity: block / warn) ──

_DANGEROUS_PATTERNS = [
    # Block: 되돌리기 극히 어려운 명령
    {
        "pattern": re.compile(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\b"),
        "severity": "block",
        "reason": "rm -rf: 재귀 강제 삭제는 복구 불가능합니다",
    },
    {
        "pattern": re.compile(r"\brm\s+-[a-zA-Z]*r\b.*(/|~|\$HOME|\.\.)"),
        "severity": "block",
        "reason": "rm -r with broad path: 광범위한 재귀 삭제는 위험합니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+push\s+.*--force\b"),
        "severity": "block",
        "reason": "git push --force: 원격 히스토리가 덮어쓰여 복구가 어렵습니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+push\s+-f\b"),
        "severity": "block",
        "reason": "git push -f: force push는 원격 히스토리를 파괴합니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+reset\s+--hard\b"),
        "severity": "block",
        "reason": "git reset --hard: 커밋되지 않은 변경사항이 영구 삭제됩니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+clean\s+-[a-zA-Z]*f"),
        "severity": "block",
        "reason": "git clean -f: 추적되지 않는 파일이 영구 삭제됩니다",
    },
    {
        "pattern": re.compile(r"\bDROP\s+(TABLE|DATABASE)\b", re.IGNORECASE),
        "severity": "block",
        "reason": "DROP TABLE/DATABASE: 데이터베이스 구조가 영구 삭제됩니다",
        "requires_context": re.compile(r"\b(psql|mysql|sqlite3|mongo|redis-cli|cockroach)\b"),
    },
    {
        "pattern": re.compile(r"\bTRUNCATE\s+TABLE\b", re.IGNORECASE),
        "severity": "block",
        "reason": "TRUNCATE TABLE: 테이블의 모든 데이터가 영구 삭제됩니다",
        "requires_context": re.compile(r"\b(psql|mysql|sqlite3|mongo|redis-cli|cockroach)\b"),
    },
    {
        "pattern": re.compile(r">\s*/dev/sd[a-z]"),
        "severity": "block",
        "reason": "디스크 디바이스 직접 쓰기: 파일시스템이 파괴됩니다",
    },
    {
        "pattern": re.compile(r"\bmkfs\b"),
        "severity": "block",
        "reason": "mkfs: 파일시스템 포맷은 모든 데이터를 삭제합니다",
    },
    {
        "pattern": re.compile(r"\bdd\s+.*of=/dev/"),
        "severity": "block",
        "reason": "dd to device: 디스크에 직접 쓰기는 데이터를 파괴합니다",
    },
    # Warn: 주의가 필요한 명령 (차단은 안 함)
    {
        "pattern": re.compile(r"\bgit\s+branch\s+-D\b"),
        "severity": "warn",
        "reason": "git branch -D: 머지되지 않은 브랜치가 강제 삭제됩니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+checkout\s+\.\s*$"),
        "severity": "warn",
        "reason": "git checkout .: 모든 변경사항이 되돌아갑니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+restore\s+\.\s*$"),
        "severity": "warn",
        "reason": "git restore .: 모든 변경사항이 되돌아갑니다",
    },
    {
        "pattern": re.compile(r"\bchmod\s+777\b"),
        "severity": "warn",
        "reason": "chmod 777: 모든 사용자에게 전체 권한을 부여합니다",
    },
    {
        "pattern": re.compile(r"\bkill\s+-9\b"),
        "severity": "warn",
        "reason": "kill -9: 프로세스가 정리 없이 강제 종료됩니다",
    },
    {
        "pattern": re.compile(r"\bpip\s+install\b(?!.*-r\s)(?!.*requirements)"),
        "severity": "warn",
        "reason": "pip install (단일 패키지): 의존성 충돌 가능성을 확인하세요",
    },
]


def _strip_string_content(command: str) -> str:
    """명령어에서 문자열 리터럴/heredoc 내용을 제거합니다 (오탐 방지).

    커밋 메시지, echo 인자 등에 포함된 위험 키워드 텍스트가
    실제 명령으로 오인되는 것을 방지합니다.
    """
    # 1) Heredoc 내용 제거: <<'EOF' ... EOF / <<EOF ... EOF
    result = re.sub(
        r"<<-?\s*['\"]?(\w+)['\"]?\s*\n.*?\n\s*\1",
        "", command, flags=re.DOTALL,
    )
    # 2) 단일 따옴표 문자열 내용 제거
    result = re.sub(r"'[^']*'", "''", result)
    # 3) 이중 따옴표 문자열 내용 제거 (escaped quote 처리)
    result = re.sub(r'"(?:[^"\\]|\\.)*"', '""', result)
    return result


def check_command(command: str, config: dict) -> dict | None:
    """명령어를 위험 패턴과 매칭합니다.

    Returns:
        매칭 시 {"severity": "block"|"warn", "reason": str},
        안전하면 None
    """
    if not command or not command.strip():
        return None

    guard_config = config.get("pre_tool_guard", {})
    if not guard_config.get("enabled", True):
        return None

    # 문자열 리터럴 내용 제거 후 패턴 매칭 (오탐 방지)
    stripped = _strip_string_content(command)

    for entry in _DANGEROUS_PATTERNS:
        # requires_context: SQL 패턴은 DB 클라이언트가 있을 때만 원본에서 체크
        ctx_re = entry.get("requires_context")
        if ctx_re:
            if ctx_re.search(command) and entry["pattern"].search(command):
                return {"severity": entry["severity"], "reason": entry["reason"]}
        elif entry["pattern"].search(stripped):
            return {"severity": entry["severity"], "reason": entry["reason"]}

    # 사용자 정의 패턴 (config.json)
    custom_patterns = guard_config.get("custom_block_patterns", [])
    for pattern_str in custom_patterns:
        try:
            if re.search(pattern_str, command):
                return {
                    "severity": "block",
                    "reason": f"사용자 정의 차단 패턴 매칭: {pattern_str}",
                }
        except re.error:
            continue

    return None


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    config = load_config()
    result = check_command(command, config)

    if result is None:
        # 안전 — 허용
        sys.exit(0)

    if result["severity"] == "block":
        output = {
            "decision": "block",
            "reason": f"⚠️ 위험 명령 차단: {result['reason']}\n명령어: {command[:200]}",
        }
        print(json.dumps(output, ensure_ascii=False))
    elif result["severity"] == "warn":
        output = {
            "decision": "allow",
            "hookSpecificOutput": {
                "additionalContext": f"⚠️ 주의: {result['reason']}\n명령어: {command[:200]}",
            },
        }
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
