# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

# 剪贴板助手

## 项目概述
截图后自动保存到桌面 `~/Desktop/temp/`，路径自动复制到系统剪贴板，方便 Ctrl+V 粘贴到对话窗口。

## 自动启停机制
Claude 会话启动时自动运行 `clipboard-monitor.py`，会话结束时自动停止。多窗口通过计数器（`.cc-monitor-counter`）协调，首个窗口启动监听，最后一个窗口关闭时停止。

## 核心脚本
脚本位于 `C:\Users\PC\.claude\scripts\`：

| 文件 | 作用 |
|------|------|
| `clipboard-monitor.py` | 后台监听剪贴板截图，每秒轮询500ms，检测到新截图自动保存并复制路径 |
| `start-hook.py` | SessionStart 钩子调用，检查 PID 锁，未启动则启动监控进程 |
| `stop-hook.py` | Stop 钩子调用，根据 PID 锁直接终止监控进程 |

## 关键路径
- 图片保存目录：`~/Desktop/temp/`
- PID 锁文件：`.cc-monitor.lock`（scripts 目录下，记录 monitor 进程 PID）
- 日志文件：`clipboard-monitor.log`（scripts 目录下）
- Python 路径：`C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe`

## Hooks 配置
`settings.json` 中配置了：
- `SessionStart` → `start-monitor.py`（启动监听）
- `Stop` → `stop-monitor.py` + 完成提示音（停止监听）

## 依赖
- Pillow (`pip install Pillow`)
- Windows 环境（使用 PowerShell 剪贴板操作）
