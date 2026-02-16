"""쿨다운 관리 — 파일별 디바운싱.

a2a_bridge.py의 check_cooldown + _load/_save_cooldown_state를 분리한 모듈.
"""

import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
COOLDOWN_STATE_PATH = PROJECT_ROOT / ".cooldown_state.json"


def _load_cooldown_state() -> dict:
    """쿨다운 상태 파일을 로드한다."""
    if not COOLDOWN_STATE_PATH.exists():
        return {}
    try:
        with open(COOLDOWN_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_cooldown_state(state: dict) -> None:
    """쿨다운 상태를 파일에 저장한다."""
    with open(COOLDOWN_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


def check_cooldown(file_path: str, config: dict) -> bool:
    """파일별 디바운싱: 쿨다운 기간 내이면 False를 반환한다.

    Returns:
        True: 호출 가능 (쿨다운 지남)
        False: 쿨다운 중 (스킵해야 함)
    """
    cooldown_seconds = config.get("cooldown_seconds_per_file", 300)
    state = _load_cooldown_state()
    now = time.time()
    last_call = state.get(file_path, 0)

    if now - last_call < cooldown_seconds:
        return False

    state[file_path] = now
    _save_cooldown_state(state)
    return True
