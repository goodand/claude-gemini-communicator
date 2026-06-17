#!/usr/bin/env python3
"""
Sanitize combined stdout/stderr for safe batch logging.

- Drops invalid UTF-8 bytes
- Removes NUL bytes
- Converts CR to LF
- Strips common ANSI CSI escape sequences
"""

from __future__ import annotations

import codecs
import re
import sys


ANSI_CSI_RE = re.compile(rb"\x1b\[[0-9;?]*[ -/]*[@-~]")


def main() -> int:
    decoder = codecs.getincrementaldecoder("utf-8")("ignore")
    out = sys.stdout
    read = sys.stdin.buffer.read1

    while True:
        chunk = read(8192)
        if not chunk:
            break
        chunk = chunk.replace(b"\x00", b"").replace(b"\r", b"\n")
        chunk = ANSI_CSI_RE.sub(b"", chunk)
        text = decoder.decode(chunk)
        if text:
            out.write(text)

    tail = decoder.decode(b"", final=True)
    if tail:
        out.write(tail)
    out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
