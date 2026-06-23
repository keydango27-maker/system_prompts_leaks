<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/debug.md -->
<!-- source-sha256: 7667cc3c8b777cf5df010be41b4347a4eaf0317571fd0345a5b538080e293c04 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: debug
description: Debug an issue in the current Claude Code session by enabling debug logging, reading logs, and suggesting fixes.
---
# 调试技巧

帮助用户调试他们在当前 Claude Code 会话中遇到的问题。

## 调试日志记录刚刚启用

到目前为止，此会话的调试日志记录处于关闭状态。在此 /debug 调用之前没有捕获任何内容。

告诉用户调试日志记录现在在 `{debug_log_path}` 处处于活动状态，要求他们重现问题，然后重新读取日志。如果无法重现，还可以使用 `claude --debug` 重新启​​动以捕获启动日志。

## 会话调试日志

当前会话的调试日志位于：`{debug_log_path}`

尚不存在日志文件。

对于其他上下文，请 grep 查找整个文件中的 [ERROR] 和 [WARN] 行。

## 守护进程

未找到守护程序锁或状态文件 — 后台守护程序似乎未在运行。如果问题涉及后台会话或 `claude agents`，则守护程序日志（如果有）位于 `{user_home}/.claude/daemon.log`。

## 问题描述

该用户没有描述具体问题。阅读调试日志并总结任何错误、警告或值得注意的问题。

## 设置

请记住，设置位于：
* 用户 - {user_home}/.claude/settings.json
* 项目 - {working_directory}/.claude/settings.json
* 本地 - {working_directory}/.claude/settings.local.json

## 说明

1.查看用户的问题描述
2. 最后 20 行显示调试文件格式。在文件中查找 [ERROR] 和 [WARN] 条目、堆栈跟踪和故障模式
3.考虑启动claude-code-guide子代理来了解相关的Claude Code功能
4. 用通俗易懂的语言解释你的发现
5.提出具体的修复或后续步骤建议