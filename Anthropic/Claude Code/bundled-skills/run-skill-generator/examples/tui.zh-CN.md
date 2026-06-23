<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run-skill-generator/examples/tui.md -->
<!-- source-sha256: 7d0502f5f81433ceee76e0ca14d99d136f01ef9480238326a9ae9fdc0f2e33f8 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

# 示例：TUI / 交互式终端应用程序

交互式终端应用程序（文本编辑器、REPL、基于curses的UI）不能
由代理的 bash 工具直接驱动 - 他们接管终端。
该技能必须展示如何将它们包装在 `tmux` 中，以便代理可以发送
输入、捕获输出并截取屏幕截图。

## tmux 模式

这是标准方法：

1. 在分离的 tmux 会话中启动 TUI
2. 使用 `tmux send-keys` 发送击键
3.使用`tmux capture-pane`读取屏幕内容
4.用`tmux kill-session`清理

该技能的 `SKILL.md` 应将其呈现为主要的驾驶方式
该应用程序。封装启动+附加序列的小型 `driver.sh` 可以
位于技能目录中，但对于大多数 TUI，原始 tmux 命令位于
技能本体就够了。

## 示例片段

> ## 运行（交互式，针对代理）
>
> 在 tmux 内启动 TUI：
>
>```bash
> tmux new-session -d -s app -x 120 -y 40 './myapp'
> ```>
> 轮询直到出现就绪标记（比固定睡眠更快+更可靠 —
> 在应用程序启动时立即返回，如果没有启动，则会失败）：
>
>```bash
> timeout 10 bash -c 'until tmux capture-pane -t app -p | grep -q "Ready"; do sleep 0.2; done'
> tmux capture-pane -t app -p
> ```>
> 发送输入（此示例导航至“设置”屏幕并切换
> 一个选项）：
>
>```bash
> tmux send-keys -t app 's'
> timeout 5 bash -c 'until tmux capture-pane -t app -p | grep -q "Settings"; do sleep 0.2; done'
> tmux send-keys -t app 'Down' 'Down' 'Space'  # navigate + toggle
> timeout 5 bash -c 'until tmux capture-pane -t app -p | grep -qF "[x]"; do sleep 0.2; done'
> tmux capture-pane -t app -p
> ```>
> 如果您发现自己写了不止几行这样的民意调查，请拉
> 他们变成了`wait_for()` 帮手在`driver.sh` 技能旁边。
>
> 退出：
>
>```bash
> tmux send-keys -t app 'q'
> tmux kill-session -t app 2>/dev/null || true
> ```>
> ### 关键参考
>
> |关键|行动|
> |---|---|
> | `j` / `k` 或 `Down` / `Up` |导航列表 |
> | `Enter` |选择 |
> | `s` |设置 |
> | `q` |退出 |

## 值得记录的细节

- **终端尺寸。** 某些 TUI 会破坏或隐藏小宽度的内容。
  在 `tmux new-session -x -y` 参数中指定已知良好的大小。
- **启动时间。** 轮询就绪标记 (`until tmux capture-pane | grep -q X`)
  而不是固定的 `sleep N` — 在应用程序启动并失败时立即返回
  当它从不这样做时很有用。说出什么字符串表示准备就绪。
- **键绑定参考。** 主键表。这是 "API"
  TUI 的一部分 — 代理需要它来驱动应用程序。
- **干净地退出。** 显示退出击键 * 和 * `tmux kill-session` 为
  后备。
- **颜色/unicode 怪癖。** 如果 `capture-pane` 输出难以阅读，
  注意有助于的标志（`-e` 用于转义序列，`-J` 用于加入包装
  行）。

## 还记录直接调用

对于以交互方式运行应用程序的人来说，tmux 太过分了。包括
也是单行：

> ## 运行（直接，对于人类）
>
>```bash
> ./myapp
> ```>
> 按 `q` 退出。