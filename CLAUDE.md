# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

# 剪贴板助手

## 项目概述
截图后自动保存到桌面 `~/Desktop/temp/`，路径自动复制到系统剪贴板，方便 Ctrl+V 粘贴到对话窗口。

## 核心脚本

| 文件 | 作用 |
|------|------|
| `scripts/clipboard-monitor.py` | 后台监听剪贴板截图，每 500ms 轮询，检测到新截图自动保存并复制路径 |
| `scripts/start-hook.py` | SessionStart 钩子调用，检查 PID 锁，未启动则启动监控进程 |
| `scripts/stop-hook.py` | Stop 钩子调用，根据 PID 锁直接终止监控进程 |
| `scripts/config.json` | 用户配置文件（保存目录、Python 路径） |

## 依赖
- Pillow (`pip install Pillow`)
- pywin32 (`pip install pywin32`)
- Windows 环境
