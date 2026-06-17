from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _sanitize_text(text: str) -> str:
    cleaned = "".join(ch for ch in text if not (0xD800 <= ord(ch) <= 0xDFFF))
    return cleaned.replace("\x00", "")


def sanitize_for_api(obj: Any) -> Any:
    if isinstance(obj, str):
        return _sanitize_text(obj)
    if isinstance(obj, dict):
        return {key: sanitize_for_api(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_api(item) for item in obj]
    if isinstance(obj, tuple):
        return tuple(sanitize_for_api(item) for item in obj)
    return obj


def safe_json_dumps(obj: Any, **kwargs: Any) -> str:
    return json.dumps(sanitize_for_api(obj), **kwargs)


def safe_json_write(path: str | Path, payload: Any, **kwargs: Any) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(safe_json_dumps(payload, **kwargs), encoding="utf-8")
