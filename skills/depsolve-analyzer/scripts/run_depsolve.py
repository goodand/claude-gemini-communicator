#!/usr/bin/env python3
"""
depsolve-analyzer CLI Wrapper
=============================

Usage:
    python run_depsolve.py analyze /path/to/project
    python run_depsolve.py analyze . --verify --verbose
    python run_depsolve.py analyze . --format json
    python run_depsolve.py phantoms .
    python run_depsolve.py graph . --mermaid
"""

import sys
from pathlib import Path

# Add depsolve_ext to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from depsolve_ext.cli import main

if __name__ == "__main__":
    sys.exit(main())
