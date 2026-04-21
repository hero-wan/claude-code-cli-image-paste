# -*- coding: utf-8 -*-
"""
剪贴板监控 — 监听剪贴板中的截图，自动保存到指定目录，
并将文件路径复制到剪贴板，方便粘贴到对话窗口。
"""
import os, sys, time, hashlib
from io import BytesIO
from datetime import datetime
from pathlib import Path

# 脚本所在目录（自动检测，无需手动配置）
SCRIPTS_DIR = Path(__file__).resolve().parent

# 加载配置文件
_config = {}
_config_file = SCRIPTS_DIR / "config.json"
if _config_file.exists():
    import json
    with open(_config_file, encoding="utf-8") as f:
        _config = json.load(f)

SAVE_DIR = Path(_config.get("save_dir", "~/Desktop/temp")).expanduser()
LOG_FILE = SCRIPTS_DIR / "clipboard-monitor.log"
LOCK_FILE = SCRIPTS_DIR / ".cc-monitor.lock"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def write_pid_lock():
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def remove_pid_lock():
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def is_process_alive(pid):
    try:
        import subprocess
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True, text=True
        )
        return str(pid) in r.stdout
    except Exception:
        return False


def copy_to_clipboard(text):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()


def main():
    log("=" * 50)
    log("剪贴板监控服务启动")

    # PID 锁检查，防止重复启动
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE) as f:
                old_pid = int(f.read().strip())
            if is_process_alive(old_pid):
                log(f"另一个实例已在运行 (PID={old_pid})，退出")
                sys.exit(0)
        except Exception:
            pass

    write_pid_lock()
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    last_hash = None
    try:
        log(f"开始监控剪贴板，保存目录: {SAVE_DIR}")
        while True:
            try:
                from PIL import ImageGrab, Image
                img = ImageGrab.grabclipboard()
                # 只处理真正的 PIL Image，忽略文件列表/文本
                if isinstance(img, Image.Image):
                    buf = BytesIO()
                    img.save(buf, "PNG")
                    h = hashlib.md5(buf.getvalue()).hexdigest()
                    if h != last_hash:
                        SAVE_DIR.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filepath = SAVE_DIR / f"screenshot_{ts}.png"
                        img.save(filepath, "PNG")
                        last_hash = h
                        log(f"截图已保存: {filepath.name}")
                        copy_to_clipboard(str(filepath).replace("\\", "/"))
                        log("路径已复制到剪贴板")
                time.sleep(0.5)
            except Exception as e:
                log(f"监控循环错误: {e}", "ERROR")
                time.sleep(1)
    except KeyboardInterrupt:
        log("收到中断信号")
    finally:
        remove_pid_lock()
        log("剪贴板监控服务停止")


if __name__ == "__main__":
    main()
