#!/usr/bin/env python3
"""
claude_sniffer.py

Claude Code API 요청/응답을 프록시로 가로채어 JSONL로 기록한다.

기본 사용:
  python3 scripts/claude_sniffer.py
  ANTHROPIC_BASE_URL=http://127.0.0.1:7735 claude

선택 환경변수:
  CLAUDE_SNIFFER_PORT
  CLAUDE_SNIFFER_TARGET
  CLAUDE_SNIFFER_LOG_DIR
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import http.server
import json
import os
import threading
import urllib.error
import urllib.request
from typing import Any


HOST = os.environ.get("CLAUDE_SNIFFER_HOST", "127.0.0.1")
PORT = int(os.environ.get("CLAUDE_SNIFFER_PORT", "7735"))
TARGET = os.environ.get("CLAUDE_SNIFFER_TARGET", "https://api.anthropic.com")
LOG_DIR = os.path.expanduser(
    os.environ.get("CLAUDE_SNIFFER_LOG_DIR", "~/.claude/api-sniffer")
)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"sniffer-{dt.datetime.now():%Y%m%d-%H%M%S}.jsonl")
REQ_COUNT = 0
LOCK = threading.Lock()

SENSITIVE_HEADERS = {
    "authorization",
    "x-api-key",
    "proxy-authorization",
    "cookie",
    "set-cookie",
}


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    sanitized: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADERS:
            sanitized[key] = "***masked***"
        else:
            sanitized[key] = value
    return sanitized


def try_parse_json(raw: bytes) -> tuple[Any | None, str | None, str | None]:
    try:
        return json.loads(raw), None, None
    except Exception as exc:  # pragma: no cover - diagnostic path
        return None, base64.b64encode(raw).decode("ascii"), repr(exc)


def collect_surrogates(
    obj: Any,
    *,
    path: str = "$",
    limit: int = 20,
    out: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if out is None:
        out = []
    if len(out) >= limit:
        return out

    if isinstance(obj, str):
        for idx, ch in enumerate(obj):
            code = ord(ch)
            if 0xD800 <= code <= 0xDFFF:
                out.append(
                    {
                        "path": path,
                        "index": idx,
                        "codepoint": f"U+{code:04X}",
                        "preview": obj[max(0, idx - 12) : idx + 12],
                    }
                )
                if len(out) >= limit:
                    break
        return out

    if isinstance(obj, list):
        for idx, item in enumerate(obj):
            collect_surrogates(item, path=f"{path}[{idx}]", limit=limit, out=out)
            if len(out) >= limit:
                break
        return out

    if isinstance(obj, dict):
        for key, value in obj.items():
            collect_surrogates(value, path=f"{path}.{key}", limit=limit, out=out)
            if len(out) >= limit:
                break
        return out

    return out


def build_error_response(status: int, message: str) -> tuple[int, dict[str, str], bytes]:
    body = json.dumps(
        {"type": "sniffer_error", "status": status, "message": message},
        ensure_ascii=False,
    ).encode("utf-8")
    return status, {"Content-Type": "application/json; charset=utf-8"}, body


def forward(
    method: str, path: str, headers: dict[str, str], body: bytes
) -> tuple[int, dict[str, str], bytes]:
    forward_headers = {
        key: value
        for key, value in headers.items()
        if key.lower()
        not in {
            "host",
            "content-length",
            "transfer-encoding",
            "accept-encoding",
            "connection",
        }
    }
    req = urllib.request.Request(
        url=TARGET + path,
        data=body if body else None,
        headers=forward_headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()
    except urllib.error.URLError as exc:
        return build_error_response(502, f"Upstream connection failed: {exc}")
    except Exception as exc:  # pragma: no cover - defensive
        return build_error_response(502, f"Unexpected upstream error: {exc!r}")


def write_log(entry: dict[str, Any]) -> None:
    # surrogate가 포함된 문자열도 \uXXXX 형태로 안전하게 남긴다.
    with open(LOG_FILE, "a", encoding="utf-8", errors="backslashreplace") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def next_seq() -> int:
    global REQ_COUNT
    with LOCK:
        REQ_COUNT += 1
        return REQ_COUNT


def print_summary(
    seq: int,
    method: str,
    path: str,
    status: int,
    req_json: Any | None,
    req_surrogates: list[dict[str, Any]],
    resp_json: Any | None,
) -> None:
    model = req_json.get("model", "?") if isinstance(req_json, dict) else "?"
    usage = resp_json.get("usage", {}) if isinstance(resp_json, dict) else {}
    input_tokens = usage.get("input_tokens", "?")
    output_tokens = usage.get("output_tokens", "?")
    cache_read = usage.get("cache_read_input_tokens", 0)
    prefix = "⚠️ " if status >= 400 else ""
    suffix = f" | surrogate_hits:{len(req_surrogates)}" if req_surrogates else ""
    print(
        f"{prefix}#{seq:03d} {method} {path} | {model} | "
        f"in:{input_tokens} out:{output_tokens} cache_read:{cache_read} | "
        f"HTTP {status}{suffix}"
    )


class SnifferHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _handle(self, method: str) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        req_body = self.rfile.read(length) if length else b""

        req_json, req_raw_b64, req_json_error = (
            try_parse_json(req_body) if req_body else (None, None, None)
        )
        req_surrogates = collect_surrogates(req_json) if req_json is not None else []

        status, resp_headers, resp_body = forward(
            method, self.path, dict(self.headers), req_body
        )
        resp_json, resp_raw_b64, resp_json_error = (
            try_parse_json(resp_body) if resp_body else (None, None, None)
        )

        seq = next_seq()
        print_summary(
            seq, method, self.path, status, req_json, req_surrogates, resp_json
        )

        entry: dict[str, Any] = {
            "seq": seq,
            "time": dt.datetime.now().isoformat(),
            "method": method,
            "path": self.path,
            "status": status,
            "request": {
                "headers": sanitize_headers(dict(self.headers)),
                "body_len": len(req_body),
                "body_sha256": sha256_hex(req_body),
                "json": req_json,
            },
            "response": {
                "headers": sanitize_headers(resp_headers),
                "body_len": len(resp_body),
                "body_sha256": sha256_hex(resp_body),
                "json": resp_json,
            },
        }

        if req_json_error:
            entry["request"]["json_error"] = req_json_error
        if req_raw_b64:
            entry["request"]["raw_b64"] = req_raw_b64
        if req_surrogates:
            entry["request"]["surrogates"] = req_surrogates

        if resp_json_error:
            entry["response"]["json_error"] = resp_json_error
        if resp_raw_b64:
            entry["response"]["raw_b64"] = resp_raw_b64

        try:
            write_log(entry)
        except Exception as exc:  # pragma: no cover - logging must not break proxying
            print(f"⚠️ log write failed: {exc!r}")

        self.send_response(status)
        skip_headers = {"transfer-encoding", "content-encoding", "connection"}
        for key, value in resp_headers.items():
            if key.lower() in skip_headers:
                continue
            try:
                self.send_header(key, value)
            except Exception:
                continue
        self.send_header("Content-Length", str(len(resp_body)))
        self.end_headers()
        self.wfile.write(resp_body)

    def do_POST(self) -> None:
        self._handle("POST")

    def do_GET(self) -> None:
        self._handle("GET")

    def log_message(self, *_: Any) -> None:
        return


def main() -> None:
    server = http.server.ThreadingHTTPServer((HOST, PORT), SnifferHandler)

    print("Claude Code API Sniffer")
    print(f"  Listening : http://{HOST}:{PORT}")
    print(f"  Target    : {TARGET}")
    print(f"  Log file  : {LOG_FILE}")
    print()
    print("사용법")
    print(f"  ANTHROPIC_BASE_URL=http://{HOST}:{PORT} claude")
    print()
    print("실시간 로그")
    print(f"  tail -f {LOG_FILE} | jq .")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSniffer 종료")
        server.shutdown()


if __name__ == "__main__":
    main()
