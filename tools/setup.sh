#!/usr/bin/env bash
# One-time setup per session (scheduled runs start fresh).
set -e
python3 -c "import playwright" 2>/dev/null || pip install --break-system-packages -q playwright
python3 -c "import piper" 2>/dev/null || pip install --break-system-packages -q piper-tts
python3 -c "import scipy, numpy" 2>/dev/null || pip install --break-system-packages -q scipy numpy
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
[ -x "${CHROME:-/usr/bin/google-chrome}" ] || python3 -m playwright install chromium
echo "setup ok"
