<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/keybindings-help.md -->
<!-- source-sha256: 98b2f8cb1a36b13fd21c6c9c46eadbf9f446544585070db12ca419396d8add75 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: keybindings-help
description: Customize keyboard shortcuts, rebind keys, add chord bindings, or modify ~/.claude/keybindings.json.
---
# 按键绑定技能

创建或修改 `~/.claude/keybindings.json` 以自定义键盘快捷键。

## 关键：先读后写

**始终先阅读 `~/.claude/keybindings.json`**（它可能尚不存在）。将更改与现有绑定合并 - 切勿替换整个文件。

- 使用**编辑**工具修改现有文件
- 仅当文件尚不存在时才使用 **Write** 工具

## 文件格式```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "$docs": "https://code.claude.com/docs/en/keybindings",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor"
      }
    }
  ]
}
```始终包含 `$schema` 和 `$docs` 字段。

## 按键语法

**修饰符**（与`+`结合）：
- `ctrl`（别名：`control`）
- `alt`（别名：`opt`、`option`） — 注：`alt` 和 `meta` 的端子相同
- `shift`
- `meta`（别名：`cmd`、`command`）

**特殊按键**：`escape`/`esc`、`enter`/`return`、`tab`、`space`、 `backspace`、`delete`、`up`、`down`、`left`、`right`

**和弦**：以空格分隔的击键，例如`ctrl+k ctrl+s`（按键之间 1 秒超时）

**示例**：`ctrl+shift+p`、`alt+enter`、`ctrl+k ctrl+n`

## 解除绑定默认快捷键

将密钥设置为 `null` 以删除其默认绑定：```json
{
  "context": "Chat",
  "bindings": {
    "ctrl+s": null
  }
}
```## 用户绑定如何与默认值交互

- 用户绑定是**附加的** - 它们附加在默认绑定之后
- 要**移动**绑定到不同的密钥：取消绑定旧密钥 (`null`) 并添加新绑定
- 仅当用户想要更改上下文中的某些内容时，上下文才需要出现在用户的文件中

## 常见模式

### 重新绑定密钥
要将外部编辑器快捷方式从 `ctrl+g` 更改为 `ctrl+e`：```json
{
  "context": "Chat",
  "bindings": {
    "ctrl+g": null,
    "ctrl+e": "chat:externalEditor"
  }
}
```### 添加和弦绑定```json
{
  "context": "Global",
  "bindings": {
    "ctrl+k ctrl+t": "app:toggleTodos"
  }
}
```## 行为规则

1. 仅包含用户想要更改的上下文（最少覆盖）
2. 验证操作和上下文是否来自下面的已知列表
3. 如果用户选择的按键与保留的快捷键或 tmux (`ctrl+b`) 和 screen (`ctrl+a`) 等常用工具冲突，则主动警告用户
4. 为现有操作添加新绑定时，新绑定是附加的（现有默认值仍然有效，除非显式取消绑定）
5. 要完全替换默认绑定，请解除旧密钥的绑定并添加新密钥

## 使用 /doctor 进行验证

`/doctor` 命令包括验证 `~/.claude/keybindings.json` 的“按键绑定配置问题”部分。

### 常见问题和修复

|问题 |原因 |修复 |
| ---| ---| ---|
| `keybindings.json must have a "bindings" array` |缺少包装对象 | `{ "bindings": [...] }` 包装装订 |
| `"bindings" must be an array` | `bindings` 不是数组 |将 `"bindings"` 设置为数组：`[{ context: ..., bindings: ... }]` |
| `Unknown context "X"` |拼写错误或上下文名称无效 |使用“可用上下文”表中的准确上下文名称 |
| `Duplicate key "X" in Y bindings` |同一键在一个上下文中定义两次 |删除重复项； JSON 仅使用最后一个值 |
| `"X" may not work: ...` |按键与终端/操作系统保留的快捷键冲突选择不同的键（请参阅保留的快捷键部分）|
| `Could not parse keystroke "X"` |无效的键语法 |检查语法：在修饰符之间使用 `+`，有效的键名 |
| `Invalid action for "X"` |操作值不是字符串或 null |操作必须是类似 `"app:help"` 或 `null` 的字符串才能解除绑定 |

### 示例 /doctor 输出```
Keybinding Configuration Issues
Location: ~/.claude/keybindings.json
  └ [Error] Unknown context "chat"
    → Valid contexts: Global, Chat, Autocomplete, ...
  └ [Warning] "ctrl+c" may not work: Terminal interrupt (SIGINT)
