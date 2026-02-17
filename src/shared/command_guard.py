"""위험 명령 패턴 검사 — 순수 유틸리티 (외부 의존 없음).

hook_pre_tool.py와 cli.py 모두에서 사용.
DAG 정방향: cli.py → shared/, hooks/ → shared/.
"""

import re


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
    """명령어에서 문자열 리터럴/heredoc 내용을 제거한다 (오탐 방지)."""
    result = re.sub(
        r"<<-?\s*['\"]?(\w+)['\"]?\s*\n.*?\n\s*\1",
        "", command, flags=re.DOTALL,
    )
    result = re.sub(r"'[^']*'", "''", result)
    result = re.sub(r'"(?:[^"\\]|\\.)*"', '""', result)
    return result


def check_command(command: str, config: dict) -> dict | None:
    """명령어를 위험 패턴과 매칭한다.

    Returns:
        매칭 시 {"severity": "block"|"warn", "reason": str}, 안전하면 None
    """
    if not command or not command.strip():
        return None

    guard_config = config.get("pre_tool_guard", {})
    if not guard_config.get("enabled", True):
        return None

    stripped = _strip_string_content(command)

    for entry in _DANGEROUS_PATTERNS:
        ctx_re = entry.get("requires_context")
        if ctx_re:
            if ctx_re.search(command) and entry["pattern"].search(command):
                return {"severity": entry["severity"], "reason": entry["reason"]}
        elif entry["pattern"].search(stripped):
            return {"severity": entry["severity"], "reason": entry["reason"]}

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
