"""Memory 레이어 — JSONL 이벤트 기반 쿼리 인터페이스.

JSONL 버스에 기록된 이벤트를 조회/필터/요약하는 기능을 제공한다.
hooks/ 또는 cli.py에서 사용. DAG 규칙: core/ → shared/ 방향만 허용.
"""

import json
from pathlib import Path

from src.shared.config import get_jsonl_path  # noqa: F401 — 재export용


def parse_jsonl_file(jsonl_path: Path) -> list:
    """JSONL 파일을 파싱하여 이벤트 리스트를 반환한다 (경로 기반)."""
    if not jsonl_path.exists():
        return []
    events = []
    for line in jsonl_path.read_text("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def load_events(config: dict) -> list:
    """config에서 JSONL 경로를 추출하여 모든 이벤트를 로드한다."""
    return parse_jsonl_file(get_jsonl_path(config))


def get_recent(config: dict, n: int = 10) -> list:
    """최근 N건의 이벤트를 반환한다."""
    events = load_events(config)
    return events[-n:]


def get_by_agent(config: dict, agent: str) -> list:
    """특정 에이전트의 이벤트를 반환한다."""
    events = load_events(config)
    return [e for e in events if agent.lower() in
            str(e.get("source_agent", e.get("source", ""))).lower()]


def get_by_type(config: dict, message_type: str) -> list:
    """특정 메시지 타입의 이벤트를 반환한다."""
    events = load_events(config)
    return [e for e in events if e.get("message_type") == message_type]


def get_conversation(config: dict, request_id: str) -> list:
    """동일 request_id의 요청/응답 쌍을 반환한다."""
    events = load_events(config)
    return [e for e in events if e.get("request_id", "").startswith(request_id)]


def get_since(config: dict, since: str) -> list:
    """특정 날짜 이후의 이벤트를 반환한다 (YYYY-MM-DD 또는 ISO)."""
    events = load_events(config)
    return [e for e in events if e.get("timestamp", "") >= since]


def summarize(config: dict) -> dict:
    """현재 세션의 이벤트 요약 통계를 반환한다."""
    events = load_events(config)
    if not events:
        return {"total": 0}

    types = {}
    agents = {}
    chains = 0
    for e in events:
        mt = e.get("message_type", "unknown")
        types[mt] = types.get(mt, 0) + 1
        sa = e.get("source_agent", e.get("source", "unknown"))
        agents[sa] = agents.get(sa, 0) + 1
        if e.get("parent_message_id"):
            chains += 1

    timestamps = [e.get("timestamp", "") for e in events if e.get("timestamp")]
    return {
        "total": len(events),
        "by_type": types,
        "by_agent": agents,
        "chains": chains,
        "first": min(timestamps) if timestamps else None,
        "last": max(timestamps) if timestamps else None,
    }
