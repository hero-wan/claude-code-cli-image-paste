# 剪贴板助手

Claude Code（Windows 终端）截图后自动保存到桌面，文件路径复制到剪贴板，可直接 Ctrl+V 粘贴到对话窗口。

## 安装

### 1. 依赖

```bash
pip install Pillow pywin32
```

### 2. 配置 Hooks

将 `scripts/` 目录复制到你喜欢的路径（如 `C:\tools\cc-clipboard\`），然后在 Claude Code 的 `settings.json` 中添加：

```json
{
  "hooks": {
    "SessionStart": "python C:/tools/cc-clipboard/start-hook.py",
    "Stop": "python C:/tools/cc-clipboard/stop-hook.py"
  }
}
```

> **注意**：路径中的 `\` 替换为 `/`，避免转义问题。

### 3. 修改配置

编辑 `scripts/config.json`：

```json
{
  "save_dir": "~/Desktop/temp",
  "python_path": ""
}
```

| 配置项 | 说明 |
|--------|------|
| `save_dir` | 截图保存目录，支持 `~` 表示用户主目录 |
| `python_path` | Python 解释器路径，留空自动检测当前 Python |

## 使用

打开 Claude Code 即可自动开始监听，无需手动操作。关闭 Claude Code 时自动停止。

## 文件说明

| 文件 | 作用 |
|------|------|
| `scripts/clipboard-monitor.py` | 后台监控剪贴板，检测截图自动保存 |
| `scripts/start-hook.py` | SessionStart 钩子，检查防重复后启动监控 |
| `scripts/stop-hook.py` | Stop 钩子，终止监控进程 |
| `scripts/config.json` | 用户配置文件 |

## 多窗口

多窗口同时运行时，只有第一个窗口会启动监控，最后一个窗口关闭时停止。

## 脚本同步说明

如果 CC hooks 配置指向的路径与本项目路径不同（如全局 `~/.claude/scripts/`），需将 `scripts/` 下的文件**同步**到 hook 配置的目录：

```
start-hook.py  →  hook配置目录/start-hook.py
stop-hook.py   →  hook配置目录/stop-hook.py
clipboard-monitor.py  →  hook配置目录/clipboard-monitor.py
config.json    →  hook配置目录/config.json
```

四个文件缺一不可。修改任一脚本后记得重新同步。
