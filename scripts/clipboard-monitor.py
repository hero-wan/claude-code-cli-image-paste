# -*- coding: utf-8 -*-
"""
剪贴板监控 — 通过 Windows 剪贴板事件监听截图，自动保存到指定目录，
并将文件路径复制到剪贴板，方便粘贴到对话窗口。

使用 AddClipboardFormatListener + 消息窗口，避免轮询导致的桌面闪烁。
"""
import os, sys, hashlib, ctypes, time
from io import BytesIO
from datetime import datetime
from pathlib import Path

import win32clipboard
import win32gui
import win32con
import win32api
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
WM_CLIPBOARDUPDATE = 0x031D
HWND_MESSAGE = -3


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
        except Exception as e:
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


def main():
    log("=" * 50)
    log("剪贴板监控服务启动（事件驱动模式）")

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

    last_hash = [None]  # 用列表以便在闭包中修改
    hwnd_clip = None

    def wnd_proc(hwnd, msg, wparam, lparam):
        if msg == WM_CLIPBOARDUPDATE:
            try:
                img = read_clipboard_image()
                if img is not None:
                    save_screenshot(img, last_hash)
            except Exception as e:
                log(f"处理剪贴板事件错误: {e}", "ERROR")
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    try:
        log("开始监听剪贴板变化")

        # 注册窗口类
        class_name = "ClipboardMonitorWindow"
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = wnd_proc
        wc.lpszClassName = class_name
        wc.hInstance = win32api.GetModuleHandle(None)
        try:
            win32gui.RegisterClass(wc)
        except Exception:
            pass  # 可能已注册

        # 创建消息窗口（不可见）
        hwnd_clip = win32gui.CreateWindowEx(
            0, class_name, "Clipboard Monitor",
            win32con.WS_OVERLAPPED,
            0, 0, 0, 0,
            HWND_MESSAGE, None, wc.hInstance, None
        )

        # 注册剪贴板格式监听
        if not user32.AddClipboardFormatListener(hwnd_clip):
            log("AddClipboardFormatListener 注册失败", "ERROR")
            sys.exit(1)

        log("事件监听已注册，等待剪贴板变化")

        # 消息循环（阻塞，几乎不占 CPU）
        win32gui.PumpMessages()

    except KeyboardInterrupt:
        log("收到中断信号")
    except Exception as e:
        log(f"监控服务异常: {e}", "ERROR")
    finally:
        if hwnd_clip:
            user32.RemoveClipboardFormatListener(hwnd_clip)
            win32gui.DestroyWindow(hwnd_clip)
        remove_pid_lock()
        log("剪贴板监控服务停止")


if __name__ == "__main__":
    main()
