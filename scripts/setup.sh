#!/bin/bash
# Phase 2 setup: SDK 의존성 설치
cd "$(dirname "$0")/.."
python3 -m pip install --user --break-system-packages -r requirements.txt
echo "Setup complete. SDK mode will be used when available."
