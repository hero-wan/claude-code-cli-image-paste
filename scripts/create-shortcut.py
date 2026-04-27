# -*- coding: utf-8 -*-
"""生成桌面快捷方式，指向 start-hook.py，带自定义图标"""
import os, sys
from pathlib import Path

import win32com.client


SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPTS_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"
CONFIG_FILE = SCRIPTS_DIR / "config.json"


def get_pythonw_path():
    """优先使用 pythonw.exe 避免黑窗，否则用当前解释器"""
    if CONFIG_FILE.exists():
        try:
            import json
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cfg = json.load(f)
            custom = cfg.get("python_path", "")
            if custom and Path(custom).exists():
                pw = Path(custom).parent / "pythonw.exe"
                if pw.exists():
                    return str(pw)
                return custom
        except Exception:
            pass

    # 默认：尝试当前解释器同目录的 pythonw.exe
    current = Path(sys.executable)
    pythonw = current.parent / "pythonw.exe"
    if pythonw.exists():
        return str(pythonw)
    return sys.executable


def main():
    if not ICON_PATH.exists():
        print(f"图标不存在: {ICON_PATH}")
        print("请先运行 generate-icon.py 生成图标")
        sys.exit(1)

    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "剪贴板助手.lnk"

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))

    pythonw = get_pythonw_path()
    start_hook = SCRIPTS_DIR / "start-hook.py"

    shortcut.TargetPath = pythonw
    shortcut.Arguments = f'"{start_hook}"'
    shortcut.WorkingDirectory = str(SCRIPTS_DIR)
    shortcut.IconLocation = str(ICON_PATH)
    shortcut.Description = "双击启动剪贴板监控助手（截图自动保存到桌面）"
    shortcut.save()

    print(f"快捷方式已创建: {shortcut_path}")
    print(f"目标: {pythonw} \"{start_hook}\"")


if __name__ == "__main__":
    main()
