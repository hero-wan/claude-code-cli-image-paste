# -*- coding: utf-8 -*-
"""
Stop Hook — Claude Code 退出时终止监控进程。
"""
import json, subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
LOCK_FILE = SCRIPTS_DIR / ".cc-monitor.lock"

if LOCK_FILE.exists():
    try:
        with open(LOCK_FILE, encoding="utf-8") as f:
            content = f.read().strip()
        try:
            lock_data = json.loads(content)
            pid = str(lock_data["pid"])
            name = lock_data.get("name", "剪贴板监控助手")
            desc = lock_data.get("desc", "")
            print(f"[stop-hook] 正在终止 {name} (PID={pid})")
            if desc:
                print(f"[stop-hook] 说明: {desc}")
        except Exception:
            pid = content
            print(f"[stop-hook] 正在终止监控进程 (PID={pid})")
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
