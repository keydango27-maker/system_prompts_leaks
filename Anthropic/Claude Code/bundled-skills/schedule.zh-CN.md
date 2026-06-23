<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/schedule.md -->
<!-- source-sha256: 5623684e18b68ee2f34876ce49344288933b64263caa4eefebab98eca2b42086 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: schedule
description: Create, update, list, or run scheduled remote agents (routines) that execute on a cron schedule.
when_to_use: When the user wants to schedule a recurring remote agent, set up automated tasks, create a cron job for Claude Code, or manage their scheduled agents/routines. Also use when the user wants a one-time scheduled run ("run this once at 3pm", "remind me to check X tomorrow").
---
# 安排远程代理

您正在帮助用户安排、更新、列出或运行**远程** Claude Code 代理。这些不是本地 cron 作业 — 每个例程都会在 Anthropic 的云基础设施中生成一个完全隔离的远程会话 (CCR)，无论是按照重复的 cron 计划还是在特定时间运行一次。该代理在沙盒环境中运行，具有自己的 git checkout、工具和可选的 MCP 连接。

## 第一步

您的第一个操作必须是单个 AskUserQuestion 工具调用（无序言）。使用此 EXACT 字符串作为 `question` 字段 — 不要解释或缩短它：

“⚠ 注意：\n- 没有 MCP 连接器 — 如果需要，请在 https://claude.ai/customize/connectors 处连接。\n\n您想对预定的远程代理做什么？”

设置 `header: "Action"` 并提供四个操作（创建/列出/更新/运行）作为选项。用户选择后，按照下面的匹配工作流程进行操作。


## 你可以做什么

使用 `RemoteTrigger` 工具（首先使用 `ToolSearch select:RemoteTrigger` 加载它；身份验证在进程中处理 - 不要使用curl）：

- `{action: "list"}` — 列出所有例程
- `{action: "get", trigger_id: "..."}` — 获取一个例程
- `{action: "create", body: {...}}` — 创建例程
- `{action: "update", trigger_id: "...", body: {...}}` — 部分更新
- `{action: "run", trigger_id: "..."}` — 立即运行例程

（注：API 使用 `trigger_id` 作为参数名称，但面向用户的术语是 "routine"。）

您不能使用 delete 例程。如果用户询问 delete，请将其定向至：https://claude.ai/code/routines

## 创建身体形状

对于重复计划：```json
{
  "name": "AGENT_NAME",
  "cron_expression": "CRON_EXPR",
  "enabled": true,
  "job_config": {
    "ccr": {
      "environment_id": "ENVIRONMENT_ID",
      "session_context": {
        "model": "claude-sonnet-4-6",
        "sources": [
          {"git_repository": {"url": "https://github.com/asgeirtj/system_prompts_leaks"}}
        ],
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]
      },
      "events": [
        {"data": {
          "uuid": "<lowercase v4 uuid>",
          "session_id": "",
          "type": "user",
          "parent_tool_use_id": null,
          "message": {"content": "PROMPT_HERE", "role": "user"}
        }}
      ]
    }
  }
}
```对于一次性运行，请将 `"cron_expression": "CRON_EXPR"` 替换为 `"run_once_at": "YYYY-MM-DDTHH:MM:SSZ"`（RFC3339 UTC，必须是将来的时间）。其他一切都相同。

自己为 `events[].data.uuid` 生成一个新的小写 UUID。

## 可用 MCP 连接器

这些是用户当前连接的 claude.ai MCP 连接器：

未找到已连接的 MCP 连接器。用户可能需要连接https://claude.ai/customize/connectors的服务器

将连接器附加到例程时，请使用上面所示的 `connector_uuid` 和 `name`（名称已被清理为仅包含字母、数字、连字符和下划线）以及连接器的 URL。 `mcp_connections` 中的 `name` 字段必须仅包含 `[a-zA-Z0-9_-]` — 不允许使用点和空格。

**重要提示：** 从用户的描述中推断座席需要哪些服务。例如，如果他们说“检查 Datadog 和 Slack me 错误”，则代理需要 Datadog 和 Slack 连接器。交叉引用上面的列表，并在未连接任何所需服务时发出警告。如果缺少所需的连接器，请引导用户先连接 https://claude.ai/customize/connectors。

## 环境

每个例程都需要作业配置中的 `environment_id`。这决定了远程代理运行的位置。询问用户要使用哪种环境。

可用环境：
- 默认（id：env_011CUM1TFSuT83jzH5ttnYHr，种类：anthropic_cloud）

使用 `id` 值作为 `job_config.ccr.environment_id` 中的 `environment_id`。


## API 现场参考

### 创建例程 — 必填字段
- `name`（字符串）— 描述性名称
- 恰好是以下之一：
  - `cron_expression`（字符串）— UTC 中的 5 字段 cron。 **最短间隔为 1 小时。**
  - `run_once_at`（字符串）— RFC3339 UTC 时间戳。一定是在未来。触发一次，然后自动禁用。
- `job_config`（对象）——会话配置（参见上面的结构）

### 创建例程 — 可选字段
- `enabled`（布尔值，默认值：true）
- `mcp_connections`（阵列） — 要连接的 MCP 服务器：```json
  [{"connector_uuid": "uuid", "name": "server-name", "url": "https://..."}]
  ```### 更新例程 — 可选字段
