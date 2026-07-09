#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
ROOT_SCRIPT = ROOT_DIR / "scripts" / "run_four_mode_small_batch_auto_eval.py"


def main() -> int:
    argv = [sys.executable, str(ROOT_SCRIPT), *sys.argv[1:]]
    os.execv(sys.executable, argv)


if __name__ == "__main__":
    raise SystemExit(main())
