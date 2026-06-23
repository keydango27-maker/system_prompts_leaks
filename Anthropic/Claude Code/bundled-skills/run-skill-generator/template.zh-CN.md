<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run-skill-generator/template.md -->
<!-- source-sha256: 3a8202ce96dd800ccd8ec381ec57dda58f673bf937fe5cf3092113fab6750e13 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: run-<unit-name>
description: Build, run, and drive <unit-name>. Use when asked to start <unit-name>, run its tests, build it, take a screenshot of its UI, or interact with the running app.
---
<一句话描述：这是什么以及代理如何驱动它。
在这里命名句柄 - “通过
对于桌面，xvfb 下的 `.claude/skills/run-<unit-name>/driver.mjs`
应用程序，或“启动开发服务器，然后通过 `chromium-cli` 驱动它”
网络应用程序 - 这样代理就知道首先要查看哪里。>

<If the unit isn't at repo root:>
以下所有路径均相对于 `<unit-dir>/`。

## 先决条件

<系统级要求。您运行的确切 `apt-get install` 行 —
不是一个通用的列表，而是真正有效的列表。目标 Ubuntu。>```bash
sudo apt-get update
sudo apt-get install -y <packages-you-actually-installed>
```<Runtime versions if they matter:>```bash
# Example: Node 20 via nvm, Python 3.12 via uv, etc.
```## 设置

<克隆后一次性安装：安装依赖项、配置、应用任何
使用确切的命令打补丁（功能门覆盖、配置存根）。>```bash
<commands>
```<Env vars — required vs optional, with sensible defaults:>```bash
export FOO_API_KEY=...   # required — get from <where>
export BAR_MODE=dev      # optional — default is prod
```## 构建

<Skip if no separate build step. Otherwise the exact command:>```bash
<command>
```## 运行（代理路径）

<这是未来代理实际使用的部分。如果您构建了一个
driver/REPL/smoke 脚本，此文档记录了如何启动它以及它的用途
确实如此。如果应用程序足够简单，`curl` 或一行字就足够了，
那句台词就放在这里。>```bash
<launch-the-driver-or-smoke-script>
```<对于 REPL 风格的驱动程序，显示 tmux 包装。轮询准备好的标记
在发送键和捕获窗格之间 - 比固定睡眠更快并且失败
大声地而不是捕获半渲染的屏幕：>```bash
tmux new-session -d -s app -x 200 -y 50
tmux send-keys -t app '<launch command>' Enter
timeout 30 bash -c 'until tmux capture-pane -t app -p | grep -q "<ready-marker>"; do sleep 0.2; done'
tmux send-keys -t app '<first driver command>' Enter
tmux capture-pane -t app -p
```<Where artifacts land (screenshots, logs) — absolute paths:>

屏幕截图 → `/tmp/shots/`。日志 → `/tmp/<app>.log`。

<If the driver has commands, a table:>

|命令 |它是做什么的 |
|---|---|
| `<cmd>` | <description> |

## 运行（人类路径）

<如果与代理路径明显不同。简述——代理商不会
使用这个，人类可以弄清楚。>```bash
<command>   # → <what happens>. <how to stop>.
```＃＃ 测试```bash
<command>
```<Expected result — "N suites pass", or specific known-flaky tests.>

---

<下面的可选部分 - 仅在相关且仅与
您实际点击的内容，而不是一般建议。>

## 陷阱

<不明显的陷阱。那些看起来应该有用的东西，但是
不要，有解决方法。如果此部分是通用的，则 delete 。>

- **<specific thing>** — <why it breaks> → <what to do instead>

## 故障排除

<Symptom → fix. Only errors you actually encountered.>

- **<exact error message or symptom>**：<cause>。 <fix>。

<!---

关于上述前沿问题的注释：
- 替换 `name:` 和 `description:` 中的 <unit-name>。 `name:`
  成为斜杠命令 (/run-<unit-name>) 并且必须匹配
  目录名称。
- Claude 扫描 `description:` 来决定是否加载此内容
  自动技能。保留动词——“开始”、“运行”、“构建”、“测试”
  "screenshot" — 它们是询问代理实际键入的内容。

驾驶员注意事项：
- 如果您编写了驱动程序脚本，它位于同一目录中（下一步
  默认情况下到此文件）。从“运行”部分引用它。
- 对于网络应用程序，通常没有驱动程序文件 - `chromium-cli`
  运行部分中的heredoc是线束。
- 如果驱动程序成长为项目测试套件想要的东西 -
  共享启动助手，真正的 e2e 工具 - 将其移动到脚本/或
  e2e/ 单元中，并更新此处的路径。该技能仍为 put。

Delete 在提交之前从上面的 `---` 开始的所有内容。 --->