所有字段可选（部分更新）：
- `name`、`cron_expression`、`run_once_at`、`enabled`、`job_config`
- `mcp_connections` — 替换 MCP 连接
- `clear_mcp_connections`（布尔值）— 删除所有 MCP 连接

### Cron 表达式示例

用户的本地时区是**大西洋/雷克雅未克**。 Cron 表达式和 `run_once_at` 时间戳始终采用 UTC。当用户说出当地时间时，将其转换为 UTC，但与他们确认：“9am Atlantic/Reykjavik = Xam UTC，因此 cron 将为 `0 X * * 1-5`。”对于一次性运行，适用相同的转换 —“下午 3 点运行”→ `"run_once_at": "YYYY-MM-DDTHH:00:00Z"`，并将下午 3 点转换为 UTC。

- `0 9 * * 1-5` — 每个工作日上午 9 点 **UTC**
- `0 */2 * * *` — 每 2 小时
- `0 0 * * *` — 每天午夜 **UTC**
- `30 14 * * 1` — 每周一下午 2:30 **UTC**
- `0 8 1 * *` — 每月一号上午 8 点 **UTC**

最短间隔为 1 小时。 `*/30 * * * *` 将被拒绝。

### 当前时间（一次性运行）

调用 /schedule 时，时间为 **2026 年 5 月 29 日星期五上午 12:03**（大西洋/雷克雅未克）/**2026-05-29T00:03:40.900Z** UTC。仅将此视为近似锚点 - 从那时起对话可能已经运行了一段时间。

**在计算任何 `run_once_at` 值之前，您必须通过 Bash 工具运行 `date -u +%Y-%m-%dT%H:%M:%SZ` 来重新检查当前时间**。不要从对话上下文中猜测或推断今天的日期。根据新获取的时间解析相对请求（“明天上午 9 点”、“3 小时后”、“下周一”），然后将解析的本地时间和 UTC 时间戳回显给用户，以便在创建例程之前进行确认。如果解决的时间已经过去，请用户澄清而不是默默地向前滚动。

## 工作流程

### 创建一个新例程：

1. **了解目标** — 询问他们希望远程代理做什么。什么存储库？什么任务？提醒他们代理远程运行 - 它无法访问本地计算机、本地文件或本地环境变量。
2. **制作提示** — 帮助他们编写有效的座席提示。好的提示是：
   - 具体说明要做什么以及成功是什么样子
   - 明确要关注哪些文件/区域
   - 明确要采取的行动（开放 PR、提交、分析等）
3. **设定时间表** — 询问时间和频率。用户的时区是Atlantic/Reykjavik。当他们说一个时间（例如，“每天早上 9 点”）时，假设他们指的是本地时间，并为 cron 表达式转换为 UTC。始终确认转换：“9am大西洋/雷克雅未克 = Xam UTC。”如果他们想要一次性运行（例如，“下午 3 点一次”、“明天早上”、“提醒我稍后检查 X”），请使用 `run_once_at` 而不是 `cron_expression` — 应用相同的时区转换。 **首先使用通过 Bash** `date -u`（上面的参考时间在长时间对话中可能会过时），根据该新值解析相对短语，并与用户确认生成的绝对时间戳。
4. **选择型号** — 默认为 `claude-sonnet-4-6`。告诉用户您默认使用哪种型号，并询问他们是否需要其他型号。
5. **验证连接** — 从用户的描述中推断代理将需要哪些服务。例如，如果他们说“检查 Datadog 和 Slack me 错误”，则代理需要 Datadog 和 Slack MCP 连接器。与上面的连接器列表交叉引用。如果有缺失，请警告用户并链接到 https://claude.ai/customize/connectors 首先进行连接。默认 git 存储库已设置为 `https://github.com/asgeirtj/system_prompts_leaks`。询问用户这是否是正确的存储库或者他们是否需要不同的存储库。
6. **查看并确认** — 在创建之前显示完整配置。让他们调整一下。
7. **创建** — 使用 `action: "create"` 调用 `RemoteTrigger` 并显示结果。响应包括例程 ID。始终在末尾输出链接：`https://claude.ai/code/routines/{ROUTINE_ID}`

### 更新例程：

1. 首先列出惯例，以便他们选择一个
2.询问他们想要改变什么
3. 显示当前值与建议值
4.确认并更新

### 列出例程：

1. 以可读格式获取并显示
2. 显示：名称、时间表（人类可读）、启用/禁用、下次运行、存储库

### 现在运行：

1. 如果未指定例程，则列出例程
2. 确认哪个例程
3.执行并确认

## 重要提示

- 这些是远程代理——它们在 Anthropic 的云中运行，而不是在用户的计算机上运行。他们无法访问本地文件、本地服务或本地环境变量。
- 显示时始终将 cron 转换为人类可读的格式
- 列出例程时，`ended_reason: "run_once_fired"` 表示已经运行过一次（在 Web UI 中显示为 "Ran"）。用户可以通过更新新的 `run_once_at` 来重新武装它。
- 默认为 `enabled: true` 除非用户另有说明
- 接受任何格式的 GitHub URL（https://github.com/org/repo, org/repo 等）并标准化为完整的 HTTPS URL（不带 .git 后缀）
- 提示是最重要的部分——花时间把它做好。远程代理以零上下文启动，因此提示必须是独立的。
- 将 delete 例程引导至 https://claude.ai/code/routines