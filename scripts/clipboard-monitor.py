# -*- coding: utf-8 -*-
"""
剪贴板监控 — 通过 Windows 剪贴板序号轮询检测截图，自动保存到指定目录，
并将文件路径复制到剪贴板，方便粘贴到对话窗口。

使用 GetClipboardSequenceNumber 轻量轮询，不打开剪贴板，避免桌面闪烁。
"""
import os, sys, hashlib, ctypes, time
from io import BytesIO
from datetime import datetime
from pathlib import Path

import win32clipboard
from PIL import ImageGrab, Image

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

# Windows API
user32 = ctypes.windll.user32


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def write_pid_lock():
    import json
    lock_data = {
        "pid": os.getpid(),
        "name": "剪贴板监控助手",
        "desc": "自动保存截图到桌面并复制路径，请勿随意终止",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, ensure_ascii=False, indent=2)


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
    for _ in range(5):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return
        except Exception:
            time.sleep(0.1)
    log("复制路径到剪贴板失败", "ERROR")


def read_clipboard_image():
    """尝试从剪贴板读取图片，成功返回 Image 对象，失败返回 None"""
    for _ in range(5):
        try:
            if not win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                return None  # 非图片内容，直接跳过
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                return img
            return None
        except Exception:
            time.sleep(0.1)
    return None


def save_screenshot(img, last_hash_ref):
    """保存图片并返回新的 hash"""
    buf = BytesIO()
    img.save(buf, "PNG")
    h = hashlib.md5(buf.getvalue()).hexdigest()
    if h != last_hash_ref[0]:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = SAVE_DIR / f"screenshot_{ts}.png"
        img.save(filepath, "PNG")
        last_hash_ref[0] = h
        log(f"截图已保存: {filepath.name}")
        copy_to_clipboard(str(filepath).replace("\\", "/"))
        log("路径已复制到剪贴板")
    return h


def get_clipboard_sequence_number():
    """获取剪贴板序列号，变化表示剪贴板内容已更新"""
    user32.GetClipboardSequenceNumber.argtypes = []
    user32.GetClipboardSequenceNumber.restype = ctypes.c_uint32
    return user32.GetClipboardSequenceNumber()


def main():
    log("=" * 50)
    log("剪贴板监控服务启动（序列号轮询模式）")

    # 设置控制台窗口标题，方便任务管理器识别
    ctypes.windll.kernel32.SetConsoleTitleW("剪贴板监控助手")

    # PID 锁检查，防止重复启动（兼容旧格式纯数字和新格式 JSON）
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE, encoding="utf-8") as f:
                content = f.read().strip()
            try:
                import json
                old_pid = int(json.loads(content)["pid"])
            except Exception:
                old_pid = int(content)
            if is_process_alive(old_pid):
                log(f"另一个实例已在运行 (PID={old_pid})，退出")
                sys.exit(0)
        except Exception:
            pass

    write_pid_lock()
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    last_hash = [None]  # 用列表以便在闭包中修改
    last_seq = get_clipboard_sequence_number()

    log(f"开始监控剪贴板，保存目录: {SAVE_DIR}")
    log(f"初始剪贴板序列号: {last_seq}")

    try:
        while True:
            time.sleep(0.5)  # 500ms 轮询间隔

            try:
                current_seq = get_clipboard_sequence_number()
                if current_seq != last_seq:
                    last_seq = current_seq
                    img = read_clipboard_image()
                    if img is not None:
                        save_screenshot(img, last_hash)
            except Exception as e:
                log(f"监控循环错误: {e}", "ERROR")

    except KeyboardInterrupt:
        log("收到中断信号")
    except Exception as e:
        log(f"监控服务异常: {e}", "ERROR")
    finally:
        remove_pid_lock()
        log("剪贴板监控服务停止")


if __name__ == "__main__":
    main()
