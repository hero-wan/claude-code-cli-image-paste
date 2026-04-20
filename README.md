# 剪贴板助手

## 项目概述
在 Claude Code 对话中截图时，图片自动保存到桌面 `~/Desktop/temp/`，文件路径自动复制到系统剪贴板，可直接 Ctrl+V 粘贴到对话窗口。

## 自动运行机制
Claude Code 会话启动时通过 Hook 自动启动剪贴板监听，会话结束时自动停止。支持多窗口协作——首个窗口启动监听，最后一个窗口关闭时停止。

### 核心脚本（位于 `C:\Users\PC\.claude\scripts\`）

| 脚本 | 作用 |
|------|------|
| `clipboard-monitor.py` | 后台循环监听剪贴板，发现截图自动保存并复制路径 |
| `start-hook.py` | SessionStart Hook 调用，检查 PID 锁，未启动则开启监听 |
| `stop-hook.py` | Stop Hook 调用，根据 PID 锁终止监听进程 |

### Hook 配置
`settings.json` 中配置了两个 Hook：
- **SessionStart** → `start-hook.py`（会话启动时自动开启监听）
- **Stop** → `stop-hook.py`（会话结束时自动关闭监听）

## 使用方式
正常情况下无需手动操作，打开 Claude Code 窗口即可自动开始监听。

## 文件说明
- 图片保存目录：`~/Desktop/temp/`
- PID 锁文件：`C:\Users\PC\.claude\scripts\.cc-monitor.lock`

## 依赖
- Pillow (`pip install Pillow`)
- Python 3.12：`C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe`
- Windows 环境（PowerShell 剪贴板操作）