```**错误**导致绑定无法工作，必须予以修复。 **警告**表示潜在的冲突，但绑定可能仍然有效。

## 保留的快捷键

### 不可重新绑定（错误）
- `ctrl+c` — 无法反弹 - 用于中断/退出（硬编码）
- `ctrl+d` — 无法反弹 - 用于退出（硬编码）
- `ctrl+m` — 无法反弹 - 与终端中的 Enter 相同（均发送 CR）
- `capslock` — Caps Lock 未提供给终端应用程序

### 终端保留（错误/警告）
- `ctrl+z` — Unix 进程挂起 (SIGTSTP)（可能冲突）
- `ctrl+\` — 终端退出信号 (SIGQUIT)（不起作用）

### macOS 保留（错误）
- `cmd+c` — macOS 系统副本
- `cmd+v` — macOS 系统粘贴
- `cmd+x` — macOS 系统剪切
- `cmd+q` — macOS 退出应用程序
- `cmd+w` — macOS 关闭窗口/选项卡
- `cmd+tab` — macOS 应用程序切换器
- `cmd+space` — macOS 聚光灯

## 可用上下文

|背景 |描述 |
| ---| ---|
| `Global` |无论焦点如何，无处不在 |
| `Chat` |当聊天输入获得焦点时 |
| `Autocomplete` |当自动完成菜单可见时 |
| `Confirmation` |当显示确认/许可对话框时 |
| `Help` |当帮助叠加层打开时 |
| `Transcript` |当查看文字记录时 |
| `HistorySearch` |搜索命令历史记录时 (ctrl+r) |
| `Task` |当任务/代理在前台运行时 |
| `ThemePicker` |当主题选择器打开时 |
| `Settings` |当设置菜单打开时 |
| `Tabs` |当选项卡导航处于活动状态时 |
| `Attachments` |在选择对话框中导航图像附件时 |
| `Footer` |当页脚指示器聚焦时 |
| `MessageSelector` |当消息选择器（快退）打开时 |
| `DiffDialog` |当差异对话框打开时 |
| `ModelPicker` |当模型选择器打开时 |
| `Select` |当选择/列表组件获得焦点时 |
| `Plugin` |当插件对话框打开时 |
| `Scroll` |当可滚动视图获得焦点时（全屏布局） |
| `Doctor` |当 /doctor 诊断屏幕打开时 |

## 可用操作

|行动|默认键 |背景 |
| ---| ---| ---|
| `app:interrupt` | `ctrl+c` |全球|
| `app:exit` | `ctrl+d` |全球|
| `app:toggleTodos` | `ctrl+t` |全球|
| `app:toggleTranscript` | `ctrl+o` |全球|
| `app:toggleBrief` | `ctrl+shift+b` |全球|
| `app:toggleTeammatePreview` | `ctrl+shift+o` |全球|
| `app:toggleTerminal` | （无）|全球|
| `app:redraw` | （无）|全球|
| `app:openFrame` | （无）|全球|
| `history:search` | `ctrl+r` |全球|
| `history:previous` | `up` |聊天 |
| `history:next` |`down` |聊天 |
| `chat:cancel` | `escape` |聊天 |
| `chat:killAgents` | `ctrl+x ctrl+k` |聊天 |
| `chat:cycleMode` | `shift+tab` |聊天 |
| `chat:modelPicker` | `meta+p` |聊天 |
| `chat:fastMode` | `meta+o` |聊天 |
| `chat:thinkingToggle` | `meta+t` |聊天 |
| `chat:workflowKeywordToggle` | `meta+w` |聊天 |
| `chat:submit` | `enter` |聊天 |
| `chat:newline` | `ctrl+j` |聊天 |
| `chat:undo` | `ctrl+_`、`ctrl+-`、`ctrl+shift+-`、`ctrl+shift+_` |聊天 |
| `chat:externalEditor` | `ctrl+x ctrl+e`，`ctrl+g` |聊天 |
| `chat:stash` | `ctrl+s` |聊天 |
| `chat:imagePaste` | `ctrl+v` |聊天 |
| `chat:clearInput` | `ctrl+l` |聊天 |
| `chat:clearScreen` | `cmd+k` |聊天 |
| `autocomplete:accept` | `tab` |自动完成 |
| `autocomplete:dismiss` | `escape` |自动完成 |
| `autocomplete:previous` | `up` |自动完成 |
| `autocomplete:next` | `down` |自动完成 |
| `confirm:yes` | `y`，`enter` |确认|
| `confirm:no` | `escape`、`n`、`escape` |设置 |
| `confirm:previous` | `up` |确认|
| `confirm:next` | `down` |确认|
| `confirm:nextField` | `tab` |确认|
| `confirm:previousField` | （无）|确认|
| `confirm:cycleMode` | `shift+tab` |确认|
| `confirm:toggle` | `space` |确认|
| `confirm:toggleExplanation` | `ctrl+e` |确认|
| `tabs:next` | `tab`，`right` |标签 |
| `tabs:previous` | `shift+tab`，`left` |标签 |
| `transcript:toggleShowAll` | `ctrl+e` |成绩单|
| `transcript:exit` | `ctrl+c`、`escape`、`q` |成绩单|
| `historySearch:next` | `ctrl+r` |历史搜索 |
| `historySearch:accept` | `escape`，`tab` |历史搜索 |
| `historySearch:cancel` | `ctrl+c` |历史搜索 |
| `historySearch:execute` | `enter` |历史搜索 |
| `historySearch:cycleScope` | `ctrl+s` |历史搜索 |
| `task:background` | `ctrl+b` |任务|
| `theme:toggleSyntaxHighlighting` | `ctrl+t` |主题选择器 |
| `theme:editCustom` | `ctrl+e` |主题选择器 |
| `help:dismiss` | `escape` |帮助 |
| `attachments:next` | `right` |附件 |
| `attachments:previous` | `left` |附件 |
| `attachments:remove` | `backspace`，`delete` |附件 |
| `attachments:exit` | `down`、`escape` |附件 |
| `footer:up` | `up`，`ctrl+p` |页脚|
| `footer:down` | `down`，`ctrl+n` |页脚|
| `footer:next` | `right` |页脚|
| `footer:previous` | `left` |页脚|
| `footer:openSelected` | `enter` |页脚|
| `footer:clearSelection` | `escape` |页脚|
| `footer:close` | `x` |页脚|
| `messageSelector:up` | `up`、`k`、`ctrl+p` |消息选择器 |
| `messageSelector:down` |`down`、`j`、`ctrl+n` |消息选择器 |
| `messageSelector:top` | `ctrl+up`、`shift+up`、`meta+up`、`shift+k` |消息选择器 |
| `messageSelector:bottom` | `ctrl+down`、`shift+down`、`meta+down`、`shift+j` |消息选择器 |
| `messageSelector:select` | `enter` |消息选择器 |
| `diff:dismiss` | `escape` |差异对话框 |
| `diff:previousSource` | `left` |差异对话框 |
| `diff:nextSource` | `right` |差异对话框 |
| `diff:back` | （无）|差异对话框 |
| `diff:viewDetails` | `enter` |差异对话框 |
| `diff:previousFile` | `up`，`k` |差异对话框 |
| `diff:nextFile` | `down`，`j` |差异对话框 |
| `modelPicker:decreaseEffort` | `left` |模型选择器 |
| `modelPicker:increaseEffort` | `right` |模型选择器 |
| `modelPicker:thisSessionOnly` | `s` |模型选择器 |
| `select:next` | `down`、`j`、`ctrl+n`、`down`、`j`、`ctrl+n` |设置 |
| `select:previous` | `up`、`k`、`ctrl+p`、`up`、`k`、`ctrl+p` |设置 |
| `select:pageUp` | `pageup` |选择 |
| `select:pageDown` | `pagedown` |选择 |
| `select:first` | `home` |选择 |
| `select:last` | `end` |选择 |
| `select:accept` | `space`、`enter` |设置 |
| `select:cancel` | `escape` |选择 |
| `plugin:toggle` | `space` |插件 |
| `plugin:install` | `i` |插件 |
| `plugin:favorite` | `f` |插件 |
| `doctor:fix` | `f` |医生|
| `permission:toggleDebug` | （无）|确认|
| `settings:search` | `/` |设置 |
| `settings:retry` | `r` |设置 |
| `settings:close` | `enter` |设置 |
| `settings:periodDay` | `d` |设置 |
| `settings:periodWeek` | `w` |设置 |
| `settings:sortByTokens` | `t` |设置 |
| `voice:pushToTalk` | `space` |聊天 |
| `scroll:pageUp` | `pageup`，`pageup` |滚动 |
| `scroll:pageDown` | `pagedown`，`pagedown` |滚动 |
| `scroll:lineUp` | `ctrl+p`、`k`、`up`、`wheelup` |成绩单|
| `scroll:lineDown` | `ctrl+n`、`j`、`down`、`wheeldown` |成绩单|
| `scroll:top` | `g`、`home`、`ctrl+home`、`g`、`home` |成绩单|
| `scroll:bottom` | `shift+g`、`end`、`ctrl+end`、`shift+g`、`end` |成绩单|
| `scroll:halfPageUp` | `ctrl+u`，`ctrl+u` |设置 |
| `scroll:halfPageDown` | `ctrl+d`，`ctrl+d` |设置 |
| `scroll:fullPageUp` | `ctrl+b`、`b`、`shift+space`、`b` |成绩单|
| `scroll:fullPageDown` | `ctrl+f`、`space`、`space` |成绩单|
| `selection:copy` | `ctrl+shift+c`，`cmd+c` |滚动 |
| `selection:clear` | （无）|未知 |
| `selection:extendLeft` | `shift+left` |滚动 |
| `selection:extendRight` | `shift+right` |滚动 |
| `selection:extendUp` | `shift+up` |滚动 |
| `selection:extendDown` | `shift+down` |滚动 |
| `selection:extendLineStart` | `shift+home` |滚动 |
| `selection:extendLineEnd` | `shift+end` |滚动 |