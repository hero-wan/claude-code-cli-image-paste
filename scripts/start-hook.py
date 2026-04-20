# -*- coding: utf-8 -*-
"""
SessionStart Hook — 检查监控是否已运行，未运行则启动。
"""
import os, sys, subprocess, json, time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
LOCK_FILE = SCRIPTS_DIR / ".cc-monitor.lock"
MONITOR = SCRIPTS_DIR / "clipboard-monitor.py"
CONFIG_FILE = SCRIPTS_DIR / "config.json"


def get_python_path():
    """从 config.json 读取 Python 路径，未配置则用当前 Python"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cfg = json.load(f)
            path = cfg.get("python_path", "")
            if path and Path(path).exists():
                return path
        except Exception:
            pass
    return sys.executable


def is_alive():
    if not LOCK_FILE.exists():
        return False
    try:
        with open(LOCK_FILE) as f:
            pid = f.read().strip()
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True, text=True
        )
        return "python" in r.stdout
    except Exception:
        return False


if not is_alive():
    python = get_python_path()
    subprocess.Popen(
        [python, str(MONITOR)],
        creationflags=subprocess.DETACHED_PROCESS,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
    time.sleep(1)
