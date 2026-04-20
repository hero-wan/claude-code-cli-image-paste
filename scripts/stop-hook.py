# -*- coding: utf-8 -*-
"""
Stop Hook — Claude Code 退出时终止监控进程。
"""
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
LOCK_FILE = SCRIPTS_DIR / ".cc-monitor.lock"

if LOCK_FILE.exists():
    try:
        with open(LOCK_FILE) as f:
            pid = f.read().strip()
        subprocess.run(
            ["taskkill", "/F", "/PID", pid],
            capture_output=True
        )
    except Exception:
        pass
    try:
        LOCK_FILE.unlink()
    except Exception:
        pass
