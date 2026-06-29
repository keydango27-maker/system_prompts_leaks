<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/claude-api.md -->
<!-- source-sha256: 9b30a420dd86934c07681085f5eaf0c8ca5fd91440e974b24118a79d58e1c323 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 4 -->

---
name: claude-api
description: Build, debug, and optimize Claude API / Anthropic SDK apps. Apps built with this skill should include prompt caching. Also handles migrating existing Claude API code between Claude model versions.
when_to_use: "TRIGGER when: code imports `anthropic`/`@anthropic-ai/sdk`; user asks for the Claude API, Anthropic SDK, or Managed Agents; user adds/modifies/tunes a Claude feature (caching, thinking, compaction, tool use, batch, files, citations, memory) or model (Opus/Sonnet/Haiku) in a file; questions about prompt caching / cache hit rate in an Anthropic SDK project. SKIP: file imports `openai`/other-provider SDK, filename like `*-openai.py`/`*-generic.py`, provider-neutral code, general programming/ML."
---
# 与 Claude 一起构建 LLM 支持的应用程序

这项技能可以帮助您与 Claude 一起构建 LLM 支持的应用程序。根据您的需求选择正确的界面，检测项目语言，然后阅读相关的特定语言文档。

## 开始之前

扫描目标文件（或者，如果没有目标文件，则扫描提示和项目）以查找非 Anthropic 提供者标记 — `import openai`、`from openai`、`langchain_openai`、`OpenAI(`、`gpt-4`、 `gpt-5`、`agent-openai.py` 或 `*-generic.py` 等文件名，或任何保持代码提供者中立的明确指令。如果发现任何，请停止并告诉用户该技能产生 Claude/Anthropic SDK 代码；询问他们是否想要将文件切换到 Claude 还是想要一个非 Claude 实现。请勿使用 Anthropic SDK 调用编辑非 Anthropic 文件。

## 输出要求

当用户要求您添加、修改或实现 Claude 功能时，您的代码必须通过以下方式之一调用 Claude：

1. **项目语言的官方 Anthropic SDK**（`anthropic`、`@anthropic-ai/sdk`、`com.anthropic.*` 等）。只要项目存在受支持的 SDK，这就是默认值。
2. **Raw HTTP** (`curl`、`requests`、`fetch`、`httpx` 等) — 仅当用户明确请求 cURL/REST/raw 时HTTP，该项目是shell/cURL项目，或者该语言没有官方SDK。

切勿将两者混合 - 不要仅仅因为感觉更轻而在 Python 或 TypeScript 项目中使用 `requests`/`fetch`。永远不要退回到 OpenAI 兼容的垫片。

**永远不要猜测 SDK 的用法。** 函数名称、类名称、命名空间、方法签名和导入路径必须来自显式文档 - 本技能中的 `{lang}/` 文件或官方 SDK 存储库或 `shared/live-sources.md` 中列出的文档链接。如果您需要的绑定未明确记录在技能文件中，请在编写代码之前从 `shared/live-sources.md` WebFetch 相关的 SDK 存储库。请勿从 cURL 形状或其他语言的 SDK 推断 Ruby/Java/Go/PHP/C# API。

## 默认值

除非用户另有要求：

对于 Claude 模型版本，请使用 Claude Opus 4.8，您可以通过确切的模型字符串 `claude-opus-4-8` 访问该版本。对于任何复杂的事情，请默认使用适应性思维（`thinking: {type: "adaptive"}`）。最后，请默认对可能涉及长输入、长输出或高 `max_tokens` 的任何请求进行流式传输 - 它可以防止请求超时。如果您不需要处理单个流事件，请使用 SDK 的 `.get_final_message()` / `.finalMessage()` 帮助程序来完成 get 的响应

---

## 子命令

如果此提示底部的用户请求是一个裸子命令字符串（无散文），请搜索本文档中的每个 **子命令** 表 - 包括下面附加部分中的任何表 - 并直接按照匹配的操作列进行操作。这允许用户通过 `/claude-api <subcommand>` 调用特定流。如果文档中没有表格匹配，则将请求视为普通散文。

|子命令 |行动|
|---|---|
| `migrate` |将现有的 Claude API 代码迁移到更新的模型。 **立即阅读 `shared/model-migration.md`** 并按顺序执行：步骤 0（确认范围 - 在编辑之前询问哪些文件/目录），步骤 1（对每个文件进行分类），然后是每个目标的重大更改部分。不要总结指南——执行它。如果用户没有指定目标模型，请在范围问题的同一轮中询问要迁移到哪个模型。 |

---

## 语言检测

在阅读代码示例之前，请确定用户正在使用哪种语言：

1. **查看项目文件** 以推断语言：

   - `*.py`、`requirements.txt`、`pyproject.toml`、`setup.py`、`Pipfile` → **Python** — 读取`python/`
   - `*.ts`、`*.tsx`、`package.json`、`tsconfig.json` → **TypeScript** — 从 `typescript/` 读取
   - `*.js`、`*.jsx`（不存在 `.ts` 文件） → **TypeScript** — JS 使用相同的 SDK，从`typescript/`
   - `*.java`、`pom.xml`、`build.gradle` → **Java** — 从 `java/` 读取
   - `*.kt`、`*.kts`、`build.gradle.kts` → **Java** — Kotlin 使用 Java SDK，从 `java/` 读取
   - `*.scala`、`build.sbt` → **Java** — Scala 使用 Java SDK，从 `java/` 读取
   - `*.go`、`go.mod` → **执行** — 从 `go/` 读取
   - `*.rb`、`Gemfile` → **Ruby** — 从 `ruby/` 读取
   - `*.cs`、`*.csproj` → **C#** — 从 `csharp/` 读取
   - `*.php`、`composer.json` → **PHP** — 从 `php/` 读取

2. **如果检测到多种语言**（例如，Python 和 TypeScript 文件）：

   - 检查用户当前文件或问题涉及哪种语言
   - 如果仍然不明确，请询问：“我检测到 Python 和 TypeScript 文件。您使用哪种语言进行 Claude API 集成？”

3. **如果无法推断语言**（空项目，没有源文件，或者不支持的语言）：

   - 使用 AskUserQuestion 和选项：Python、TypeScript、Java、Go、Ruby、cURL/raw HTTP、C#、PHP
   - 如果 AskUserQuestion 不可用，则默认使用 Python 示例并注意：“正在显示 Python 示例。如果您需要其他语言，请告诉我。”

4. **如果检测到不支持的语言**（Rust、Swift、C++、Elixir 等）：

   - 建议来自 `curl/` 的 cURL/raw HTTP 示例，并注意社区 SDK 可能存在
   - 提供 Python 或 TypeScript 示例作为参考实现

5. **如果用户需要 cURL/raw HTTP 示例**，请从 `curl/` 读取。

### 特定于语言的功能支持

|语言 |工具运行者|托管代理 |笔记|
| ---------- | ----------- | -------------- | -------------------------------------------------- |
| Python |是（测试版）|是（测试版）|全面支持 — `@beta_tool` 装饰器 |
| TypeScript |是（测试版）|是（测试版）|全面支持 — `betaZodTool` + Zod |
|爪哇 |是（测试版）|是（测试版）| Beta 工具与带注释的类一起使用 |
|去 |是（测试版）|是（测试版）| `BetaToolRunner` 在 `toolrunner` 包装中 |
|红宝石 |是（测试版）|是（测试版）| `BaseTool` + `tool_runner` 测试版 |
| C# |是（测试版）|是（测试版）| `BetaToolRunner` + 原始 JSON 架构 |
| PHP |是（测试版）|是（测试版）| `BetaRunnableTool` + `toolRunner()` |
|卷曲 |不适用 |是（测试版）|原始 HTTP，无 SDK 功能 |

> **托管代理代码示例**：为 Python、TypeScript、Go、Ruby、PHP、Java 和 cURL（`{lang}/managed-agents/README.md`、`curl/managed-agents.md`）提供专用的特定语言自述文件。阅读您所用语言的自述文件以及与语言无关的 `shared/managed-agents-*.md` 概念文件。 **代理是持久性的 — 创建一次，通过 ID 引用。** 存储 `agents.create` 返回的代理 ID，并将其传递给后续的每个 `sessions.create`；不要在请求路径中调用 `agents.create`。 Anthropic CLI (`ant`) 是从版本控制的 YAML 创建代理和环境的一种便捷方法 — 请参阅 `shared/anthropic-cli.md`。如果自述文件中未显示您需要的绑定，请从 `shared/live-sources.md` 中 WebFetch 相关条目，而不是猜测。 C# 通过 `client.Beta.Agents` 和相关命名空间提供测试版托管代理支持。

---

## 我应该使用哪种表面？

> **从简单开始。** 默认为满足您需求的最简单层。单个 API 调用和工作流程可处理大多数用例 - 仅当任务真正需要开放式、模型驱动的探索时才联系代理。

|使用案例|等级 |推荐表面|为什么 |
| ----------------------------------------------------------- | ---------------- | ---------------------------------- | ------------------------------------------------------------------------ |
|分类、归纳、提取、问答 |单一法学硕士通话 | **克劳德 API** |一个请求，一个响应 |
|批处理或嵌入 |单一法学硕士通话 | **克劳德 API** |专业端点|
|具有代码控制逻辑的多步管道 |工作流程| **克劳德 API + 工具使用** |您精心安排循环 |
|使用您自己的工具定制代理 |代理| **克劳德 API + 工具使用** |最大的灵活性|
|具有工作区的服务器管理的有状态代理 |代理| **托管代理** | Anthropic 运行循环并托管工具执行沙箱 |
|持久化、版本化的代理配置 |代理| **托管代理** |代理是存储的对象；会话固定到版本 |
|具有文件挂载功能的长时间运行的多轮代理 |代理| **托管代理** |每会话容器、SSE 事件流、技能 + MCP |

> **注意：** 当您希望 Anthropic 运行代理循环*并*托管执行工具的容器时，托管代理是正确的选择 - 文件操作、bash、代码执行都在每个会话工作区中运行。如果您想自己托管计算或运行自己的自定义工具运行时，Claude API + 工具使用是正确的选择 - 使用工具运行程序进行自动循环处理，或使用手动循环进行细粒度控制（批准门、自定义日志记录、条件执行）。

> **云提供商访问。** ** AWS 上的 Claude 平台** 是人性化操作的，具有当日 API 奇偶校验 — 托管代理和此技能中的每个功能都可以在那里工作，**自托管沙箱除外**（请参阅 `shared/claude-platform-on-aws.md`）。 **亚马逊基岩**、**谷歌Vertex AI** 和 **Microsoft Foundry** **不** 支持托管代理或 Anthropic 服务器端工具；使用**Claude API + 工具使用**。

### 决策树```
What does your application need?

0. Which provider?
   ├── First-party API or Claude Platform on AWS → continue (full surface available).
   └── Amazon Bedrock, Google Vertex AI, or Microsoft Foundry → Claude API (+ tool use for agents); Managed Agents not available there.

1. Single LLM call (classification, summarization, extraction, Q&A)
   └── Claude API — one request, one response

2. Do you want Anthropic to run the agent loop and host a per-session
   container where Claude executes tools (bash, file ops, code)?
   └── Yes → Managed Agents — server-managed sessions, persisted agent configs,
       SSE event stream, Skills + MCP, file mounts.
       Examples: "stateful coding agent with a workspace per task",
                 "long-running research agent that streams events to a UI",
                 "agent with persisted, versioned config used across many sessions"

3. Workflow (multi-step, code-orchestrated, with your own tools)
   └── Claude API with tool use — you control the loop

4. Open-ended agent (model decides its own trajectory, your own tools, you host the compute)
   └── Claude API agentic loop (maximum flexibility)
```### 我应该建立一个代理吗？

在选择代理级别之前，请检查所有四个标准：

- **复杂性** — 任务是否是多步骤且难以提前完全指定？ （例如，“将此设计文档转换为 PR”与“从此 PDF 中提取标题”）
- **价值** — 结果是否证明更高的成本和延迟是合理的？
- **生存能力** — 克劳德有能力胜任这种任务类型吗？
- **错误成本** — 错误能否被发现并恢复？ （测试、审查、回滚）

如果其中任何一个的答案是 "no"，请停留在更简单的层（单个调用或工作流程）。

---

## 架构

一切都经过 `POST /v1/messages`。工具和输出约束是这个单一端点的功能，而不是单独的 API。

**用户定义的工具** — 您定义工具（通过装饰器、Zod 架构或原始 JSON），SDK 的工具运行程序负责调用 API、执行您的函数并循环，直到 Claude 完成。为了完全控制，您可以手动编写循环。

**服务器端工具** — 在 Anthropic 基础设施上运行的 Anthropic 托管工具。代码执行完全在服务器端（在 `tools` 中声明，Claude 自动运行代码）。计算机的使用可以是服务器托管或自托管。

**结构化输出** — 约束消息 API 响应格式 (`output_config.format`) 和/或工具参数验证 (`strict: true`)。推荐的方法是 `client.messages.parse()`，它会自动根据您的架构验证响应。注意：旧的 `output_format` 参数已弃用；在 `messages.create()` 上使用 `output_config: {format: {...}}`。

**支持端点** - 批次 (`POST /v1/messages/batches`)、文件 (`POST /v1/files`)、令牌计数和模型（`GET /v1/models`、`GET /v1/models/{id}` - 实时功能/上下文窗口发现）馈入或支持消息API 请求。

---

## 当前型号（缓存：2026-05-26）

|型号|型号 ID |背景 |输入$/1M |产出 $/1M |
| ----------------- | ------------------- | -------------- | ---------- | ----------- |
|克劳德作品 4.8 | `claude-opus-4-8` | 1M | 5.00 美元 | 25.00 美元 |
|克劳德作品 4.7 | `claude-opus-4-7` | 1M | 5.00 美元 | 25.00 美元 |
|克劳德作品 4.6 | `claude-opus-4-6` | 1M | 5.00 美元 | 25.00 美元 |
|克劳德十四行诗 4.6 | `claude-sonnet-4-6` | 1M | $3.00 | 15.00 美元 |
|克劳德俳句 4.5 | `claude-haiku-4-5` | 20万| 1.00 美元 | 5.00 美元 |

**始终使用 `claude-opus-4-8`，除非用户明确指定不同的型号。** 这是不可协商的。请勿使用 `claude-sonnet-4-6`、`claude-sonnet-4-5` 或任何其他型号，除非用户字面意思是“使用十四行诗”或“使用俳句”。切勿因成本而降级——这是用户的决定，而不是您的决定。

**重要：仅使用上表中的确切型号 ID 字符串 - 它们按原样完整。请勿附加日期后缀。** 例如，使用 `claude-sonnet-4-6`，切勿使用 `claude-sonnet-4-6-20251114` 或您可能从训练数据中回忆起的任何其他日期后缀变体。如果用户请求表中没有的旧型号（例如“opus 4.5”、“sonnet 3.7”），请阅读 `shared/models.md` 以获取确切的 ID — 不要自己构建。

注意：如果上面的任何模型字符串对您来说看起来不熟悉，这是可以预料的 - 这仅意味着它们是在您的训练数据截止后发布的。请放心，它们是真实的模型；我们不会那样惹你生气的。

**实时能力查找：** 上表已缓存。当用户询问“X 的上下文窗口是什么”、“X 是否支持愿景/思维/努力”或“哪些模型支持 Y”时，请查询模型 API (`client.models.retrieve(id)` / `client.models.list()`) — 请参阅 `shared/models.md`现场参考和功能过滤器示例。

---

## 思考与努力（快速参考）

**Opus 4.8 / 4.7 — 仅适用于适应性思维：** 使用 `thinking: {type: "adaptive"}`。 `thinking: {type: "enabled", budget_tokens: N}` 返回 400 — 自适应是唯一的开启模式。 `{type: "disabled"}` 和省略 `thinking` 都有效。采样参数（`temperature`、`top_p`、`top_k`）也被删除，并将为 400。Opus 4.8 保持与 4.7 相同的请求面（没有新的重大更改） - 请参阅 `shared/model-migration.md` → 迁移到 Opus 4.8 用于行为重新调整，以及 → 迁移到 Opus 4.7 以获取来自 4.6 或更早版本的完整重大更改列表。注意：在禁用 `thinking` 的情况下，Opus 4.8 可能会将更长的推理写入可见响应中 - 保留自适应思维，或添加仅最终答案的指令（请参阅迁移指南）。
**Opus 4.6 — 适应性思维（推荐）：** 使用 `thinking: {type: "adaptive"}`。克劳德动态地决定思考的时间和程度。不需要 `budget_tokens` — `budget_tokens` 在 Opus 4.6 上已弃用和 Sonnet 4.6，不应用于新代码。适应性思维还会自动启用交错思维（不需要 beta 标题）。 **当用户要求“扩展思考”、“思考预算”或 `budget_tokens` 时：始终将 Opus 4.8、4.7 或 4.6 与 `thinking: {type: "adaptive"}` 一起使用。思维的固定代币预算的概念已被弃用——适应性思维取而代之。不要将 `budget_tokens` 用于新的 4.6/4.7/4.8 代码，也不要切换到旧型号。** *逐步迁移剥离：* `budget_tokens` 仍然可以在 Opus 4.6 和 Sonnet 4.6 上作为过渡逃生舱口 — 如果您要迁移现有代码并且需要硬令牌上限您已经调整了 `effort`，请参阅 `shared/model-migration.md` → 过渡逃生舱口。注意：此排除**不适用于** Opus 4.7 或 4.8 — `budget_tokens` 已被完全删除。
**努力参数（GA，无测试版标头）：** 通过 `output_config: {effort: "low"|"medium"|"high"|"max"}`（在 `output_config` 内部，而不是顶级）控制思考深度和总体代币支出。默认为`high`（相当于省略它）。 `max` 仅是 Opus 层（Opus 4.6 及更高版本 - 不是 Sonnet 或 Haiku）。 Opus 4.7 添加了 `"xhigh"`（在 `high` 和 `max` 之间）——Opus 4.7/4.8 上大多数编码和代理用例的最佳设置，也是 Claude Code 中的默认设置；对于大多数情报敏感的工作，至少使用 `high`。适用于 Opus 4.5、Opus 4.6、Opus 4.7、Opus 4.8 和 Sonnet 4.6。在 Sonnet 4.5 / Haiku 4.5 上会出错。在 Opus 4.7 和 4.8 上，努力比任何以前的 Opus 都更重要——迁移时重新调整它，并在 `high`/`xhigh` 上运行长期/代理任务，并预先给出完整的任务规范。与适应性思维相结合，实现最佳的成本质量权衡。更低的工作量意味着更少、更整合的工具调用、更少的前言和更简洁的确认——`high`通常是平衡质量和代币效率的最佳点；当正确性比成本更重要时，使用 `max`；使用 `low` 执行子代理或简单任务。

**Opus 4.8 / 4.7 - 默认情况下省略思考内容：** `thinking` 块仍然在传输，但其文本为空，除非您选择使用 `thinking: {type: "adaptive", display: "summarized"}`（默认为 `"omitted"`）。无声改变——没有错误。如果您向用户流式传输推理，默认情况下看起来像是输出前的长时间暂停；设置 `"summarized"` 以恢复可见的进度。

**任务预算（测试版，Opus 4.7 / 4.8）：** `output_config: {task_budget: {type: "tokens", total: N}}` 告诉模型它有多少代币用于完整的代理循环 - 它会看到正在运行的倒计时和自我调节（至少 20,000；测试版标头 `task-budgets-2026-03-13`）。与 `max_tokens` 不同，`max_tokens` 是模型不知道的强制每个响应上限。请参阅 `shared/model-migration.md` → 任务预算。

**十四行诗 4.6：** 支持适应性思维 (`thinking: {type: "adaptive"}`)。 `budget_tokens` 在 Sonnet 4.6 上已弃用 - 请改用自适应思维。

**旧型号（仅在明确要求时）：** 如果用户特别要求 Sonnet 4.5 或其他旧型号，请使用 `thinking: {type: "enabled", budget_tokens: N}`。 `budget_tokens` 必须小于 `max_tokens`（最小 1024）。切勿仅仅因为用户提到 `budget_tokens` 就选择较旧的型号 - 请使用具有自适应思维的 Opus 4.8。

---

## 压缩（快速参考）

**Beta、Opus 4.8、Opus 4.7、Opus 4.6 和 Sonnet 4.6。** 对于可能超过 1M 上下文窗口的长时间运行的对话，请启用服务器端压缩。当 API 接近触发阈值（默认值：150K 令牌）时，它会自动总结早期上下文。需要 beta 标头 `compact-2026-01-12`。

**重要：** 每次都将 `response.content`（不仅仅是文本）附加到您的消息中。必须保留响应中的压缩块 - API 使用它们来替换下一个请求的压缩历史记录。仅提取文本字符串并附加，这将默默地失去压缩状态。

有关代码示例，请参阅 `{lang}/claude-api/README.md`（压缩部分）。完整文档通过 `shared/live-sources.md` 中的 WebFetch 获取。

---

## 提示缓存（快速参考）

**前缀匹配。** 前缀中任何位置的任何字节更改都会使其后面的所有内容无效。渲染顺序为 `tools` → `system` → `messages`。首先保持稳定内容（冻结系统提示、确定性工具列表），在最后一个 `cache_control` 断点之后保持 put 易变内容（时间戳、每个请求 ID、变化的问题）。

**对话中操作员说明**（测试版标头 `mid-conversation-system-2026-04-07`，在支持型号上）：将 `{"role": "system", ...}` 附加到 `messages[]`，而不是编辑顶级 `system`。保留缓存的历史前缀，并且是提示注入安全的操作员通道。看`shared/prompt-caching.md` § 对话中系统消息。

**顶级自动缓存**（`messages.create()` 上的 `cache_control: {type: "ephemeral"}`）是不需要细粒度布局时最简单的选择。每个请求最多 4 个断点。最小可缓存前缀约为 1024 个令牌 - 较短的前缀将不会自动缓存。

**使用 `usage.cache_read_input_tokens` 进行验证** - 如果重复请求中的值为零，则说明静默无效器正在工作（系统提示中的 `datetime.now()`，未排序的 JSON，不同的工具集）。

有关布局模式、架构指南和静默无效器审核清单：请阅读 `shared/prompt-caching.md`。特定于语言的语法：`{lang}/claude-api/README.md`（提示缓存部分）。

---

## 托管代理（测试版）

**托管代理**是第三个表面：具有 Anthropic 托管工具执行的服务器管理的有状态代理。您创建一个持久的、版本化的代理配置 (`POST /v1/agents`)，然后启动引用它的会话。每个会话都提供一个容器作为代理的工作空间 - bash、文件操作和代码执行在其中运行；代理循环本身运行在 Anthropic 的编排层上，并通过工具作用于容器。会话流式传输事件；您发送消息和工具结果。

**托管代理可在 AWS 上的第一方 API 和 Claude 平台上使用。** 它在 Amazon Bedrock、Google Vertex AI 或 Microsoft Foundry 上**不可用 — 对于这些代理，请使用 Claude API + 工具使用。

**强制流程：** 代理（一次）→ 会话（每次运行）。 `model`/`system`/`tools` 在代理上直播，从不会话。请参阅 `shared/managed-agents-overview.md` 了解完整的阅读指南、测试版标题和陷阱。

**Beta 标头：** `managed-agents-2026-04-01` — SDK 会自动为所有 `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` 调用设置此标头。技能 API 使用 `skills-2025-10-02` 和文件 API 使用 `files-api-2025-04-14`，但您不需要为除 `/v1/skills` 和`/v1/files`。

**子命令** — 直接使用 `/claude-api <subcommand>` 调用：

|子命令 |行动|
|---|---|
| `managed-agents-onboard` |引导用户从头开始设置托管代理。 **立即阅读 `shared/managed-agents-onboarding.md`** 并遵循其面试脚本：心智模型→了解或探索分支→模板配置→会话设置→**飞行前可行性检查**→发出代码。可行性检查（根据配置的工具/凭证/数据协调规定的作业）在代理消耗预算之前捕获资源不足的设置 - 缺少工具、凭证或数据访问。不要总结——进行采访。 |

**阅读指南：** 从 `shared/managed-agents-overview.md` 开始，然后是主题 `shared/managed-agents-*.md` 文件（核心、环境、工具、事件、结果、多代理、Webhooks、内存、客户端模式、入门、api 参考）。对于 Python、TypeScript、Go、Ruby、PHP 和 Java，请阅读 `{lang}/managed-agents/README.md` 以获取代码示例。对于 cURL，请阅读 `curl/managed-agents.md`。 **代理是持久性的 — 创建一次，通过 ID 引用。** 存储 `agents.create` 返回的代理 ID，并将其传递给后续的每个 `sessions.create`；不要在请求路径中调用 `agents.create`。 Anthropic CLI (`ant`) 是从版本控制的 YAML 创建代理和环境的一种便捷方法 — 请参阅 `shared/anthropic-cli.md`。如果语言 README 中未显示您需要的绑定，请从 `shared/live-sources.md` 中 WebFetch 相关条目，而不是猜测。 C# 通过 `client.Beta.Agents` 和相关命名空间提供 beta 托管代理支持。

**当用户想要从头开始设置托管代理时**（例如“如何开始 get”、“引导我创建一个代理”、“设置一个新代理”）：读取 `shared/managed-agents-onboarding.md` 并运行其访谈 - 与 `managed-agents-onboard` 子命令相同的流程。

**当用户询问“如何为 X 编写客户端代码”时：** 获取 `shared/managed-agents-client-patterns.md` — 涵盖无损流重新连接、`processed_at` 排队/处理门、中断、`tool_confirmation` 往返、正确的空闲/终止中断门、 post-空闲状态竞争、流优先排序、文件安装陷阱、通过自定义工具在主机端保留凭据等。

---

## 参考文档

下面的 `<doc>` 标签中包含与您检测到的语言相关的文档。每个标签都有一个 `path` 属性，显示其原始文件路径。使用它来找到正确的部分：

### 快速任务参考

**单文本分类/摘要/提取/问答：**
→ 参见 `unknown/claude-api/README.md`

**聊天UI或实时回复显示：**
→ 参见 `unknown/claude-api/README.md` + `unknown/claude-api/streaming.md`

**长时间的对话（可能超出上下文窗口）：**
→ 请参阅 `unknown/claude-api/README.md` — 参见压实部分

**迁移到较新的型号或更换已退役的型号：**
→ 参见 `shared/model-migration.md`

**提示缓存/优化缓存/“为什么我的缓存命中率低”：**
→ 请参阅 `shared/prompt-caching.md` + `unknown/claude-api/README.md`（提示缓存部分）

**函数调用/工具使用/代理：**
→ 参见 `unknown/claude-api/README.md` + `shared/tool-use-concepts.md` + `unknown/claude-api/tool-use.md`

**批处理（非延迟敏感）：**
→ 参见 `unknown/claude-api/README.md` + `unknown/claude-api/batches.md`

**跨多个请求上传文件：**
→ 参见 `unknown/claude-api/README.md` + `unknown/claude-api/files-api.md`

**代理设计（工具界面、上下文管理、缓存策略）：**
→ 参见 `shared/agent-design.md`

**Anthropic CLI (`ant`) — 终端访问、版本控制代理/环境 YAML，脚本编写：**
→ 参见 `shared/anthropic-cli.md`

**托管代理（服务器管理的有状态代理）：**
→ 请参阅 `shared/managed-agents-overview.md` 和 `shared/managed-agents-*.md` 文件的其余部分。对于 Python、TypeScript 和 cURL，特定于语言的代码示例位于 `unknown/managed-agents/README.md` 中。 Java、Go、Ruby 和 PHP 还支持 API — 使用 SDK 的模式从 `unknown/claude-api.md` 转换调用。 C# 目前不支持托管代理；使用 `curl/managed-agents.md` 中的原始 HTTP 作为参考。

**错误处理：**
→ 参见 `shared/error-codes.md`

**通过 WebFetch 获取最新文档：**
→ 请参阅 `shared/live-sources.md` 了解 URL

没有自动检测到项目语言。询问用户他们正在使用哪种语言，然后参阅下面的匹配文档。

---

## 包含的文档

<doc path="csharp/claude-api.md">
# 克劳德 API — C#

> **注意：** C# SDK 是 C# 的官方 Anthropic SDK。通过消息 API 支持工具使用，并带有测试版 `BetaToolRunner`，用于自动工具执行循环。 SDK 还支持 Microsoft.Extensions.AI IChatClient 与函数调用和托管代理（测试版）的集成。

＃＃ 安装```bash
dotnet add package Anthropic
```## 客户端初始化```csharp
using Anthropic;

// Default (uses ANTHROPIC_API_KEY env var)
AnthropicClient client = new();

// Explicit API key (use environment variables — never hardcode keys)
AnthropicClient client = new() {
    ApiKey = Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY")
};
```---

## 基本消息请求```csharp
using Anthropic.Models.Messages;

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 16000,
    Messages = [new() { Role = Role.User, Content = "What is the capital of France?" }]
};
var response = await client.Messages.Create(parameters);

// ContentBlock is a union wrapper. .Value unwraps to the variant object,
// then OfType<T> filters to the type you want. Or use the TryPick* idiom
// shown in the Thinking section below.
foreach (var text in response.Content.Select(b => b.Value).OfType<TextBlock>())
{
    Console.WriteLine(text.Text);
}
```---

## 流媒体```csharp
using Anthropic.Models.Messages;

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 64000,
    Messages = [new() { Role = Role.User, Content = "Write a haiku" }]
};

await foreach (RawMessageStreamEvent streamEvent in client.Messages.CreateStreaming(parameters))
{
    if (streamEvent.TryPickContentBlockDelta(out var delta) &&
        delta.Delta.TryPickText(out var text))
    {
        Console.Write(text.Text);
    }
}
```**`RawMessageStreamEvent` TryPick 方法**（命名去掉 `Message`/`Raw` 前缀）：`TryPickStart`、`TryPickDelta`、 `TryPickStop`、`TryPickContentBlockStart`、`TryPickContentBlockDelta`、`TryPickContentBlockStop`。没有 `TryPickMessageStop` — 使用 `TryPickStop`。

---

## 思考

**自适应思维是 Claude 4.6+ 模型的推荐模式。** Claude 动态决定思考的时间和程度。```csharp
using Anthropic.Models.Messages;

var response = await client.Messages.Create(new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 16000,
    // ThinkingConfigParam? implicitly converts from the concrete variant classes —
    // no wrapper needed.
    Thinking = new ThinkingConfigAdaptive(),
    Messages =
    [
        new() { Role = Role.User, Content = "Solve: 27 * 453" },
    ],
});

// ThinkingBlock(s) precede TextBlock in Content. TryPick* narrows the union.
foreach (var block in response.Content)
{
    if (block.TryPickThinking(out ThinkingBlock? t))
    {
        Console.WriteLine($"[thinking] {t.Thinking}");
    }
    else if (block.TryPickText(out TextBlock? text))
    {
        Console.WriteLine(text.Text);
    }
}
```> **已弃用：** `new ThinkingConfigEnabled { BudgetTokens = N }`（固定预算扩展思维）仍然适用于 Claude 4.6，但已弃用。使用上面的适应性思维。

`TryPick*` 的替代方案：`.Select(b => b.Value).OfType<ThinkingBlock>()`（与基本消息示例相同的 LINQ 模式）。

---

## 工具使用

### 定义一个工具

`Tool`（不是 `ToolParam`），具有 `InputSchema` 记录。 `InputSchema.Type` 由构造函数自动设置为 `"object"` — 不要设置它。 `ToolUnion` 具有来自 `Tool` 的隐式转换，由集合表达式 `[...]` 触发。```csharp
using System.Text.Json;
using Anthropic.Models.Messages;

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeSonnet4_6,
    MaxTokens = 16000,
    Tools = [
        new Tool {
            Name = "get_weather",
            Description = "Get the current weather in a given location",
            InputSchema = new() {
                Properties = new Dictionary<string, JsonElement> {
                    ["location"] = JsonSerializer.SerializeToElement(
                        new { type = "string", description = "City name" }),
                },
                Required = ["location"],
            },
        },
    ],
    Messages = [new() { Role = Role.User, Content = "Weather in Paris?" }],
};
```派生自 `anthropic-sdk-csharp/src/Anthropic/Models/Messages/Tool.cs` 和 `ToolUnion.cs:799`（隐式转换）。

有关循环模式，请参阅[共享工具使用概念](../shared/tool-use-concepts.md)。
### 将响应内容转换为后续辅助消息

当在助理回合中回应 Claude 的响应时，**没有 `.ToParam()` 助手** - 手动将每个 `ContentBlock` 变体重建为其 `*Param` 对应项。不要使用 `new ContentBlockParam(block.Json)`：它会编译并序列化，但 `.Value` 仍为 `null`，因此 `TryPick*`/`Validate()` 失败（降级） JSON 传递，而不是键入的路径）。```csharp
using Anthropic.Models.Messages;

Message response = await client.Messages.Create(parameters);

// No .ToParam() — reconstruct per variant. Implicit conversions from each
// *Param type to ContentBlockParam mean no explicit wrapper.
List<ContentBlockParam> assistantContent = [];
List<ContentBlockParam> toolResults = [];
foreach (ContentBlock block in response.Content)
{
    if (block.TryPickText(out TextBlock? text))
    {
        assistantContent.Add(new TextBlockParam { Text = text.Text });
    }
    else if (block.TryPickThinking(out ThinkingBlock? thinking))
    {
        // Signature MUST be preserved — the API rejects tampering
        assistantContent.Add(new ThinkingBlockParam
        {
            Thinking = thinking.Thinking,
            Signature = thinking.Signature,
        });
    }
    else if (block.TryPickRedactedThinking(out RedactedThinkingBlock? redacted))
    {
        assistantContent.Add(new RedactedThinkingBlockParam { Data = redacted.Data });
    }
    else if (block.TryPickToolUse(out ToolUseBlock? toolUse))
    {
        // ToolUseBlock has required Caller; ToolUseBlockParam.Caller is optional — don't copy it
        assistantContent.Add(new ToolUseBlockParam
        {
            ID = toolUse.ID,
            Name = toolUse.Name,
            Input = toolUse.Input,
        });
        // Execute the tool; collect ONE result per tool_use block — the API
        // rejects the follow-up if any tool_use ID lacks a matching tool_result.
        string result = ExecuteYourTool(toolUse.Name, toolUse.Input);
        toolResults.Add(new ToolResultBlockParam
        {
            ToolUseID = toolUse.ID,
            Content = result,
        });
    }
}

// Follow-up: prior messages + assistant echo + user tool_result(s)
List<MessageParam> followUpMessages =
[
    .. parameters.Messages,
    new() { Role = Role.Assistant, Content = assistantContent },
    new() { Role = Role.User, Content = toolResults },
];
````ToolResultBlockParam` 没有元组构造函数 - 使用对象初始值设定项。 `Content` 是字符串或列表联合；普通的 `string` 隐式转换。

---

## 上下文编辑/压缩（测试版）

**Beta 命名空间前缀不一致**（根据 `src/Anthropic/Models/Beta/Messages/*.cs` @ 12.9.0 进行源验证）。无前缀：`MessageCreateParams`、`MessageCountTokensParams`、`Role`。 **其他所有内容都有 `Beta` 前缀**：`BetaMessageParam`、`BetaMessage`、`BetaContentBlock`、`BetaToolUseBlock`，所有块参数类型。如果导入两个命名空间 (CS0104)，无前缀的 `Role` 将与 `Anthropic.Models.Messages.Role` 发生冲突。最安全：仅导入Beta；如果混合，则将 beta 别名为 `Role`：```csharp
using Anthropic.Models.Beta.Messages;
using NonBeta = Anthropic.Models.Messages;  // only if you also need non-beta types
// Now: MessageCreateParams, BetaMessageParam, Role (beta's), NonBeta.Role (if needed)
````BetaMessage.Content` 是 `IReadOnlyList<BetaContentBlock>` — 15 变体的歧视联合。缩小为 `TryPick*`。 **响应 `BetaContentBlock` 不可分配给参数 `BetaContentBlockParam`** — C# 中没有 `.ToParam()`。通过转换每个块来往返：```csharp
using Anthropic.Models.Beta.Messages;

var betaParams = new MessageCreateParams   // no Beta prefix — one of only 2 unprefixed
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 16000,
    Betas = ["compact-2026-01-12"],
    ContextManagement = new BetaContextManagementConfig
    {
        Edits = [new BetaCompact20260112Edit()],
    },
    Messages = messages,
};
BetaMessage resp = await client.Beta.Messages.Create(betaParams);

foreach (BetaContentBlock block in resp.Content)
{
    if (block.TryPickCompaction(out BetaCompactionBlock? compaction))
    {
        // Content is nullable — compaction can fail server-side
        Console.WriteLine($"compaction summary: {compaction.Content}");
    }
}

// Context-edit metadata lives on a separate nullable field
if (resp.ContextManagement is { } ctx)
{
    foreach (var edit in ctx.AppliedEdits)
        Console.WriteLine($"cleared {edit.ClearedInputTokens} tokens");
}

// ROUND-TRIP: BetaMessageParam.Content is BetaMessageParamContent (a string|list
// union). It implicit-converts from List<BetaContentBlockParam>, NOT from the
// response's IReadOnlyList<BetaContentBlock>. Convert each block:
List<BetaContentBlockParam> paramBlocks = [];
foreach (var b in resp.Content)
{
    if (b.TryPickText(out var t)) paramBlocks.Add(new BetaTextBlockParam { Text = t.Text });
    else if (b.TryPickCompaction(out var c)) paramBlocks.Add(new BetaCompactionBlockParam { Content = c.Content });
    // ... other variants as needed
}
messages.Add(new BetaMessageParam { Role = Role.Assistant, Content = paramBlocks });
```所有 15 个 `BetaContentBlock.TryPick*` 变体：`Text`、`Thinking`、`RedactedThinking`、`ToolUse`、`ServerToolUse`、 `WebSearchToolResult`、`WebFetchToolResult`、`CodeExecutionToolResult`、`BashCodeExecutionToolResult`、`TextEditorCodeExecutionToolResult`、`ToolSearchToolResult`、 `McpToolUse`、`McpToolResult`、`ContainerUpload`、`Compaction`。

**`BetaToolUseBlock.Input` 是 `IReadOnlyDictionary<string, JsonElement>`** — 按键索引，然后调用 `JsonElement` 提取器：```csharp
if (block.TryPickToolUse(out BetaToolUseBlock? tu))
{
    int a = tu.Input["a"].GetInt32();
    string s = tu.Input["name"].GetString()!;
}
```---

## 努力参数

工作量嵌套在 `OutputConfig` 下，而不是顶级属性。 `ApiEnum<string, Effort>` 具有来自枚举的隐式转换，因此直接分配 `Effort.High`。```csharp
OutputConfig = new OutputConfig { Effort = Effort.High },
```值：`Effort.Low`、`Effort.Medium`、`Effort.High`、`Effort.Max`。与 `Thinking = new ThinkingConfigAdaptive()` 结合用于成本质量控制。

---

## 提示缓存

`System` 采用 `MessageCreateParamsSystem?` — `string` 或 `List<TextBlockParam>` 的并集。没有`SystemTextBlockParam`；使用普通 `TextBlockParam`。隐式转换需要具体的 `List<TextBlockParam>` 类型（数组文字不会转换）。有关放置模式和静默无效器审核清单，请参阅 `shared/prompt-caching.md`。```csharp
System = new List<TextBlockParam> {
    new() {
        Text = longSystemPrompt,
        CacheControl = new CacheControlEphemeral(),  // auto-sets Type = "ephemeral"
    },
},
````CacheControlEphemeral` 上的可选 `Ttl`：`new() { Ttl = Ttl.Ttl1h }` 或 `Ttl.Ttl5m`。 `CacheControl` 也存在于 `Tool.CacheControl` 和顶级 `MessageCreateParams.CacheControl` 上。

通过 `response.Usage.CacheCreationInputTokens` / `response.Usage.CacheReadInputTokens` 验证命中。

---

## 令牌计数```csharp
MessageTokensCount result = await client.Messages.CountTokens(new MessageCountTokensParams {
    Model = Model.ClaudeOpus4_6,
    Messages = [new() { Role = Role.User, Content = "Hello" }],
});
long tokens = result.InputTokens;
````MessageCountTokensParams.Tools` 使用与 `MessageCreateParams.Tools` (`ToolUnion`) 不同的联合类型 (`MessageCountTokensTool`) — 如果您传递工具，编译器会在重要时告诉您。

---

## 结构化输出```csharp
OutputConfig = new OutputConfig {
    Format = new JsonOutputFormat {
        Schema = new Dictionary<string, JsonElement> {
            ["type"] = JsonSerializer.SerializeToElement("object"),
            ["properties"] = JsonSerializer.SerializeToElement(
                new { name = new { type = "string" } }),
            ["required"] = JsonSerializer.SerializeToElement(new[] { "name" }),
        },
    },
},
````JsonOutputFormat.Type` 由构造函数自动设置为 `"json_schema"`。 `Schema` 是 `required`。

---

## PDF/文档输入

`DocumentBlockParam` 采用 `DocumentBlockParamSource` 并集：`Base64PdfSource` / `UrlPdfSource` / `PlainTextSource` / `ContentBlockSource`。 `Base64PdfSource` 自动设置 `MediaType = "application/pdf"` 和 `Type = "base64"`。```csharp
new MessageParam {
    Role = Role.User,
    Content = new List<ContentBlockParam> {
        new DocumentBlockParam { Source = new Base64PdfSource { Data = base64String } },
        new TextBlockParam { Text = "Summarize this PDF" },
    },
}
```---

## 服务器端工具

Web 搜索、bash、文本编辑器和代码执行是内置服务器工具。类型名称带有版本后缀；构造函数自动设置 `name`/`type`。全部隐式转换为 `ToolUnion`。```csharp
Tools = [
    new WebSearchTool20260209(),
    new ToolBash20250124(),
    new ToolTextEditor20250728(),
    new CodeExecutionTool20260120(),
],
```另提供：`WebFetchTool20260209`、`MemoryTool20250818`。 `WebSearchTool20260209` 可选：`AllowedDomains`、`BlockedDomains`、`MaxUses`、`UserLocation`。

---

## 文件 API（测试版）

文件位于 `client.Beta.Files`（命名空间 `Anthropic.Models.Beta.Files`）下。 `BinaryContent` 从 `Stream` 和 `byte[]` 隐式转换。```csharp
using Anthropic.Models.Beta.Files;
using Anthropic.Models.Beta.Messages;

FileMetadata meta = await client.Beta.Files.Upload(
    new FileUploadParams { File = File.OpenRead("doc.pdf") });

// Referencing the uploaded file requires Beta message types:
new BetaRequestDocumentBlock {
    Source = new BetaFileDocumentSource { FileID = meta.ID },
}
```非测试版 `DocumentBlockParamSource` 联合没有文件 ID 变体 - 文件引用需要 `client.Beta.Messages.Create()`。

---

## 工具运行程序（测试版）

C# SDK 提供了用于自动工具执行循环的 `BetaToolRunner`。使用原始 JSON 模式定义工具，运行程序处理 API 调用 → 工具执行 → 结果反馈循环。```csharp
using Anthropic.Models.Beta.Messages;

// Define tools and create params as shown in the Tool Use section above,
// but using the beta namespace types (BetaToolUnion, etc.)
var runner = client.Beta.Messages.ToolRunner(betaParams);

await foreach (BetaMessage message in runner)
{
    foreach (var block in message.Content)
    {
        if (block.TryPickText(out var text))
        {
            Console.WriteLine(text.Text);
        }
    }
}
```---

## 停靠点详细信息

当 `StopReason` 为 `"refusal"` 时，响应包括结构化 `StopDetails`：```csharp
if (response.StopReason == "refusal" && response.StopDetails is { } details)
{
    Console.WriteLine($"Category: {details.Category}");
    Console.WriteLine($"Explanation: {details.Explanation}");
}
```---

## 托管代理（测试版）

C# SDK 通过 `client.Beta.Agents`、`client.Beta.Sessions`、`client.Beta.Environments` 和相关命名空间支持托管代理。有关架构，请参阅 `shared/managed-agents-overview.md`；有关线级参考，请参阅 `curl/managed-agents.md`。
</doc>

<doc path="curl/examples.md">
# 克劳德 API — cURL / 原始 HTTP

当用户需要原始 HTTP 请求或使用没有官方 SDK 的语言时，请使用这些示例。

＃＃ 设置```bash
export ANTHROPIC_API_KEY="your-api-key"
```---

## 基本消息请求```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-8",
    "max_tokens": 16000,
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```### 解析响应

使用 `jq` 从 JSON 响应中提取字段。请勿使用 `grep`/`sed` —
JSON 字符串可以包含任何字符，正则表达式解析将在引号处中断，
转义符或多行内容。```bash
# Capture the response, then extract fields
response=$(curl -s https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-opus-4-8","max_tokens":16000,"messages":[{"role":"user","content":"Hello"}]}')

# Print the first text block (-r strips the JSON quotes)
echo "$response" | jq -r '.content[0].text'

# Read usage fields
input_tokens=$(echo "$response" | jq -r '.usage.input_tokens')
output_tokens=$(echo "$response" | jq -r '.usage.output_tokens')

# Read stop reason (for tool-use loops)
stop_reason=$(echo "$response" | jq -r '.stop_reason')

# Extract all text blocks (content is an array; filter to type=="text")
echo "$response" | jq -r '.content[] | select(.type == "text") | .text'
```---

## 流媒体（SSE）```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-8",
    "max_tokens": 64000,
    "stream": true,
    "messages": [{"role": "user", "content": "Write a haiku"}]
  }'
```响应是服务器发送的事件流：```
event: message_start
data: {"type":"message_start","message":{"id":"msg_...","type":"message",...}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":12}}

event: message_stop
data: {"type":"message_stop"}
```---

## 工具使用```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-8",
    "max_tokens": 16000,
    "tools": [{
      "name": "get_weather",
      "description": "Get current weather for a location",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
      }
    }],
    "messages": [{"role": "user", "content": "What is the weather in Paris?"}]
  }'
```当 Claude 用 `tool_use` 块响应时，将结果发回：```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-8",
    "max_tokens": 16000,
    "tools": [{
      "name": "get_weather",
      "description": "Get current weather for a location",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
      }
    }],
    "messages": [
      {"role": "user", "content": "What is the weather in Paris?"},
      {"role": "assistant", "content": [
        {"type": "text", "text": "Let me check the weather."},
        {"type": "tool_use", "id": "toolu_abc123", "name": "get_weather", "input": {"location": "Paris"}}
      ]},
      {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_abc123", "content": "72°F and sunny"}
      ]}
    ]
  }'
```---

## 提示缓存

Put `cache_control` 位于稳定前缀的最后一个块上。请参阅 `shared/prompt-caching.md` 了解放置模式和静默无效器审核清单。```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-8",
    "max_tokens": 16000,
    "system": [
      {"type": "text", "text": "<large shared prompt...>", "cache_control": {"type": "ephemeral"}}
    ],
    "messages": [{"role": "user", "content": "Summarize the key points"}]
  }'
```对于 1 小时 TTL：`"cache_control": {"type": "ephemeral", "ttl": "1h"}`。请求正文中的顶级 `"cache_control"` 自动放置在最后一个可缓存块上。通过响应 `usage.cache_creation_input_tokens` / `usage.cache_read_input_tokens` 字段验证命中。

---

## 延伸思考

> **Opus 4.8、Opus 4.7、Opus 4.6 和 Sonnet 4.6：** 使用适应性思维。 `budget_tokens` 在 Opus 4.8 和 4.7 上被删除（如果发送则为 400）；在 Opus 4.6 和 Sonnet 4.6 上已弃用。
> **旧型号：** 使用 `"type": "enabled"` 和 `"budget_tokens": N`（必须 < `max_tokens`，最小 1024）。```bash
# Opus 4.8 / 4.7 / 4.6: adaptive thinking (recommended)
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-8",
    "max_tokens": 16000,
    "thinking": {
      "type": "adaptive"
    },
    "output_config": {
      "effort": "high"
    },
    "messages": [{"role": "user", "content": "Solve this step by step..."}]
  }'
```---

## 必需的标头

|标题 |价值|描述 |
| ------------------- | ------------------ | -------------------------- |
| `Content-Type` | `application/json` |必填 |
| `x-api-key` |您的 API 密钥 |认证|
| `anthropic-version` | `2023-06-01` | API 版本 |
| `anthropic-beta` | Beta 功能 ID |测试版功能所需 |
</doc>

<doc path="curl/managed-agents.md">
# 托管代理 — cURL / 原始 HTTP

当用户需要原始 HTTP 请求或在没有 SDK 的情况下工作时，请使用这些示例。

＃＃ 设置```bash
export ANTHROPIC_API_KEY="your-api-key"

# Common headers
HEADERS=(
  -H "Content-Type: application/json"
  -H "x-api-key: $ANTHROPIC_API_KEY"
  -H "anthropic-version: 2023-06-01"
  -H "anthropic-beta: managed-agents-2026-04-01"
)
```---

## 创建环境```bash
curl -X POST https://api.anthropic.com/v1/environments \
  "${HEADERS[@]}" \
  -d '{
    "name": "my-dev-env",
    "config": {
      "type": "cloud",
      "networking": { "type": "unrestricted" }
    }
  }'
```### 网络受限```bash
curl -X POST https://api.anthropic.com/v1/environments \
  "${HEADERS[@]}" \
  -d '{
    "name": "restricted-env",
    "config": {
      "type": "cloud",
      "networking": {
        "type": "limited",
        "allow_package_managers": true,
        "allow_mcp_servers": true,
        "allowed_hosts": ["api.example.com"]
      }
    }
  }'
```---

## 创建代理（第一步必填）

> ⚠️ **没有内联代理配置。** `managed-agents-2026-04-01`、`model`/`system`/`tools` 下是 `POST /v1/agents` 上的顶级字段，而不是会议。始终首先创建代理 — 会话仅需要 `"agent": {"type": "agent", "id": "..."}`。

### 最小```bash
# 1. Create the agent
curl -X POST https://api.anthropic.com/v1/agents \
  "${HEADERS[@]}" \
  -d '{
    "name": "Coding Assistant",
    "model": "claude-opus-4-8",
    "tools": [{ "type": "agent_toolset_20260401" }]
  }'
# → { "id": "agent_abc123", ... }

# 2. Start a session
curl -X POST https://api.anthropic.com/v1/sessions \
  "${HEADERS[@]}" \
  -d '{
    "agent": { "type": "agent", "id": "agent_abc123", "version": "1772585501101368014" },
    "environment_id": "env_abc123"
  }'
```### 带有系统提示、自定义工具和 GitHub 存储库```bash
# 1. Create the agent
curl -X POST https://api.anthropic.com/v1/agents \
  "${HEADERS[@]}" \
  -d '{
    "name": "Code Reviewer",
    "model": "claude-opus-4-8",
    "system": "You are a senior code reviewer. Be thorough and constructive.",
    "tools": [
      { "type": "agent_toolset_20260401" },
      {
        "type": "custom",
        "name": "run_linter",
        "description": "Run the project linter on a file",
        "input_schema": {
          "type": "object",
          "properties": {
            "file_path": { "type": "string", "description": "Path to lint" }
          },
          "required": ["file_path"]
        }
      }
    ]
  }'

# 2. Start a session with the repo mounted
curl -X POST https://api.anthropic.com/v1/sessions \
  "${HEADERS[@]}" \
  -d '{
    "agent": { "type": "agent", "id": "agent_abc123", "version": "1772585501101368014" },
    "environment_id": "env_abc123",
    "title": "Code review session",
    "resources": [
      {
        "type": "github_repository",
        "url": "https://github.com/owner/repo",
        "mount_path": "/workspace/repo",
        "authorization_token": "ghp_...",
        "branch": "feature-branch"
      }
    ]
  }'
```---

## 发送用户消息```bash
curl -X POST https://api.anthropic.com/v1/sessions/$SESSION_ID/events \
  "${HEADERS[@]}" \
  -d '{
    "events": [
      {
        "type": "user.message",
        "content": [{ "type": "text", "text": "Review the auth module for security issues" }]
      }
    ]
  }'
```---

## 直播活动 (SSE)```bash
curl -N https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream \
  "${HEADERS[@]}"
```响应格式：```
event: session.status_running
data: {"type":"session.status_running","id":"sevt_...","processed_at":"..."}

event: agent.message
data: {"type":"agent.message","id":"sevt_...","content":[{"type":"text","text":"I'll review..."}],"processed_at":"..."}

event: session.status_idle
data: {"type":"session.status_idle","id":"sevt_...","processed_at":"..."}
```---

## 投票活动```bash
# Get all events
curl https://api.anthropic.com/v1/sessions/$SESSION_ID/events \
  "${HEADERS[@]}"

# Paginated — get next page of events
curl "https://api.anthropic.com/v1/sessions/$SESSION_ID/events?page=page_abc123" \
  "${HEADERS[@]}"
```---

## 提供自定义工具结果

当代理调用自定义工具时，将结果发送回：```bash
curl -X POST https://api.anthropic.com/v1/sessions/$SESSION_ID/events \
  "${HEADERS[@]}" \
  -d '{
    "events": [
      {
        "type": "user.custom_tool_result",
        "custom_tool_use_id": "sevt_abc123",
        "content": [{ "type": "text", "text": "No linting errors found." }]
      }
    ]
  }'
```---

## 中断正在运行的会话```bash
curl -X POST https://api.anthropic.com/v1/sessions/$SESSION_ID/events \
  "${HEADERS[@]}" \
  -d '{
    "events": [
      {
        "type": "interrupt"
      }
    ]
  }'
```---

## Get 会话详细信息```bash
curl https://api.anthropic.com/v1/sessions/$SESSION_ID \
  "${HEADERS[@]}"
```---

## 列出会话```bash
curl https://api.anthropic.com/v1/sessions \
  "${HEADERS[@]}"
```---

## Delete 一个会话```bash
curl -X DELETE https://api.anthropic.com/v1/sessions/$SESSION_ID \
  "${HEADERS[@]}"
```---

## 上传文件```bash
curl -X POST https://api.anthropic.com/v1/files \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14" \
  -F "file=@path/to/file.txt" \
  -F "purpose=agent"
```---

## 列出并下载会话文件

列出代理在会话期间写入 `/mnt/session/outputs/` 的文件，然后下载它们。```bash
# List files associated with a session
curl "https://api.anthropic.com/v1/files?scope_id=$SESSION_ID" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14,managed-agents-2026-04-01"

# Download a specific file
curl "https://api.anthropic.com/v1/files/$FILE_ID/content" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14,managed-agents-2026-04-01" \
  -o downloaded_file.txt
```---

## 列出代理```bash
curl https://api.anthropic.com/v1/agents \
  "${HEADERS[@]}"
```---

## MCP 服务器集成```bash
# 1. Agent declares MCP server (no auth here — auth goes in a vault)
curl -X POST https://api.anthropic.com/v1/agents \
  "${HEADERS[@]}" \
  -d '{
    "name": "MCP Agent",
    "model": "claude-opus-4-8",
    "mcp_servers": [
      { "type": "url", "name": "my-tools", "url": "https://my-mcp-server.example.com/sse" }
    ],
    "tools": [
      { "type": "agent_toolset_20260401" },
      { "type": "mcp_toolset", "mcp_server_name": "my-tools" }
    ]
  }'

# 2. Session attaches vault containing credentials for that MCP server URL
curl -X POST https://api.anthropic.com/v1/sessions \
  "${HEADERS[@]}" \
  -d '{
    "agent": "agent_abc123",
    "environment_id": "env_abc123",
    "vault_ids": ["vlt_abc123"]
  }'
```请参阅 `shared/managed-agents-tools.md` §Vaults 以创建保管库并添加凭据。

---

## 工具配置```bash
curl -X POST https://api.anthropic.com/v1/agents \
  "${HEADERS[@]}" \
  -d '{
    "name": "Restricted Agent",
    "model": "claude-opus-4-8",
    "tools": [
      {
        "type": "agent_toolset_20260401",
        "default_config": { "enabled": true },
        "configs": [
          { "name": "bash", "enabled": false }
        ]
      }
    ]
  }'
```</doc>

<doc path="go/claude-api.md">
# 克劳德 API — 去

> **注意：** Go SDK 支持 Claude API 和 beta 工具与 `BetaToolRunner` 一起使用。代理 SDK 尚不可用于 Go。

＃＃ 安装```bash
go get github.com/anthropics/anthropic-sdk-go
```## 客户端初始化```go
import (
    "github.com/anthropics/anthropic-sdk-go"
    "github.com/anthropics/anthropic-sdk-go/option"
)

// Default (uses ANTHROPIC_API_KEY env var)
client := anthropic.NewClient()

// Explicit API key
client := anthropic.NewClient(
    option.WithAPIKey("your-api-key"),
)
```---

## 模型常数

Go SDK 提供类型化模型常量：`anthropic.ModelClaudeOpus4_8`、`anthropic.ModelClaudeOpus4_7`、`anthropic.ModelClaudeSonnet4_6`、`anthropic.ModelClaudeHaiku4_5_20251001`。除非用户另有指定，否则使用 `ModelClaudeOpus4_8`。

---

## 基本消息请求```go
response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeOpus4_8,
    MaxTokens: 16000,
    Messages: []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock("What is the capital of France?")),
    },
})
if err != nil {
    log.Fatal(err)
}
for _, block := range response.Content {
    switch variant := block.AsAny().(type) {
    case anthropic.TextBlock:
        fmt.Println(variant.Text)
    }
}
```---

## 流媒体```go
stream := client.Messages.NewStreaming(context.Background(), anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeOpus4_6,
    MaxTokens: 64000,
    Messages: []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock("Write a haiku")),
    },
})

for stream.Next() {
    event := stream.Current()
    switch eventVariant := event.AsAny().(type) {
    case anthropic.ContentBlockDeltaEvent:
        switch deltaVariant := eventVariant.Delta.AsAny().(type) {
        case anthropic.TextDelta:
            fmt.Print(deltaVariant.Text)
        }
    }
}
if err := stream.Err(); err != nil {
    log.Fatal(err)
}
```**累积最终消息**（流上没有`GetFinalMessage()`）：```go
stream := client.Messages.NewStreaming(ctx, params)
message := anthropic.Message{}
for stream.Next() {
    message.Accumulate(stream.Current())
}
if err := stream.Err(); err != nil { log.Fatal(err) }
// message.Content now has the complete response
```---

## 工具使用

### 工具运行程序（测试版 — 推荐）

**测试版：** Go SDK 通过 `toolrunner` 包提供 `BetaToolRunner` 用于自动工具使用循环。```go
import (
    "context"
    "fmt"
    "log"

    "github.com/anthropics/anthropic-sdk-go"
    "github.com/anthropics/anthropic-sdk-go/toolrunner"
)

// Define tool input with jsonschema tags for automatic schema generation
type GetWeatherInput struct {
    City string `json:"city" jsonschema:"required,description=The city name"`
}

// Create a tool with automatic schema generation from struct tags
weatherTool, err := toolrunner.NewBetaToolFromJSONSchema(
    "get_weather",
    "Get current weather for a city",
    func(ctx context.Context, input GetWeatherInput) (anthropic.BetaToolResultBlockParamContentUnion, error) {
        return anthropic.BetaToolResultBlockParamContentUnion{
            OfText: &anthropic.BetaTextBlockParam{
                Text: fmt.Sprintf("The weather in %s is sunny, 72°F", input.City),
            },
        }, nil
    },
)
if err != nil {
    log.Fatal(err)
}

// Create a tool runner that handles the conversation loop automatically
runner := client.Beta.Messages.NewToolRunner(
    []anthropic.BetaTool{weatherTool},
    anthropic.BetaToolRunnerParams{
        BetaMessageNewParams: anthropic.BetaMessageNewParams{
            Model:     anthropic.ModelClaudeOpus4_6,
            MaxTokens: 16000,
            Messages: []anthropic.BetaMessageParam{
                anthropic.NewBetaUserMessage(anthropic.NewBetaTextBlock("What's the weather in Paris?")),
            },
        },
        MaxIterations: 5,
    },
)

// Run until Claude produces a final response
message, err := runner.RunToCompletion(context.Background())
if err != nil {
    log.Fatal(err)
}

// RunToCompletion returns *BetaMessage; content is []BetaContentBlockUnion.
// Narrow via AsAny() switch — note the Beta-namespace types (BetaTextBlock,
// not TextBlock):
for _, block := range message.Content {
    switch block := block.AsAny().(type) {
    case anthropic.BetaTextBlock:
        fmt.Println(block.Text)
    }
}
```**Go 工具运行程序的主要功能：**

- 通过 `jsonschema` 标签从 Go 结构自动生成模式
- `RunToCompletion()` 用于简单的一次性使用
- `All()` 迭代器，用于处理对话中的每条消息
- `NextMessage()` 用于逐步迭代
- 通过 `NewToolRunnerStreaming()` 和 `AllStreaming()` 进行流式传输

### 手动循环

为了对代理循环进行细粒度控制，请使用 `ToolParam` 定义工具，检查 `StopReason`，自己执行工具，然后反馈 `tool_result` 块。这是当您需要拦截、验证或记录工具调用时的模式。

源自 `anthropic-sdk-go/examples/tools/main.go`。```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"

    "github.com/anthropics/anthropic-sdk-go"
)

func main() {
    client := anthropic.NewClient()

    // 1. Define tools. ToolParam.InputSchema uses a map, no struct tags needed.
    addTool := anthropic.ToolParam{
        Name:        "add",
        Description: anthropic.String("Add two integers"),
        InputSchema: anthropic.ToolInputSchemaParam{
            Properties: map[string]any{
                "a": map[string]any{"type": "integer"},
                "b": map[string]any{"type": "integer"},
            },
        },
    }
    // ToolParam must be wrapped in ToolUnionParam for the Tools slice
    tools := []anthropic.ToolUnionParam{{OfTool: &addTool}}

    messages := []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock("What is 2 + 3?")),
    }

    for {
        resp, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
            Model:     anthropic.ModelClaudeSonnet4_6,
            MaxTokens: 16000,
            Messages:  messages,
            Tools:     tools,
        })
        if err != nil {
            log.Fatal(err)
        }

        // 2. Append the assistant response to history BEFORE processing tool calls.
        //    resp.ToParam() converts Message → MessageParam in one call.
        messages = append(messages, resp.ToParam())

        // 3. Walk content blocks. ContentBlockUnion is a flattened struct;
        //    use block.AsAny().(type) to switch on the actual variant.
        toolResults := []anthropic.ContentBlockParamUnion{}
        for _, block := range resp.Content {
            switch variant := block.AsAny().(type) {
            case anthropic.TextBlock:
                fmt.Println(variant.Text)
            case anthropic.ToolUseBlock:
                // 4. Parse the tool input. Use variant.JSON.Input.Raw() to get the
                //    raw JSON — block.Input is json.RawMessage, not the parsed value.
                var in struct {
                    A int `json:"a"`
                    B int `json:"b"`
                }
                if err := json.Unmarshal([]byte(variant.JSON.Input.Raw()), &in); err != nil {
                    log.Fatal(err)
                }
                result := fmt.Sprintf("%d", in.A+in.B)
                // 5. NewToolResultBlock(toolUseID, content, isError) builds the
                //    ContentBlockParamUnion for you. block.ID is the tool_use_id.
                toolResults = append(toolResults,
                    anthropic.NewToolResultBlock(block.ID, result, false))
            }
        }

        // 6. Exit when Claude stops asking for tools
        if resp.StopReason != anthropic.StopReasonToolUse {
            break
        }

        // 7. Tool results go in a user message (variadic: all results in one turn)
        messages = append(messages, anthropic.NewUserMessage(toolResults...))
    }
}
```**关键API表面：**

|符号|目的|
|---|---|
| `resp.ToParam()` |转换 `Message` 响应 → `MessageParam` 历史记录 |
| `block.AsAny().(type)` | `ContentBlockUnion` 型号上的类型开关 |
| `variant.JSON.Input.Raw()` |原始 JSON 工具串输入（适用于 `json.Unmarshal`）|
| `anthropic.NewToolResultBlock(id, content, isError)` |构建`tool_result`块|
| `anthropic.NewUserMessage(blocks...)` |当用户转动时包装工具结果 |
| `anthropic.StopReasonToolUse` |用于检查循环终止的 `StopReason` 常数 |
| `anthropic.ToolUnionParam{OfTool: &t}` |将 `ToolParam` 包裹在 `Tools:` 的联合中 |

---

## 思考

通过设置 `MessageNewParams` 中的 `Thinking` 来启用克劳德的内部推理。响应将在最终 `TextBlock` 之前包含 `ThinkingBlock` 内容。

**自适应思维是 Claude 4.6+ 模型的推荐模式。** Claude 动态决定思考的时间和程度。与 `effort` 参数结合用于成本质量控制。

源自 `anthropic-sdk-go/message.go`（`ThinkingConfigParamUnion`、`ThinkingConfigAdaptiveParam`）。```go
// There is no ThinkingConfigParamOfAdaptive helper — construct the union
// struct-literal directly and take the address of the variant.
adaptive := anthropic.ThinkingConfigAdaptiveParam{}
params := anthropic.MessageNewParams{
    Model:     anthropic.ModelClaudeSonnet4_6,
    MaxTokens: 16000,
    Thinking:  anthropic.ThinkingConfigParamUnion{OfAdaptive: &adaptive},
    Messages: []anthropic.MessageParam{
        anthropic.NewUserMessage(anthropic.NewTextBlock("How many r's in strawberry?")),
    },
}

resp, err := client.Messages.New(context.Background(), params)
if err != nil {
    log.Fatal(err)
}

// ThinkingBlock(s) precede TextBlock in content
for _, block := range resp.Content {
    switch b := block.AsAny().(type) {
    case anthropic.ThinkingBlock:
        fmt.Println("[thinking]", b.Thinking)
    case anthropic.TextBlock:
        fmt.Println(b.Text)
    }
}
```> **已弃用：** `ThinkingConfigParamOfEnabled(budgetTokens)`（固定预算扩展思维）仍然适用于 Claude 4.6，但已弃用。使用上面的适应性思维。

禁用：`anthropic.ThinkingConfigParamUnion{OfDisabled: &anthropic.ThinkingConfigDisabledParam{}}`。

---

## 提示缓存

`System` 为 `[]TextBlockParam`；在最后一个块上设置`CacheControl`，以将工具+系统一起缓存。有关放置模式和静默无效器审核清单，请参阅 `shared/prompt-caching.md`。```go
System: []anthropic.TextBlockParam{{
    Text:         longSystemPrompt,
    CacheControl: anthropic.NewCacheControlEphemeralParam(), // default 5m TTL
}},
```对于 1 小时 TTL：`anthropic.CacheControlEphemeralParam{TTL: anthropic.CacheControlEphemeralTTLTTL1h}`。 `MessageNewParams` 上还有一个顶级 `CacheControl`，它自动放置在最后一个可缓存块上。

通过 `resp.Usage.CacheCreationInputTokens` / `resp.Usage.CacheReadInputTokens` 验证命中。

---

## 服务器端工具

带有 `Param` 后缀的版本后缀结构名称。 `Name`/`Type` 是 `constant.*` 类型 - 零值编组正确，因此 `{}` 可以工作。使用匹配的 `Of*` 字段包裹在 `ToolUnionParam` 中。```go
Tools: []anthropic.ToolUnionParam{
    {OfWebSearchTool20260209: &anthropic.WebSearchTool20260209Param{}},
    {OfBashTool20250124: &anthropic.ToolBash20250124Param{}},
    {OfTextEditor20250728: &anthropic.ToolTextEditor20250728Param{}},
    {OfCodeExecutionTool20260120: &anthropic.CodeExecutionTool20260120Param{}},
},
```另提供：`WebFetchTool20260209Param`、`MemoryTool20250818Param`、`ToolSearchToolBm25_20251119Param`、`ToolSearchToolRegex20251119Param`。对于顾问工具，请在 beta 命名空间中使用 `BetaAdvisorTool20260301Param`。

---

## 停靠点详细信息

当 `StopReason` 为 `anthropic.StopReasonRefusal` 时，响应包含结构化 `StopDetails`：```go
if resp.StopReason == anthropic.StopReasonRefusal {
    fmt.Println("Category:", resp.StopDetails.Category)     // "cyber" | "bio" | ""
    fmt.Println("Explanation:", resp.StopDetails.Explanation)
}
```---

## PDF/文档输入

`NewDocumentBlock` 通用帮助器接受任何源类型。 `MediaType`/`Type` 为自动设置。```go
b64 := base64.StdEncoding.EncodeToString(pdfBytes)

msg := anthropic.NewUserMessage(
    anthropic.NewDocumentBlock(anthropic.Base64PDFSourceParam{Data: b64}),
    anthropic.NewTextBlock("Summarize this document"),
)
```其他来源：`URLPDFSourceParam{URL: "https://..."}`、`PlainTextSourceParam{Data: "..."}`。

---

## 文件 API（测试版）

下 `client.Beta.Files`。方法是**`Upload`**（不是`New`/`Create`），参数结构是`BetaFileUploadParams`。 `File` 字段采用 `io.Reader`；使用 `anthropic.File()` 附加文件名 + 内容类型以进行多部分编码。```go
f, _ := os.Open("./upload_me.txt")
defer f.Close()

meta, err := client.Beta.Files.Upload(ctx, anthropic.BetaFileUploadParams{
    File:  anthropic.File(f, "upload_me.txt", "text/plain"),
    Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaFilesAPI2025_04_14},
})
// meta.ID is the file_id to reference in subsequent message requests
```其他 `Beta.Files` 方法：`List`、`Delete`、`Download`、`GetMetadata`。

---

## 上下文编辑/压缩（测试版）

将 `Beta.Messages.New` 与 `BetaMessageNewParams` 上的 `ContextManagement` 一起使用。没有 `NewBetaAssistantMessage` — 使用 `.ToParam()` 进行往返。```go
params := anthropic.BetaMessageNewParams{
    Model:     anthropic.ModelClaudeOpus4_6,  // also supported: ModelClaudeSonnet4_6
    MaxTokens: 16000,
    Betas:     []anthropic.AnthropicBeta{"compact-2026-01-12"},
    ContextManagement: anthropic.BetaContextManagementConfigParam{
        Edits: []anthropic.BetaContextManagementConfigEditUnionParam{
            {OfCompact20260112: &anthropic.BetaCompact20260112EditParam{}},
        },
    },
    Messages: []anthropic.BetaMessageParam{ /* ... */ },
}

resp, err := client.Beta.Messages.New(ctx, params)
if err != nil {
    log.Fatal(err)
}

// Round-trip: append response to history via .ToParam()
params.Messages = append(params.Messages, resp.ToParam())

// Read compaction blocks from the response
for _, block := range resp.Content {
    if c, ok := block.AsAny().(anthropic.BetaCompactionBlock); ok {
        fmt.Println("compaction summary:", c.Content)
    }
}
```其他编辑类型：`BetaClearToolUses20250919EditParam`、`BetaClearThinking20251015EditParam`。
</doc>

<doc path="java/claude-api.md">
# 克劳德 API — Java

> **注意：** Java SDK 支持 Claude API 和 beta 工具与带注释的类一起使用。代理 SDK 尚不可用于 Java。

## 安装

行家：```xml
<dependency>
    <groupId>com.anthropic</groupId>
    <artifactId>anthropic-java</artifactId>
    <version>2.34.0</version>
</dependency>
```摇篮：```groovy
implementation("com.anthropic:anthropic-java:2.34.0")
```## 客户端初始化```java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;

// Default (reads ANTHROPIC_API_KEY from environment)
AnthropicClient client = AnthropicOkHttpClient.fromEnv();

// Explicit API key
AnthropicClient client = AnthropicOkHttpClient.builder()
    .apiKey("your-api-key")
    .build();
```---

## 基本消息请求```java
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.Model;

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(16000L)
    .addUserMessage("What is the capital of France?")
    .build();

Message response = client.messages().create(params);
response.content().stream()
    .flatMap(block -> block.text().stream())
    .forEach(textBlock -> System.out.println(textBlock.text()));
```---

## 流媒体```java
import com.anthropic.core.http.StreamResponse;
import com.anthropic.models.messages.RawMessageStreamEvent;

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(64000L)
    .addUserMessage("Write a haiku")
    .build();

try (StreamResponse<RawMessageStreamEvent> streamResponse = client.messages().createStreaming(params)) {
    streamResponse.stream()
        .flatMap(event -> event.contentBlockDelta().stream())
        .flatMap(deltaEvent -> deltaEvent.delta().text().stream())
        .forEach(textDelta -> System.out.print(textDelta.text()));
}
```---

## 思考

**自适应思维是 Claude 4.6+ 模型的推荐模式。** Claude 动态决定思考的时间和程度。构建器具有直接 `.thinking(ThinkingConfigAdaptive)` 过载 - 无需手动联合包装。```java
import com.anthropic.models.messages.ContentBlock;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;
import com.anthropic.models.messages.ThinkingConfigAdaptive;

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_SONNET_4_6)
    .maxTokens(16000L)
    .thinking(ThinkingConfigAdaptive.builder().build())
    .addUserMessage("Solve this step by step: 27 * 453")
    .build();

for (ContentBlock block : client.messages().create(params).content()) {
    block.thinking().ifPresent(t -> System.out.println("[thinking] " + t.thinking()));
    block.text().ifPresent(t -> System.out.println(t.text()));
}
```> **已弃用：** `ThinkingConfigEnabled.builder().budgetTokens(N)`（以及 `.enabledThinking(N)` 快捷方式）仍然适用于 Claude 4.6，但已弃用。使用上面的适应性思维。

`ContentBlock` 缩小：`.thinking()` / `.text()` 返回 `Optional<T>` — 使用 `.ifPresent(...)` 或 `.stream().flatMap(...)`。替代方案：`isThinking()` / `asThinking()` 布尔+展开对（抛出错误的变体）。

---

## 工具使用（测试版）

Java SDK 支持测试版工具与带注释的类一起使用。工具类实现 `Supplier<String>`，以便通过 `BetaToolRunner` 自动执行。

### Tool Runner（自动循环）```java
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.BetaMessage;
import com.anthropic.helpers.BetaToolRunner;
import com.fasterxml.jackson.annotation.JsonClassDescription;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import java.util.function.Supplier;

@JsonClassDescription("Get the weather in a given location")
static class GetWeather implements Supplier<String> {
    @JsonPropertyDescription("The city and state, e.g. San Francisco, CA")
    public String location;

    @Override
    public String get() {
        return "The weather in " + location + " is sunny and 72°F";
    }
}

BetaToolRunner toolRunner = client.beta().messages().toolRunner(
    MessageCreateParams.builder()
        .model("claude-opus-4-8")
        .maxTokens(16000L)
        .putAdditionalHeader("anthropic-beta", "structured-outputs-2025-11-13")
        .addTool(GetWeather.class)
        .addUserMessage("What's the weather in San Francisco?")
        .build());

for (BetaMessage message : toolRunner) {
    System.out.println(message);
}
```### 记忆工具

Java SDK 提供 `BetaMemoryToolHandler` 用于实现内存工具后端。您提供一个管理文件存储的处理程序，`BetaToolRunner` 自动处理内存工具调用。```java
import com.anthropic.helpers.BetaMemoryToolHandler;
import com.anthropic.helpers.BetaToolRunner;
import com.anthropic.models.beta.messages.BetaMemoryTool20250818;
import com.anthropic.models.beta.messages.BetaMessage;
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.ToolRunnerCreateParams;

// Implement BetaMemoryToolHandler with your storage backend (e.g., filesystem)
BetaMemoryToolHandler memoryHandler = new FileSystemMemoryToolHandler(sandboxRoot);

MessageCreateParams createParams = MessageCreateParams.builder()
    .model("claude-opus-4-8")
    .maxTokens(4096L)
    .addTool(BetaMemoryTool20250818.builder().build())
    .addUserMessage("Remember that my favorite color is blue")
    .build();

BetaToolRunner toolRunner = client.beta().messages().toolRunner(
    ToolRunnerCreateParams.builder()
        .betaMemoryToolHandler(memoryHandler)
        .initialMessageParams(createParams)
        .build());

for (BetaMessage message : toolRunner) {
    System.out.println(message);
}
```有关内存工具的更多详细信息，请参阅[共享内存工具概念](../shared/tool-use-concepts.md)。

### 非 Beta 工具声明（手动 JSON 架构）

`Tool.InputSchema.Properties` 是一个自由格式的 `Map<String, JsonValue>` 包装器 - 通过 `putAdditionalProperty` 构建属性模式。 `type: "object"` 是默认值。构建器有一个直接的 `.addTool(Tool)` 重载，它会自动包装在 `ToolUnion` 中。```java
import com.anthropic.core.JsonValue;
import com.anthropic.models.messages.Tool;

Tool tool = Tool.builder()
    .name("get_weather")
    .description("Get the current weather in a given location")
    .inputSchema(Tool.InputSchema.builder()
        .properties(Tool.InputSchema.Properties.builder()
            .putAdditionalProperty("location", JsonValue.from(Map.of("type", "string")))
            .build())
        .required(List.of("location"))
        .build())
    .build();

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_SONNET_4_6)
    .maxTokens(16000L)
    .addTool(tool)
    .addUserMessage("Weather in Paris?")
    .build();
```对于手动工具循环，处理响应中的 `tool_use` 块，发送回 `tool_result`，循环直至 `stop_reason` 为 `"end_turn"`。请参阅[共享工具使用概念](../shared/tool-use-concepts.md)。

### 使用内容块构建 `MessageParam`（工具结果往返）

`MessageParam.Content` 是内部联合类（字符串 | 列表）。使用构建器的 `.contentOfBlockParams(List<ContentBlockParam>)` 别名 - 没有具有静态 `ofBlockParams` 的单独 `MessageParamContent` 类：```java
import com.anthropic.models.messages.MessageParam;
import com.anthropic.models.messages.ContentBlockParam;
import com.anthropic.models.messages.ToolResultBlockParam;

List<ContentBlockParam> results = List.of(
    ContentBlockParam.ofToolResult(ToolResultBlockParam.builder()
        .toolUseId(toolUseBlock.id())
        .content(yourResultString)
        .build())
);

MessageParam toolResultMsg = MessageParam.builder()
    .role(MessageParam.Role.USER)
    .contentOfBlockParams(results)   // builder alias for Content.ofBlockParams(...)
    .build();
```---

## 努力参数

努力嵌套在 `OutputConfig` 内部 - `MessageCreateParams.Builder` 上没有直接的 `.effort()`。```java
import com.anthropic.models.messages.OutputConfig;

.outputConfig(OutputConfig.builder()
    .effort(OutputConfig.Effort.HIGH)  // or LOW, MEDIUM, MAX
    .build())
```与 `Thinking = ThinkingConfigAdaptive` 结合用于成本质量控制。

---

## 提示缓存

系统消息为 `TextBlockParam` 和 `CacheControlEphemeral` 的列表。使用 `.systemOfTextBlockParams(...)` — 普通的 `.system(String)` 重载无法进行缓存控制。有关放置模式和静默无效器审核清单，请参阅 `shared/prompt-caching.md`。```java
import com.anthropic.models.messages.TextBlockParam;
import com.anthropic.models.messages.CacheControlEphemeral;

.systemOfTextBlockParams(List.of(
    TextBlockParam.builder()
        .text(longSystemPrompt)
        .cacheControl(CacheControlEphemeral.builder()
            .ttl(CacheControlEphemeral.Ttl.TTL_1H)  // optional; also TTL_5M
            .build())
        .build()))
````MessageCreateParams.Builder` 和 `Tool.builder()` 上还有顶级 `.cacheControl(CacheControlEphemeral)`。

通过 `response.usage().cacheCreationInputTokens()` / `response.usage().cacheReadInputTokens()` 验证命中。

---

## 令牌计数```java
import com.anthropic.models.messages.MessageCountTokensParams;

long tokens = client.messages().countTokens(
    MessageCountTokensParams.builder()
        .model(Model.CLAUDE_SONNET_4_6)
        .addUserMessage("Hello")
        .build()
).inputTokens();
```---

## 结构化输出

基于类的重载会从 POJO 自动派生 JSON 模式，并为您提供类型化的 `.text()` 返回 - 无需手动模式，无需手动解析。```java
import com.anthropic.models.messages.StructuredMessageCreateParams;

record Book(String title, String author) {}
record BookList(List<Book> books) {}

StructuredMessageCreateParams<BookList> params = MessageCreateParams.builder()
    .model(Model.CLAUDE_SONNET_4_6)
    .maxTokens(16000L)
    .outputConfig(BookList.class)  // returns a typed builder
    .addUserMessage("List 3 classic novels")
    .build();

client.messages().create(params).content().stream()
    .flatMap(cb -> cb.text().stream())
    .forEach(typed -> {
        // typed.text() returns BookList, not String
        for (Book b : typed.text().books()) System.out.println(b.title());
    });
```支持 Jackson 注释：`@JsonPropertyDescription`、`@JsonIgnore`、`@ArraySchema(minItems=...)`。手册架构路径：`OutputConfig.builder().format(JsonOutputFormat.builder().schema(...).build())`。

---

## PDF/文档输入

`DocumentBlockParam` 构建器具有源快捷方式。包裹`ContentBlockParam.ofDocument()`并通过`.addUserMessageOfBlockParams()`。```java
import com.anthropic.models.messages.DocumentBlockParam;
import com.anthropic.models.messages.ContentBlockParam;
import com.anthropic.models.messages.TextBlockParam;

DocumentBlockParam doc = DocumentBlockParam.builder()
    .base64Source(base64String)  // or .urlSource("https://...") or .textSource("...")
    .title("My Document")        // optional
    .build();

.addUserMessageOfBlockParams(List.of(
    ContentBlockParam.ofDocument(doc),
    ContentBlockParam.ofText(TextBlockParam.builder().text("Summarize this").build())))
```---

## 服务器端工具

版本后缀类型； `name`/`type` 由构建器自动设置。每种类型都存在直接 `.addTool()` 重载 — 无需手动 `ToolUnion` 包装。```java
import com.anthropic.models.messages.WebSearchTool20260209;
import com.anthropic.models.messages.ToolBash20250124;
import com.anthropic.models.messages.ToolTextEditor20250728;
import com.anthropic.models.messages.CodeExecutionTool20260120;

.addTool(WebSearchTool20260209.builder()
    .maxUses(5L)                              // optional
    .allowedDomains(List.of("example.com"))   // optional
    .build())
.addTool(ToolBash20250124.builder().build())
.addTool(ToolTextEditor20250728.builder().build())
.addTool(CodeExecutionTool20260120.builder().build())
```另提供：`WebFetchTool20260209`、`MemoryTool20250818`、`ToolSearchToolBm25_20251119`。对于顾问工具，请在 beta 命名空间中使用 `BetaAdvisorTool20260301`。

### Beta 命名空间（MCP，压缩）

对于仅限测试版的功能，请使用 `com.anthropic.models.beta.messages.*` — 类名具有 `Beta` 前缀并存在于测试版包中。 beta `MessageCreateParams.Builder` 具有直接 `.addTool(BetaToolBash20250124)` 重载和 `.addMcpServer()`：```java
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.BetaToolBash20250124;
import com.anthropic.models.beta.messages.BetaCodeExecutionTool20260120;
import com.anthropic.models.beta.messages.BetaRequestMcpServerUrlDefinition;

MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(16000L)
    .addBeta("mcp-client-2025-11-20")
    .addTool(BetaToolBash20250124.builder().build())
    .addTool(BetaCodeExecutionTool20260120.builder().build())
    .addMcpServer(BetaRequestMcpServerUrlDefinition.builder()
        .name("my-server")
        .url("https://example.com/mcp")
        .build())
    .addUserMessage("...")
    .build();

client.beta().messages().create(params);
````BetaTool*` 类型不可与非 beta `Tool*` 互换 — 每个请求选择一个命名空间。

**读取响应中的服务器工具块：** `ServerToolUseBlock` 具有 `.id()`、`.name()`（枚举）和 `._input()` 返回原始 `JsonValue` — 没有键入`.input()`。对于代码执行结果，展开两个级别：```java
for (ContentBlock block : response.content()) {
    block.serverToolUse().ifPresent(stu -> {
        System.out.println("tool: " + stu.name() + " input: " + stu._input());
    });
    block.codeExecutionToolResult().ifPresent(r -> {
        r.content().resultBlock().ifPresent(result -> {
            System.out.println("stdout: " + result.stdout());
            System.out.println("stderr: " + result.stderr());
            System.out.println("exit: " + result.returnCode());
        });
    });
}
```---

## 停靠点详细信息

当 `stopReason()` 为 `"refusal"` 时，响应包括结构化 `stopDetails()`：```java
response.stopDetails().ifPresent(details -> {
    System.out.println("Category: " + details.category());
    System.out.println("Explanation: " + details.explanation());
});
```---

## 错误类型

`AnthropicServiceException` 公开 `.errorType()` 返回 `Optional<ErrorType>` 进行编程错误分类：```java
try {
    client.messages().create(params);
} catch (AnthropicServiceException e) {
    e.errorType().ifPresent(type ->
        System.out.println("Error type: " + type)  // RATE_LIMIT_ERROR, OVERLOADED_ERROR, etc.
    );
}
```---

## 文件 API（测试版）

下 `client.beta().files()`。消息中的文件引用需要测试版消息类型（非测试版 `DocumentBlockParam.Source` 没有文件 ID 变体）。```java
import com.anthropic.models.beta.files.FileUploadParams;
import com.anthropic.models.beta.files.FileMetadata;
import com.anthropic.models.beta.messages.BetaRequestDocumentBlock;
import java.nio.file.Paths;

FileMetadata meta = client.beta().files().upload(
    FileUploadParams.builder()
        .file(Paths.get("/path/to/doc.pdf"))  // or .file(InputStream) or .file(byte[])
        .build());

// Reference in a beta message:
BetaRequestDocumentBlock doc = BetaRequestDocumentBlock.builder()
    .fileSource(meta.id())
    .build();
```其他方法：`.list()`、`.delete(String fileId)`、`.download(String fileId)`、`.retrieveMetadata(String fileId)`。
</doc>

<doc path="php/claude-api.md">
# 克劳德 API — PHP

> **注意：** PHP SDK 是 PHP 的官方 Anthropic SDK。 Beta 工具运行程序可通过 `$client->beta->messages->toolRunner()` 获取。通过 `StructuredOutputModel` 类支持结构化输出助手。代理 SDK 不可用。支持 Bedrock、Vertex AI 和 Foundry 客户端。

＃＃ 安装```bash
composer require "anthropic-ai/sdk"
```## 客户端初始化```php
use Anthropic\Client;

// Using API key from environment variable
$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));
```### 亚马逊基岩```php
use Anthropic\Bedrock;

// Constructor is private — use the static factory. Reads AWS credentials from env.
$client = Bedrock\Client::fromEnvironment(region: 'us-east-1');
```### 谷歌顶点人工智能```php
use Anthropic\Vertex;

// Constructor is private. Parameter is `location`, not `region`.
$client = Vertex\Client::fromEnvironment(
    location: 'us-east5',
    projectId: 'my-project-id',
);
```### 人类铸造厂```php
use Anthropic\Foundry;

// Constructor is private. baseUrl or resource is required.
$client = Foundry\Client::withCredentials(
    authToken: getenv('ANTHROPIC_FOUNDRY_AUTH_TOKEN'),
    baseUrl: 'https://<resource>.services.ai.azure.com/anthropic',
);
```---

## 基本消息请求```php
$message = $client->messages->create(
    model: 'claude-opus-4-8',
    maxTokens: 16000,
    messages: [
        ['role' => 'user', 'content' => 'What is the capital of France?'],
    ],
);

// content is an array of polymorphic blocks (TextBlock, ToolUseBlock,
// ThinkingBlock). Accessing ->text on content[0] without checking the block
// type will throw if the first block is not a TextBlock (e.g., when extended
// thinking is enabled and a ThinkingBlock comes first). Always guard:
foreach ($message->content as $block) {
    if ($block->type === 'text') {
        echo $block->text;
    }
}
```如果您只想要第一个文本块：```php
foreach ($message->content as $block) {
    if ($block->type === 'text') {
        echo $block->text;
        break;
    }
}
```---

## 流媒体

> **需要 SDK v0.5.0+。** v0.4.0 及更早版本使用单个 `$params` 阵列；使用命名参数调用会抛出 `Unknown named parameter $model`。升级：`composer require "anthropic-ai/sdk:^0.7"````php
use Anthropic\Messages\RawContentBlockDeltaEvent;
use Anthropic\Messages\TextDelta;

$stream = $client->messages->createStream(
    model: 'claude-opus-4-8',
    maxTokens: 64000,
    messages: [
        ['role' => 'user', 'content' => 'Write a haiku'],
    ],
);

foreach ($stream as $event) {
    if ($event instanceof RawContentBlockDeltaEvent && $event->delta instanceof TextDelta) {
        echo $event->delta->text;
    }
}
```---

## 工具使用

### 工具运行程序（测试版）

**测试版：** PHP SDK 通过 `$client->beta->messages->toolRunner()` 提供工具运行程序。使用 `BetaRunnableTool` 定义工具 — 定义数组加上 `run` 闭包：```php
use Anthropic\Lib\Tools\BetaRunnableTool;

$weatherTool = new BetaRunnableTool(
    definition: [
        'name' => 'get_weather',
        'description' => 'Get the current weather for a location.',
        'input_schema' => [
            'type' => 'object',
            'properties' => [
                'location' => ['type' => 'string', 'description' => 'City and state'],
            ],
            'required' => ['location'],
        ],
    ],
    run: function (array $input): string {
        return "The weather in {$input['location']} is sunny and 72°F.";
    },
);

$runner = $client->beta->messages->toolRunner(
    maxTokens: 16000,
    messages: [['role' => 'user', 'content' => 'What is the weather in Paris?']],
    model: 'claude-opus-4-8',
    tools: [$weatherTool],
);

foreach ($runner as $message) {
    foreach ($message->content as $block) {
        if ($block->type === 'text') {
            echo $block->text;
        }
    }
}
```### 手动循环

Tools are passed as arrays. **SDK 使用驼峰式键**（`inputSchema`、`toolUseID`、`stopReason`）并自动映射到 API snake_case 上线 — 自 v0.5.0 起。有关循环模式，请参阅[共享工具使用概念](../shared/tool-use-concepts.md)。```php
use Anthropic\Messages\ToolUseBlock;

$tools = [
    [
        'name' => 'get_weather',
        'description' => 'Get the current weather in a given location',
        'inputSchema' => [  // camelCase, not input_schema
            'type' => 'object',
            'properties' => [
                'location' => ['type' => 'string', 'description' => 'City and state'],
            ],
            'required' => ['location'],
        ],
    ],
];

$messages = [['role' => 'user', 'content' => 'What is the weather in SF?']];

$response = $client->messages->create(
    model: 'claude-opus-4-8',
    maxTokens: 16000,
    tools: $tools,
    messages: $messages,
);

while ($response->stopReason === 'tool_use') {  // camelCase property
    $toolResults = [];
    foreach ($response->content as $block) {
        if ($block instanceof ToolUseBlock) {
            // $block->name  : string               — tool name to dispatch on
            // $block->input : array<string,mixed>  — parsed JSON input
            // $block->id    : string               — pass back as toolUseID
            $result = executeYourTool($block->name, $block->input);
            $toolResults[] = [
                'type' => 'tool_result',
                'toolUseID' => $block->id,  // camelCase, not tool_use_id
                'content' => $result,
            ];
        }
    }

    // Append assistant turn + user turn with tool results
    $messages[] = ['role' => 'assistant', 'content' => $response->content];
    $messages[] = ['role' => 'user', 'content' => $toolResults];

    $response = $client->messages->create(
        model: 'claude-opus-4-8',
        maxTokens: 16000,
        tools: $tools,
        messages: $messages,
    );
}

// Final text response
foreach ($response->content as $block) {
    if ($block->type === 'text') {
        echo $block->text;
    }
}
````$block->type === 'tool_use'` 也可以工作； `instanceof ToolUseBlock` 缩小为 PHPStan。


---

## 延伸思考

**自适应思维是 Claude 4.6+ 模型的推荐模式。** Claude 动态决定思考的时间和程度。```php
use Anthropic\Messages\ThinkingBlock;

$message = $client->messages->create(
    model: 'claude-opus-4-8',
    maxTokens: 16000,
    thinking: ['type' => 'adaptive'],
    messages: [
        ['role' => 'user', 'content' => 'Solve: 27 * 453'],
    ],
);

// ThinkingBlock(s) precede TextBlock in content
foreach ($message->content as $block) {
    if ($block instanceof ThinkingBlock) {
        echo "Thinking:\n{$block->thinking}\n\n";
        // $block->signature is an opaque string — preserve verbatim if
        // passing thinking blocks back in multi-turn conversations
    } elseif ($block->type === 'text') {
        echo "Answer: {$block->text}\n";
    }
}
```> **已弃用：** `['type' => 'enabled', 'budgetTokens' => N]`（固定预算扩展思维）仍然适用于 Claude 4.6，但已弃用。使用上面的适应性思维。

`$block->type === 'thinking'` 也适用于检查； `instanceof` 缩小为 PHPStan。

---

## 提示缓存

`system:` 采用文本块数组；在最后一个块上设置 `cacheControl`。数组形状语法（驼峰命名法键）是惯用的。有关放置模式和静默无效器审核清单，请参阅 `shared/prompt-caching.md`。```php
$message = $client->messages->create(
    model: 'claude-opus-4-8',
    maxTokens: 16000,
    system: [
        ['type' => 'text', 'text' => $longSystemPrompt, 'cacheControl' => ['type' => 'ephemeral']],
    ],
    messages: [['role' => 'user', 'content' => 'Summarize the key points']],
);
```对于 1 小时 TTL：`'cacheControl' => ['type' => 'ephemeral', 'ttl' => '1h']`。 There's also a top-level `cacheControl:` on `messages->create(...)` that auto-places on the last cacheable block.

通过 `$message->usage->cacheCreationInputTokens` / `$message->usage->cacheReadInputTokens` 验证命中。

---

## 结构化输出

### 使用 StructuredOutputModel（推荐）

定义一个实现 `StructuredOutputModel` 的 PHP 类并将其作为 `outputConfig` 传递：```php
use Anthropic\Lib\Contracts\StructuredOutputModel;
use Anthropic\Lib\Concerns\StructuredOutputModelTrait;
use Anthropic\Lib\Attributes\Constrained;

class Person implements StructuredOutputModel
{
    use StructuredOutputModelTrait;

    #[Constrained(description: 'Full name')]
    public string $name;

    public int $age;

    public ?string $email = null;  // nullable = optional field
}

$message = $client->messages->create(
    model: 'claude-opus-4-8',
    maxTokens: 16000,
    messages: [['role' => 'user', 'content' => 'Generate a profile for Alice, age 30']],
    outputConfig: ['format' => Person::class],
);

$person = $message->parsedOutput();  // Person instance
echo $person->name;
```类型是根据 PHP 类型提示推断的。使用 `#[Constrained(description: '...')]` 添加描述。可空属性 (`?string`) 成为可选字段。

### 原始模式```php
$message = $client->messages->create(
    model: 'claude-opus-4-8',
    maxTokens: 16000,
    messages: [['role' => 'user', 'content' => 'Extract: John (john@co.com), Enterprise plan']],
    outputConfig: [
        'format' => [
            'type' => 'json_schema',
            'schema' => [
                'type' => 'object',
                'properties' => [
                    'name' => ['type' => 'string'],
                    'email' => ['type' => 'string'],
                    'plan' => ['type' => 'string'],
                ],
                'required' => ['name', 'email', 'plan'],
                'additionalProperties' => false,
            ],
        ],
    ],
);

// First text block contains valid JSON
foreach ($message->content as $block) {
    if ($block->type === 'text') {
        $data = json_decode($block->text, true);
        break;
    }
}
```---

## Beta 功能和服务器端工具

**`betas:` 不是 `$client->messages->create()` 上的参数** — 它仅存在于 beta 命名空间中。将其用于需要显式选择加入标头的功能：```php
use Anthropic\Beta\Messages\BetaRequestMCPServerURLDefinition;

$response = $client->beta->messages->create(
    model: 'claude-opus-4-8',
    maxTokens: 16000,
    mcpServers: [
        BetaRequestMCPServerURLDefinition::with(
            name: 'my-server',
            url: 'https://example.com/mcp',
        ),
    ],
    betas: ['mcp-client-2025-11-20'],  // only valid on ->beta->messages
    messages: [['role' => 'user', 'content' => 'Use the MCP tools']],
);
```**服务器端工具**（bash、web_search、text_editor、code_execution）是 GA 并且在两条路径上工作 - `Anthropic\Messages\ToolBash20250124` / `WebSearchTool20260209` / `ToolTextEditor20250728` / `CodeExecutionTool20260120` 对于非测试版，`Anthropic\Beta\Messages\BetaToolBash20250124` / `BetaWebSearchTool20260209` / `BetaToolTextEditor20250728` / `BetaCodeExecutionTool20260120` 测试版。这些不需要 `betas:` 标头。

---

## 停靠点详细信息

当 `stopReason` 为 `'refusal'` 时，响应包含结构化 `stopDetails`：```php
if ($message->stopReason === 'refusal' && $message->stopDetails !== null) {
    echo "Category: " . $message->stopDetails->category . "\n";     // "cyber" | "bio" | null
    echo "Explanation: " . $message->stopDetails->explanation . "\n";
}
```---

## 错误类型

`APIStatusException` 公开用于编程错误分类的 `->type` 属性：```php
try {
    $client->messages->create(...);
} catch (\Anthropic\Core\Exceptions\APIStatusException $e) {
    echo $e->type?->value;  // "rate_limit_error", "overloaded_error", etc.
}
```</doc>

<doc path="python/claude-api/README.md">
# 克劳德 API — Python

## 安装```bash
pip install anthropic
```## 客户端初始化```python
import anthropic

# Default — resolves credentials from the environment:
# ANTHROPIC_API_KEY, or ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile.
# Prefer this for local dev; don't hardcode a key.
client = anthropic.Anthropic()

# Explicit API key (only when you must inject a specific key)
client = anthropic.Anthropic(api_key="your-api-key")

# Async client
async_client = anthropic.AsyncAnthropic()
```---

## 客户端配置

### 每个请求覆盖

使用 `with_options()` 覆盖单个调用的客户端设置，而不改变客户端：```python
client.with_options(timeout=5.0, max_retries=5).messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```### 超时

默认请求超时为 10 分钟。传递浮点数（秒）或 `httpx.Timeout` 进行精细控制。超时时，SDK 引发 `anthropic.APITimeoutError`（并根据 `max_retries` 重试）。```python
import httpx

client = anthropic.Anthropic(timeout=20.0)
client = anthropic.Anthropic(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)
```### 重试

The SDK auto-retries connection errors, 408, 409, 429, and ≥500 with exponential backoff (default 2 retries).在客户端或通过`with_options()`设置`max_retries`； `max_retries=0` 禁用。

### 异步性能（aiohttp 后端）

对于高并发异步工作负载，请安装 `anthropic[aiohttp]` 并传递 `DefaultAioHttpClient` 而不是默认的 httpx 后端：```python
from anthropic import AsyncAnthropic, DefaultAioHttpClient

async with AsyncAnthropic(http_client=DefaultAioHttpClient()) as client:
    ...
```### 自定义 HTTP 客户端（代理、基础 URL）

使用 `DefaultHttpxClient` / `DefaultAsyncHttpxClient` — 不是原始 `httpx.Client` — 因此保留 SDK 的默认超时和连接限制：```python
from anthropic import Anthropic, DefaultHttpxClient

client = Anthropic(
    base_url="http://my.test.server.example.com:8083",  # or ANTHROPIC_BASE_URL env var
    http_client=DefaultHttpxClient(proxy="http://my.test.proxy.example.com"),
)
```### 日志记录

设置 `ANTHROPIC_LOG=debug`（或 `info`）以通过标准 `logging` 模块启用 SDK 日志记录。

---

## 基本消息请求```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
# response.content is a list of content block objects (TextBlock, ThinkingBlock,
# ToolUseBlock, ...). Check .type before accessing .text.
for block in response.content:
    if block.type == "text":
        print(block.text)
```---

## 系统提示```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    system="You are a helpful coding assistant. Always provide examples in Python.",
    messages=[{"role": "user", "content": "How do I read a JSON file?"}]
)
```### 对话中系统消息（测试版，模型门控）

对于在对话中到达的操作员指令（模式切换、注入状态），请将 `{"role": "system", ...}` 附加到 `messages`，而不是编辑顶级 `system` — 这会保留缓存的前缀并携带操作员权限。必须遵循用户消息；不能是 `messages[0]`。不受支持的型号返回 400 (`role 'system' is not supported on this model`)。请参阅 `shared/prompt-caching.md` 了解何时使用此与顶级 `system`。```python
response = client.messages.create(
    model=MODEL_ID,  # must support mid-conversation system messages
    max_tokens=16000,
    system=[{"type": "text", "text": STABLE_SYSTEM, "cache_control": {"type": "ephemeral"}}],
    messages=history + [
        {"role": "user", "content": user_message},
        {"role": "system", "content": "Terse mode enabled — keep responses under 40 words."},
    ],
    extra_headers={"anthropic-beta": "mid-conversation-system-2026-04-07"},
)
```---

## 愿景（图像）

### Base64```python
import base64

with open("image.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data
                }
            },
            {"type": "text", "text": "What's in this image?"}
        ]
    }]
)
```### URL```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": "https://example.com/image.png"
                }
            },
            {"type": "text", "text": "Describe this image"}
        ]
    }]
)
```---

## 提示缓存

Cache large context to reduce costs (up to 90% savings). **缓存是前缀匹配** - 前缀中任何位置的任何字节更改都会使其后面的所有内容无效。有关放置模式、架构指南（冻结系统提示、确定性工具顺序、put 易失性内容的位置）和静默无效器审核清单，请阅读 `shared/prompt-caching.md`。

### 自动缓存（推荐）

使用顶级 `cache_control` 自动缓存请求中的最后一个可缓存块 - 无需注释各个内容块：```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    cache_control={"type": "ephemeral"},  # auto-caches the last cacheable block
    system="You are an expert on this large document...",
    messages=[{"role": "user", "content": "Summarize the key points"}]
)
```### 手动缓存控制

为了进行细粒度控制，请将 `cache_control` 添加到特定内容块：```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    system=[{
        "type": "text",
        "text": "You are an expert on this large document...",
        "cache_control": {"type": "ephemeral"}  # default TTL is 5 minutes
    }],
    messages=[{"role": "user", "content": "Summarize the key points"}]
)

# With explicit TTL (time-to-live)
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    system=[{
        "type": "text",
        "text": "You are an expert on this large document...",
        "cache_control": {"type": "ephemeral", "ttl": "1h"}  # 1 hour TTL
    }],
    messages=[{"role": "user", "content": "Summarize the key points"}]
)
```### 验证缓存命中```python
print(response.usage.cache_creation_input_tokens)  # tokens written to cache (~1.25x cost)
print(response.usage.cache_read_input_tokens)      # tokens served from cache (~0.1x cost)
print(response.usage.input_tokens)                 # uncached tokens (full cost)
```如果 `cache_read_input_tokens` 在重复的相同前缀请求中为零，则说明静默无效器正在工作 - `datetime.now()` 或系统提示中的 UUID、未排序的 `json.dumps()` 或不同的工具集。有关完整审核表，请参阅 `shared/prompt-caching.md`。

---

## 延伸思考

> **Opus 4.8、Opus 4.7、Opus 4.6 和 Sonnet 4.6：** 使用适应性思维。 `budget_tokens` 在 Opus 4.8 和 4.7 上被删除（如果发送则为 400）；在 Opus 4.6 和 Sonnet 4.6 上已弃用。
> **旧型号：** 使用 `thinking: {type: "enabled", budget_tokens: N}`（必须 < `max_tokens`，最小 1024）。```python
# Opus 4.8 / 4.7 / 4.6: adaptive thinking (recommended)
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},  # low | medium | high | max
    messages=[{"role": "user", "content": "Solve this step by step..."}]
)

# Access thinking and response
for block in response.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Response: {block.text}")
```---

## 错误处理```python
import anthropic

try:
    response = client.messages.create(...)
except anthropic.BadRequestError as e:
    print(f"Bad request: {e.message}")
except anthropic.AuthenticationError:
    print("Invalid API key")
except anthropic.PermissionDeniedError:
    print("API key lacks required permissions")
except anthropic.NotFoundError:
    print("Invalid model or endpoint")
except anthropic.RateLimitError as e:
    retry_after = int(e.response.headers.get("retry-after", "60"))
    print(f"Rate limited. Retry after {retry_after}s.")
except anthropic.APIStatusError as e:
    if e.status_code >= 500:
        print(f"Server error ({e.status_code}). Retry later.")
    else:
        print(f"API error: {e.message}")
except anthropic.APIConnectionError:
    print("Network error. Check internet connection.")
```---

## Response Helpers

每个响应对象都会公开 `_request_id`（从 `request-id` 标头填充）——在向 Anthropic 报告故障时记录它。尽管有下划线前缀，但该属性是公共的。```python
message = client.messages.create(...)
print(message._request_id)       # req_018EeWyXxfu5pfWkrYcMdjWG
print(message.to_json())          # serialize the Pydantic model
print(message.to_dict())          # plain dict
```要访问原始标头或其他响应元数据，请使用 `.with_raw_response`：```python
raw = client.messages.with_raw_response.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(raw.headers.get("request-id"))
message = raw.parse()  # the Message object messages.create() would have returned
```---

## 多轮对话

API 是无状态的 — 每次发送完整的对话历史记录。```python
class ConversationManager:
    """Manage multi-turn conversations with the Claude API."""

    def __init__(self, client: anthropic.Anthropic, model: str, system: str = None):
        self.client = client
        self.model = model
        self.system = system
        self.messages = []

    def send(self, user_message: str, **kwargs) -> str:
        """Send a message and get a response."""
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 16000),
            system=self.system,
            messages=self.messages,
            **kwargs
        )

        assistant_message = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        self.messages.append({"role": "assistant", "content": assistant_message})

        return assistant_message

# Usage
conversation = ConversationManager(
    client=anthropic.Anthropic(),
    model="claude-opus-4-8",
    system="You are a helpful assistant."
)

response1 = conversation.send("My name is Alice.")
response2 = conversation.send("What's my name?")  # Claude remembers "Alice"
```**规则：**

- 允许连续的相同角色消息 - API 将它们组合成一个回合
- 第一条消息必须是 `user`
- 在支持模型的 `mid-conversation-system-2026-04-07` beta 下，允许在对话中发送 `role: "system"` 消息 — 请参阅上面的§对话中系统消息

---

### 压缩（长对话）

> **Beta、Opus 4.8、Opus 4.7、Opus 4.6 和 Sonnet 4.6。** 当对话接近 200K 上下文窗口时，压缩会自动总结服务器端较早的上下文。 API 返回 `compaction` 块；您必须在后续请求中将其传回 - 附加 `response.content`，而不仅仅是文本。```python
import anthropic

client = anthropic.Anthropic()
messages = []

def chat(user_message: str) -> str:
    messages.append({"role": "user", "content": user_message})

    response = client.beta.messages.create(
        betas=["compact-2026-01-12"],
        model="claude-opus-4-8",
        max_tokens=16000,
        messages=messages,
        context_management={
            "edits": [{"type": "compact_20260112"}]
        }
    )

    # Append full content — compaction blocks must be preserved
    messages.append({"role": "assistant", "content": response.content})

    return next(block.text for block in response.content if block.type == "text")

# Compaction triggers automatically when context grows large
print(chat("Help me build a Python web scraper"))
print(chat("Add support for JavaScript-rendered pages"))
print(chat("Now add rate limiting and error handling"))
```---

## 停止原因

响应中的 `stop_reason` 字段指示模型停止生成的原因：

|价值|意义|
|--------|---------|
| `end_turn` |克劳德很自然地完成了回应|
| `max_tokens` |达到 `max_tokens` 限制 — 增加限制或使用流式传输 |
| `stop_sequence` |按下自定义停止顺序 |
| `tool_use` |克劳德想要调用一个工具——执行它并继续 |
| `pause_turn` |模型已暂停并可以恢复（代理流）|
| `refusal` | Claude refused for safety reasons — check `stop_details` |

### 结构化止损详细信息

当 `stop_reason` 为 `"refusal"` 时，响应包括 `stop_details` 对象，其中包含有关拒绝的结构化信息：```python
if response.stop_reason == "refusal" and response.stop_details:
    print(f"Category: {response.stop_details.category}")   # "cyber" | "bio" | None
    print(f"Explanation: {response.stop_details.explanation}")
```---

## 成本优化策略

### 1. 对重复上下文使用提示缓存```python
# Automatic caching (simplest — caches the last cacheable block)
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    cache_control={"type": "ephemeral"},
    system=large_document_text,  # e.g., 50KB of context
    messages=[{"role": "user", "content": "Summarize the key points"}]
)

# First request: full cost
# Subsequent requests: ~90% cheaper for cached portion
```### 2. 选择正确的型号```python
# Default to Opus for most tasks
response = client.messages.create(
    model="claude-opus-4-8",  # $5.00/$25.00 per 1M tokens
    max_tokens=16000,
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)

# Use Sonnet for high-volume production workloads
standard_response = client.messages.create(
    model="claude-sonnet-4-6",  # $3.00/$15.00 per 1M tokens
    max_tokens=16000,
    messages=[{"role": "user", "content": "Summarize this document"}]
)

# Use Haiku only for simple, speed-critical tasks
simple_response = client.messages.create(
    model="claude-haiku-4-5",  # $1.00/$5.00 per 1M tokens
    max_tokens=256,
    messages=[{"role": "user", "content": "Classify this as positive or negative"}]
)
```### 3. 在请求之前使用令牌计数```python
count_response = client.messages.count_tokens(
    model="claude-opus-4-8",
    messages=messages,
    system=system
)

estimated_input_cost = count_response.input_tokens * 0.000005  # $5/1M tokens
print(f"Estimated input cost: ${estimated_input_cost:.4f}")
```---

## 使用指数退避重试

> **注意：** Anthropic SDK 使用指数退避自动重试速率限制 (429) 和服务器错误 (5xx)。您可以使用 `max_retries` 进行配置（默认值：2）。仅当您需要的行为超出 SDK 提供的范围时，才实施自定义重试逻辑。```python
import time
import random
import anthropic

def call_with_retry(
    client: anthropic.Anthropic,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    **kwargs
):
    """Call the API with exponential backoff retry."""
    last_exception = None

    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            last_exception = e
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                last_exception = e
            else:
                raise  # Client errors (4xx except 429) should not be retried

        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
        print(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s")
        time.sleep(delay)

    raise last_exception
```</doc>

<doc path="python/claude-api/batches.md">
# 消息批次 API — Python

批次 API (`POST /v1/messages/batches`) 以标准价格的 50% 异步处理消息 API 请求。

## 关键事实

- 每批最多 100,000 个请求或 256 MB
- 大多数批次在 1 小时内完成；最长24小时
- 结果在创建后 29 天内可用
- 所有代币使用成本降低 50%
- 支持所有消息 API 功能（视觉、工具、缓存等）

---

## 创建一个批次```python
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

client = anthropic.Anthropic()

message_batch = client.messages.batches.create(
    requests=[
        Request(
            custom_id="request-1",
            params=MessageCreateParamsNonStreaming(
                model="claude-opus-4-8",
                max_tokens=16000,
                messages=[{"role": "user", "content": "Summarize climate change impacts"}]
            )
        ),
        Request(
            custom_id="request-2",
            params=MessageCreateParamsNonStreaming(
                model="claude-opus-4-8",
                max_tokens=16000,
                messages=[{"role": "user", "content": "Explain quantum computing basics"}]
            )
        ),
    ]
)

print(f"Batch ID: {message_batch.id}")
print(f"Status: {message_batch.processing_status}")
```---

## 投票完成```python
import time

while True:
    batch = client.messages.batches.retrieve(message_batch.id)
    if batch.processing_status == "ended":
        break
    print(f"Status: {batch.processing_status}, processing: {batch.request_counts.processing}")
    time.sleep(60)

print("Batch complete!")
print(f"Succeeded: {batch.request_counts.succeeded}")
print(f"Errored: {batch.request_counts.errored}")
```---

## 检索结果

> **注意：** 下面的示例使用 `match/case` 语法，需要 Python 3.10+。对于早期版本，请改用 `if/elif` 链条。```python
for result in client.messages.batches.results(message_batch.id):
    match result.result.type:
        case "succeeded":
            msg = result.result.message
            text = next((b.text for b in msg.content if b.type == "text"), "")
            print(f"[{result.custom_id}] {text[:100]}")
        case "errored":
            if result.result.error.type == "invalid_request":
                print(f"[{result.custom_id}] Validation error - fix request and retry")
            else:
                print(f"[{result.custom_id}] Server error - safe to retry")
        case "canceled":
            print(f"[{result.custom_id}] Canceled")
        case "expired":
            print(f"[{result.custom_id}] Expired - resubmit")
```---

## 取消批次```python
cancelled = client.messages.batches.cancel(message_batch.id)
print(f"Status: {cancelled.processing_status}")  # "canceling"
```---

## 列出批次（自动分页）

迭代任何 `list()` 调用的返回值会在所有页面上自动分页 - 如果您想要完整的集合，请勿索引到 `.data`：```python
for batch in client.messages.batches.list(limit=20):
    print(batch.id, batch.processing_status)
```For manual control, use `first_page.has_next_page()` / `first_page.get_next_page()` / `first_page.next_page_info()`; `first_page.data` 保存当前页面的项目，`first_page.last_id` 是光标。

---

## 带有提示缓存的批处理```python
shared_system = [
    {"type": "text", "text": "You are a literary analyst."},
    {
        "type": "text",
        "text": large_document_text,  # Shared across all requests
        "cache_control": {"type": "ephemeral"}
    }
]

message_batch = client.messages.batches.create(
    requests=[
        Request(
            custom_id=f"analysis-{i}",
            params=MessageCreateParamsNonStreaming(
                model="claude-opus-4-8",
                max_tokens=16000,
                system=shared_system,
                messages=[{"role": "user", "content": question}]
            )
        )
        for i, question in enumerate(questions)
    ]
)
```---

## 完整的端到端示例```python
import anthropic
import time
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

client = anthropic.Anthropic()

# 1. Prepare requests
items_to_classify = [
    "The product quality is excellent!",
    "Terrible customer service, never again.",
    "It's okay, nothing special.",
]

requests = [
    Request(
        custom_id=f"classify-{i}",
        params=MessageCreateParamsNonStreaming(
            model="claude-haiku-4-5",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": f"Classify as positive/negative/neutral (one word): {text}"
            }]
        )
    )
    for i, text in enumerate(items_to_classify)
]

# 2. Create batch
batch = client.messages.batches.create(requests=requests)
print(f"Created batch: {batch.id}")

# 3. Wait for completion
while True:
    batch = client.messages.batches.retrieve(batch.id)
    if batch.processing_status == "ended":
        break
    time.sleep(10)

# 4. Collect results
results = {}
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        msg = result.result.message
        results[result.custom_id] = next((b.text for b in msg.content if b.type == "text"), "")

for custom_id, classification in sorted(results.items()):
    print(f"{custom_id}: {classification}")
```</doc>

<doc path="python/claude-api/files-api.md">
# 文件 API — Python

文件 API 上传文件以在消息 API 请求中使用。通过内容块中的 `file_id` 引用文件，避免跨多个 API 调用重新上传。

**测试版：** 在 API 调用中传递 `betas=["files-api-2025-04-14"]`（SDK 自动设置所需的标头）。

## 关键事实

- Maximum file size: 500 MB
- 总存储空间：每个组织 100 GB
- 文件持续存在直至被删除
- 文件操作（上传、列表、delete）免费；消息中使用的内容按输入令牌计费
- 不适用于 Amazon Bedrock 或 Google Vertex AI

---

## 上传文件

`file` 参数接受 `(filename, content, content_type)` 元组、`pathlib.Path`（或任何 `PathLike` — 为您读取、与 `AsyncAnthropic` 异步安全）或打开的二进制文件对象。```python
import anthropic
from pathlib import Path

client = anthropic.Anthropic()

uploaded = client.beta.files.upload(
    file=("report.pdf", open("report.pdf", "rb"), "application/pdf"),
)
# or: client.beta.files.upload(file=Path("report.pdf"))
print(f"File ID: {uploaded.id}")
print(f"Size: {uploaded.size_bytes} bytes")
```---

## 在消息中使用文件

### PDF/文本文档```python
response = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Summarize the key findings in this report."},
            {
                "type": "document",
                "source": {"type": "file", "file_id": uploaded.id},
                "title": "Q4 Report",           # optional
                "citations": {"enabled": True}   # optional, enables citations
            }
        ]
    }],
    betas=["files-api-2025-04-14"],
)
for block in response.content:
    if block.type == "text":
        print(block.text)
```＃＃＃ 图像```python
image_file = client.beta.files.upload(
    file=("photo.png", open("photo.png", "rb"), "image/png"),
)

response = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {
                "type": "image",
                "source": {"type": "file", "file_id": image_file.id}
            }
        ]
    }],
    betas=["files-api-2025-04-14"],
)
```---

## 管理文件

### 列出文件

直接迭代列表结果 - SDK 在所有页面上自动分页。如果您只需要首页，则仅使用 `.data`。```python
for f in client.beta.files.list():
    print(f"{f.id}: {f.filename} ({f.size_bytes} bytes)")
```### Get 文件元数据```python
file_info = client.beta.files.retrieve_metadata("file_011CNha8iCJcU1wXNR6q4V8w")
print(f"Filename: {file_info.filename}")
print(f"MIME type: {file_info.mime_type}")
```### Delete 一个文件```python
client.beta.files.delete("file_011CNha8iCJcU1wXNR6q4V8w")
```### 下载文件

只能下载由代码执行工具或技能创建的文件（不能下载用户上传的文件）。```python
file_content = client.beta.files.download("file_011CNha8iCJcU1wXNR6q4V8w")
file_content.write_to_file("output.txt")
```---

## 完整的端到端示例

上传文档一次，询问多个相关问题：```python
import anthropic

client = anthropic.Anthropic()

# 1. Upload once
uploaded = client.beta.files.upload(
    file=("contract.pdf", open("contract.pdf", "rb"), "application/pdf"),
)
print(f"Uploaded: {uploaded.id}")

# 2. Ask multiple questions using the same file_id
questions = [
    "What are the key terms and conditions?",
    "What is the termination clause?",
    "Summarize the payment schedule.",
]

for question in questions:
    response = client.beta.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "document",
                    "source": {"type": "file", "file_id": uploaded.id}
                }
            ]
        }],
        betas=["files-api-2025-04-14"],
    )
    print(f"\nQ: {question}")
    text = next((b.text for b in response.content if b.type == "text"), "")
    print(f"A: {text[:200]}")

# 3. Clean up when done
client.beta.files.delete(uploaded.id)
```</doc>

<doc path="python/claude-api/streaming.md">
# 流媒体 — Python

## 快速入门```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a story"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```### 异步```python
async with async_client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a story"}]
) as stream:
    async for text in stream.text_stream:
        print(text, end="", flush=True)
```### 低级：`stream=True`

`messages.stream()`（上图）是推荐的助手——它累积状态并公开 `text_stream` / `get_final_message()`。如果您只需要原始事件迭代器并希望降低内存使用量，请将 `stream=True` 传递给 `messages.create()`：```python
for event in client.messages.create(
    model="claude-opus-4-8",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a story"}],
    stream=True,
):
    print(event.type)
```这种形式不会为您完成最终消息的积累。

---

## 处理不同的内容类型

克劳德可能会返回文本、思维块或工具使用。妥善处理每一项：

> **Opus 4.8 / Opus 4.7 / Opus 4.6：** 使用 `thinking: {type: "adaptive"}`。在旧型号上，请改用 `thinking: {type: "enabled", budget_tokens: N}`。```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    messages=[{"role": "user", "content": "Analyze this problem"}]
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "thinking":
                print("\n[Thinking...]")
            elif event.content_block.type == "text":
                print("\n[Response:]")

        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
```---

## 使用工具进行流式传输

Python 工具运行程序当前返回完整消息。如果您需要使用工具进行每个令牌流式传输，请在手动循环中对各个 API 调用使用流式传输：```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=64000,
    tools=tools,
    messages=messages
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    response = stream.get_final_message()
    # Continue with tool execution if response.stop_reason == "tool_use"
```---

## 获取最终消息```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Hello"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # Get full message after streaming
    final_message = stream.get_final_message()
    print(f"\n\nTokens used: {final_message.usage.output_tokens}")
```---

## 带有进度更新的流媒体```python
def stream_with_progress(client, **kwargs):
    """Stream a response with progress updates."""
    total_tokens = 0
    content_parts = []

    with client.messages.stream(**kwargs) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    text = event.delta.text
                    content_parts.append(text)
                    print(text, end="", flush=True)

            elif event.type == "message_delta":
                if event.usage and event.usage.output_tokens is not None:
                    total_tokens = event.usage.output_tokens

        final_message = stream.get_final_message()

    print(f"\n\n[Tokens used: {total_tokens}]")
    return "".join(content_parts)
```---

## 流中的错误处理```python
try:
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=64000,
        messages=[{"role": "user", "content": "Write a story"}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
except anthropic.APIConnectionError:
    print("\nConnection lost. Please retry.")
except anthropic.RateLimitError:
    print("\nRate limited. Please wait and retry.")
except anthropic.APIStatusError as e:
    print(f"\nAPI error: {e.status_code}")
```---

## 流事件类型

|事件类型 |描述 |当它发生时 |
| -------------------- | ------------------------ | | --------------------------------- |
| `message_start` |包含消息元数据 |一次在开始 |
| `content_block_start` |新内容块开始 |当文本/tool_use 块开始时 |
| `content_block_delta` |增量内容更新 |对于每个令牌/块|
| `content_block_stop` |内容块完成 |当一个块完成时 |
| `message_delta` |消息级更新 |包含`stop_reason`，用法|
| `message_stop` |留言完毕 |一次在最后|

## 最佳实践

1. **始终刷新输出** — 使用 `flush=True` 立即显示令牌
2. **处理部分响应** — 如果流中断，您的内容可能不完整
3. **跟踪令牌使用情况** — `message_delta` 事件包含使用信息
4. **使用超时** — 为您的应用程序设置适当的超时
5. **默认流式传输** — 即使在流式传输时也使用 `.get_final_message()` 至 get 完整响应，为您提供超时保护，无需处理单个事件
6. **无流式传输的大型 `max_tokens` 会引发 `ValueError`** — SDK 拒绝非流式请求，预计将超过约 10 分钟（空闲连接下降）。通过 `stream=True` / 使用 `messages.stream()` 或显式覆盖 `timeout` 来抑制守卫。
</doc>

<doc path="python/claude-api/tool-use.md">
# 工具使用 — Python

有关概念概述（工具定义、工具选择、提示），请参阅 [shared/tool-use-concepts.md](../../shared/tool-use-concepts.md)。

## 工具运行程序（推荐）

**测试版：** Python SDK 中的工具运行程序处于测试版状态。

使用 `@beta_tool` 装饰器将工具定义为类型化函数，然后将它们传递给 `client.beta.messages.tool_runner()`：```python
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

@beta_tool
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get current weather for a location.

    Args:
        location: City and state, e.g., San Francisco, CA.
        unit: Temperature unit, either "celsius" or "fahrenheit".
    """
    # Your implementation here
    return f"72°F and sunny in {location}"

# The tool runner handles the agentic loop automatically
runner = client.beta.messages.tool_runner(
    model="claude-opus-4-8",
    max_tokens=16000,
    tools=[get_weather],
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
)

# Each iteration yields a BetaMessage; iteration stops when Claude is done
for message in runner:
    print(message)
```对于异步使用，请将 `@beta_async_tool` 与 `async def` 函数结合使用。

**工具运行程序的主要优点：**

- 无手动循环 — SDK 负责调用工具并反馈结果
- 通过装饰器进行类型安全的工具输入
- 工具模式是根据函数签名自动生成的
- 当 Claude 不再有工具调用时迭代会自动停止

---

## MCP 工具转换助手

**测试版。** 将 [MCP（模型上下文协议）](https://modelcontextprotocol.io/) 工具、提示和资源转换为 Anthropic API 类型，以便与工具运行程序一起使用。需要 `pip install anthropic[mcp]` (Python 3.10+)。

> **注意：** Claude API 还支持 `mcp_servers` 参数，该参数允许 Claude 直接连接到远程 MCP 服务器。当您需要本地 MCP 服务器、提示、资源或对 MCP 连接的更多控制时，请使用这些帮助程序。

### MCP 带工具运行器的工具```python
from anthropic import AsyncAnthropic
from anthropic.lib.tools.mcp import async_mcp_tool
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

client = AsyncAnthropic()

async with stdio_client(StdioServerParameters(command="mcp-server")) as (read, write):
    async with ClientSession(read, write) as mcp_client:
        await mcp_client.initialize()

        tools_result = await mcp_client.list_tools()
        # tool_runner is sync — returns the runner, not a coroutine
        runner = client.beta.messages.tool_runner(
            model="claude-opus-4-8",
            max_tokens=16000,
            messages=[{"role": "user", "content": "Use the available tools"}],
            tools=[async_mcp_tool(t, mcp_client) for t in tools_result.tools],
        )
        async for message in runner:
            print(message)
```对于同步使用，请使用 `mcp_tool` 而不是 `async_mcp_tool`。

### MCP 提示```python
from anthropic.lib.tools.mcp import mcp_message

prompt = await mcp_client.get_prompt(name="my-prompt")
response = await client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[mcp_message(m) for m in prompt.messages],
)
```### MCP 资源作为内容```python
from anthropic.lib.tools.mcp import mcp_resource_to_content

resource = await mcp_client.read_resource(uri="file:///path/to/doc.txt")
response = await client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            mcp_resource_to_content(resource),
            {"type": "text", "text": "Summarize this document"},
        ],
    }],
)
```### 将 MCP 资源作为文件上传```python
from anthropic.lib.tools.mcp import mcp_resource_to_file

resource = await mcp_client.read_resource(uri="file:///path/to/data.json")
uploaded = await client.beta.files.upload(file=mcp_resource_to_file(resource))
```如果无法转换 MCP 值（例如，不支持的内容类型，如音频、不支持的 MIME 类型），转换函数会引发 `UnsupportedMCPValueError`。

---

## 手动代理循环

当您需要对循环进行细粒度控制（例如，自定义日志记录、条件工具执行、人机交互批准）时，请使用此选项：```python
import anthropic

client = anthropic.Anthropic()
tools = [...]  # Your tool definitions
messages = [{"role": "user", "content": user_input}]

# Agentic loop: keep going until Claude stops calling tools
while True:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=tools,
        messages=messages
    )

    # If Claude is done (no more tool calls), break
    if response.stop_reason == "end_turn":
        break

    # Server-side tool hit iteration limit; re-send to continue
    if response.stop_reason == "pause_turn":
        messages = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response.content},
        ]
        continue

    # Extract tool use blocks from the response
    tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

    # Append assistant's response (including tool_use blocks)
    messages.append({"role": "assistant", "content": response.content})

    # Execute each tool and collect results
    tool_results = []
    for tool in tool_use_blocks:
        result = execute_tool(tool.name, tool.input)  # Your implementation
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool.id,  # Must match the tool_use block's id
            "content": result
        })

    # Append tool results as a user message
    messages.append({"role": "user", "content": tool_results})

# Final response text
final_text = next(b.text for b in response.content if b.type == "text")
```---

## 处理工具结果```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}]
)

for block in response.content:
    if block.type == "tool_use":
        tool_name = block.name
        tool_input = block.input
        tool_use_id = block.id

        result = execute_tool(tool_name, tool_input)

        followup = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=16000,
            tools=tools,
            messages=[
                {"role": "user", "content": "What's the weather in Paris?"},
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    }]
                }
            ]
        )
```---

## 多个工具调用```python
tool_results = []

for block in response.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": result
        })

# Send all results back at once
if tool_results:
    followup = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=tools,
        messages=[
            *previous_messages,
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ]
    )
```---

## 工具结果中的错误处理```python
tool_result = {
    "type": "tool_result",
    "tool_use_id": tool_use_id,
    "content": "Error: Location 'xyz' not found. Please provide a valid city name.",
    "is_error": True
}
```---

## 工具选择```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    tools=tools,
    tool_choice={"type": "tool", "name": "get_weather"},  # Force specific tool
    messages=[{"role": "user", "content": "What's the weather in Paris?"}]
)
```---

## 代码执行

### 基本用法```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": "Calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
    }],
    tools=[{
        "type": "code_execution_20260120",
        "name": "code_execution"
    }]
)

for block in response.content:
    if block.type == "text":
        print(block.text)
    elif block.type == "bash_code_execution_tool_result":
        print(f"stdout: {block.content.stdout}")
```### 上传文件进行分析```python
# 1. Upload a file
uploaded = client.beta.files.upload(file=open("sales_data.csv", "rb"))

# 2. Pass to code execution via container_upload block
# Code execution is GA; Files API is still beta (pass via extra_headers)
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    extra_headers={"anthropic-beta": "files-api-2025-04-14"},
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze this sales data. Show trends and create a visualization."},
            {"type": "container_upload", "file_id": uploaded.id}
        ]
    }],
    tools=[{"type": "code_execution_20260120", "name": "code_execution"}]
)
```### 检索生成的文件```python
import os

OUTPUT_DIR = "./claude_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

for block in response.content:
    if block.type == "bash_code_execution_tool_result":
        result = block.content
        if result.type == "bash_code_execution_result" and result.content:
            for file_ref in result.content:
                if file_ref.type == "bash_code_execution_output":
                    metadata = client.beta.files.retrieve_metadata(file_ref.file_id)
                    file_content = client.beta.files.download(file_ref.file_id)
                    # Use basename to prevent path traversal; validate result
                    safe_name = os.path.basename(metadata.filename)
                    if not safe_name or safe_name in (".", ".."):
                        print(f"Skipping invalid filename: {metadata.filename}")
                        continue
                    output_path = os.path.join(OUTPUT_DIR, safe_name)
                    file_content.write_to_file(output_path)
                    print(f"Saved: {output_path}")
```### 容器重复使用```python
# First request: set up environment
response1 = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Install tabulate and create data.json with sample data"}],
    tools=[{"type": "code_execution_20260120", "name": "code_execution"}]
)

# Get container ID from response
container_id = response1.container.id

# Second request: reuse the same container
response2 = client.messages.create(
    container=container_id,
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Read data.json and display as a formatted table"}],
    tools=[{"type": "code_execution_20260120", "name": "code_execution"}]
)
```### 响应结构```python
for block in response.content:
    if block.type == "text":
        print(block.text)  # Claude's explanation
    elif block.type == "server_tool_use":
        print(f"Running: {block.name} - {block.input}")  # What Claude is doing
    elif block.type == "bash_code_execution_tool_result":
        result = block.content
        if result.type == "bash_code_execution_result":
            if result.return_code == 0:
                print(f"Output: {result.stdout}")
            else:
                print(f"Error: {result.stderr}")
        else:
            print(f"Tool error: {result.error_code}")
    elif block.type == "text_editor_code_execution_tool_result":
        print(f"File operation: {block.content}")
```---

## 记忆工具

### 基本用法```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Remember that my preferred language is Python."}],
    tools=[{"type": "memory_20250818", "name": "memory"}],
)
```### SDK 内存助手

子类`BetaAbstractMemoryTool`：```python
from anthropic.lib.tools import BetaAbstractMemoryTool

class MyMemoryTool(BetaAbstractMemoryTool):
    def view(self, command): ...
    def create(self, command): ...
    def str_replace(self, command): ...
    def insert(self, command): ...
    def delete(self, command): ...
    def rename(self, command): ...

memory = MyMemoryTool()

# Use with tool runner
runner = client.beta.messages.tool_runner(
    model="claude-opus-4-8",
    max_tokens=16000,
    tools=[memory],
    messages=[{"role": "user", "content": "Remember my preferences"}],
)

for message in runner:
    print(message)
```有关完整的实现示例，请使用 WebFetch：

- `https://github.com/anthropics/anthropic-sdk-python/blob/main/examples/memory/basic.py`

---

## 结构化输出

### JSON 输出（Pydantic — 推荐）```python
from pydantic import BaseModel
from typing import List
import anthropic

class ContactInfo(BaseModel):
    name: str
    email: str
    plan: str
    interests: List[str]
    demo_requested: bool

client = anthropic.Anthropic()

response = client.messages.parse(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": "Extract: Jane Doe (jane@co.com) wants Enterprise, interested in API and SDKs, wants a demo."
    }],
    output_format=ContactInfo,
)

# response.parsed_output is a validated ContactInfo instance
contact = response.parsed_output
print(contact.name)           # "Jane Doe"
print(contact.interests)      # ["API", "SDKs"]
```### 原始模式```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": "Extract info: John Smith (john@example.com) wants the Enterprise plan."
    }],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "plan": {"type": "string"},
                    "demo_requested": {"type": "boolean"}
                },
                "required": ["name", "email", "plan", "demo_requested"],
                "additionalProperties": False
            }
        }
    }
)

import json
# output_config.format guarantees the first block is text with valid JSON
text = next(b.text for b in response.content if b.type == "text")
data = json.loads(text)
```### 严格工具使用```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Book a flight to Tokyo for 2 passengers on March 15"}],
    tools=[{
        "name": "book_flight",
        "description": "Book a flight to a destination",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "date": {"type": "string", "format": "date"},
                "passengers": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8]}
            },
            "required": ["destination", "date", "passengers"],
            "additionalProperties": False
        }
    }]
)
```### 同时使用两者```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Plan a trip to Paris next month"}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "next_steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["summary", "next_steps"],
                "additionalProperties": False
            }
        }
    },
    tools=[{
        "name": "search_flights",
        "description": "Search for available flights",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "date": {"type": "string", "format": "date"}
            },
            "required": ["destination", "date"],
            "additionalProperties": False
        }
    }]
)
```</doc>

<doc path="python/managed-agents/README.md">
# 托管代理 — Python

> **此处未显示绑定：** 本自述文件涵盖了 Python 最常见的托管代理流程。如果您需要未显示的类、方法、命名空间、字段或行为，请从 `shared/live-sources.md` Web 获取 Python SDK 存储库**或相关文档页面**，而不是猜测。请勿从 cURL 形状或其他语言的 SDK 进行推断。

> **代理是持久性的 — 创建一次，通过 ID 引用。** 存储 `agents.create` 返回的代理 ID，并将其传递给后续的每个 `sessions.create`；不要在请求路径中调用 `agents.create`。 Anthropic CLI 是从版本控制的 YAML 创建代理和环境的一种便捷方法 - 其 URL 位于 `shared/live-sources.md` 中。为了完整性，下面的示例展示了代码内创建；在生产中，创建调用属于设置，而不是请求路径。

＃＃ 安装```bash
pip install anthropic
```## 客户端初始化```python
import anthropic

# Default — resolves credentials from the environment:
# ANTHROPIC_API_KEY, or ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile.
# Prefer this for local dev; don't hardcode a key.
client = anthropic.Anthropic()

# Explicit API key (only when you must inject a specific key)
client = anthropic.Anthropic(api_key="your-api-key")
```---

## 创建环境```python
environment = client.beta.environments.create(
    name="my-dev-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
    },
)
print(environment.id)  # env_...
```---

## 创建代理（第一步必填）

> ⚠️ **没有内联代理配置。** `model`/`system`/`tools` 存在于代理对象上，而不是会话上。始终以 `agents.create()` 开始 — 会话仅需要 `agent={"type": "agent", "id": agent.id}`。

### 最小```python
# 1. Create the agent (reusable, versioned)
agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-opus-4-8",
    tools=[{"type": "agent_toolset_20260401", "default_config": {"enabled": True}}],
)

# 2. Start a session
session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": agent.version},
    environment_id=environment.id,
)
print(session.id, session.status)
```### 带有系统提示和自定义工具```python
import os

agent = client.beta.agents.create(
    name="Code Reviewer",
    model="claude-opus-4-8",
    system="You are a senior code reviewer.",
    tools=[
        {"type": "agent_toolset_20260401"},
        {
            "type": "custom",
            "name": "run_tests",
            "description": "Run the test suite",
            "input_schema": {
                "type": "object",
                "properties": {
                    "test_path": {"type": "string", "description": "Path to test file"}
                },
                "required": ["test_path"],
            },
        },
    ],
)

session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": agent.version},
    environment_id=environment.id,
    title="Code review session",
    resources=[
        {
            "type": "github_repository",
            "url": "https://github.com/owner/repo",
            "mount_path": "/workspace/repo",
            "authorization_token": os.environ["GITHUB_TOKEN"],
            "branch": "main",
        }
    ],
)
```---

## 发送用户消息```python
client.beta.sessions.events.send(
    session_id=session.id,
    events=[
        {
            "type": "user.message",
            "content": [{"type": "text", "text": "Review the auth module"}],
        }
    ],
)
```> 💡 **流优先：**在发送消息之前*（或同时）打开流。流仅传递打开后发生的事件 - 发送后流意味着早期事件以一批方式缓冲到达。请参阅[转向模式](../../shared/managed-agents-events.md#steering-patterns)。

---

## 直播活动 (SSE)```python
import json

# Stream-first: open stream, then send while stream is live
with client.beta.sessions.events.stream(
    session_id=session.id,
) as stream:
    client.beta.sessions.events.send(
        session_id=session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": "..."}]}],
    )
    for event in stream:
        ...  # process events

# Standalone stream iteration:
with client.beta.sessions.events.stream(
    session_id=session.id,
) as stream:
    for event in stream:
        if event.type == "agent.message":
            for block in event.content:
                if block.type == "text":
                    print(block.text, end="", flush=True)
        elif event.type == "agent.custom_tool_use":
            # Custom tool invocation — session is now idle
            print(f"\nCustom tool call: {event.name}")
            print(f"Input: {json.dumps(event.input)}")
            # Send result back (see below)
        elif event.type == "session.status_idle":
            print("\n--- Agent idle ---")
        elif event.type == "session.status_terminated":
            print("\n--- Session terminated ---")
            break
```---

## 提供自定义工具结果```python
client.beta.sessions.events.send(
    session_id=session.id,
    events=[
        {
            "type": "user.custom_tool_result",
            "custom_tool_use_id": "sevt_abc123",
            "content": [{"type": "text", "text": "All 42 tests passed."}],
        }
    ],
)
```---

## 投票活动```python
events = client.beta.sessions.events.list(
    session_id=session.id,
)
for event in events.data:
    print(f"{event.type}: {event.id}")
```> ⚠️ **优先选择 SDK 而不是原始 `requests`/`httpx`。** 如果您手动滚动轮询循环，请不要假设 `timeout=(5, 60)` 或 `httpx.Timeout(120)` 总计上限调用持续时间——两者都是**每块**读取超时（在每个字节上重置），因此滴流响应可能会永远阻塞。对于硬挂钟截止日期，请在循环级别跟踪 `time.monotonic()` 并显式保释，或使用 `asyncio.wait_for()` 包装。请参阅[接收事件](../../shared/managed-agents-events.md#receiving-events)。

---

## 使用自定义工具的完整流媒体循环```python
import json


def run_custom_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a custom tool and return the result."""
    if tool_name == "run_tests":
        # Your tool implementation here
        return "All tests passed."
    return f"Unknown tool: {tool_name}"


def run_session(client, session_id: str):
    """Stream events and handle custom tool calls."""
    while True:
        with client.beta.sessions.events.stream(
            session_id=session_id,
        ) as stream:
            tool_calls = []
            for event in stream:
                if event.type == "agent.message":
                    for block in event.content:
                        if block.type == "text":
                            print(block.text, end="", flush=True)
                elif event.type == "agent.custom_tool_use":
                    tool_calls.append(event)
                elif event.type == "session.status_idle":
                    break
                elif event.type == "session.status_terminated":
                    return

        if not tool_calls:
            break

        # Process custom tool calls
        results = []
        for call in tool_calls:
            result = run_custom_tool(call.name, call.input)
            results.append({
                "type": "user.custom_tool_result",
                "custom_tool_use_id": call.id,
                "content": [{"type": "text", "text": result}],
            })

        client.beta.sessions.events.send(
            session_id=session_id,
            events=results,
        )
```---

## 上传文件```python
with open("data.csv", "rb") as f:
    file = client.beta.files.upload(
        file=f,
    )

# Use in a session
session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": agent.version},
    environment_id=environment.id,
    resources=[{"type": "file", "file_id": file.id, "mount_path": "/workspace/data.csv"}],
)
```---

## 列出并下载会话文件

列出代理在会话期间写入 `/mnt/session/outputs/` 的文件，然后下载它们。```python
# List files associated with a session
files = client.beta.files.list(
    scope_id=session.id,
    betas=["managed-agents-2026-04-01"],
)
for f in files.data:
    print(f.filename, f.size_bytes)
    # Download each file and save to disk
    file_content = client.beta.files.download(f.id)
    file_content.write_to_file(f.filename)
```> 💡 `session.status_idle` 和 `files.list` 中出现的输出文件之间存在短暂的索引滞后（~1–3 秒）。如果列表为空，请重试一次或两次。

---

## 会话管理```python
# Get session details
session = client.beta.sessions.retrieve(session_id="sesn_011CZxAbc123Def456")
print(session.status, session.usage)

# List sessions
sessions = client.beta.sessions.list()

# Delete a session
client.beta.sessions.delete(session_id="sesn_011CZxAbc123Def456")

# Archive a session
client.beta.sessions.archive(session_id="sesn_011CZxAbc123Def456")
```---

## MCP 服务器集成```python
# Agent declares MCP server (no auth here — auth goes in a vault)
agent = client.beta.agents.create(
    name="MCP Agent",
    model="claude-opus-4-8",
    mcp_servers=[
        {"type": "url", "name": "my-tools", "url": "https://my-mcp-server.example.com/sse"},
    ],
    tools=[
        {"type": "agent_toolset_20260401", "default_config": {"enabled": True}},
        {"type": "mcp_toolset", "mcp_server_name": "my-tools"},
    ],
)

# Session attaches vault(s) containing credentials for those MCP server URLs
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    vault_ids=[vault.id],
)
```请参阅 `shared/managed-agents-tools.md` §Vaults 以创建保管库和添加凭据。
</doc>

<doc path="ruby/claude-api.md">
# 克劳德 API — 红宝石

> **注意：** Ruby SDK 支持 Claude API。工具运行程序可通过 `client.beta.messages.tool_runner()` 获得测试版。代理 SDK 尚不可用于 Ruby。

＃＃ 安装```bash
gem install anthropic
```## 客户端初始化```ruby
require "anthropic"

# Default (uses ANTHROPIC_API_KEY env var)
client = Anthropic::Client.new

# Explicit API key
client = Anthropic::Client.new(api_key: "your-api-key")
```---

## 基本消息请求```ruby
message = client.messages.create(
  model: :"claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    { role: "user", content: "What is the capital of France?" }
  ]
)
# content is an array of polymorphic block objects (TextBlock, ThinkingBlock,
# ToolUseBlock, ...). .type is a Symbol — compare with :text, not "text".
# .text raises NoMethodError on non-TextBlock entries.
message.content.each do |block|
  puts block.text if block.type == :text
end
```---

## 流媒体```ruby
stream = client.messages.stream(
  model: :"claude-opus-4-8",
  max_tokens: 64000,
  messages: [{ role: "user", content: "Write a haiku" }]
)

stream.text.each { |text| print(text) }
```---

## 工具使用

Ruby SDK 支持通过原始 JSON 模式定义使用工具，并且还提供用于自动工具执行的测试版工具运行程序。

### 工具运行程序（测试版）```ruby
class GetWeatherInput < Anthropic::BaseModel
  required :location, String, doc: "City and state, e.g. San Francisco, CA"
end

class GetWeather < Anthropic::BaseTool
  doc "Get the current weather for a location"

  input_schema GetWeatherInput

  def call(input)
    "The weather in #{input.location} is sunny and 72°F."
  end
end

client.beta.messages.tool_runner(
  model: :"claude-opus-4-8",
  max_tokens: 16000,
  tools: [GetWeather.new],
  messages: [{ role: "user", content: "What's the weather in San Francisco?" }]
).each_message do |message|
  puts message.content
end
```### 手动循环

有关工具定义格式和代理循环模式，请参阅[共享工具使用概念](../shared/tool-use-concepts.md)。

---

## 提示缓存

`system_:`（尾随下划线 - 避免阴影 `Kernel#system`）采用文本块数组；在最后一个块上设置 `cache_control`。普通哈希通过 `OrHash` 类型别名工作。有关放置模式和静默无效器审核清单，请参阅 `shared/prompt-caching.md`。```ruby
message = client.messages.create(
  model: :"claude-opus-4-8",
  max_tokens: 16000,
  system_: [
    { type: "text", text: long_system_prompt, cache_control: { type: "ephemeral" } }
  ],
  messages: [{ role: "user", content: "Summarize the key points" }]
)
```对于 1 小时 TTL：`cache_control: { type: "ephemeral", ttl: "1h" }`。 `messages.create` 上还有一个顶级 `cache_control:`，它自动放置在最后一个可缓存块上。

通过 `message.usage.cache_creation_input_tokens` / `message.usage.cache_read_input_tokens` 验证命中。

---

## 停靠点详细信息

当 `stop_reason` 为 `:refusal` 时，响应包括结构化 `stop_details`：```ruby
if message.stop_reason == :refusal && message.stop_details
  puts "Category: #{message.stop_details.category}"     # :cyber, :bio, or nil
  puts "Explanation: #{message.stop_details.explanation}"
end
```---

## 错误类型

`APIStatusError` 公开用于编程错误分类的 `.type` 字段：```ruby
begin
  client.messages.create(...)
rescue Anthropic::APIStatusError => e
  puts e.type  # :rate_limit_error, :overloaded_error, etc.
end
```</doc>

<doc path="shared/agent-design.md">
# 代理设计模式

该文件涵盖了在 Claude API 上构建代理的决策启发法：要达到哪些原语、如何设计工具界面以及如何管理长期运行的上下文和成本。有关每个工具的机制和代码示例，请参阅 `tool-use-concepts.md` 和特定于语言的文件夹。

---

## 型号参数

|参数|何时使用它 |期待什么 |
| --- | --- | --- |
| **适应性思维** (`thinking: {type: "adaptive"}`) |当你想让克劳德控制思考的时间和程度时。 | Claude 确定每个请求的思考深度，并自动在工具调用之间交错思考。没有需要调整的代币预算。 |
| **努力** (`output_config: {effort: ...}`) |在调整彻底性和代币效率之间的权衡时。 |更少的工作量 → 更少且更整合的工具调用、更少的序言、更简洁的确认。 `medium` 通常是有利的平衡。当正确性比成本更重要时，请使用 `max`。 |

有关模型支持和参数详细信息，请参阅 `SKILL.md` §思考与努力。

---

## 设计你的工具表面

### Bash 与专用工具对比

Claude 不知道您的应用程序的安全边界、审批策略或用户体验界面。 Claude 发出工具调用；你的安全带可以处理它们。这些工具调用的形式决定了线束可以做什么。

**bash 工具**为 Claude 提供了广泛的编程杠杆 - 它几乎可以执行任何操作。但它只为安全带提供了一个不透明的命令字符串，每个动作的形状都相同。将操作提升为**专用工具**可为工具提供特定于操作的挂钩，其中包含可以拦截、门控、渲染或审核的类型化参数。

**何时将某个操作提升为专用工具：**

- **安全边界。** 需要门控的操作是自然的候选者。可逆性是一个有用的标准：难以逆转的操作（外部 API 呼叫、发送消息、删除数据）可以在用户确认后进行门控。 `send_email` 工具易于浇口； `bash -c "curl -X POST ..."` 不是。
- **陈旧性检查。** 如果自 Claude 上次读取文件以来文件发生更改，专用的 `edit` 工具可以拒绝写入。 Bash 无法强制执行该不变式。
- **渲染。** 某些操作受益于自定义 UI。 Claude Code 将提问提升为一种工具，以便它可以呈现为模式、呈现选项并阻止代理循环直到得到答复。
- **调度。** `glob` 和 `grep` 等只读工具可以标记为并行安全。当相同的操作通过 bash 运行时，线束无法区分并行安全 `grep` 和并行不安全 `git push`，因此它必须进行序列化。

**经验法则：** 从 bash 开始了解广度。当您需要门控、渲染、审核或并行化操作时，升级为专用工具。

---

## Anthropic 提供的工具

|工具|侧面|何时使用它 |期待什么 |
| --- | --- | --- | --- |
| **Bash** |客户| Claude 需要执行 shell 命令。 |克劳德发出命令；你的安全带执行它们。提供参考实现。 |
| **文本编辑器** |客户|克劳德需要读取或编辑文件。 | Claude 通过您的实现查看、创建和编辑文件。提供参考实现。 |
| **计算机使用** |客户端或服务器 | Claude 需要与 GUI、Web 应用程序或可视界面进行交互。 |克劳德截取屏幕截图并发出鼠标/键盘命令。可以自托管（您运行环境）或人工托管。 |
| **代码执行** |服务器|克劳德需要在您不想管理的沙箱中运行代码。 | Anthropic 托管容器，带有内置文件和 bash 子工具。没有客户端执行。 |
| **网络搜索/获取** |服务器|克劳德需要超过其培训截止时间的信息（新闻、时事、最近的文档）或特定 URL 的内容。 |克劳德发出查询或URL； Anthropic 执行它并返回带有引用的结果。 |
| **内存** |客户|克劳德需要保存跨会话的上下文。 | Claude 读取/写入 `/memories` 目录。您实现存储后端。 |

**客户端**工具由 Anthropic 定义（名称、架构、Claude 的使用模式），但由您的工具执行。 Anthropic 提供参考实现。 **服务器端**工具完全在 Anthropic 基础设施上运行 - 在 `tools` 中声明它们，Claude 处理其余的事情。

---

## 组合工具调用：编程工具调用

使用标准工具时，每个工具调用都是一个往返：Claude 调用该工具，结果到达 Claude 的上下文中，Claude 对此进行推理，然后调用下一个工具。三个连续操作（读取配置文件→查找订单→检查库存）意味着三个往返。每个都会增加延迟和令牌，并且大多数中间数据不再需要。

**编程工具调用 (PTC)** 让 Claude 将这些调用组合成一个脚本代替。该脚本在代码执行容器中运行。当脚本调用工具时，容器会暂停，执行调用（客户端或服务器端），结果返回到正在运行的代码，而不是 Claude 的上下文。该脚本使用正常的控制流（循环、过滤器、分支）对其进行处理。只有脚本的最终输出返回给克劳德。

|何时使用它 |期待什么 |
| --- | --- |
|许多连续的工具调用，或者您想要在到达上下文窗口之前过滤的大型中间结果。 |克劳德编写将工具作为函数调用的代码。在代码执行容器中运行。代币成本与最终输出而不是中间结果成比例。 |

---

## 扩展工具和指令集

|特色 |何时使用它 |期待什么 |
| --- | --- | --- |
| **工具搜索** |可用的工具有很多，但根据请求只有少数相关工具。不希望上下文中的所有模式都预先存在。 | Claude 搜索工具集并仅加载相关模式。工具定义是附加的，而不是交换的——保留缓存（请参阅下面的缓存）。 |
| **技能** |克劳德应仅在相关时加载特定于任务的指令。 |每个技能都是一个带有 `SKILL.md` 的文件夹。默认情况下，技能的描述位于上下文中；当任务需要时，克劳德会读取完整的文件。 |

两种模式都保持固定上下文较小并按需加载细节。

---

## 长时间运行的代理：管理上下文

|图案|何时使用它 |期待什么 |
| --- | --- | --- |
| **上下文编辑** |经过多次轮换，上下文变得陈旧（旧的工具结果、完整的思维）。 |根据可配置的阈值清除工具结果和思维障碍。保持文字记录精简而不进行总结。 |
| **压实** |对话可能达到或超过上下文窗口限制。 |早期的上下文被总结为服务器端的压缩块。请参阅 `SKILL.md` §压实以了解关键的 `response.content` 处理。 |
| **内存** |状态必须在会话中持续存在（而不仅仅是在一次对话中）。 |克劳德在内存目录中读取/写入文件。进程重新启动后仍然存在。 |

**在它们之间进行选择：** 上下文编辑和压缩在一个会话中运行 - 编辑修剪陈旧的轮次，压缩在接近极限时进行总结。内存用于跨会话持久化。许多长期运行的代理都使用这三种方法。

---

## 代理缓存

**首先阅读 `prompt-caching.md`。** 它涵盖了前缀匹配不变式、断点放置、静默无效器审核，以及为什么在会话中更改工具或模型会破坏缓存。本节仅介绍针对这些约束的特定于代理的解决方法。

|约束（来自 `prompt-caching.md`）|特定于代理的解决方法 |
| --- | --- |
|在会话中编辑系统提示会使缓存失效。 |将 `{"role": "system", ...}` 消息附加到 `messages[]`（测试版，在支持型号上 — 请参阅 `prompt-caching.md` § 对话中系统消息）。缓存的前缀保持不变，模型将其视为操作员权限指令而不是用户文本。在不支持它的型号上，在用户回合中回退到 `<system-reminder>` 文本块。 |
|在会话中切换模型会使缓存失效。 |为子任务生成一个具有更便宜模型的**子代理**；将主循环保留在一个模型上。 Claude Code 的 Explore 子代理以这种方式使用 Haiku。 |
|在会话中添加/删除工具会使缓存失效。 |使用**工具搜索**进行动态发现 - 它附加工具模式而不是交换它们，因此保留现有前缀。 |

对于多轮断点放置，请使用顶级自动缓存 - 请参阅 `prompt-caching.md` §放置模式。

---

有关任何这些功能的实时文档，请参阅 `live-sources.md`。
</doc>

<doc path="shared/anthropic-cli.md">
# 人类 CLI (`ant`)

`ant` CLI 将每个 Claude API 资源公开为 shell 子命令。与 `curl` 相比：请求正文是从键入的标志或管道 YAML 而不是手写的 JSON 构建的，`@path` 将文件内容内联到任何字符串字段，`--transform` 提取具有 GJSON 路径的字段（无 `jq`），列表端点自动分页（`--max-items N` 限制总结果；`--limit` 仅设置服务器页面大小），并且 `beta:` 前缀自动设置右侧`anthropic-beta` 标头。

## 何时使用 CLI 与 SDK

**CLI 用于控制平面，SDK 用于数据平面。** 代理和环境是您使用 `ant` 定义、配置和调试的相对静态资源 - 将 YAML 检查到您的存储库中，从 CI 中应用，从终端进行检查。会话是动态的，由您的应用程序通过 SDK 驱动 — 按任务创建、流式传输事件、对工具调用做出反应、集成到您的产品中。两者命中相同的API；划分是关于调用所在的位置，而不是调用的内容可能的。

| |控制平面 → `ant` |数据平面 → SDK |
|---|---|---|
|资源 |代理、环境、技能、保管库、文件 |会议、活动 |
|节奏|每次部署/临时|一次每项任务/每回合|
|住在 | `*.yaml` 在您的仓库 + CI + 终端 |申请代码 |
|典型调用 | `create < agent.yaml`、`update --version N`、`list`、`retrieve`、`archive`、`--debug` | `sessions.create()`、`events.stream()`、`events.send()` |

## 安装并授权```sh
# macOS
brew install anthropics/tap/ant
xattr -d com.apple.quarantine "$(brew --prefix)/bin/ant"

# Linux / WSL — pick the release from github.com/anthropics/anthropic-cli/releases
curl -fsSL "https://github.com/anthropics/anthropic-cli/releases/download/v${VERSION}/ant_${VERSION}_$(uname -s | tr A-Z a-z)_$(uname -m | sed -e s/x86_64/amd64/ -e s/aarch64/arm64/).tar.gz" \
  | sudo tar -xz -C /usr/local/bin ant

# Or from source (Go 1.22+)
go install github.com/anthropics/anthropic-cli/cmd/ant@latest
```**Auth** — CLI 解析凭据的方式与 SDK 相同（第一个匹配获胜）：显式标志，然后是 `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` 环境变量，然后是 `ANTHROPIC_PROFILE`，然后是来自的活动配置文件`ant auth login`。使用 `ANTHROPIC_BASE_URL` 或 `--base-url` 覆盖主机。

- **API 键**：在环境中设置 `ANTHROPIC_API_KEY`。
- **OAuth 配置文件**（无需管理静态密钥）：`ant auth login` 打开浏览器，交换短期令牌，并将配置文件存储在 `~/.config/anthropic/` 下。后续的 `ant`（和 SDK）呼叫会自动接听它。 `ant auth status` 显示活动配置文件； `ant auth logout` 将其清除。

要将活动凭证交给子进程或 raw-HTTP 脚本：```sh
# Bare access token — for curl's Authorization header
curl https://api.anthropic.com/v1/messages \
  -H "Authorization: Bearer $(ant auth print-credentials --access-token)" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-opus-4-8", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello"}]}'

# .env format — sets ANTHROPIC_AUTH_TOKEN (and ANTHROPIC_BASE_URL if the profile has one).
# Output is bare KEY=value (no `export`), so use `set -a` to auto-export for child processes:
set -a; eval "$(ant auth print-credentials --env)"; set +a
python my_script.py   # SDK picks up ANTHROPIC_AUTH_TOKEN
```OAuth 代币继续为 `Authorization: Bearer`（不是 `x-api-key:`）。该令牌是短暂的，并且在通过环境变量传递时不会自动刷新，因此对于长时间运行的脚本，请在其过期之前重新运行 `print-credentials`。如果 `ANTHROPIC_API_KEY` 和 `ANTHROPIC_AUTH_TOKEN` 均已设置，则 SDK 会同时发送这两个请求，并且 API 会拒绝该请求 — 在 `eval` 之前取消设置 `ANTHROPIC_API_KEY` `--env` 输出。

## 命令结构```
ant <resource>[:<subresource>] <action> [flags]
```Beta 资源（代理、会话、环境、部署、技能、保管库、内存存储）位于 `beta:` 下 — CLI 自动发送正确的 `anthropic-beta` 标头，因此请勿自行传递它，除非使用 `--beta <header>` 覆盖。对于自托管环境，`ant beta:worker poll/run` 和 `ant beta:environments:work stats/stop` 驱动和监视工作队列 — 请参阅 `shared/managed-agents-self-hosted-sandboxes.md`。```sh
ant models list
ant messages create --model claude-opus-4-8 --max-tokens 1024 --message '{role: user, content: "Hello"}'
ant beta:agents retrieve --agent-id agent_01...
ant beta:sessions:events list --session-id session_01...
````ant --help` 列出资源；将 `--help` 附加到任何子命令以获取其标志。

## 全局标志

|旗帜|目的|
| --- | --- |
| `--format` | `auto`（默认：TTY 时漂亮，管道传输时紧凑）、`json`、`jsonl`、`yaml`、`pretty`、 `raw`、`explore`（交互式 TUI）|
| `--transform` |应用于响应的 GJSON 路径（列表端点上的每个项目）。 `--format raw` 时不适用。 |
| `-r`，`--raw-output` |如果转换后的结果是字符串，则打印它，不带引号（jq 语义）。与 `--transform` 配对进行标量捕获。 |
| `--max-items` |从自动分页列表端点返回的总结果上限（与 `--limit` 不同，它是服务器页面大小）。 |
| `--format-error` / `--transform-error` |与 `--format`/`--transform` 相同，应用于错误响应。 `-r` 不适用于错误路径 — 对于未加引号的错误标量，请使用 `--format-error yaml`。 |
| `--base-url` |覆盖 API 主机 |
| `--debug` |打印完整的 HTTP 请求 + 对 stderr 的响应（API 密钥已编辑）|

## 输出 — `--transform` + `--format`

`--transform` 采用 [GJSON 路径](https://github.com/tidwall/gjson/blob/master/SYNTAX.md)。在列表端点上，它运行**每个项目**，而不是在信封上运行。```sh
ant beta:agents list --transform '{id,name,model}' --format jsonl
```**提取标量以供 shell 使用：** 将 `--transform` 与 `-r` 配对（`--raw-output` — 打印不带引号的字符串，jq 样式）：```sh
AGENT_ID=$(ant beta:agents create --name "My Agent" --model '{id: claude-sonnet-4-6}' \
  --transform id -r)
```## 输入 — 标志、stdin、`@file`

**标志** — 标量场直接映射。结构化字段接受宽松的 YAML 语法（不带引号的键）或严格的 JSON。可重复标志构建数组（每个 `--tool`、`--event`、`--message` 附加一个元素）：```sh
ant beta:agents create \
  --name "Research Agent" \
  --model '{id: claude-opus-4-8}' \
  --tool '{type: agent_toolset_20260401}' \
  --tool '{type: custom, name: search_docs, input_schema: {type: object, properties: {query: {type: string}}}}'
```**Stdin** — 通过管道传输完整的 JSON 或 YAML 主体。与标志合并；标志在冲突时获胜（对于数组字段，任何标志完全替换标准输入数组 - 它不会附加）。引用heredoc分隔符（`<<'YAML'`）以禁用体内的shell扩展：```sh
ant beta:agents create <<'YAML'
name: Research Agent
model: claude-opus-4-8
system: |
  You are a research assistant. Cite sources for every claim.
tools:
  - type: agent_toolset_20260401
YAML
```**`@file` 引用** — 将文件的内容内联到任何字符串值字段中。在结构化标志值内，引用路径。二进制文件自动进行 base64 处理；使用 `@file://`（文本）或 `@data://`（base64）强制。将字面上的前导 `@` 转义为 `\@`。```sh
ant beta:agents create --name "Researcher" --model '{id: claude-sonnet-4-6}' --system @./prompts/researcher.txt

ant messages create --model claude-opus-4-8 --max-tokens 1024 \
  --message '{role: user, content: [
    {type: document, source: {type: base64, media_type: application/pdf, data: "@./scan.pdf"}},
    {type: text, text: "Extract the text from this scanned document."}
  ]}' \
  --transform 'content.0.text' -r
```本机采用文件路径的标志（例如 `beta:files upload` 上的 `--file`）接受不带 `@` 的裸路径。

## 版本控制的托管代理资源

这是定义代理和环境的推荐流程 - 将 YAML 检查到您的存储库中，并通过 `create`（第一次）/`update`（此后）进行同步。有关现场参考，请参阅 `shared/managed-agents-core.md`。```yaml
# summarizer.agent.yaml
name: Summarizer
model: claude-sonnet-4-6
system: |
  You are a helpful assistant that writes concise summaries.
tools:
  - type: agent_toolset_20260401
```

```sh
# Create (once) — capture the ID
AGENT_ID=$(ant beta:agents create < summarizer.agent.yaml --transform id -r)

# Update (CI) — needs ID + current version (optimistic lock)
ant beta:agents update --agent-id "$AGENT_ID" --version 1 < summarizer.agent.yaml
```环境模式相同 (`ant beta:environments create|update < env.yaml`)，然后使用两个 ID 启动会话：```sh
ant beta:sessions create --agent "$AGENT_ID" --environment-id "$ENV_ID" --title "Task"
ant beta:sessions:events send --session-id "$SID" \
  --event '{type: user.message, content: [{type: text, text: "Summarize X"}]}'
ant beta:sessions:events list --session-id "$SID" --transform 'content.0.text' -r
ant beta:sessions:events stream --session-id "$SID"   # live event stream
```### 交互式会话循环（发送前流）

`ant beta:sessions:events stream` 仅传送流打开*之后*发出的事件 - 因此在发送启动之前*打开它以避免错过早期事件。使用进程替换将流保存在文件描述符上，发送，然后读取：```sh
exec {stream}< <(ant beta:sessions:events stream --session-id "$SID" \
  --transform '{type,text:content.#(type=="text").text,err:error.message}' --format yaml)

ant beta:sessions:events send --session-id "$SID" > /dev/null <<'YAML'
events:
  - type: user.message
    content:
      - type: text
        text: Summarize the repo README
YAML

type=
while IFS= read -r -u "$stream" line; do
  case "$line" in
    type:\ session.status_idle) break ;;
    type:\ session.error)
      IFS= read -r -u "$stream" next || next=
      case "$next" in err:\ *) msg=${next#err: } ;; *) msg=unknown ;; esac
      printf '\n[Error: %s]\n' "$msg"; break ;;
    type:\ *) type=${line#type: } ;;
    text:*)
      [[ $type == agent.message ]] || continue
      val=${line#text: }
      case "$val" in '|-'|'|') ;; *) printf '%s' "$val" ;; esac ;;
    \ \ *)
      if [[ $type == agent.message ]]; then printf '%s\n' "${line#  }"; fi ;;
  esac
done
exec {stream}<&-
```这适用于交互式探索和演示。对于需要对 `agent.tool_use` / `agent.custom_tool_use` 事件做出反应、在断开后重新连接或针对 `events.list` 进行重复数据删除的应用程序代码，请使用 SDK — 请参阅 `shared/managed-agents-client-patterns.md`。

## 脚本模式

列表端点上的 `--transform id -r` 每行发出一个裸 ID — 与 `xargs` 组合，或使用 `--max-items N` 绑定结果集，而无需通过 `head` 进行管道传输：```sh
FIRST=$(ant beta:agents list --transform id -r --max-items 1)
ant beta:agents:versions list --agent-id "$FIRST" --transform '{version,created_at}' --format jsonl
```错误整形镜像了成功路径（注意：`-r` 不适用于错误输出 — 此处使用 `--format-error yaml` 作为不带引号的标量）：```sh
ant beta:agents retrieve --agent-id bogus --transform-error error.message --format-error yaml 2>&1
```外壳完成：`ant @completion {zsh|bash|fish|powershell}`。

如需完整、始终最新的参考（包括每个端点标志），请 WebFetch `shared/live-sources.md` 中的 **Anthropic CLI** URL。
</doc>

<doc path="shared/claude-platform-on-aws.md">
# AWS 上的克劳德平台

**人工操作**通过 AWS 基础设施访问 Claude 开发者平台 — SigV4 身份验证、AWS IAM 访问控制和 AWS Marketplace 计费。由于 Anthropic 对其进行操作，**API 表面与第一方匹配并具有当日奇偶校验**：托管代理、服务器端工具、批处理、文件以及此技能中的每个功能都以相同的方式工作（**自托管沙箱除外** — `config:{type:"self_hosted"}` 此处不可用；使用`cloud`）。型号 ID 是裸露的第一方字符串（`claude-opus-4-8`、`claude-sonnet-4-6`） - **无提供商前缀**。

> **与 Amazon Bedrock 不同。** Bedrock 由合作伙伴运营（AWS 运行该服务；发布计划各不相同，功能子集、`anthropic.` 前缀的型号 ID）。 AWS 上的 Claude Platform 与 Bedrock 共存；根据您是否需要具有完整 Anthropic API 奇偶校验（本页）的 AWS 原生 IAM/计费与 Bedrock 自己的生态系统进行选择。

---

## 客户端和安装

|语言 |安装 |客户|
|---|---|---|
| Python | `pip install -U "anthropic[aws]"` | `from anthropic import AnthropicAWS` → `AnthropicAWS()` |
| TypeScript | `npm install @anthropic-ai/aws-sdk` | `import AnthropicAws from "@anthropic-ai/aws-sdk"` → `new AnthropicAws()` |
|去 | `go get github.com/anthropics/anthropic-sdk-go` | `import anthropicaws "github.com/anthropics/anthropic-sdk-go/aws"` → `anthropicaws.NewClient(ctx, anthropicaws.ClientConfig{})` |
| C# | `dotnet add package Anthropic.Aws` | `new AnthropicAwsClient()` |
|爪哇 |请参阅 `shared/live-sources.md` 中的 SDK 存储库 |请参阅 `shared/live-sources.md` 中的 SDK 存储库 |
|红宝石 | `gem install anthropic aws-sdk-core` |请参阅 `shared/live-sources.md` 中的 SDK 存储库 |
| PHP | `composer require anthropic-ai/sdk aws/aws-sdk-php` |请参阅 `shared/live-sources.md` 中的 SDK 存储库 |

构建完成后，**像 `Anthropic()` 一样使用客户端** — `client.messages.create(...)`、`client.beta.sessions.*` 等，使用裸模型 ID。```python
from anthropic import AnthropicAWS

client = AnthropicAWS()  # region + workspace_id from env; see below
client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```---

## 所需配置

必须有两个值可用（构造函数参数或环境） - **没有默认回退**：

|价值|环境变量 |笔记|
|---|---|---|
| AWS 区域 | `AWS_REGION` |必需的。与 `AnthropicBedrock` 不同，没有 `us-east-1` 后备。 |
|工作区 ID | `ANTHROPIC_AWS_WORKSPACE_ID` |必需的。将请求路由到您的 Claude 工作区。 |

端点模式：`https://aws-external-anthropic.{region}.api.aws/v1/...`。请求使用 SigV4 签名，服务名称为 `aws-external-anthropic`。

## 身份验证

客户端通过标准优先级链解析 AWS 凭证：显式构造函数参数 → 环境 (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_SESSION_TOKEN`) → 共享配置文件 → 假定的角色/实例元数据。

**对于 SigV4 不实用的情况（例如浏览器、简单脚本），也支持短期 API 密钥**。使用每种语言的令牌生成器包创建一个；在客户端上将其作为 `api_key` 传递。生命周期是**请求的持续时间、基础凭证的到期时间和**12 小时**中的较小者。有关程序包名称和 IAM 详细信息，请 WebFetch `shared/live-sources.md` 中的 AWS 上的 Claude Platform 页面。

---

## 告诉用户什么

- 将其视为第一方：该技能的每个部分均保持不变。 **不要**应用 Bedrock 的功能可用性掩模。
- 型号 ID 是裸露的 (`claude-opus-4-8`)。 **不要**添加 `anthropic.` 前缀。
- 缺失区域或 `workspace_id` 在客户端构建时抛出（未发送请求）。 **403** 表示请求已到达服务器 — 检查主体上是否存在 **错误的** `workspace_id` 或缺少的 IAM 操作。请参阅 `shared/live-sources.md` 中的 IAM 操作参考。
</doc>

<doc path="shared/error-codes.md">
# HTTP 错误代码参考

此文件记录了 Claude API 返回的 HTTP 错误代码、其常见原因以及如何处理它们。有关特定于语言的错误处理示例，请参阅 `python/` 或 `typescript/` 文件夹。

## 错误代码摘要

|代码|错误类型 |可重试 |共同原因|
| ---- | ----------------------- | ---------| ------------------------------------------------ |
| 400 | `invalid_request_error` |没有 |请求格式或参数无效 |
| 401 | 401 `authentication_error` |没有 | API 密钥无效或丢失 |
| 403 | 403 `permission_error` |没有 | API 密钥缺少权限 |
| 404 | 404 `not_found_error` |没有 |端点或模型 ID 无效 |
| 413 | 413 `request_too_large` |没有 |请求超出大小限制 |
| 429 | 429 `rate_limit_error` |是的 |请求过多 |
| 500 | 500 `api_error` |是的 |人为服务问题 |
| 529 | 529 `overloaded_error` |是的 | API 暂时超载 |

## 详细错误信息

### 400 错误请求

**原因：**

- 请求正文中的 JSON 格式错误
- 缺少必需的参数（`model`、`max_tokens`、`messages`）
- 无效的参数类型（例如，需要整数的字符串）
- 空消息数组
- 消息不交替用户/助理

**错误示例：**```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "messages: roles must alternate between \"user\" and \"assistant\""
  },
  "request_id": "req_011CSHoEeqs5C35K2UUqR7Fy"
}
```**修复：** 发送前验证请求结构。检查：

- `model` 是有效的型号 ID
- `max_tokens` 是正整数
- `messages` 数组非空且正确交替

---

### 401 未经授权

**原因：**

- 缺少 `x-api-key` 标头或 `Authorization` 标头
- API 密钥格式无效
- 撤销或删除 API 密钥
- OAuth 不记名令牌通过 `x-api-key` 而不是 `Authorization: Bearer` 发送
- `ANTHROPIC_API_KEY` 和 `ANTHROPIC_AUTH_TOKEN` 均已设置 — SDK 发送两个标头，并且 API 拒绝请求

**修复：** 设置 `ANTHROPIC_API_KEY`，或运行 `ant auth login` 并将客户端构造函数留空。对于具有 OAuth 令牌的原始 HTTP，请使用 `Authorization: Bearer <token>`（而不是 `x-api-key:`）。

---

### 403 禁止

**原因：**

- API 密钥无法访问请求的模型
- 组织级别的限制
- 尝试在没有测试版访问权限的情况下访问测试版功能

**修复：** 在控制台中检查您的 API 密钥权限。您可能需要不同的 API 密钥或请求访问特定功能。

---

### 404 未找到

**原因：**

- 型号 ID 中的拼写错误（例如，`claude-sonnet-4.6` 而不是 `claude-sonnet-4-6`）
- 使用已弃用的模型 ID
- API 端点无效

**修复：** 使用模型文档中的准确模型 ID。您可以使用别名（例如 `claude-opus-4-8`）。

---

### 413 请求太大

**原因：**

- 请求正文超出最大大小
- 输入中的标记过多
- 图像数据太大

**修复：** 减少输入大小 - 截断对话历史记录、压缩/调整图像大小或将大文档拆分为块。

---

### 400 验证错误

一些 400 错误与参数验证特别相关：

- `max_tokens` 超出型号限制
- `temperature` 值无效（必须为 0.0-1.0）
- 扩展思维中的 `budget_tokens` >= `max_tokens`
- 无效的工具定义架构

**Opus 4.8 / 4.7 上特定型号的 400：**

- `temperature`、`top_p`、`top_k` 已删除 — 发送其中任何一个都会返回 400。 Delete 参数；请参阅 `shared/model-migration.md` → Per-SDK 语法参考。
- `thinking: {type: "enabled", budget_tokens: N}` 已删除 — 发送它会返回 400。请改用 `thinking: {type: "adaptive"}`。

**对旧模型（Opus 4.6 及更早版本）进行扩展思考的常见错误：**```
# Wrong: budget_tokens must be < max_tokens
thinking: budget_tokens=10000, max_tokens=1000  → Error!

# Correct
thinking: budget_tokens=10000, max_tokens=16000
```---

### 429 费率有限

**原因：**

- 超出每分钟请求数 (RPM)
- 超出每分钟令牌数 (TPM)
- 每日超出代币数量 (TPD)

**要检查的标题：**

- `retry-after`：重试前等待的秒数
- `x-ratelimit-limit-*`：你的极限
- `x-ratelimit-remaining-*`：剩余配额

**修复：** Anthropic SDK 使用指数退避自动重试 429 和 5xx 错误（默认值：`max_retries=2`）。有关自定义重试行为，请参阅特定于语言的错误处理示例。

---

### 500 内部服务器错误

**原因：**

- 临时人类服务问题
- API 处理中的错误

**修复：** 使用指数退避重试。如果持续存在，请检查 [status.anthropic.com](https://status.anthropic.com)。

---

### 529 超载

**原因：**

- API 需求高
- 服务能力达到

**修复：** 使用指数退避重试。考虑使用不同的模型（俳句通常负载较少），随着时间的推移分散请求，或实现请求排队。

---

## 常见错误和修复

|错误|错误 |修复 |
| ------------------------------------------- | ---------------- | ------------------------------------------------------- |
| Opus 4.8 / 4.7 上的 `temperature`/`top_p`/`top_k` | 400 |删除参数（参见`shared/model-migration.md`）|
| Opus 4.8 / 4.7 上的 `budget_tokens` | 400 |使用`thinking: {type: "adaptive"}` |
| `budget_tokens` >= `max_tokens`（旧型号）| 400 |确保 `budget_tokens` < `max_tokens` |
|型号 ID 中的拼写错误 | 404 | 404使用有效的型号 ID，例如 `claude-opus-4-8` |
|第一条消息是 `assistant` | 400 |第一条消息必须是 `user` |
|连续的相同角色消息 | 400 |备用 `user` 和 `assistant` |
| API 输入代码 | 401（泄露密钥）|使用环境变量 |
|自定义重试需求 | 429/5xx | 429/5xx SDK 自动重试；使用 `max_retries` 进行定制 |

## SDK 中的类型异常

**始终使用 SDK 的类型化异常类**，而不是使用字符串匹配检查错误消息。每个 HTTP 错误代码映射到特定的异常类：

| HTTP 代码 | TypeScript 类 | Python 类 |
| ---------| --------------------------------- | --------------------------------- |
| 400 | `Anthropic.BadRequestError` | `anthropic.BadRequestError` |
| 401 | 401 `Anthropic.AuthenticationError` | `anthropic.AuthenticationError` |
| 403 | 403 `Anthropic.PermissionDeniedError` | `anthropic.PermissionDeniedError` |
| 404 | 404 `Anthropic.NotFoundError` | `anthropic.NotFoundError` |
| 413 | 413 `Anthropic.RequestTooLargeError` | `anthropic.RequestTooLargeError` |
| 429 | 429 `Anthropic.RateLimitError` | `anthropic.RateLimitError` |
| 500+ | `Anthropic.InternalServerError` | `anthropic.InternalServerError` |
| 529 | 529 `Anthropic.OverloadedError` | `anthropic.OverloadedError` |
|任何| `Anthropic.APIError` | `anthropic.APIError` |```typescript
// ✅ Correct: use typed exceptions
try {
  const response = await client.messages.create({...});
} catch (error) {
  if (error instanceof Anthropic.RateLimitError) {
    // Handle rate limiting
  } else if (error instanceof Anthropic.APIError) {
    console.error(`API error ${error.status}:`, error.message);
  }
}

// ❌ Wrong: don't check error messages with string matching
try {
  const response = await client.messages.create({...});
} catch (error) {
  const msg = error instanceof Error ? error.message : String(error);
  if (msg.includes("429") || msg.includes("rate_limit")) { ... }
}
```所有异常类都扩展 `Anthropic.APIError`，它具有 `status` 属性。使用 `instanceof` 从最具体到最不具体的检查（例如，在 `APIError` 之前检查 `RateLimitError`）。

### 错误 `.type` 字段

所有 `APIStatusError` 子类现在公开 `.type` 属性（Python：`.type`，TypeScript：`.type`，Java： `.errorType()`、Go：`.Type()`、Ruby：`.type`、PHP：`.type`）返回 API 错误类型字符串（例如， `"invalid_request_error"`、`"authentication_error"`、`"rate_limit_error"`、`"overloaded_error"`）。当您需要比 HTTP 状态代码更精细的粒度时，请使用此功能进行编程错误分类 - 例如，区分 `"billing_error"` 和 `"permission_error"`（两者都映射到 403）。```python
except anthropic.APIStatusError as e:
    if e.type == "rate_limit_error":
        # handle rate limiting
    elif e.type == "overloaded_error":
        # handle overload
```</doc>

<doc path="shared/live-sources.md">
# 实时文档源

此文件包含用于从 platform.claude.com 和代理 SDK 存储库获取当前信息的 WebFetch URL。当用户需要自上次更新缓存内容以来可能已更改的最新数据时，请使用这些数据。

## 何时使用 WebFetch

- 用户明确要求提供 "latest" 或 "current" 信息
- 缓存数据似乎不正确
- 用户询问缓存内容中未涵盖的功能
- 用户需要具体的API详细信息或示例

## Claude API 文档 URL

### 型号和定价

|主题 | URL |提取提示|
| ---------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
|型号概览 | `https://platform.claude.com/docs/en/about-claude/models/overview.md` | “提取所有 Claude 模型的当前模型 ID、上下文窗口和定价”|
|迁移指南 | `https://platform.claude.com/docs/en/about-claude/models/migration-guide.md` | “在迁移到较新的 Claude 模型时提取重大更改、已弃用的参数和每个模型的迁移步骤”|
|定价| `https://platform.claude.com/docs/en/pricing.md` | “提取当前每百万代币的输入和输出定价”|

### 核心特性

|主题 | URL |提取提示|
| ----------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
|延伸思考| `https://platform.claude.com/docs/en/build-with-claude/extended-thinking.md` | “提取扩展思维参数、budget_tokens 要求以及使用示例”|
|适应性思维| `https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking.md` | “提取适应性思维设置、努力水平和 Claude Opus 4.8 使用示例”|
|努力参数| `https://platform.claude.com/docs/en/build-with-claude/effort.md` | “提取努力水平、成本质量权衡以及与思维的互动” |
|工具使用| `https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md` | “提取工具定义架构、tool_choice 选项和处理工具结果” |
|流媒体| `https://platform.claude.com/docs/en/build-with-claude/streaming.md` | “提取流事件类型、SDK 示例和最佳实践” |
|提示缓存 | `https://platform.claude.com/docs/en/build-with-claude/prompt-caching.md` | “摘录 cache_control 用法、定价优势和实施示例” |

### 媒体和文件

|主题 | URL |提取提示|
| ----------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
|愿景 | `https://platform.claude.com/docs/en/build-with-claude/vision.md` | “提取支持的图像格式、大小限制和代码示例”|
| PDF 支持 | `https://platform.claude.com/docs/en/build-with-claude/pdf-support.md` | “提取 PDF 处理功能、限制和示例”|

### API 操作

|主题 | URL |提取提示|
| ---------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
|批处理| `https://platform.claude.com/docs/en/build-with-claude/batch-processing.md` | “提取批次 API 端点、请求格式和轮询结果” |
|文件 API | `https://platform.claude.com/docs/en/build-with-claude/files.md` | “提取文件上传、下载和消息中的引用，包括支持的类型和测试标头” |
|令牌计数 | `https://platform.claude.com/docs/en/build-with-claude/token-counting.md` | “提取令牌计数 API 用法和示例”|
|速率限制 |`https://platform.claude.com/docs/en/api/rate-limits.md` | “按级别和型号提取当前速率限制”|
|错误 | `https://platform.claude.com/docs/en/api/errors.md` | “提取 HTTP 错误代码、含义和重试指南” |
|亚马逊基岩 | `https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock.md` | “按语言提取 AnthropicBedrockMantle 客户端、`anthropic.` 前缀的模型 ID、身份验证路径、功能可用性和区域” |
| AWS 上的 Claude 平台 | `https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws.md` | “按语言提取 AnthropicAWS 客户端、SigV4 身份验证、凭证优先级、短期 API 密钥、workspace_id 和区域要求” |
| AWS 上的 Claude 平台 — IAM 操作 | `https://platform.claude.com/docs/en/api/claude-platform-on-aws-iam-actions.md` | “提取每个 API 功能所需的 IAM 操作名称、资源 ARN 和策略示例” |

### 工具

|主题 | URL |提取提示|
| -------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
|代码执行 | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool.md` | “提取代码执行工具设置、文件上传、容器重用和响应处理” |
|电脑使用 | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use.md` | “提取计算机使用工具设置、功能和实施示例”|
| Bash 工具 | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool.md` | “提取 bash 工具架构、参考实现和安全注意事项” |
|文本编辑器 | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool.md` | “提取文本编辑器工具命令、架构和参考实现”|
|记忆工具| `https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool.md` | “提取内存工具命令、目录结构和实现模式”|
|工具搜索| `https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool.md` | “提取工具搜索设置、何时使用以及缓存交互”|
|编程工具调用 | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling.md` | “从代码中提取 PTC 设置、脚本执行模型和工具调用”|
|技能 | `https://platform.claude.com/docs/en/agents-and-tools/skills.md` | “提取技能文件夹结构、SKILL.md 格式和加载行为”|

### 高级功能

|主题 | URL |提取提示|
| ------------------ | ------------------------------------------------------------------------------------------ | --------------------------------------------------- |
|结构化输出 | `https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md` | “提取 output_config.format 用法和架构实施” |
|压实| `https://platform.claude.com/docs/en/build-with-claude/compaction.md` | “提取压缩设置、触发配置和压缩流”|
|上下文编辑 | `https://platform.claude.com/docs/en/build-with-claude/context-editing.md` | “提取上下文编辑阈值、清除的内容和配置”|
|引文| `https://platform.claude.com/docs/en/build-with-claude/citations.md` | 《摘录引文格式及实现》|
|上下文窗口 | `https://platform.claude.com/docs/en/build-with-claude/context-windows.md` | “提取上下文窗口大小和令牌管理”|

### 托管代理

当缓存的 `shared/managed-agents-*.md` 概念文件或 `{lang}/managed-agents/README.md` 中未涵盖托管代理绑定、行为或线路级别详细信息时，请使用这些内容。

|主题 | URL |提取提示|
| -------------------- |-------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
|概述 | `https://platform.claude.com/docs/en/managed-agents/overview.md` | “提取高级架构以及代理/会话/环境/保管库如何组合在一起” |
|快速入门 | `https://platform.claude.com/docs/en/managed-agents/quickstart.md` | “提取最小的端到端代理→环境→会话→流代码路径”|
|代理设置| `https://platform.claude.com/docs/en/managed-agents/agent-setup.md` | “提取代理创建/更新/列表版本/归档生命周期和参数”|
|定义结果 | `https://platform.claude.com/docs/en/managed-agents/define-outcomes.md` | “提取结果定义、评估挂钩和成功标准配置”|
|会议 | `https://platform.claude.com/docs/en/managed-agents/sessions.md` | “提取会话生命周期、状态转换、空闲/终止语义和恢复规则”|
|环境 | `https://platform.claude.com/docs/en/managed-agents/environments.md` | “提取环境配置（云/网络）、管理端点和重用模型” |
|自托管沙箱 | `https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes.md` | “提取配置：{type：self_hosted}，ANTHROPIC_ENVIRONMENT_KEY，EnvironmentWorker.run/run_one，beta_agent_toolset，ant beta：worker轮询/运行，webhook驱动的唤醒” |
|自托管沙箱 — 安全 | `https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes-security.md` | “提取客户拥有的内容（强化、出口、密钥保管、信任边界）与 Anthropic 无法做到的内容”|
|活动和流媒体 | `https://platform.claude.com/docs/en/managed-agents/events-and-streaming.md` | “提取事件流类型、流优先排序、重新连接/重复数据删除和转向模式” |
|工具| `https://platform.claude.com/docs/en/managed-agents/tools.md` | “提取内置工具集、自定义工具定义和工具结果线格式” |
|文件 | `https://platform.claude.com/docs/en/managed-agents/files.md` | “提取文件上传、安装路径、会话资源以及列出/下载会话输出” |
|权限政策 | `https://platform.claude.com/docs/en/managed-agents/permission-policies.md` | “提取权限策略类型（允许/拒绝/确认）和每个工具配置” |
|多代理| `https://platform.claude.com/docs/en/managed-agents/multi-agent.md` | “提取多代理组合模式、子代理调用和结果切换”|
|可观察性| `https://platform.claude.com/docs/en/managed-agents/observability.md` | “提取托管代理公开的日志记录、跟踪和使用情况遥测”|
|网络钩子 | `https://platform.claude.com/docs/en/managed-agents/webhooks.md` | “提取 webhook 端点注册、HMAC 签名验证、支持的事件类型和传递语义”|
| GitHub | `https://platform.claude.com/docs/en/managed-agents/github.md` | “提取 github_repository 资源形状、多存储库安装和令牌轮换”|
| MCP 连接器 | `https://platform.claude.com/docs/en/managed-agents/mcp-connector.md` | “在会话中提取有关代理和基于保管库的凭据注入的 MCP 服务器声明” |
|保险库 | `https://platform.claude.com/docs/en/managed-agents/vaults.md` | “提取保管库创建、凭证添加/轮换、OAuth 刷新形状和存档” |
|技能 | `https://platform.claude.com/docs/en/managed-agents/skills.md` | “为托管代理提取技能打包和加载模型”|
|内存| `https://platform.claude.com/docs/en/managed-agents/memory.md` | “提取内存资源形状、范围和生命周期”|
|入职 | `https://platform.claude.com/docs/en/managed-agents/onboarding.md` | “提取首次运行设置、先决条件和帐户/区域要求”|
|云容器| `https://platform.claude.com/docs/en/managed-agents/cloud-containers.md` | “提取云容器运行时、镜像配置、和网络/存储旋钮” |
|移民| `https://platform.claude.com/docs/en/managed-agents/migration.md` | “提取从早期 API/预览形状到 GA 托管代理的迁移路径”|

### 人类 CLI

`ant` CLI 提供对 Claude API 的终端访问。每个 API 资源都作为子命令公开。这是一种从版本控制的 YAML 创建代理、环境、会话和其他资源并以交互方式检查响应的便捷方法。

|主题 | URL |提取提示|
| ------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
|人择CLI | `https://platform.claude.com/docs/en/api/sdks/cli.md` | “提取 CLI 安装、身份验证、命令结构和 beta:agents/environments/sessions 命令” |

---

## 克劳德 API SDK 存储库

当缓存的 `{lang}/` 技能文件或上面的托管代理文档中未涵盖绑定（类、方法、命名空间、字段）时，WebFetch 这些。 SDK 包括对 `/v1/agents`、`/v1/sessions`、`/v1/environments` 的 beta 托管代理支持以及相关资源 — 在存储库中搜索 `BetaManagedAgents`、`beta.agents`、 `beta.sessions`，或该语言的等效命名空间。

| SDK | URL |提取提示|
| ---------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Python | `https://github.com/anthropics/anthropic-sdk-python` | “提取 beta 托管代理命名空间、类和方法签名（`client.beta.agents`、`client.beta.sessions`）” |
| TypeScript | `https://github.com/anthropics/anthropic-sdk-typescript` | “提取 beta 托管代理命名空间、类和方法签名（`client.beta.agents`、`client.beta.sessions`）” |
|爪哇 | `https://github.com/anthropics/anthropic-sdk-java` | “提取 beta 托管代理类、构建器和方法签名（`client.beta().agents()`、`BetaManagedAgents*`）”|
|去 | `https://github.com/anthropics/anthropic-sdk-go` | “提取 beta 托管代理类型和方法签名（`client.Beta.Agents`、`BetaManagedAgents*` 事件类型）” |
|红宝石 | `https://github.com/anthropics/anthropic-sdk-ruby` | “提取 beta 托管代理方法和参数形状（`client.beta.agents`、`client.beta.sessions`）” |
| C# | `https://github.com/anthropics/anthropic-sdk-csharp` | “提取 beta 托管代理类和方法签名（NuGet 包，`BetaManagedAgents*` 类型）” |
| PHP | `https://github.com/anthropics/anthropic-sdk-php` | “提取 beta 托管代理类和方法签名（`$client->beta->agents`、`BetaManagedAgents*` 参数）”|

---

## 后备策略

如果 WebFetch 失败（网络问题，URL 已更改）：

1. 使用特定于语言的文件中的缓存内容（注意缓存日期）
2. 告知用户数据可能已过时
3. 建议他们直接检查 platform.claude.com 或 GitHub 存储库
</doc>

<doc path="shared/managed-agents-api-reference.md">
# 托管代理 — 端点参考

所有端点都需要 `x-api-key` 和 `anthropic-version: 2023-06-01` 标头。托管代理端点还需要 `anthropic-beta` 标头。

## 测试版标头```
anthropic-beta: managed-agents-2026-04-01
```SDK 自动为所有 `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` 调用添加此标头。技能端点使用`skills-2025-10-02`；文件端点使用 `files-api-2025-04-14`。

---

## SDK 方法参考

所有资源都位于 `beta` 命名空间下。 Python 和 TypeScript 共享相同的方法名称。

|资源 | Python / TypeScript (`client.beta.*`) |去 (`client.Beta.*`) |
| --- | --- | --- |
|代理| `agents.create` / `retrieve` / `update` / `list` / `archive` | `Agents.New` / `Get` / `Update` / `List` / `Archive` |
|代理版本 | `agents.versions.list` | `Agents.Versions.List` |
|环境 | `environments.create` / `retrieve` / `update` / `list` / `delete` / `archive` | `Environments.New` / `Get` / `Update` / `List` / `Delete` / `Archive` |
|环境工作（自托管）| `environments.work.poller` / `stats` / `stop` |参见 `shared/managed-agents-self-hosted-sandboxes.md` |
|会议 | `sessions.create` / `retrieve` / `update` / `list` / `delete` / `archive` | `Sessions.New` / `Get` / `Update` / `List` / `Delete` / `Archive` |
|会议活动 | `sessions.events.list` / `send` / `stream` | `Sessions.Events.List` / `Send` / `StreamEvents` |
|会话主题 | `sessions.threads.list` / `retrieve` / `archive`; `sessions.threads.events.list` / `stream` | `Sessions.Threads.List` / `Get` / `Archive`; `Sessions.Threads.Events.List` / `StreamEvents` |
|会议资源 | `sessions.resources.add` / `retrieve` / `update` / `list` / `delete` | `Sessions.Resources.Add` / `Get` / `Update` / `List` / `Delete` |
|保险库 | `vaults.create` / `retrieve` / `update` / `list` / `delete` / `archive` | `Vaults.New` / `Get` / `Update` / `List` / `Delete` / `Archive` |
|证书 | `vaults.credentials.create` / `retrieve` / `update` / `list` / `delete` / `archive` / `mcp_oauth_validate` | `Vaults.Credentials.New` / `Get` / `Update` / `List` / `Delete` / `Archive` / `McpOauthValidate` |
|内存存储 | `memory_stores.create` / `retrieve` / `update` / `list` / `delete` / `archive` | `MemoryStores.New` / `Get` / `Update` / `List` / `Delete` / `Archive` |
|回忆| `memory_stores.memories.create` / `retrieve` / `update` / `list` / `delete` | `MemoryStores.Memories.New` / `Get` / `Update` / `List` / `Delete` |
|内存版本 | `memory_stores.memory_versions.list` / `retrieve` / `redact` | `MemoryStores.MemoryVersions.List` / `Get` / `Redact` |

**需要注意的命名怪癖：**
- 代理和会话线程**没有 delete** — 只有 `archive`。存档是**永久**：代理变为只读，新会话无法引用它，并且无法取消存档。在归档生产代理之前与用户确认。环境、会话、保管库、凭证和内存存储都有 `delete` 和 `archive`；会话资源、文件、技能和记忆仅限于 `delete`；内存版本两者都没有——只有 `redact`。
- 会话资源使用 `add`（不是 `create`）。
- Go 的事件流是 `StreamEvents` （不是 `Stream`）。
- 自托管工作线程**不在** `client.beta.*` 下 - 它是来自 `anthropic.lib.environments` / `@anthropic-ai/sdk/helpers/beta/environments` 的 `EnvironmentWorker`；只有 `environments.work.poller/stats/stop` 是客户端方法。

**代理简写：** 会话创建时的 `agent` 接受裸字符串（`agent="agent_abc123"` — 使用最新版本）或完整引用对象 (`{type: "agent", id: "agent_abc123", version: 123}`)。

**模型简写：** 代理创建时的 `model` 接受裸字符串（`model="claude-opus-4-8"` — 使用 `standard` 速度）或完整配置对象 (`{id: "claude-opus-4-6", speed: "fast"}`)。注意：`speed: "fast"` 仅在 Opus 4.6 上受支持。

---

## 代理

**每个流程的第一步。** 会话需要预先创建的代理 - `managed-agents-2026-04-01` 下没有内联代理配置。

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------ | ---------------- | ---------------------------------------------------- |
| `GET` | `/v1/agents` |代理列表 |代理列表 |
| `POST` | `/v1/agents` |创建代理|创建保存的代理配置 |
| `GET` | `/v1/agents/{agent_id}` |获取代理 | Get代理详情|
| `POST` | `/v1/agents/{agent_id}` |更新代理 |更新代理配置 |
| `POST` | `/v1/agents/{agent_id}/archive` |档案代理|存档代理。使其**只读**；现有会话继续，新会话无法引用它。没有取消存档——这是最终状态。 |
| `GET` | `/v1/agents/{agent_id}/versions` |列出代理版本 |列出代理版本 |

## 会议

|方法|路径|运营|描述|
| -------- | ------------------------------------------------ | ---------------- | ---------------------------------------------------- |
| `GET` | `/v1/sessions` |列表会话 |列出会话（分页） |
| `POST` | `/v1/sessions` |创建会话 |创建新会话 |
| `GET` | `/v1/sessions/{session_id}` |获取会话 | Get 会议详情 |
| `POST` | `/v1/sessions/{session_id}` |更新会话 |更新会话 `metadata`/`title` 或 `agent.tools`/`agent.mcp_servers`/`vault_ids`（会话本地覆盖；会话必须是`idle`）。请参阅 `shared/managed-agents-core.md` → 在会话中更新代理配置。 |
| `DELETE` | `/v1/sessions/{session_id}` |删除会话 | Delete 一个会话 |
| `POST` | `/v1/sessions/{session_id}/archive` |档案会议 |存档会话 |

## 活动

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------ | ---------------- | ---------------------------------------------------- |
| `GET` | `/v1/sessions/{session_id}/events` |列表事件 |列出事件（轮询、分页）|
| `POST` | `/v1/sessions/{session_id}/events` |发送事件 |发送事件（用户消息、工具结果）|
| `GET` | `/v1/sessions/{session_id}/events/stream` |流媒体活动 |通过 SSE 串流事件 |

## 会话线程

多代理会话中的每个子代理事件流。参见 `shared/managed-agents-multiagent.md`。

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------ | ---------------- | ---------------------------------------------------- |
| `GET` | `/v1/sessions/{session_id}/threads` |列表线程 |列出主题（分页）|
| `GET` | `/v1/sessions/{session_id}/threads/{thread_id}` |获取线程 |检索一个线程（包含 `agent` 快照、`status`、`parent_thread_id`、`stats`、`usage`） |
| `POST` | `/v1/sessions/{session_id}/threads/{thread_id}/archive` |归档线程 |归档主题 |
| `GET` | `/v1/sessions/{session_id}/threads/{thread_id}/events` |列表线程事件 |列出一个线程的过去事件（分页）|
| `GET` | `/v1/sessions/{session_id}/threads/{thread_id}/stream` | StreamThread 事件 |通过 SSE 流式传输一个线程 (SDK: `threads.events.stream`) |

## 会议资源

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------------- | ---------------- | ---------------------------------------------------- |
| `GET` | `/v1/sessions/{session_id}/resources` |资源列表 |列出附加到会话的资源 |
| `POST` | `/v1/sessions/{session_id}/resources` |添加资源 |附加 `file` 或 `github_repository` 资源（SDK 方法：`add`，而不是 `create`）。 `memory_store` 资源仅在会话创建时附加。 |
| `GET` | `/v1/sessions/{session_id}/resources/{resource_id}` |获取资源 | Get 单个资源 |
| `POST` | `/v1/sessions/{session_id}/resources/{resource_id}` |更新资源 |更新资源 |
| `DELETE` | `/v1/sessions/{session_id}/resources/{resource_id}` |删除资源 |从会话中删除资源 |

## 环境

|方法|路径|运营|描述 |
| -------- | ---------------------------------------------------------------- | -------------------- | ----------------------------------- |
| `POST` | `/v1/environments` |创建环境|创造环境 |
| `GET` | `/v1/environments` |列出环境 |列出环境 |
| `GET` | `/v1/environments/{environment_id}` |获取环境 | Get 环境详情 |
| `POST` | `/v1/environments/{environment_id}` |更新环境 |更新环境 |
| `DELETE` | `/v1/environments/{environment_id}` |删除环境 | Delete 环境。返回 204。
| `POST` | `/v1/environments/{environment_id}/archive` |档案环境 |存档环境。使其**只读**；现有会话继续，新会话无法引用它。没有取消存档——这是最终状态。 |
| `GET` | `/v1/environments/{environment_id}/work/stats` |工作队列统计 |自托管工作队列深度/待处理/工作人员。 `x-api-key` 授权参见 `shared/managed-agents-self-hosted-sandboxes.md`。 |
| `POST` | `/v1/environments/{environment_id}/work/{work_id}/stop` |停止工作 |自托管：停止已声明的工作项。 `x-api-key` 授权|

对于 `type: "self_hosted"`，`config` 是裸 `{"type": "self_hosted"}` — `networking` 和 `packages` 不适用。

## 金库

保管库存储 Anthropic 代表您管理的 MCP 凭证 — 具有自动刷新功能的 OAuth 凭证或静态不记名令牌。通过 `vault_ids` 连接到会话。请参阅 `managed-agents-tools.md` §Vaults 了解概念指南和凭证形状。

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------ | ---------------- | ---------------------------------------------------- |
| `POST` | `/v1/vaults` |创建保管库 |创建保管库 |
| `GET` | `/v1/vaults` |列表Vaults |列出保险库 |
| `GET` | `/v1/vaults/{vault_id}` |获取金库 | Get 金库详情 |
| `POST` | `/v1/vaults/{vault_id}` |更新保管库 |更新金库 |
| `DELETE` | `/v1/vaults/{vault_id}` |删除保管库 | Delete 金库 |
| `POST` | `/v1/vaults/{vault_id}/archive` |档案库 |档案库 |

## 凭证

凭证是存储在保险库内的个人秘密。

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------------------------ | ------------------ | ---------------------------- |
| `POST` | `/v1/vaults/{vault_id}/credentials` |创建凭证 |创建凭证 |
| `GET` | `/v1/vaults/{vault_id}/credentials` |列表凭证 |列出保管库中的凭据 |
| `GET` | `/v1/vaults/{vault_id}/credentials/{credential_id}` |获取凭证 | Get 凭证元数据 |
| `POST` | `/v1/vaults/{vault_id}/credentials/{credential_id}` |更新凭证 |更新凭证 |
| `DELETE` | `/v1/vaults/{vault_id}/credentials/{credential_id}` |删除凭证 | Delete 凭证 |
| `POST` | `/v1/vaults/{vault_id}/credentials/{credential_id}/archive` |档案凭证 |归档凭证 |
| `POST` | `/v1/vaults/{vault_id}/credentials/{credential_id}/mcp_oauth_validate` | McpOauth验证 |验证 MCP OAuth 凭证 |

## 内存存储

跨会话保存的工作区范围的持久内存。通过 `resources[]` 中的 `{"type": "memory_store", "memory_store_id": ...}` 条目附加到会话（仅限会话创建时间）。有关概念指南、FUSE 安装代理界面、先决条件和版本控制，请参阅 `shared/managed-agents-memory.md`。

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------ | ------------------ | ---------------------------------------------------- |
| `POST` | `/v1/memory_stores` |创建内存存储 |创建商店（`name`、`description`、`metadata`）|
| `GET` | `/v1/memory_stores` |列出内存存储|列出商店（`include_archived`、`created_at_{gte,lte}`）|
| `GET` | `/v1/memory_stores/{memory_store_id}` |获取内存存储 | Get 店铺详情 |
| `POST` | `/v1/memory_stores/{memory_store_id}` |更新内存存储|更新商店 |
| `DELETE` | `/v1/memory_stores/{memory_store_id}` |删除内存存储 | Delete 商店 |
| `POST` | `/v1/memory_stores/{memory_store_id}/archive` |存档内存存储|档案商店。使其**只读**；现有会话继续，新会话无法引用它。没有取消存档。 |

## 回忆

商店内的单个文本文档（每个≤ 100KB）。 `create` 在 `path` 处创建，如果路径被占用，则返回 `409`（`memory_path_conflict_error`，与 `conflicting_memory_id`）； `update` 由 `mem_...` ID 突变（重命名和/或内容）。仅 `update` 接受 `precondition` (`{"type": "content_sha256", "content_sha256": ...}`) — 不匹配返回 `409` (`memory_precondition_failed_error`)。列表端点接受 `view: "basic"|"full"`（控制是否填充 `content`；`retrieve` 默认为 `full`）。

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------------------------ | -------------- | ---------------------------------------------------- |
| `GET` | `/v1/memory_stores/{memory_store_id}/memories` |列表回忆 |返回 `Memory \| MemoryPrefix`；按 `path_prefix`、`depth`、`order_by`/`order` 筛选 |
| `POST` | `/v1/memory_stores/{memory_store_id}/memories` |创建内存|在 `path` 创建（SDK：`memories.create`）； `409 memory_path_conflict_error` 如果被占用 |
| `GET` | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` |获取内存|读取1个内存（默认为`view="full"`）|
| `PATCH` | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` |更新内存 |通过 ID 更改 `content`、`path` 或两者；可选 `precondition` |
| `DELETE` | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` |删除内存| Delete（可选`expected_content_sha256`）|

## 内存版本

不可变的排列快照 (`memver_...`) — 审计和回滚表面。 `operation` ∈ `created` / `modified` / `deleted`。

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------------------------------------------------ | -------------------- | ---------------------------------------------------- |
| `GET` | `/v1/memory_stores/{memory_store_id}/memory_versions` |列出内存版本 |最新优先；按 `memory_id`、`operation`、`session_id`、`api_key_id`、`created_at_{gte,lte}` | 筛选
| `GET` | `/v1/memory_stores/{memory_store_id}/memory_versions/{version_id}` |获取内存版本 |列表字段 + 完整 `content` |
| `POST` | `/v1/memory_stores/{memory_store_id}/memory_versions/{version_id}/redact` |编辑内存版本 |透明 `content`/`content_sha256`/`content_size_bytes`/`path`；保留演员+时间戳|

## 文件

|方法|路径|运营|描述 |
| -------- | ------------------------------------------------ | ---------------- | ---------------------------------------------------- |
| `POST` | `/v1/files` |上传文件 |上传文件 |
| `GET` | `/v1/files` |列表文件 |列出文件 |
| `GET` | `/v1/files/{file_id}` |获取文件 | Get 文件元数据（SDK 方法：`retrieve_metadata`）|
| `GET` | `/v1/files/{file_id}/content` |下载文件 |下载文件内容 |
| `DELETE` | `/v1/files/{file_id}` |删除文件 | Delete 文件 |

## 技能

|方法|路径|运营|描述 |
| -------- | --------------------------------------------------------------------------- | ------------------ | ---------------------------- |
| `POST` | `/v1/skills` |创建技能 |创建技能|
| `GET` | `/v1/skills` |列表技能 |列出技能 |
| `GET` | `/v1/skills/{skill_id}` |获得技能 | Get技能详情|
| `DELETE` | `/v1/skills/{skill_id}` |删除技能 | Delete 一项技能 |
| `POST` | `/v1/skills/{skill_id}/versions` |创建版本 |创建技能版本 |
| `GET` | `/v1/skills/{skill_id}/versions` |列表版本 |列出技能版本 |
| `GET` | `/v1/skills/{skill_id}/versions/{version}` |获取版本 | Get技能版|
| `DELETE` | `/v1/skills/{skill_id}/versions/{version}` |删除版本 | Delete技能版|

---

## 请求/响应架构快速参考

### CreateAgent 请求正文

**始终从这里开始。** `model`、`system`、`tools`、`mcp_servers`、`skills` 是该对象上的顶级字段 — 它们不会进入会话。```json
{
  "name": "string (required, 1-256 chars)",
  "model": "claude-opus-4-8 (required — bare string, or {id, speed} object)",
  "description": "string (optional, up to 2048 chars)",
  "system": "string (optional, up to 100,000 chars)",
  "tools": [
    { "type": "agent_toolset_20260401" }
  ],
  "skills": [
    { "type": "anthropic", "skill_id": "xlsx" },
    { "type": "custom", "skill_id": "skill_abc123", "version": "1" }
  ],
  "mcp_servers": [
    {
      "type": "url",
      "name": "github",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  ],
  "multiagent": {
    "type": "coordinator",
    "agents": [
      "agent_abc123",
      { "type": "agent", "id": "agent_def456", "version": 4 },
      { "type": "self" }
    ]
  },
  "metadata": {
    "key": "value (max 16 pairs, keys ≤64 chars, values ≤512 chars)"
  }
}
```> 限制：`tools` 最大 128、`skills` 最大 20、`mcp_servers` 最大 20（唯一名称）。 `multiagent.agents` 1–20 个条目（字符串 ID | `{type:"agent",id,version?}` | `{type:"self"}`） — 请参阅 `shared/managed-agents-multiagent.md`。

### CreateSession 请求正文```json
{
  "agent": "agent_abc123 (required — string shorthand for latest version, or {type: \"agent\", id, version} object)",
  "environment_id": "env_abc123 (required)",
  "title": "string (optional)",
  "resources": [
    {
      "type": "github_repository",
      "url": "https://github.com/owner/repo (required)",
      "authorization_token": "ghp_... (required)",
      "mount_path": "/workspace/repo (optional — defaults to /workspace/<repo-name>)",
      "checkout": { "type": "branch", "name": "main" }
    }
  ],
  "vault_ids": ["vlt_abc123 (optional — MCP credentials with auto-refresh)"],
  "metadata": {
    "key": "value"
  }
}
```> `agent` 字段仅接受字符串 ID 或 `{type: "agent", id, version}` — `model`/`system`/`tools` 位于代理上，不在此处。
>
> **`checkout`** 接受 `{type: "branch", name: "..."}` 或 `{type: "commit", sha: "..."}`。省略存储库的默认分支。

### 创建环境请求正文```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "config": {
    "type": "cloud | self_hosted",
    "networking": {
      "type": "unrestricted | limited (union — see SDK types)"
    },
    "packages": { }
  },
  "metadata": { "key": "value" }
}
```### SendEvents 请求正文```json
{
  "events": [
    {
      "type": "user.message",
      "content": [
        {
          "type": "text",
          "text": "Hello"
        }
      ]
    }
  ]
}
```### 定义结果事件```json
{
  "type": "user.define_outcome",
  "description": "Build a DCF model for Costco in .xlsx",
  "rubric": { "type": "file", "file_id": "file_01..." },
  "max_iterations": 5
}
```> 需要 `rubric`：`{type: "text", content}` 或 `{type: "file", file_id}`。 `max_iterations` 默认 3 个，最大 20 个。与 `outcome_id` + `processed_at` 回显。参见 `shared/managed-agents-outcomes.md`。

### 工具结果事件```json
{
  "type": "user.custom_tool_result",
  "custom_tool_use_id": "sevt_abc123",
  "content": [{ "type": "text", "text": "Result data" }],
  "is_error": false
}
```---

## 错误处理

托管代理端点使用标准 Anthropic API 错误格式。返回错误，并带有 HTTP 状态代码和包含 `type`、`error` 和 `request_id` 的 JSON 正文：```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Description of what went wrong"
  },
  "request_id": "req_011CRv1W3XQ8XpFikNYG7RnE"
}
```向 Anthropic 报告问题时包括 `request_id` — 它可以让我们端到端地跟踪请求。内部 `error.type` 是以下之一：

|状态 |错误类型 |描述 |
|---|---|---|
| 400 | `invalid_request_error` |请求格式错误或缺少所需参数 |
| 401 | 401 `authentication_error` | API 密钥无效或丢失 |
| 403 | 403 `permission_error` | API 密钥没有执行此操作的权限 |
| 404 | 404 `not_found_error` |请求的资源不存在 |
| 409 | 409 `invalid_request_error` |请求与资源的当前状态冲突（例如，发送到存档会话）|
| 413 | 413 `request_too_large` |请求正文超出允许的最大大小 |
| 429 | 429 `rate_limit_error` |请求太多 — 检查速率限制标头以了解重试时间 |
| 500 | 500 `api_error` |发生内部服务器错误 |
| 529 | 529 `overloaded_error` |服务暂时超载 — 通过退避重试 |

请注意，`409 Conflict`携带`error.type: "invalid_request_error"`（没有单独的`conflict_error`类型）；检查 HTTP 状态和 `message` 以区分与其他无效请求的冲突。

---

## 速率限制

托管代理端点具有每个组织的每分钟请求 (RPM) 限制，独立于您的[消息 API 令牌限制](https://platform.claude.com/docs/en/api/rate-limits)。会话内的模型推理仍然借鉴组织的标准 ITPM/OTPM 限制。

|端点组 |范围 |转速|最大并发数 |
|---|---|---|---|
|创建操作（代理、会话、保管库）|组织| 300 | 300 — |
|所有其他操作（代理、会话、保管库）|组织| 600 | — |
|所有操作（环境）|组织| 60| 5 |

文件和技能端点使用标准的基于层的[速率限制](https://platform.claude.com/docs/en/api/rate-limits)。

当超出限制时，API 返回 `429`，其中包含 `rate_limit_error`（请参阅[错误处理](#error-handling) 了解响应信封）和 `retry-after` 标头，指示重试之前要等待多少秒。 Anthropic SDK 读取此标头并自动重试。
</doc>

<doc path="shared/managed-agents-client-patterns.md">
# 托管代理 — 常见客户端模式

您在驱动托管代理会话时将在客户端编写的模式，以工作 SDK 示例为基础。

代码示例为 TypeScript — Python 和 cURL 遵循相同的形状；有关等效项，请参见 `python/managed-agents/README.md` 和 `curl/managed-agents.md`。

---

## 1. 无损流重连

**问题：** SSE 没有重播。如果连接在会话中途断开，则简单的重新连接会重新打开来自 "now" 的流，并且您会默默地错过其间发出的每个事件。

**解决方案：**重新连接时，在使用直播流之前*通过 `events.list()` 获取完整的事件历史记录，并在直播流赶上时对事件 ID 进行重复数据删除。```ts
const seenEventIds = new Set<string>()
const stream = await client.beta.sessions.events.stream(session.id)

// Stream is now open and buffering server-side. Read history first.
for await (const event of client.beta.sessions.events.list(session.id)) {
  seenEventIds.add(event.id)
  handle(event)
}

// Tail the live stream. Dedupe only gates handle() — terminal checks must run
// even for already-seen events, or a terminal event that was in the history
// response gets skipped by `continue` and the loop never exits.
for await (const event of stream) {
  if (!seenEventIds.has(event.id)) {
    seenEventIds.add(event.id)
    handle(event)
  }
  if (event.type === 'session.status_terminated') break
  if (event.type === 'session.status_idle' && event.stop_reason.type !== 'requires_action') break
}
```---

## 2. `processed_at` — 已排队与已处理

流中的每个事件都带有 `processed_at` (ISO 8601)。对于客户端发送的事件（`user.message`、`user.interrupt`、`user.tool_confirmation`、`user.custom_tool_result`），当事件已排队但尚未被代理拾取时，它是 `null`，并且一旦代理处理它，就会填充它。同一事件在流中出现两次 - 一次使用 `processed_at: null`，一次使用时间戳。```ts
for await (const event of stream) {
  if (event.type === 'user.message') {
    if (event.processed_at == null) onQueued(event.id)
    else onProcessed(event.id, event.processed_at)
  }
}
```使用它来驱动您发送的任何内容的待处理→已确认的 UI 状态。如何将本地呈现的乐观消息映射到服务器分配的 `event.id` 取决于应用程序（通常通过 `events.send()` 的返回值或 FIFO 排序）。

---

## 3. 中断正在运行的会话

作为正常事件发送 `user.interrupt`。会话持续运行，直到达到安全边界，然后进入空闲状态。```ts
await client.beta.sessions.events.send(session.id, {
  events: [{ type: 'user.interrupt' }],
})

// Drain until the session is truly done — see Pattern 5 for the full gate.
for await (const event of stream) {
  if (event.type === 'session.status_terminated') break
  if (
    event.type === 'session.status_idle' &&
    event.stop_reason.type !== 'requires_action'
  ) break
}
```参考：`interrupt.ts` — 在看到 `span.model_request_start` 时发送中断，排空至空闲状态，然后通过 `sessions.retrieve()` 进行验证。

---

## 4.`tool_confirmation` 往返

当代理具有 `permission_policy: { type: 'always_ask' }` 时，对该工具的任何调用都会触发带有 `evaluated_permission === 'ask'` 的 `agent.tool_use` 事件，并且会话将空闲以等待决策。回复 `user.tool_confirmation`。```ts
for await (const event of stream) {
  if (event.type === 'agent.tool_use' && event.evaluated_permission === 'ask') {
    await client.beta.sessions.events.send(session.id, {
      events: [{
        type: 'user.tool_confirmation',
        tool_use_id: event.id,         // not a toolu_ id — use event.id
        result: 'allow',               // or 'deny'
        // deny_message: '...',        // optional, only with result: 'deny'
      }],
    })
  }
}
```要点：
- `tool_use_id` 是 `event.id`（通常为 `sevt_...`），**不是** `toolu_...` ID。
- `result` 是 `'allow' | 'deny'`。使用 `deny_message` 告诉模型您拒绝的“原因”——它会返回给代理。
- 多个待处理工具：使用 `evaluated_permission === 'ask'` 对每个 `agent.tool_use` 事件响应一次。

参考号：`tool-permissions.ts`。

---

## 5. 正确的怠速中断门

请勿单独破坏 `session.status_idle`。会话暂时空闲——例如在并行工具执行之间、等待 `user.tool_confirmation` 时或等待 `user.custom_tool_result` 时。空闲时通过端子 `stop_reason` 或 `session.status_terminated` 断开。```ts
for await (const event of stream) {
  handle(event)
  if (event.type === 'session.status_terminated') break
  if (event.type === 'session.status_idle') {
    if (event.stop_reason.type === 'requires_action') continue // waiting on you — handle it
    break // end_turn or retries_exhausted — both terminal
  }
}
````stop_reason.type` 上的 `session.status_idle` 值：
- `requires_action` — 代理正在等待客户端事件（工具确认、自定义工具结果）。处理好，别弄坏。
- `retries_exhausted` — 终端故障。中断，然后检查 `sessions.retrieve()` 的错误状态。
- `end_turn` — 正常完成。

---

## 6. Post-空闲状态-写入竞赛

在会话的可查询状态反映之前，SSE 流会稍微发出 `session.status_idle`。空闲时中断并立即调用 `sessions.delete()` 或 `sessions.archive()` 的客户端将间歇性地返回 400，并显示“运行时无法 delete/archive”。

清理前轮询：```ts
let s
for (let i = 0; i < 10; i++) {
  s = await client.beta.sessions.retrieve(session.id)
  if (s.status !== 'running') break
  await new Promise(r => setTimeout(r, 200))
}
if (s?.status !== 'running') {
  await client.beta.sessions.archive(session.id)
} // else: still running after 2s — don't archive, let it settle or escalate
```---

## 7. 先流，后发送

始终在发送启动事件之前**打开流。否则，代理可能会在附加消费者之前处理事件并发出第一个事件，而您将错过它们。```ts
const stream = await client.beta.sessions.events.stream(session.id)
await client.beta.sessions.events.send(session.id, {
  events: [{ type: 'user.message', content: [{ type: 'text', text: 'Hello' }] }],
})
for await (const event of stream) { /* ... */ }
````Promise.all([stream, send])` 形状也可以工作，但流优先更简单并且具有相同的效果 - 流在打开时开始缓冲。

---

## 8. 文件挂载陷阱

**装载的资源具有与您上传的文件不同的 `file_id`。** 会话创建会生成会话范围的副本。```ts
const uploaded = await client.beta.files.upload({ file, purpose: 'agent_resource' })
// uploaded.id         → the original file
const session = await client.beta.sessions.create({
  /* ... */
  resources: [{ type: 'file', file_id: uploaded.id, mount_path: '/workspace/data.csv' }],
})
// session.resources[0].file_id !== uploaded.id  ← different IDs
```Delete 原图来自 `files.delete(uploaded.id)`；会话范围内的副本与会话一起被垃圾收集。 `mount_path` 必须是绝对的 — 请参阅 `shared/managed-agents-environments.md`。

---

## 9. 非 MCP API 和 CLI 的秘密 — 通过自定义工具将它们保留在主机端

**问题：**您希望代理调用第三方 API 或运行需要密钥（API 密钥、令牌、服务帐户凭据）的 CLI，但当前无法在会话容器内设置环境变量，并且保管库当前保存仅 MCP 凭证 — 它们不会暴露给容器的 shell。因此，`curl`、已安装的 CLI 或通过 `bash` 工具运行的 SDK 客户端没有一流的位置可以读取机密。

**解决方案：** 将经过身份验证的呼叫移至您这边。在代理上声明自定义工具；当代理发出 `agent.custom_tool_use` 时，您的协调器（读取 SSE 流的进程）使用自己的凭据执行调用，并使用 `user.custom_tool_result` 进行响应。容器永远看不到密钥。```ts
// Agent template: declare the tool, no credentials
tools: [{ type: 'custom', name: 'linear_graphql', input_schema: { /* query, vars */ } }]

// Orchestrator: handle the call with host-side creds
for await (const event of stream) {
  if (event.type === 'agent.custom_tool_use' && event.name === 'linear_graphql') {
    const result = await linear.request(event.input.query, event.input.vars) // host's key
    await client.beta.sessions.events.send(session.id, {
      events: [{ type: 'user.custom_tool_result', tool_use_id: event.id, result }],
    })
  }
}
```相同的形状适用于 `gh` CLI、本地 eval 脚本或需要主机端身份验证或二进制文件的任何其他内容。

**安全说明：** 这不会公开公共端点。 `agent.custom_tool_use` 到达您的协调器已使用 Anthropic API 密钥打开的 SSE 流，并且 `user.custom_tool_result` 在同一密钥下通过 `events.send()` 返回。您的编排器是客户端，而不是服务器 - 未经身份验证的任何内容都不会监听。

**不要将 API 密钥嵌入系统提示或用户消息中作为解决方法。** 提示和消息存储在会话的事件历史记录中，由 `events.list()` 返回，并包含在压缩摘要中 — 放置在那里的秘密可通过 API 永久保留并可读会议的。
</doc>

<doc path="shared/managed-agents-core.md">
# 托管代理 — 核心概念

## 架构

托管代理围绕四个核心概念构建：

|概念 |端点 |它是什么 |
|---|---|---|
| **代理** | `/v1/agents` |定义代理功能和角色的持久版本化对象：模型、系统提示、工具、MCP 服务器、技能。 **必须在开始会话之前创建。** 请参阅下面的代理部分。 |
| **会议** | `/v1/sessions` |与代理的有状态交互。通过 ID + 环境 + 初始指令引用预先创建的代理。产生事件流。 |
| **环境** | `/v1/environments` |定义容器配置的模板。 |
| **集装箱** |不适用 |一个隔离的计算实例，代理的 **工具** 在其中执行（bash、文件操作、代码）。代理循环不在这里运行——它运行在 Anthropic 的编排层上，并通过工具调用作用于容器。 |```
                       ┌─────────────────────────────────────┐
                       │  Anthropic orchestration layer      │
Agent (config) ───────▶│  (agent loop: Claude + tool calls)  │
                       └──────────────┬──────────────────────┘
                                      │ tool calls
                                      ▼
Environment (template) ──▶ Container (tool execution workspace)
                                 │
                         Session ─┤
                                 ├── Resources (files, repos, memory stores — attached at startup)
                                 ├── Vault IDs (MCP credential references)
                                 └── Conversation (event stream in/out)
```> **创建代理是先决条件。** 会话通过 ID 引用预先创建的代理 — `model`/`system`/`tools` 存在于代理对象上，而不存在于会话上。每个流程都以 `POST /v1/agents` 开头。

---

## 会话生命周期```
rescheduling → running ↔ idle → terminated
```|状态 |描述 |
| -------------- | ------------------------------------------------------------------ |
| `idle` |代理已完成当前任务，正在等待输入。它要么等待输入以通过 `user.message` 继续工作，要么被阻止等待 `user.custom_tool_result` 或 `user.tool_confirmation`。随附的 `stop_reason` 包含有关代理停止工作原因的更多信息。 |
| `running` |会话已开始运行，代理正在积极工作。 |
| `rescheduling` |发生可重试错误后，会话正在（重新）调度，准备好被编排系统拾取。 |
| `terminated` |会话已终止，进入不可逆转且无法使用的状态。  |

- 当会话为 `running` 或 `idle` 时，可以发送事件。消息按顺序排队并处理。
- 代理在收到新事件时转换 `idle → running`，然后在完成后返回到 `idle`。
- 错误在流中显示为 `session.error` 事件，而不是状态值。

### 内置会话功能

- **上下文压缩** — 如果您接近最大上下文，API 会自动压缩会话历史记录以保持交互继续
- **提示缓存** — 历史重复令牌被缓存，减少处理时间和成本
- **扩展思考** — 默认情况下打开，以 `agent.thinking` 事件的形式返回

### 会话操作

|运营|笔记|
|---|---|
|列表/获取 |按 ID 分页列表或单个资源 |
|更新 |仅`title`可更新|
|档案 |会话变为**只读**。不可逆。 |
| Delete |永久删除会话、事件历史记录、容器和检查点。 |

这些是操作/检查调用——通常是从终端发出的，而不是应用程序代码。从外壳（参见 `shared/anthropic-cli.md`）：```sh
ant beta:sessions list --transform '{id,title,status,created_at}' --format jsonl
ant beta:sessions retrieve --session-id "$SID"
ant beta:sessions:events stream --session-id "$SID"   # watch events live
ant beta:sessions archive  --session-id "$SID"
ant beta:sessions delete   --session-id "$SID"
```---

## 会议

会话是环境中正在运行的代理实例。

### 会话对象

API返回的关键字段：

|领域 |类型 |描述 |
| ---------------- | -------- | --------------------------------------------------- |
| `type` |字符串|始终 `"session"` |
| `id` |字符串|唯一的会话ID |
| `title` |字符串|人类可读的标题 |
| `status` |字符串| `idle`、`running`、`rescheduling`、`terminated` |
| `created_at` |字符串| ISO 8601 时间戳 |
| `updated_at` |字符串| ISO 8601 时间戳 |
| `archived_at` |字符串| ISO 8601 时间戳（可为空） |
| `environment_id` |字符串|环境 ID |
| `agent` |对象|代理配置|
| `resources` |数组|附加文件、存储库和内存存储 |
| `metadata` |对象|用户提供的键值对（最多 8 个键）|
| `usage` |对象|代币使用统计 |

### 创建会话

**没有代理，会话就没有意义。** 会话通过 ID 引用预先创建的代理。首先通过 `agents.create()` 创建代理，然后引用它：```ts
// 1. Create the agent (reusable, versioned)
const agent = await client.beta.agents.create(
  {
    name: "Coding Assistant",
    model: "claude-opus-4-8",
    system: "You are a helpful coding agent.",
    tools: [{ type: "agent_toolset_20260401"}],
  },
);

// 2. Start a session that references it
const session = await client.beta.sessions.create(
  {
    agent: agent.id,  // string shorthand → latest version. Or: { type: "agent", id: agent.id, version: agent.version }
    environment_id: environmentId,
    title: "Hello World Session",
  },
);
```> 💡 **在控制台中实时观看。** 在开发时，打印一个链接，以便您可以单击进入会话 UI，而不是解析事件流：`https://platform.claude.com/workspaces/{workspace}/sessions/{session.id}`。使用 `default` 作为工作区 slug，除非您在非默认工作区中创建会话；您工作区的会话列表位于 `https://platform.claude.com/workspaces/default/sessions`。将此 `print`/`console.log` 包含在您为本地迭代的用户生成的代码中。

**会话创建参数：**

|领域|类型 |必填 |描述 |
| ---------------- | -------- | -------- | ---------------------------------------------------------- |
| `agent` |字符串或对象 | **是** |字符串简写 `"agent_abc123"`（最新版本）或 `{type: "agent", id, version}` |
| `environment_id`|字符串| **是** |环境 ID |
| `title` |字符串|没有 |人类可读的名称（出现在日志/仪表板中）|
| `resources` |数组|没有 |文件、GitHub 存储库或内存存储在启动时附加到容器。内存存储仅供会话创建（不可通过 `resources.add()` 添加）。 |
| `vault_ids` |数组|没有 |保管库 ID (`vlt_*`) — 具有自动刷新功能的 MCP 凭证。请参见 `shared/managed-agents-tools.md` → 保险库。 |
| `metadata` |对象|没有 |用户提供的键值对 |

**代理配置字段**（传递到 `agents.create()`，而不是 `sessions.create()`）：

|领域|类型 |必填 |描述 |
| ------------- | -------- | -------- | ---------------------------------------------------------- |
| `name` |字符串| **是** |人类可读的名称（1-256 个字符）|
| `model` |字符串或对象 | **是** | Claude 模型 ID（裸字符串，或 `{id, speed}` 对象）。支持所有 Claude 4.5+ 型号。 |
| `system` |字符串|没有 |系统提示符 — 定义代理的行为（最多 100K 个字符）|
| `tools` |数组|没有 |包括三种：(1) 预构建的 Claude Agent 工具 (`agent_toolset_20260401`)、(2) MCP 工具 (`mcp_toolset`) 和 (3) 自定义客户端工具。最大 128。
| `mcp_servers` |数组|没有 | MCP 服务器连接 — 标准化第三方功能（例如 GitHub、Asana）。最多 20 个，名称唯一。请参阅 `shared/managed-agents-tools.md` → MCP 服务器。 |
| `skills` |数组|没有 |定制的 "best-practices" 上下文，渐进式披露。最多 20 个。参见 `shared/managed-agents-tools.md` → 技能。 |
| `description` |字符串|没有 |代理描述（最多 2048 个字符）|
| `multiagent` |对象|没有 | `{type: "coordinator", agents: [...]}` — 该代理可以委派的名册。参见 `shared/managed-agents-multiagent.md`。 |
| `metadata` |对象|没有 |任意键值对（最多 16 个，键≤64 个字符，值≤512 个字符）|

---

## 代理

**这是每个托管代理流程开始的地方。** 代理对象是持久的、版本化的配置 - 您创建一次，然后在每次启动会话时通过 ID 引用它。无代理 → 无会话。

### 代理对象

API 是 **扁平** — `model`、`system`、`tools` 等是顶级字段，未包装在 `agent:{}` 子对象中。

|领域|类型 |必填 |描述 |
| ------------------ | -------- | -------- | -------------------------------------------------- |
| `name` |字符串|是的 |人类可读的名称 |
| `model` |字符串|是的 |克劳德型号 ID |
| `system` |字符串|没有 |系统提示|
| `tools` |数组|没有 |代理工具集/MCP 工具集/自定义工具|
| `mcp_servers` |数组|没有 | MCP 服务器连接 |
| `skills` |数组|没有 |技能参考（最多 20 条）|
| `description` |字符串|没有 |代理说明 |
| `multiagent` |对象|没有 |协调员名册 — 参见 `shared/managed-agents-multiagent.md` |
| `metadata` |对象|没有 |任意键值对 |

### 生命周期：创建一次，运行多次，就地更新

代理是一个**持久资源**，而不是每次运行的参数。预期模式：```
┌─ setup (once) ─────────┐     ┌─ runtime (every invocation) ─┐
│ agents.create()        │     │ sessions.create(             │
│   → store agent_id     │ ──→ │   agent={type:..., id: ID}   │
│     in config/env/db   │     │ )                            │
└────────────────────────┘     └──────────────────────────────┘
```**反模式：** 在每个脚本运行的顶部调用 `agents.create()`。这会累积孤立的代理对象，在每次调用时产生创建延迟，并破坏版本控制模型。如果您在名为 per-request 或 per-cron-tick 的函数中看到 `agents.create()`，那么这是错误的 - 将其提升到一次性设置并保留 ID。

> **推荐 — 将代理和环境定义为 YAML + 通过 `ant` CLI 应用。** 拆分为 **CLI 用于控制平面，SDK 用于数据平面**：代理环境是您使用 `ant` 管理的相对静态资源（版本控制的 YAML，从 CI 应用）；会话是动态的，由您的应用程序通过 SDK 驱动。有关 `ant beta:agents create < agent.yaml` / `update --version N` 流程，请参阅 `shared/anthropic-cli.md` → *版本控制的托管代理资源*。本文档其他地方显示的 SDK `agents.create()` 调用是代码内等效项 - 当您需要以编程方式配置时使用它，但更喜欢 YAML 流程来处理人类维护的任何内容。

### 版本控制

每个 `POST /v1/agents/{id}` （更新）都会创建一个新的不可变版本（数字时间戳，例如 `1772585501101368014`）。代理的历史记录仅可追加 — 您无法编辑过去的版本。

**为什么版本：**
- **再现性** — 将会话固定到已知良好的配置：`{type: "agent", id, version: 3}`
- **安全迭代** — 更新代理而不中断旧版本上已运行的会话
- **回滚** — 如果新的系统提示出现问题，请在调试时将新会话固定回之前的版本

**`version` 是可选的。** 省略它（或使用字符串简写 `agent="agent_abc123"`）到 get 在会话创建时的最新版本。将其明确 (`{type: "agent", id, version: N}`) 传递到引脚以实现可重复性。

**获取要固定的版本：** `agents.create()` 和 `agents.update()` 都在响应中返回 `version`。将其与 `agent_id` 一起存放。要获取现有代理的当前最新版本：`GET /v1/agents/{id}` → `.version`。

**何时更新与创建新的：**当它在概念上是具有调整行为的相同代理时更新（`POST /v1/agents/{id}`）（更好的提示，额外的工具）。当角色/目的不同时，创建一个新代理。经验法则：如果您给它相同的 `name`，请更新。

### 代理端点

|运营|方法|路径|
| ---------------- | -------- | -------------------------------------------------- |
|创建| `POST` | `/v1/agents` |
|列表 | `GET` | `/v1/agents` |
| Get | `GET` | `/v1/agents/{id}` |
|更新 | `POST` | `/v1/agents/{id}` |
|档案 | `POST` | `/v1/agents/{id}/archive` |

> ⚠️ **存档是永久的。**存档使代理只读：现有会话继续运行，但**新会话无法引用它**，并且没有取消存档。由于代理没有 `delete`，因此这是终端生命周期状态。切勿将生产代理归档为例行清理 - 首先与用户确认。

### 在会话中使用代理

通过字符串 ID（最新版本）或通过具有显式版本的对象引用代理：```python
# String shorthand — uses the agent's latest version
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment_id,
)

# Or pin to a specific version (int)
session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": agent.version},
    environment_id=environment_id,
)
```### 在会话中更新代理配置

`sessions.update()` 可以在 **现有** 会话上更改 `agent.tools`、`agent.mcp_servers`（包括权限策略）和 `vault_ids`。这是**会话本地覆盖** - 它不会创建新的代理版本，也不会传播回代理对象。提供的阵列是**完全替换**；添加一个工具 `GET` 会话，进行修改，然后将 `POST` 返回。会话必须是 `idle` — 如果正在运行，则首先中断。```python
client.beta.sessions.update(
    session.id,
    agent={
        "tools": [
            {"type": "agent_toolset_20260401"},
            {"type": "mcp_toolset", "mcp_server_name": "linear"},
        ],
        "mcp_servers": [{"type": "url", "name": "linear", "url": "https://mcp.linear.app/sse"}],
    },
    vault_ids=["vlt_..."],
)
```</doc>

<doc path="shared/managed-agents-environments.md">
# 托管代理 — 环境和资源

## 环境

创建会话需要 `environment_id`。环境是**可重用的配置模板**，用于在 Anthropic 的基础设施中启动容器 - 您可以为不同的用例创建不同的环境（例如，数据可视化与 Web 开发，使用不同的包集）。 Anthropic 处理扩展、容器生命周期和工作编排。

**环境名称必须是唯一的。** 使用现有名称创建环境会返回 409。

### 网络

|网络政策|描述 |
| ---------------- | ------------------------------------------------------------------------ |
| `unrestricted` |完全出口（合法阻止列表除外）|
| `limited` |默认拒绝；通过 `allowed_hosts` / `allow_package_managers` / `allow_mcp_servers` 选择加入 |```json
{
  "networking": {
    "type": "limited",
    "allow_package_managers": true,
    "allow_mcp_servers": true,
    "allowed_hosts": ["api.example.com"]
  }
}
```所有三个 `limited` 字段都是可选的。 `allow_package_managers`（默认`false`）允许PyPI/npm等； `allow_mcp_servers`（默认 `false`）允许代理配置的 MCP 服务器端点，而不将它们列在 `allowed_hosts` 中。

**MCP 警告：** 在 `limited` 网络下，设置 `allow_mcp_servers: true` 或将每个 MCP 服务器域添加到 `allowed_hosts`。否则容器无法到达它们并且工具会默默地失败。

### 创建环境

SDK 自动添加 `managed-agents-2026-04-01`。 TypeScript：```ts
const env = await client.beta.environments.create({
  name: "my_env",
  config: {
    type: "cloud",
    networking: { type: "unrestricted" },
  },
});
```### 自托管沙箱

要在**您自己的基础设施**而不是 Anthropic 的基础设施中运行工具执行，请设置 `config: {type: "self_hosted"}` - 代理循环保留在 Anthropic 一侧，但 `bash` / 文件操作 / 代码在您通过出站轮询工作人员控制的容器中执行。 `networking` 块不适用（您控制出口）。资源安装（`file`、`github_repository`）和内存存储的行为不同 - 请参阅 `shared/managed-agents-self-hosted-sandboxes.md` 了解工作线程、凭证以及云与自托管的比较。

### 环境增删改查

|运营|方法|路径|笔记|
| ---------------- | -------- | ------------------------------------------------------ | -----|
|创建| `POST` | `/v1/environments` | |
|列表 | `GET` | `/v1/environments` |分页（`limit`、`after_id`、`before_id`）|
| Get | `GET` | `/v1/environments/{id}` | |
|更新 | `POST` | `/v1/environments/{id}` |更改仅适用于**新**容器；现有会话保留其原始配置 |
| Delete | `DELETE` | `/v1/environments/{id}` |返回 204。
|档案 | `POST` | `/v1/environments/{id}/archive` |使其**只读**；现有会话继续，新会话无法引用它。没有取消归档——最终状态。 |

---

## 资源

将文件、GitHub 存储库和内存存储附加到会话。 **会话创建会阻塞，直到安装所有资源** — 在每个文件和存储库都就位之前，容器不会运行 `running`。每个会话最多 **999 个文件资源**。每个会话支持多个 GitHub 存储库。有关 `type: "memory_store"` 资源（持久跨会话内存 — 每个会话最多 8 个），请参阅 `shared/managed-agents-memory.md`。

### 文件上传（输入 — 主机 → 代理）

首先通过文件 API 上传文件，然后通过 `file_id` + `mount_path` 引用：```ts
// 1. Upload
const file = await client.beta.files.upload({
  file: fs.createReadStream("data.csv"),
  purpose: "agent",
});

// 2. Attach as a session resource
const session = await client.beta.sessions.create({
  agent: agent.id,
  environment_id: envId,
  resources: [
    { type: "file", file_id: file.id, mount_path: "/workspace/data.csv" }
  ],
});
```**`mount_path` 是必需的**并且必须是绝对的。父目录是自动创建的。代理工作目录默认为 `/workspace`。文件以只读方式安装 - 代理将修改后的版本写入新路径。

### 会话输出（输出 — 代理 → 主机）

代理可以在会话期间将文件写入 `/mnt/session/outputs/`。这些由文件 API 自动捕获，然后可以列出和下载：```ts
// After the turn completes, list output files scoped to this session:
for await (const f of client.beta.files.list({
  scope_id: session.id,
  betas: ["managed-agents-2026-04-01"],
})) {
  console.log(f.filename, f.size_bytes);
  const resp = await client.beta.files.download(f.id);
  const text = await resp.text();
}
```**要求：**
- 的`write`工具（或`bash`) 必须启用代理才能创建输出文件。
- 会话范围`files.list` / `files.download`捕获写入的输出`/mnt/session/outputs/`。
- 过滤器参数是**`scope_id`**（REST 查询参数`?scope_id=<session_id>`）。这SDK的文件资源仅自动添加`files-api-2025-04-14`标题，所以通过`betas: ["managed-agents-2026-04-01"]`显式（或原始的两个标头HTTP) — 没有它API可能会拒绝`scope_id`作为未知领域。需要`@anthropic-ai/sdk` ≥ 0.88.0 / `anthropic` (Python) ≥ 0.92.0 — 旧版本无法输入`scope_id`。这`ant` CLI**尚未**暴露此标志；使用SDK或卷曲。
- 传递返回的会话ID`sessions.create()`逐字记录（例如`sesn_011CZx...`） - 这API验证前缀。
- 之间存在短暂的索引滞后（~1-3 秒）`session.status_idle`和输出文件出现在`files.list`。如果为空，请重试一次或两次。

> **回退时`scope_id`过滤不可用**（较旧SDK，或者端点返回错误）：发送后续`user.message`要求代理人`read`下的每个文件`/mnt/session/outputs/`并返回内容。代理将文件主体流式传输回来`agent.message`文本。这仅适用于文本文件并消耗输出令牌 - 使用它来解锁，而不是作为主路径。

这为您提供了一个双向文件桥：上传参考数据，下载代理工件。

### GitHub 存储库

在代理开始执行之前，在初始化期间将 GitHub 存储库克隆到会话容器中。代理可以通过以下方式读取、编辑、提交和推送`bash` (`git`）。每个会话支持多个存储库 - 添加一个`resources`每个存储库的条目。存储库被缓存，因此使用相同存储库的未来会话启动速度更快。

存储库在会话的生命周期内附加 - 要更改安装的存储库，请创建一个新会话。您**可以**轮换存储库的`authorization_token`在运行会话中通过`client.beta.sessions.resources.update(resource_id, {session_id, authorization_token})`;资源`id`在会话创建时返回`resources.list()`。

**字段：**

|领域 |必填 |笔记|
|---|---|---|
|`type` | ✅ | `"github_repository"` |
| `url`| ✅ | GitHub 存储库URL |
| `authorization_token`| ✅ |具有存储库访问权限的 GitHub 个人访问令牌。 **从未回响API回应。** |
|`mount_path`| ❌ |将克隆存储库的路径。默认为`/workspace/<repo-name>`. |
| `checkout` | ❌ | `{type: "branch", name: "..."}`或者`{type: "commit", sha: "..."}`。默认为存储库的默认分支。 |

**令牌权限级别**（细粒度 PAT）：
-`Contents: Read`— 仅克隆
-`Contents: Read and write`— 推送更改并创建拉取请求

**身份验证如何工作：**`authorization_token`永远不会被放置在容器内。`git pull` / `git push`针对附加存储库的 GitHub REST 调用通过 Anthropic 端 git 代理进行路由，该代理在请求离开沙箱后注入令牌。容器中运行的代码（包括代理编写的任何内容）无法读取或泄露。

> ️ **要生成拉取请求**，你还需要 GitHub **MCP服务器**访问 —`github_repository`资源仅提供文件系统+ git 访问权限。看`shared/managed-agents-tools.md` → MCP服务器。 PR 的工作流程是：编辑已挂载的仓库中的文件 → 通过推送分支`bash`（通过 git 代理使用身份验证`authorization_token`) → 通过创建 PRMCP `create_pull_request`工具（通过保管库验证）。

**TypeScript:**

```ts
// 1. Create the agent — declare GitHub MCP (no auth here)
const agent = await client.beta.agents.create(
  {
    name: 'GitHub Agent',
    model: 'claude-opus-4-8',
    mcp_servers: [
      { type: 'url', name: 'github', url: 'https://api.githubcopilot.com/mcp/' },
    ],
    tools: [
      { type: 'agent_toolset_20260401', default_config: { enabled: true } },
      { type: 'mcp_toolset', mcp_server_name: 'github' },
    ],
  },
);

// 2. Start a session — attach vault for MCP auth + mount the repo
const session = await client.beta.sessions.create({
  agent: agent.id,
  environment_id: envId,
  vault_ids: [vaultId],  // vault contains the GitHub MCP OAuth credential
  resources: [
    {
      type: 'github_repository',
      url: 'https://github.com/owner/repo',
      authorization_token: process.env.GITHUB_TOKEN,  // repo clone token (≠ MCP auth)
      checkout: { type: 'branch', name: 'main' },
    },
  ],
});
```**Python：**```python
import os

agent = client.beta.agents.create(
    name="GitHub Agent",
    model="claude-opus-4-8",
    mcp_servers=[{
        "type": "url",
        "name": "github",
        "url": "https://api.githubcopilot.com/mcp/",
    }],
    tools=[
        {"type": "agent_toolset_20260401", "default_config": {"enabled": True}},
        {"type": "mcp_toolset", "mcp_server_name": "github"},
    ],
)

session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=env_id,
    vault_ids=[vault_id],  # vault contains the GitHub MCP OAuth credential
    resources=[{
        "type": "github_repository",
        "url": "https://github.com/owner/repo",
        "authorization_token": os.environ["GITHUB_TOKEN"],  # repo clone token (≠ MCP auth)
        "checkout": {"type": "branch", "name": "main"},
    }],
)
```---

## 文件 API

上传和管理用作会话资源的文件，并下载代理写入 `/mnt/session/outputs/` 的文件。

|运营|方法|路径| SDK |
| ---------------- | -------- | -------------------------------------------------- | --- |
|上传 | `POST` | `/v1/files` | `client.beta.files.upload({ file })` |
|列表 | `GET` | `/v1/files?scope_id=...` | `client.beta.files.list({ scope_id, betas: ["managed-agents-2026-04-01"] })` |
| Get 元数据 | `GET` | `/v1/files/{id}` | `client.beta.files.retrieveMetadata(id)` |
|下载 | `GET` | `/v1/files/{id}/content` | `client.beta.files.download(id)` → `Response` |
| Delete | `DELETE` | `/v1/files/{id}` | `client.beta.files.delete(id)` |

List 上的 `scope_id` 过滤器将结果范围限定为该会话写入 `/mnt/session/outputs/` 的文件。如果没有过滤器，您 get 所有文件都会上传到您的帐户。
</doc>

<doc path="shared/managed-agents-events.md">
# 托管代理 — 事件和指导

## 活动

### 发送事件

通过 `POST /v1/sessions/{id}/events` 将事件发送到会话。

|事件类型 |何时发送 |
| ---------------------------------- | --------------------------------------------------- |
| `user.message` |发送用户消息 |
| `user.interrupt` |在代理运行时中断它 |
| `user.tool_confirmation` |批准/拒绝工具调用（当 `always_ask` 策略时）|
| `user.custom_tool_result` |提供自定义工具调用的结果 |
| `user.define_outcome` |启动一个按标题分级的迭代循环 — 请参阅 `shared/managed-agents-outcomes.md` |

### 接收事件

三种方法：

1. **流式传输 (SSE)**：`GET /v1/sessions/{id}/events/stream` — 实时服务器发送的事件。 **长寿** — 服务器定期发送心跳以保持连接处于活动状态。
2. **轮询**：`GET /v1/sessions/{id}/events` — 分页事件列表（查询参数：`limit` 默认 1000、`page`）。 **立即返回** — 这是一个普通的分页 GET，而不是一个长轮询。
3. **Webhooks**：Anthropic POST 会话状态转换到您的 HTTPS 端点 — 精简负载（仅 ID）、HMAC 签名、控制台注册。参见 `shared/managed-agents-webhooks.md`。

所有收到的事件都带有 `id`、`type` 和 `processed_at`（ISO 8601；如果代理尚未处理，则为 `null`）。

> ⚠️ **稳健的轮询（原始 HTTP）。** 如果您绕过 SDK 并运行自己的轮询循环，请不要依赖 `requests` 或 `httpx` 超时作为挂钟上限 - 它们是**每块**读取超时，每次字节到达时重置。即使使用 `timeout=(5, 60)` 或 `httpx.Timeout(120)`，缓慢的响应（心跳、楔入的分块编码主体、行为不当的代理）也可以无限期地阻止调用。这两个库都没有内置“总挂钟”超时。对于严格的截止日期：在循环级别跟踪 `time.monotonic()` 并在单个请求超出预算时中断/取消（例如，通过看门狗线程，或围绕异步 httpx 的 `asyncio.wait_for()`）。 **首选 SDK** — `client.beta.sessions.events.stream()` 和 `client.beta.sessions.events.list()` 处理超时 + 理智重试。
>
> 如果 `GET /v1/sessions/{id}/events`（分页）在标头后挂起，则您可能错误地遇到了 `GET /v1/sessions/{id}/events` 或服务器端停顿 - 报告它；不要将其视为客户端配置问题。

### 事件类型（已接收）

事件类型使用点表示法，按命名空间分组：

|事件类型 |描述 |
| --- | --- |
| `agent.message` |代理文本输出 |
| `agent.thinking` |扩展思维块|
| `agent.tool_use` |代理使用了内置工具（`agent_toolset_20260401`）|
| `agent.tool_result` |内置工具的结果 |
| `agent.mcp_tool_use` |代理使用了 MCP 工具 |
| `agent.mcp_tool_result` |来自 MCP 工具的结果 |
| `agent.custom_tool_use` |代理调用了自定义工具 — 会话空闲，您使用 `user.custom_tool_result` 进行响应 |
| `agent.thread_context_compacted` |对话上下文被压缩 |
| `session.status_idle` |代理已完成当前任务，正在等待输入。它要么等待输入以通过 `user.message` 继续工作，要么被阻止等待 `user.custom_tool_result` 或 `user.tool_confirmation`。随附的 `stop_reason` 包含有关代理停止工作原因的更多信息。 |
| `session.status_running` |会话已开始运行，代理正在积极工作。 |
| `session.status_rescheduled` |发生可重试错误后，会话正在（重新）调度，准备好被编排系统拾取。 |
| `session.status_terminated` |会话已终止，进入不可逆转且无法使用的状态。  |
| `session.error` |处理过程中发生错误 |
| `span.model_request_start` |模型推理开始 |
| `span.model_request_end` |模型推理完成 |
| `span.outcome_evaluation_start` / `_ongoing` / `_end` |以结果为导向的课程的评分者进度 - 请参阅 `shared/managed-agents-outcomes.md` |
| `session.thread_created` |生成子代理线程（多代理）— 请参阅 `shared/managed-agents-multiagent.md` |
| `session.thread_status_running` / `_idle` / `_rescheduled` / `_terminated` |子代理线程状态转换（多代理）。 `_idle` 为 `stop_reason`。 |
| `agent.thread_message_sent` / `_received` |跨线程消息，携带`to_session_thread_id` / `from_session_thread_id`（多代理）|

该流还会回显用户发送的事件（`user.message`、`user.interrupt`、`user.tool_confirmation`、`user.custom_tool_result`、`user.define_outcome`）。

---

## 转向模式

通过事件表面推动会话的实用模式。

### 流优先排序

**发送事件之前打开流。**流仅传送打开*之后*发生的事件 - 它不会重播当前状态或历史事件。如果您先发送消息，然后打开流，则早期事件（包括快速状态转换）会在单个批次中缓冲到达，并且您将失去实时对它们做出反应的能力。```ts
// ✅ Correct — stream and send concurrently
const [response] = await Promise.all([
  streamEvents(sessionId),   // opens SSE connection
  sendMessage(sessionId, text),
]);

// ❌ Wrong — events before stream opens arrive as a single buffered batch
await sendMessage(sessionId, text);
const response = await streamEvents(sessionId);
```**有关完整历史记录**，请使用 `GET /v1/sessions/{id}/events`（分页列表）——该流仅向您提供连接之后的实时事件。

### 流丢失后重新连接

**SSE 流没有重播。** 如果您的连接断开（httpx 读取超时、网络故障）并且您重新连接，则*在*重新连接后，您只会发出 get 事件。间隙期间发出的任何事件都会从流中丢失。

**整合模式：** 在每次（重新）连接时，将流与历史记录获取重叠并按事件 ID 进行重复数据删除：```python
def connect_with_consolidation(client, session_id):
    # 1. Open the SSE stream first
    stream = client.beta.sessions.events.stream(session_id=session_id)

    # 2. Fetch history to cover any gap
    history = client.beta.sessions.events.list(
        session_id=session_id,
    )

    # 3. Yield history first, then stream — dedupe by event.id
    seen = set()
    for ev in history.data:
        seen.add(ev.id)
        yield ev
    for ev in stream:
        if ev.id not in seen:
            seen.add(ev.id)
            yield ev
```### 消息队列

**您不必在发送下一条消息之前等待响应。** 用户事件在服务器端排队并按顺序处理。这对于用户发送快速跟进的聊天桥非常有用：```ts
// All three go into one session; agent processes them in order
await sendMessage(sessionId, "Summarize the README");
await sendMessage(sessionId, "Actually also check the CONTRIBUTING guide");
await sendMessage(sessionId, "And compare the two");
// Stream once — agent responds to all three as a coherent turn
```事件可以随时发送到会话。无需等待特定会话状态即可通过 `client.beta.sessions.events.send()` 将新事件排入队列

### 中断

`interrupt` 事件**跳过队列**（在任何待处理的用户消息之前）并强制会话进入 `idle`。将此用于 "stop" / "nevermind" / "cancel" 命令：```ts
await client.beta.sessions.events.send(sessionId, {
  events: [{ type: 'interrupt' }],
});
```代理在任务中停止。它不会将中断视为消息——它只是停止。发送后续 `user` 事件来解释要做什么。如果结果有效，则中断还会标记 `span.outcome_evaluation_end.result: "interrupted"`（请参阅 `shared/managed-agents-outcomes.md`）。

> **注意**：在当前实现中，中断事件可能具有空 ID。进行故障排除时，请使用 `processed_at` 时间戳以及周围的事件 ID。

### 事件负载

有些事件除了状态更改本身之外还携带有用的元数据：

`session.status_idle` — 包括 `stop_reason` 字段，该字段详细说明会话停止的原因以及用户需要采取什么类型的进一步操作。```json
{
  "id": "sevt_456",
  "processed_at": "2026-04-07T04:27:43.197Z",
  "stop_reason": {
    "event_ids": [
      "sevt_123"
    ],
    "type": "requires_action"
  },
  "type": "status_idle"
}
````span.model_request_end` 包含用于成本跟踪和效率分析的 `model_usage` 字段：```json
{
  "type": "span.model_request_end",
  "id": "sevt_456",
  "is_error": false,
  "model_request_start_id": "sevt_123",
  "model_usage": {
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 6656,
    "input_tokens": 3571,
    "output_tokens": 727
  },
  "processed_at": "2026-04-07T04:11:32.189Z"
}
```**`agent.thread_context_compacted`** — 在汇总对话历史记录以适应上下文时发出。包括 `pre_compaction_tokens`，以便您知道被挤压了多少：```json
{
  "id": "sevt_abc123",
  "processed_at": "2026-03-24T14:05:15.787Z",
  "type": "agent.thread_context_compacted"
}
```### 存档

会话完成后，将其存档以释放资源：```ts
await client.beta.sessions.archive(sessionId);
```> 归档**会话**是例行清理——会话是每次运行且一次性的。 **不要将此推广到代理或环境**：这些是持久的、可重用的资源，并且对它们进行归档是永久性的（不能取消归档；新会话无法引用它们）。请参阅 `shared/managed-agents-overview.md` → 常见陷阱。
</doc>

<doc path="shared/managed-agents-memory.md">
# 托管代理 — 内存存储

> **公开测试版。** 内存存储在 `managed-agents-2026-04-01` beta 标头下发布； SDK 在所有 `client.beta.memory_stores.*` 呼叫上自动设置它。如果缺少 `client.beta.memory_stores`，请升级到最新的 SDK 版本。

默认情况下，会话是短暂的——当会话结束时，代理学到的任何东西都会消失。 **内存存储**是工作区范围内的小文本文档集合，在会话之间持续存在。当存储附加到会话时（通过 `resources[]`），它会作为文件系统目录安装到容器中；代理使用普通文件工具读取和写入它，系统提示符告诉它挂载就在那里。

内存的每次突变都会产生一个不可变的**内存版本** (`memver_...`)，为您提供审计跟踪和时间点回滚/编辑。

## 对象模型

|对象| ID 前缀 |范围 |笔记|
| --- | --- | --- | --- |
|内存存储| `memstore_...` |工作空间 |通过 `resources[]` 附加到会话 |
|内存| `mem_...` |商店 |一个文本文件，地址为 `path`（每个 ≤ 100KB — 更喜欢许多小文件）|
|记忆版 | `memver_...` |内存|每个突变的不可变快照； `operation` ∈ `created` / `modified` / `deleted` |

## 创建商店

`description` 被传递给代理，以便它知道商店包含什么 - 为模型编写它，而不是为人类编写。```python
store = client.beta.memory_stores.create(
    name="User Preferences",
    description="Per-user preferences and project context.",
)
print(store.id)  # memstore_01Hx...
```其他SDK：TypeScript `client.beta.memoryStores.create({...})`；转到 `client.Beta.MemoryStores.New(ctx, ...)`。有关每种语言的完整表，请参阅 `shared/managed-agents-api-reference.md` → SDK 方法参考。

商店支持 `retrieve` / `update` / `list`（带 `include_archived`、`created_at_{gte,lte}` 滤镜） / `delete` / **`archive`**。存档使存储只读 - 现有会话附件继续，新会话无法引用它；没有取消存档。

### 种子内容（可选）

在任何会话运行之前预加载参考材料。 `memories.create` 在给定的 `path` 处创建内存；如果内存已存在，则调用返回 `409`（`memory_path_conflict_error`，带有 `conflicting_memory_id`）。商店 ID 是第一个位置参数。```python
client.beta.memory_stores.memories.create(
    store.id,
    path="/formatting_standards.md",
    content="All reports use GAAP formatting. Dates are ISO-8601...",
)
```## 附加到会话

内存存储与 `file` 和 `github_repository` 资源一起位于会话的 `resources[]` 数组中（请参阅 `shared/managed-agents-environments.md` → 资源）。内存存储仅在 **会话创建时间** 附加 - `sessions.resources.add()` 不接受 `memory_store`。```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    resources=[
        {
            "type": "memory_store",
            "memory_store_id": store.id,
            "access": "read_write",  # or "read_only"; default is "read_write"
            "instructions": "User preferences and project context. Check before starting any task.",
        }
    ],
)
```|领域 |必填 |笔记|
| --- | --- | --- |
| `type` | ✅ | `"memory_store"` |
| `memory_store_id` | ✅ | `memstore_...` |
| `access` | — | `"read_write"`（默认）或 `"read_only"` — 在挂载的文件系统级别强制执行 |
| `instructions` | — |除了商店的 `name`/`description` 之外，还有针对该商店的会话特定指南。 ≤ 4,096 个字符。 |

**每个会话最多 8 个内存存储。** 当不同的内存片具有不同的所有者或生命周期时，附加多个内存存储 — 例如一个只读共享引用存储加上一个可读写的每用户存储，或者每个最终用户/团队/项目共享单个代理配置一个存储。

### 代理如何看待它（FUSE 安装）

每个附加存储都安装在 `/mnt/memory/<store-name>/` 的会话容器中。代理使用标准文件工具（`bash`、`read`、`write`、`edit`、`glob`、 `grep`) — 没有专用的内存工具。 `access: "read_only"` 使挂载在文件系统级别为只读； `"read_write"` 允许代理在其下创建、编辑和 delete 文件。每个挂载的简短描述（名称、路径、`instructions`、访问权限）会自动注入系统提示符中，以便代理知道该存储的存在，而无需您提及。

代理在挂载下进行的写入将持久保存回存储并生成内存版本，就像主机端 `memories.update` 调用一样。

## 直接管理内存（主机端）

使用它们来审查工作流程、纠正不良记忆或在带外播种商店。

### 列表

返回 `Memory | MemoryPrefix` 条目 — `MemoryPrefix`（`type: "memory_prefix"`，只是 `path`）在分层列出时是一个类似目录的节点。使用 `path_prefix` 范围（包括尾部斜杠：`"/notes/"` 匹配 `/notes/a.md` 但不匹配 `/notes_backup/old.md`）和 `depth` 来限制树遍历。 `order_by` / `order` 对结果进行排序。通过 `view="full"` 将 `content` 包含在每个项目中；默认 `"basic"` 仅返回元数据。```python
for m in client.beta.memory_stores.memories.list(store.id, path_prefix="/"):
    if m.type == "memory":
        print(f"{m.path}  ({m.content_size_bytes} bytes, sha={m.content_sha256[:8]})")
    else:  # "memory_prefix"
        print(f"{m.path}/")
```＃＃＃ 读```python
mem = client.beta.memory_stores.memories.retrieve(memory_id, memory_store_id=store.id)
print(mem.content)
````retrieve`默认为`view="full"`（包含内容）； `view` 主要与列表端点有关。

### 创建与更新

|运营|致辞 |语义 |
| --- | --- | --- |
| `memories.create(store_id, path=..., content=...)` | **路径** |创建于 `path`。如果路径已被占用，则为 `409`（`memory_path_conflict_error`，包括 `conflicting_memory_id`）。 |
| `memories.update(mem_id, memory_store_id=..., path=..., content=...)` | **`mem_...` ID** |改变现有的记忆。更改 `content`、`path`（重命名）或两者。重命名到占用的路径会返回相同的 `409 memory_path_conflict_error`。 |```python
mem = client.beta.memory_stores.memories.create(
    store.id,
    path="/preferences/formatting.md",
    content="Always use tabs, not spaces.",
)

client.beta.memory_stores.memories.update(
    mem.id,
    memory_store_id=store.id,
    path="/archive/2026_q1_formatting.md",  # rename
)
```### 乐观并发（以 `update` 为前提）

`memories.update` 接受 `precondition`，因此您可以读取 → 修改 → 写回，而不会破坏并发写入器。唯一支持的类型是 `content_sha256`。如果不匹配，API 将返回 `409` (`memory_precondition_failed_error`) — 重新读取并重试新状态。```python
client.beta.memory_stores.memories.update(
    mem.id,
    memory_store_id=store.id,
    content="CORRECTED: Always use 2-space indentation.",
    precondition={"type": "content_sha256", "content_sha256": mem.content_sha256},
)
```### Delete```python
client.beta.memory_stores.memories.delete(mem.id, memory_store_id=store.id)
```通过 `expected_content_sha256` 获得有条件的 delete。

## 审计和回滚——内存版本

每个突变都会创建一个不可变的 `memver_...` 快照。版本在父内存的生命周期内累积； `memories.retrieve` 始终返回当前头，版本端点为您提供历史记录。

|触发它的操作 | `operation` 字段上版本|
| --- | --- |
| `memories.create` 走在新的道路上 | `"created"` |
| `memories.update` 更改 `content`、`path` 或两者（或代理端写入挂载）| `"modified"` |
| `memories.delete` | `"deleted"` |

每个版本还记录 `created_by` — 一个带有 `type` ∈ `session_actor` / `api_actor` / `user_actor` 的 actor 对象 — 并且在编辑后， `redacted_at` + `redacted_by`。

### 列出版本

最新在前，分页。按 `memory_id`、`operation`、`session_id`、`api_key_id` 或 `created_at_gte` / `created_at_lte` 进行过滤。通过 `view="full"` 包含 `content`；默认仅元数据。```python
for v in client.beta.memory_stores.memory_versions.list(store.id, memory_id=mem.id):
    print(f"{v.id}: {v.operation}")
```### 检索版本```python
version = client.beta.memory_stores.memory_versions.retrieve(
    version_id, memory_store_id=store.id
)
print(version.content)
```### 编辑版本

擦除历史版本中的内容，同时保留审核跟踪（参与者 + 时间戳）。清除 `content`、`content_sha256`、`content_size_bytes` 和 `path`；其他一切都保留。用于泄露机密、PII 或用户删除请求。```python
client.beta.memory_stores.memory_versions.redact(version_id, memory_store_id=store.id)
```## 端点参考

请参阅 `shared/managed-agents-api-reference.md` → 内存存储/内存/内存版本，了解完整的 HTTP 方法/路径表。原始HTTP基本路径：```
POST   /v1/memory_stores
POST   /v1/memory_stores/{memory_store_id}/archive
GET    /v1/memory_stores/{memory_store_id}/memories
PATCH  /v1/memory_stores/{memory_store_id}/memories/{memory_id}
GET    /v1/memory_stores/{memory_store_id}/memory_versions
POST   /v1/memory_stores/{memory_store_id}/memory_versions/{version_id}/redact
```对于 cURL 示例和 CLI (`ant beta:memory-stores ...`)，请在 `shared/live-sources.md` → 托管代理中 WebFetch 内存 URL。
</doc>

<doc path="shared/managed-agents-multiagent.md">
# 托管代理 — 多代理会话

协调代理可以在一个会话中委托给其他代理。所有代理**共享容器和文件系统**；每个都在自己的 **线程** 中运行 - 一个上下文隔离的事件流，具有自己的对话历史记录、模型、系统提示、工具、MCP 服务器和技能（来自该代理自己的配置）。线程是持久的：协调器可以向其先前调用的子代理发送后续消息，并且该子代理保留其先前的轮次。

SDK 在所有 `client.beta.{agents,sessions}.*` 调用上自动设置 `managed-agents-2026-04-01` beta 标头；多代理不需要额外的标头。

---

## 声明协调员名单

`multiagent` 是 `agents.create()` / `agents.update()` 上的 **顶级字段** — **不是** `tools[]` 条目。 `agents` 列出 1–20 名名册条目。 `sessions.create()` 上没有任何变化 - 名册是从协调器的配置中解析的。```python
orchestrator = client.beta.agents.create(
    name="Engineering Lead",
    model="claude-opus-4-8",
    system="You coordinate engineering work. Delegate code review to the reviewer and test writing to the test agent.",
    tools=[{"type": "agent_toolset_20260401"}],
    multiagent={
        "type": "coordinator",
        "agents": [
            reviewer.id,                                            # bare string — latest version
            {"type": "agent", "id": test_writer.id, "version": 4},  # pinned version
            {"type": "self"},                                       # the coordinator itself
        ],
    },
)

session = client.beta.sessions.create(agent=orchestrator.id, environment_id=env.id)
```|名册条目 |形状|笔记|
|---|---|---|
|字符串简写 | `"agent_abc123"` |引用存储代理的最新版本。 |
|代理参考| `{type: "agent", id, version?}` |省略 `version` 以在协调器保存时间固定最新的值。 |
|自我| `{type: "self"}` |协调器可以生成自身的副本。 |

名册中最多 **20 名独特特工**；协调器可能会生成每个副本的**多个副本**。 **仅一级委派** — 深度 > 1 将被忽略。

---

## 线程

会话级事件流是**主线程** — 它显示协调器的跟踪以及子代理活动的精简视图（线程状态转换和跨线程消息，而不是每个子代理工具调用）。通过每线程端点深入到特定的子代理：

|运营| HTTP | SDK (`client.beta.sessions.threads.*`) |
|---|---|---|
|列出主题 | `GET /v1/sessions/{sid}/threads` | `.list(session_id)` |
|找回一个 | `GET /v1/sessions/{sid}/threads/{tid}` | `.retrieve(thread_id, session_id=...)` |
|档案 | `POST /v1/sessions/{sid}/threads/{tid}/archive` | `.archive(thread_id, session_id=...)` |
|列出线程事件 | `GET /v1/sessions/{sid}/threads/{tid}/events` | `.events.list(thread_id, session_id=...)` |
|流线程事件 | `GET /v1/sessions/{sid}/threads/{tid}/stream` | `.events.stream(thread_id, session_id=...)` |

每个 `SessionThread` 均携带 `id`、`status` (`running` | `idle` | `rescheduling` | `rescheduling` `terminated`)、`agent`（代理配置的已解析快照 — `id`、`name`、`model`、`system`、 `tools`、`skills`、`mcp_servers`、`version`)、`parent_thread_id`（主线程为空，包含在列表中）， `archived_at`，以及可选的 `stats`/`usage`。 **会话状态聚合线程状态** — 如果任何线程为 `running`，则 `session.status` 为 `running`。最多 **25 个并发线程**。当耗尽每个线程流时，在 `session.thread_status_idle` 上中断（并像检查会话级空闲一样检查其 `stop_reason`）。

---

## 多代理事件（在会话流上）

|活动 |有效载荷亮点|意义|
|---|---|---|
| `session.thread_created` | `session_thread_id`，`agent_name` |创建了一个新线程。 |
| `session.thread_status_running` | `session_thread_id`，`agent_name` |线程开始活动。 |
| `session.thread_status_idle` | `session_thread_id`，`agent_name`，**`stop_reason`** |线程正在等待输入。检查 `stop_reason`（与 `session.status_idle.stop_reason` 形状相同）。 |
| `session.thread_status_rescheduled` | `session_thread_id`，`agent_name` |线程在发生可重试错误后正在重新调度。 |
| `session.thread_status_terminated` | `session_thread_id`，`agent_name` |线程已存档或遇到终端错误。 |
| `agent.thread_message_sent` | `to_session_thread_id`、`to_agent_name`、`content` |协调器向另一个线程发送了后续任务。 |
| `agent.thread_message_received` | `from_session_thread_id`、`from_agent_name`、`content` |代理将其结果发送给协调器。 |

---

## 子代理线程中的工具权限和自定义工具

当子代理需要您的客户端（`always_ask` 确认或自定义工具结果）时，该请求将**交叉发布到主线程**，并使用 `session_thread_id` 标识原始线程 - 因此您只需观看会话流。回复 `user.tool_confirmation`（携带 `tool_use_id`）或 `user.custom_tool_result`（携带 `custom_tool_use_id`），并**回显原始事件中的 `session_thread_id`**（ SDK 参数类型和文档字符串期望它）。服务器还通过工具使用 ID 进行路由，因此回显是腰带式的而不是承重式的 - 但包括它。```python
for event_id in stop.event_ids:
    pending = events_by_id[event_id]
    confirmation = {
        "type": "user.tool_confirmation",
        "tool_use_id": event_id,
        "result": "allow",
    }
    if pending.session_thread_id is not None:
        confirmation["session_thread_id"] = pending.session_thread_id
    client.beta.sessions.events.send(session.id, events=[confirmation])
```相同的模式适用于 `user.custom_tool_result`。

---

## 陷阱

- **请勿将 put 列入 `sessions.create()` 或 `tools[]` 中的名册。** `multiagent` 是顶级代理字段；更新协调器，然后启动引用它的会话。
- **不要假设共享上下文。** 线程共享文件系统，但不共享对话历史记录或工具。如果协调器需要子代理来执行某些操作，则必须在委托消息中说明（或将其写入磁盘）。
- **深度 > 1 被忽略。** 子代理自己的 `multiagent` 花名册（如果有）不会级联 — 只有会话的协调员代表。

对于 Python 之外的每种语言绑定，WebFetch `https://platform.claude.com/docs/en/managed-agents/multi-agent.md`（请参阅 `shared/live-sources.md`）。
</doc>

<doc path="shared/managed-agents-onboarding.md">
# 托管代理 — 入职流程

> **通过 `/claude-api managed-agents-onboard` 调用？** 您来对地方了。进行下面的采访——不要向用户总结，而是提出问题。

当用户想要从头开始设置托管代理时，请使用此选项：**知识与探索分支 → 配置模板 → 设置会话 → 飞行前可行性检查 → 发出工作代码。** 飞行前检查 (§3) 不是可选的 - 缺少所需工具、凭据或数据访问的设置将在运行中失败，并且间隙通常在设置时可见。

> 与此一起阅读 `shared/managed-agents-core.md` — 它包含每个旋钮的完整详细信息。本文档是采访脚本，而不是参考资料。

---

Claude Managed Agents 是一个托管代理：Anthropic 在其编排层上运行代理循环，并为每个会话提供一个沙盒容器，代理的工具将在其中执行（或者，在 `self_hosted` 环境中，您自己的工作人员运行这些工具 — 请参阅 `shared/managed-agents-self-hosted-sandboxes.md`）。您提供代理配置和环境配置；工具（事件流、沙箱编排、提示缓存、上下文压缩和扩展思维）已为您处理。

**您提供什么：**
- **代理配置** — 工具、技能、模型、系统提示。可重用且版本化。
- **环境配置** — 您的代理工具在其中执行的沙箱（`cloud`：网络、包；或 `self_hosted`：您自己的基础设施）。可跨代理重复使用。

代理的每次运行都是一个**会话**。

---

## 1.了解或探索？

询问用户：

> 您是否已经知道您想要构建的代理，或者您想先探索一些常见模式？

### 探索路径 — 显示模式

四种形状，相同的运行时代码路径（`sessions.create()` → `sessions.events.send()` → 流）。只有触发器和接收器不同。

|图案|触发|示例|
|---|---|---|
|事件触发|网络钩子 | GitHub PR 推送 → CMA（GitHub 工具）→ Slack |
|预定 |克朗 |每日简报：浏览器 + GitHub + Jira → CMA → Slack |
|一劳永逸的公关 |人类 | Slack 斜杠命令→ CMA（GitHub 工具）→ PR 传递 CI |
|研究+仪表板|人类 |主题 → CMA（网络搜索 + `frontend-design` 技能）→ HTML 仪表板 |

询问哪种形状适合，然后使用它作为参考继续了解路径。

### 知道路径——配置模板

三轮。对每轮的问题进行批处理；不要一次问一个。

**A 轮 — 工具。** 从这里开始；这是最具体的部分。三种类型；询问用户想要哪个（任意组合）：

|类型 |它是什么 |如何指导|
|---|---|---|
| **预构建的 Claude Agent 工具** (`agent_toolset_20260401`) |即用型：`bash`、`read`、`write`、`edit`、`glob`、`grep`、 `web_fetch`、`web_search`。一次性全部启用，或通过 `enabled: true/false` 单独启用。 |建议启用完整的工具集。列出 8 个工具，以便用户知道他们将获得什么。完整详细信息：`shared/managed-agents-tools.md` → 代理工具集。 |
| **MCP 工具** |通过 `mcp_toolset` 进行第三方集成（GitHub、Linear、Asana 等）。凭证位于保险库中，而不是内联的。 |询问哪些服务。对于每个，请浏览 MCP 服务器 URL + 保管库凭据。完整详细信息：`shared/managed-agents-tools.md` → MCP 服务器 + 保管库。 |
| **自定义工具** |用户自己的应用程序处理这些工具调用 - 代理触发 `agent.custom_tool_use`，应用程序发回结果消息。 |询问每个工具：名称、描述、输入模式。处理事件的应用程序代码是*他们的*代码 - 不要生成它。完整详细信息：`shared/managed-agents-tools.md` → 自定义工具。 |

**B 轮 — 技能、文件和存储库。** 代理启动时手头上有什么。

*技能*——两种类型；两者的工作方式相同——克劳德在相关时自动使用它们。每个代理最多 20 个。
- [ ] **预建特工技能**：`xlsx`、`docx`、`pptx`、`pdf`。按名称参考。
- [ ] **自定义技能**：通过技能 API 上传到用户组织的技能。参考 `skill_id` + 可选`version`。如果该技能尚不存在，请引导用户完成`POST /v1/skills` + `POST /v1/skills/{id}/versions`（测试版标头`skills-2025-10-02`）。完整细节：`shared/managed-agents-tools.md`→ 技能+技能API。

*GitHub 存储库* — 代理需要在磁盘上存储任何存储库吗？对于每个：
- [ ] 回购协议URL (`https://github.com/org/repo`)
- [ ] `authorization_token`（PAT 或 GitHub 应用程序令牌范围仅限于存储库）
- [ ] 可选`mount_path`（默认为`/workspace/<repo-name>`） 和`checkout`（分支机构或 SHA）

发出为`resources: [{type: "github_repository", url, authorization_token, ...}]`。完整细节：`shared/managed-agents-environments.md`→ GitHub 存储库。

> ️ **PR创作需要GitHubMCP服务器也是。**`github_repository`只提供文件系统访问权限——要打开 PR，还要附加 GitHubMCPA 轮中的服务器并通过保险库对其进行凭证。工作流程是：编辑已挂载的仓库中的文件 → 通过推送分支`bash`→ 通过以下方式创建公关MCP `create_pull_request`工具。

*文件* — 用于为会话提供种子的任何本地文件？对于每个：
- [ ] 通过文件上传API→ 坚持`file_id`- [ ] 选择一个`mount_path`— 绝对的，例如`/workspace/data.csv`（父级自动创建；文件以只读方式挂载）

发出为`resources: [{type: "file", file_id, mount_path}]`。最多 999 个文件资源。代理工作目录默认为`/workspace`。完整细节：`shared/managed-agents-environments.md`→ 文件API。

**C轮——身份、成功标准、环境：**
- [ ] 姓名？
- [ ] Job（一两句话——成为系统提示）？
- [ ] **什么意思"done"看起来像？** 推动具体的、可检查的成功标准——不是“一份好的报告”，而是“带有数字的 CSV”`price`每个 SKU 的列。”明确的标准为代理提供了明确的目标，并让您验证结果；模糊的标准让它猜测什么"done"方法。如果它们是可评分的，请计划在第 2 节中连接**结果**，以便安全带根据它们进行评分和修改。看`shared/managed-agents-outcomes.md`。
- [ ] 网络：从容器不受限制的互联网，或锁定特定主机的出口？ （如果锁定，MCP服务器域必须位于`allowed_hosts`或者工具默默地失败。）
- [ ] 型号？ （默认`claude-opus-4-8`）

---

## 2. 设置会话

每次运行。指向代理+环境，附加凭据，启动。

**保管库凭据**（如果代理声明MCP服务器）：
- [ ] 现有保管库，还是创建一个？ （`client.beta.vaults.create()` + `vaults.credentials.create()`）

凭证是只写的，匹配MCP服务器由URL，自动刷新。看`shared/managed-agents-tools.md`→ 保险库。

**开球——选择一个：**
- [ ] **会话：** 第一`user.message`给代理。
- [ ] **结果分级**（当§C 轮产生可检查标准时推荐）：发送`user.define_outcome`用标题*而不是*a`user.message`— 该工具根据评分标准进行迭代和评分，直到满意为止。两个都不要发送。看`shared/managed-agents-outcomes.md`。

会话创建会阻塞，直到安装所有资源为止。在发送启动之前打开事件流。流是SSE；继续`session.status_terminated`，或在`session.status_idle`带终端`stop_reason`——即除了`requires_action`，在会话等待工具确认或自定义工具结果时短暂触发（请参阅`shared/managed-agents-client-patterns.md`模式 5）。使用量登陆`span.model_request_end`。代理编写的工件最终会出现在`/mnt/session/outputs/`— 通过下载`files.list({scope_id: session.id, betas: ["managed-agents-2026-04-01"]})`。

**控制台逃生舱口。** 在您发出的运行时块中，打印会话的控制台URL就在之后`sessions.create()`这样用户就可以在迭代时在 UI 中观看它：`print(f"Watch in Console: https://platform.claude.com/workspaces/default/sessions/{session.id}")`（交换`default`为用户的工作区 slug（如果他们指定了一个）。

---

## 3. 飞行前可行性检查——根据资源协调作业

**在发出任何代码之前执行此操作。** 常见的、可避免的失败是资源不足的运行：要求很明确，但代理缺少工具、凭据、数据访问或操作上下文。特工在几个回合后发现了差距，连忙失败，然后放弃——烧掉预算却什么也没产生。该间隙通常在设置时可见。在这里抓住它，而不是在会话失败之后。

逐条执行规定的工作。对于代理必须采取的每项操作，确认有资源覆盖它 - 如果没有，请大声说出差距：

|间隙类|检查 |如果丢失 |
|---|---|---|
| **工具/集成**（最容易捕获的前期配置 - 配置是静态可检查的）|作业中的每个动词都映射到启用的工具或MCP服务器。 「分诊票」→ 票务MCP服务器; “打开 PR”→ GitHubMCP服务器（一个`github_repository`单独安装无法打开PR）； “搜索网络”→ `web_search` 在工具集中启用。 |在§A 轮中添加工具/MCP 服务器，或者从作业中删除请求。 |
| **凭证/访问** |每台 MCP 服务器都附有一个保管库凭证 (§2)。作业涉及的每个外部主机都是可访问的 - 网络 `unrestricted`，或者主机位于 `allowed_hosts` 中。 |创建/附加保管库；加宽`allowed_hosts`。这些直到运行时才会失败——第 4 节中的冒烟测试是您如何以低廉的成本展示它们的方法。 |
| **数据** |作业引用的每个文件、数据集或存储库均安装为 `resource`（文件、`github_repository` 或内存存储）。 |在§B轮中上传+挂载它，或者告诉代理从哪里获取它。 |
| **及时的质量/标准** |该工作足够具体，可以采取行动，并且 "done" 是可检查的（§C 轮）。 |抓紧工作；连线一个结果。 |

向用户说明任何未满足的差距并在生成代码之前解决它们。不要发出您已经知道资源不足的配置 - 代理无法完成缺少工具、凭据或数据的任务。

---

## 4. 发出代码

直接从上次面试答案到代码 - 没有关于设置与运行时分割的序言，没有“内部化的关键事情......”，没有关于 `agents.create()` 是一次性的讲座。下面的两块结构已经表明了这一点；不叙述它。生成**两个清晰分离的块**：

**块 1 — 设置（运行一次，存储 ID）。** 最好将此作为 **YAML 文件 + `ant` CLI 命令** — 代理和环境是版本控制的定义，CLI 流程是用户应签入其存储库的内容并从 CI 运行。仅当用户明确希望使用语言进行设置或 `ant` CLI 不可用时，才回退到 SDK 代码。

发出：
1. `<name>.agent.yaml`，包含 §Round A–C 的所有内容（平面：`name`、`model`、`system`、`tools`、 `mcp_servers`、`skills`)
2. `<name>.environment.yaml` §C 轮网络
3. 应用命令：```sh
   AGENT_ID=$(ant beta:agents create < <name>.agent.yaml --transform id -r)
   ENV_ID=$(ant beta:environments create < <name>.environment.yaml --transform id -r)
   # CI sync: ant beta:agents update --agent-id "$AGENT_ID" --version N < <name>.agent.yaml
   ```有关完整的 CLI 参考，请参阅 `shared/anthropic-cli.md`。如果改为发出 SDK 代码，请将其标记为 `# ONE-TIME SETUP — run once, save the IDs to config/.env` 并调用 `environments.create()` → `agents.create()`。

**块 2 — 运行时（在每次调用时运行）。** 这是检测到的语言中的 SDK 代码（Python/TS/cURL — 请参阅 SKILL.md → 语言检测）。运行时路径需要以编程方式对事件（工具确认、自定义工具结果、重新连接）作出反应，这是 SDK 的领域 — 此处不要发出 shell 循环。
1.从config/env加载`env_id` + `agent_id`
2. `sessions.create(agent=AGENT_ID, environment_id=ENV_ID, resources=[...], vault_ids=[...])` — 这会阻塞，直到资源挂载，因此在花费任何令牌之前，*此处*会出现错误的文件/存储库挂载。
3. **当作业依赖于 MCP 服务器、凭据或可访问的主机时，首先进行冒烟测试。** 凭据和 MCP 连接故障不会在 `sessions.create()` 上出现 - 仅当代理首次尝试使用它们时。发送一个廉价的探测回合（“确认您可以到达 <service> 并列出 1-2 项；先不要开始任务”），检查它是否成功，*然后*发送真正的启动。这里的几百个令牌击败了失控的会话，该会话因丢失的凭证而失败并放弃。跳过没有外部依赖项的代理。
4. 打开流，`events.send()` 开始（`user.message`，或者 `user.define_outcome`，如果§2 选择结果分级路径），循环直到 `session.status_terminated` 或 `session.status_idle && stop_reason.type !== 'requires_action'`（参见`shared/managed-agents-client-patterns.md` 全栅极的模式 5 — 裸露时不会破裂 `session.status_idle`)

> ⚠️ **永远不要在同一个不受保护的块中发出 `agents.create()` 和 `sessions.create()`。** 这教会用户在每次运行时创建一个新代理 - #1 反模式。如果他们需要单个脚本，请将代理创建包装在 `if not os.getenv("AGENT_ID"):` 中。

从 `python/managed-agents/README.md`、`typescript/managed-agents/README.md` 或 `curl/managed-agents.md` 中提取准确的语法。不要发明字段名称。
</doc>

<doc path="shared/managed-agents-outcomes.md">
# 托管代理 — 结果

**结果**将会话从“对话”提升为“工作”：您陈述 "done" 的样子，然后工具运行迭代 → 评分 → 修改循环，直到工件符合标准、达到 `max_iterations` 或被中断。一个单独的**评分器**（独立上下文窗口）根据您的评分标准对每次迭代进行评分，并将每个标准的差距反馈给代理。

SDK 在所有 `client.beta.sessions.*` 调用上自动设置 `managed-agents-2026-04-01` beta 标头；结果不需要额外的标头。

---

## `user.define_outcome` 事件

结果不是 `sessions.create()` 上的字段。您创建一个正常会话，然后发送 `user.define_outcome` 事件。代理收到收据后开始工作 — **不要同时发送 `user.message`** 来启动它。```python
session = client.beta.sessions.create(
    agent=AGENT_ID,
    environment_id=ENVIRONMENT_ID,
    title="Financial analysis on Costco",
)

client.beta.sessions.events.send(
    session_id=session.id,
    events=[
        {
            "type": "user.define_outcome",
            "description": "Build a DCF model for Costco in .xlsx",
            "rubric": {"type": "text", "content": RUBRIC_MD},
            # or: "rubric": {"type": "file", "file_id": rubric.id}
            "max_iterations": 5,  # optional; default 3, max 20
        }
    ],
)
```|领域 |类型 |笔记|
|---|---|---|
| `type` | `"user.define_outcome"` | |
| `description` |字符串|任务。这就是代理的工作目标 — 不需要单独的 `user.message`。 |
| `rubric` | `{type: "text", content}` \| `{type: "file", file_id}` | **必填。** Markdown 具有明确的、可独立评分的标准。通过 `client.beta.files.upload(...)`（测试版 `files-api-2025-04-14`）上传一次即可在会话之间重复使用。 |
| `max_iterations` |整数 |选修的。默认 **3**，最大 **20**。 |

该事件通过服务器分配的 `outcome_id` 和 `processed_at` 在流上回显。

> **编写评分标准。** 使用明确的、可评分的标准（“CSV 有一个数字 `price` 列”），而不是共鸣（“数据看起来不错”）——评分者独立对每个标准进行评分，因此模糊的标准会产生嘈杂的循环。如果您没有标题，请让 Claude 分析一个已知良好的工件，并将该分析转化为一个。

---

## 结果特定事件

这些事件与常见的 `agent.*` / `session.*` 事件一起出现在标准事件流 (`sessions.events.stream` / `.list`) 上。

|活动 |有效载荷亮点|意义|
|---|---|---|
| `span.outcome_evaluation_start` | `outcome_id`、`iteration`（0 索引）|评分者开始对迭代 *N* 进行评分。 |
| `span.outcome_evaluation_ongoing` | `outcome_id` |分级机运行时的心跳。评分者的推理是不透明的——你看到的是它正在工作，而不是它在想什么。 |
| `span.outcome_evaluation_end` | `outcome_evaluation_start_id`、`outcome_id`、`iteration`、`result`、`explanation`、`usage` | Grader 完成了一次迭代。 `result` 驱动接下来发生的情况（下表）。 |

### `span.outcome_evaluation_end.result`

| `result` |下一页 |
|---|---|
| `satisfied` |会话 → `idle`。终端为这个结果。 |
| `needs_revision` |代理开始另一个迭代。 |
| `max_iterations_reached` |不再有分级机循环。代理可以运行一个最终修订版，然后进行会话 → `idle`。 |
| `failed` |会话 → `idle`。评分标准从根本上与任务不匹配（例如描述和评分标准矛盾）。 |
| `interrupted` |仅当 `_start` 在 `user.interrupt` 到达之前已触发时才发出。 |```json
{
  "type": "span.outcome_evaluation_end",
  "id": "sevt_01jkl...",
  "outcome_evaluation_start_id": "sevt_01def...",
  "outcome_id": "outc_01a...",
  "result": "satisfied",
  "explanation": "All 12 criteria met: revenue projections use 5 years of historical data, ...",
  "iteration": 0,
  "usage": { "input_tokens": 2400, "output_tokens": 350, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 1800 },
  "processed_at": "2026-03-25T14:03:00Z"
}
```---

## 检查状态并检索可交付成果

**状态** — 观看 `span.outcome_evaluation_end` 的流，或轮询会话并读取 `outcome_evaluations`：```python
session = client.beta.sessions.retrieve(session.id)
for ev in session.outcome_evaluations:
    print(f"{ev.outcome_id}: {ev.result}")  # outc_01a...: satisfied
```**可交付成果** — 代理写入`/mnt/session/outputs/`。空闲后，通过文件获取API和`scope_id=session.id`。这与文档中记录的会话输出机制相同`shared/managed-agents-environments.md`→ 会话输出（包括双 beta 标头要求`files.list`）。

---

## 交互规则和陷阱

- **一次一个结果。** 通过发送下一个结果进行链接`user.define_outcome`仅在前一个终端之后`span.outcome_evaluation_end` (`satisfied` / `max_iterations_reached` / `failed` / `interrupted`）。该会话保留了连锁结果的历史记录。
- **允许转向，但可选。** 您*可以*发送`user.message`事件的中间结果会推动方向，但代理已经知道要继续工作直到终端 - 不要发送“继续”提示。
- **`user.interrupt`暂停当前​​结果** — 它标志着`result: "interrupted"`并离开会议`idle`，准备好迎接新的结果或对话的转变。
- **结束后，会话可重复使用** — 继续对话或定义新结果。
- **结果 ≠ 会话创建字段。** 不要put `outcome`, `rubric`， 或者`description`在`sessions.create()`— 结果总是作为`user.define_outcome`事件。
- **怠速中断门未改变。** 在排水回路中，继续使用`event.type === 'session.status_idle' && event.stop_reason?.type !== 'requires_action'`— 不要**不要**打开门`span.outcome_evaluation_end`独自一人（在`needs_revision`会话继续运行）。看`shared/managed-agents-client-patterns.md`模式5。

对于生的HTTP形状和每种语言SDK超越的绑定Python, 网页抓取`https://platform.claude.com/docs/en/managed-agents/define-outcomes.md`（看`shared/live-sources.md`).
</doc>

<doc path="shared/managed-agents-overview.md"># 托管代理 — 概述

托管代理为每个会话提供一个容器作为代理的工作区。代理循环运行在 Anthropic 的编排层上；容器是代理的*工具*执行的地方 -bash命令、文件操作、代码。您创建一个持久的 **Agent** 配置（模型、系统提示、工具、MCP服务器、技能），然后启动引用它的**会话**。会话将事件流式传输回给您；您发送用户消息和工具结果。

## ⚠️ 强制流程：代理（一次）→ 会话（每次运行）

**为什么代理是单独的对象：版本控制。** 代理是持久的、版本化的配置 - 每次更新都会创建一个新的不可变版本，并且会话在创建时固定到一个版本。这使您可以在代理上进行迭代（调整提示、添加工具），而无需中断已运行的会话，如果更改出现回滚，则可以回滚，并可以并排进行 A/B 测试版本。如果你这样做，这些都不起作用`agents.create()`每次跑步都是新鲜的。

每个会话都引用预先创建的`/v1/agents`目的。创建代理一次，存储 ID，并在运行中重复使用它。

|步骤|致电 |频率|
|---|---|---|
| 1 |`POST /v1/agents` — `model`, `system`, `tools`, `mcp_servers`, `skills`住在这里| **一次。** 商店`agent.id`**和**`agent.version`. |
| 2 | `POST /v1/sessions` — `agent: "agent_abc123"`或者`{type: "agent", id, version}`| **每次运行。** 字符串速记使用最新版本。 |

如果你要写`sessions.create()`和`model`, `system`， 或者`tools`在会话主体上 — **停止**。那些田野还活着`agents.create()`。会话仅需要一个*指针*。

**生成代码时，将设置与运行时分开。**`agents.create()`属于安装脚本（或受保护的脚本）`if agent_id is None:`块），而不是在热路径的顶部。如果用户的代码调用`agents.create()`在每次调用时，他们都会积累孤立代理并白白支付创建延迟的费用。正确的形状是：创建一次 → 持久化 ID（配置文件、环境变量、秘密管理器） → 每次运行都会加载 ID 并调用`sessions.create()`。

**要更改代理的行为，请使用`POST /v1/agents/{id}`— 不要创建新的。** 每次更新都会改变版本；正在运行的会话保留其固定版本，新会话get最新的（或通过明确固定`{type: "agent", id, version}`）。看`shared/managed-agents-core.md`→ 代理 → 版本控制。改变`tools`/`mcp_servers`/`vault_ids`在**一个正在运行的会话**上而不接触代理对象，使用`sessions.update()`- 看`shared/managed-agents-core.md`→ 在会话中更新代理配置。

## 测试版标头

托管代理处于测试阶段。这SDK自动设置所需的测试标头：

|测试版标题 |它能实现什么 |
| ------------------------------------------ | ---------------------------------------------------------------- |
|`managed-agents-2026-04-01`|代理、环境、会话、事件、会话资源、会话线程、结果、多代理、保管库、凭证、内存存储 |
| `skills-2025-10-02` |技能 API（用于管理自定义技能定义）|
| `files-api-2025-04-14` |用于文件上传的文件 API |

**哪个测试标头位于何处：** SDK 在 `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` 调用上自动设置 `managed-agents-2026-04-01`，并且在 `files-api-2025-04-14` / `skills-2025-10-02` 上自动设置`client.beta.files.*` / `client.beta.skills.*` 来电。调用托管代理端点时，您不需要添加技能或文件 beta 标头。 **例外 - 会话范围的文件列表：** `client.beta.files.list({scope_id: session.id})` 是采用托管代理参数的文件端点，因此它需要 **两个** 标头。在该调用上显式传递 `betas: ["managed-agents-2026-04-01"]`（SDK 添加“文件”标头；您添加“托管代理”标头）。请参阅 `shared/managed-agents-environments.md` → 会话输出。


## 阅读指南

|用户想要... |阅读这些文件 |
| -------------------------------------- | ------------------------------------------------------- |
| **Get 从头开始​​/“帮我设立一个代理”** | `shared/managed-agents-onboarding.md` — 引导采访（WHERE→WHO→WHAT→WATCH），然后发出代码 |
|了解 API 的工作原理 | `shared/managed-agents-core.md` |
|查看完整端点参考 | `shared/managed-agents-api-reference.md` |
| **创建代理**（第一步必需）| `shared/managed-agents-core.md`（代理部分）+语言文件 |
|更新/版本化代理 | `shared/managed-agents-core.md`（代理 → 版本控制）— 更新，不要重新创建 |
|创建会话 | `shared/managed-agents-core.md` + `{lang}/managed-agents/README.md` |
|配置工具和权限 | `shared/managed-agents-tools.md` |
|设置 MCP 服务器 | `shared/managed-agents-tools.md`（MCP 服务器部分）|
|流事件/处理 tool_use | `shared/managed-agents-events.md` + 语言文件 |
| Get 通过 webhook 通知会话状态更改（无轮询）| `shared/managed-agents-webhooks.md` — 控制台注册端点、HMAC 验证、精简有效负载 + 获取 |
|定义结果/评分标准迭代循环 | `shared/managed-agents-outcomes.md` — `user.define_outcome` 事件、分级机、`span.outcome_evaluation_*` 事件 |
|协调多个代理/子代理/线程 | `shared/managed-agents-multiagent.md` — 关于代理、会话线程、交叉发布工具确认的 `multiagent: {type: "coordinator", agents: [...]}` |
|设置环境 | `shared/managed-agents-environments.md` + 语言文件 |
|在您自己的基础设施/VPC（自托管沙箱）中运行工具执行 | `shared/managed-agents-self-hosted-sandboxes.md` — `config:{type:"self_hosted"}`、`ANTHROPIC_ENVIRONMENT_KEY`、`EnvironmentWorker.run()` / `ant beta:worker poll` |
|上传文件/附加存储库 | `shared/managed-agents-environments.md`（资源）|
|为代理提供跨会话持久记忆 | `shared/managed-agents-memory.md` — 内存存储、`memory_store` 会话资源、先决条件、版本/编辑 |
|将代理/环境定义为版本控制的 YAML；从外壳驱动API | `shared/anthropic-cli.md` — `ant beta:agents create < agent.yaml`、`--transform`、`@file` 内联 |
|存储 MCP 凭据 | `shared/managed-agents-tools.md`（金库部分）|
|呼叫需要秘密的非 MCP API / CLI | `shared/managed-agents-client-patterns.md` 模式 9 — 无容器环境变量；保险库仅限 MCP；通过自定义工具保守主机端的秘密 |

## 常见陷阱

- **首先是代理，然后是会话 — 无例外** — 会话的 `agent` 字段**仅**接受字符串 ID 或 `{type: "agent", id, version}`。 `model`、`system`、`tools`、`mcp_servers`、`skills` 是 **`POST /v1/agents` 上的顶级字段**，从不开启`sessions.create()`。如果用户尚未创建代理，则这是每个示例的第零步。
- **代理一次，不是每次运行** — `agents.create()` 是一个设置步骤。将返回的`agent_id`存储起来并重复使用；不要在热路径的顶部调用 `agents.create()`。如果代理的配置需要更改，`POST /v1/agents/{id}` - 每次更新都会创建一个新版本，并且会话可以固定到特定版本以实现可重复性。
- **MCP 身份验证通过保管库** — 代理的 `mcp_servers` 数组仅声明 `{type, name, url}`（无身份验证）。凭证位于保管库 (`client.beta.vaults.credentials.create`) 中，并通过 `vault_ids` 附加到会话。人择使用存储的刷新令牌自动刷新 OAuth 令牌。
- **首次运行前协调资源** — 具有明确要求但缺少工具、凭据、数据安装或上下文的会话将在运行中发现差距，然后连枷并放弃。创建会话之前，请检查任务中的每个操作是否映射到已配置的工具/MCP 服务器，每个 MCP 服务器都有保管库凭证，并且每个引用的文件/主机均已安装/可访问。帮助用户设置时，请运行 `shared/managed-agents-onboarding.md` → §3 飞行前可行性检查中的调节。
- **流式传输至 get 事件** — `GET /v1/sessions/{id}/events/stream` 是实时接收代理输出的主要方式。
- **SSE 流没有重播 — 通过整合重新连接** — 如果在 `agent.tool_use`、`agent.mcp_tool_use` 或 `agent.custom_tool_use` 等待解决时流丢失（前两个为 `user.tool_confirmation`，最后一个为 `user.custom_tool_result`），会话死锁（客户端断开连接 → 会话空闲 → 重新连接发生 → 没有客户端解析发生）。每次（重新）连接时：使用 `GET /v1/sessions/{id}/events/stream` 打开流，获取 `GET /v1/sessions/{id}/events`，按事件 ID 进行重复数据删除，然后继续。请参阅 `shared/managed-agents-events.md` → 丢失流后重新连接。
- **不要相信 HTTP 库超时作为挂钟上限** — `requests` `timeout=(c, r)` 和 `httpx.Timeout(n)` 是*每块*读取超时；它们会重置每个字节，因此滴流连接可能会无限期地阻塞。对于原始 HTTP 轮询的严格截止日期，请在循环级别跟踪 `time.monotonic()` 并明确保释。与手卷 HTTP 相比，更喜欢 SDK 的 `sessions.events.stream()` / `session.events.list()`。请参阅 `shared/managed-agents-events.md` → 接收事件。
- **消息队列** — 您可以在会话为 `running` 或 `idle` 时发送事件；它们是按顺序处理的。发送下一条消息之前无需等待响应。
- **环境 `config.type` 是 `"cloud"` 或 `"self_hosted"`** — `cloud` 在 Anthropic 的基础设施上运行容器； `self_hosted` 将工具执行移至您自己的（请参见 `shared/managed-agents-self-hosted-sandboxes.md`）。
- **存档在每个资源上都是永久的** — 存档代理、环境、会话、保管库、凭证或内存存储使其变为只读，无需取消存档。特别是对于代理、环境和内存存储，新会话无法引用已归档资源（现有会话继续）。不要在生产代理、环境或内存存储上调用 `.archive()` 作为清理 - **在归档之前始终与用户确认**。
</doc>

<doc path="shared/managed-agents-self-hosted-sandboxes.md">
# 托管代理 — 自托管沙箱

使用 `config.type: "self_hosted"`，**代理循环保留在 Anthropic 的编排层**，但**工具执行转移到您控制的基础设施** - bash、文件操作和代码在容器内运行，因此文件系统内容和网络出口永远不会离开您的环境。与 `config.type: "cloud"` 对比，其中 Anthropic 运行容器。连接性是**仅限出站**：您的工作人员长轮询 Anthropic 的工作队列； Anthropic 永远不会拨入您的网络。

＃＃ 流动```
1. Create environment:      config: {type: "self_hosted"}        → env_...
2. Generate environment key (Console, on the environment page)   → sk-ant-oat01-...  as ANTHROPIC_ENVIRONMENT_KEY
3. Run a worker:            EnvironmentWorker.run()  or  ant beta:worker poll
4. Sessions reference       environment_id=env_... exactly as for cloud
```## 创建环境```python
client = anthropic.Anthropic()

environment = client.beta.environments.create(
    name="self-hosted", config={"type": "self_hosted"}
)
````{"type": "self_hosted"}` 是整个配置 - 没有池、容量或网络子字段；你控制你身边的人。

## 运行一个worker — SDK（主路径）

`EnvironmentWorker` 包装轮询 → 调度 → 工具执行循环。 `.run()` 是常开循环； `.run_one()` / `.runOne()` 处理一个工作项（用于 webhook 驱动的唤醒）。

**Python — 始终开启：**```python
import asyncio
import os
from anthropic import AsyncAnthropic
from anthropic.lib.environments import EnvironmentWorker


async def main() -> None:
    environment_key = os.environ["ANTHROPIC_ENVIRONMENT_KEY"]
    environment_id = os.environ["ANTHROPIC_ENVIRONMENT_ID"]
    async with AsyncAnthropic(auth_token=environment_key) as client:
        await EnvironmentWorker(
            client,
            environment_id=environment_id,
            environment_key=environment_key,
            workdir="/workspace",
        ).run()


asyncio.run(main())
```**TypeScript — 始终开启：**```typescript
import Anthropic from "@anthropic-ai/sdk";
import { EnvironmentWorker } from "@anthropic-ai/sdk/helpers/beta/environments";

const environmentKey = process.env.ANTHROPIC_ENVIRONMENT_KEY!;
const environmentId = process.env.ANTHROPIC_ENVIRONMENT_ID!;
const client = new Anthropic({ authToken: environmentKey });
const ctrl = new AbortController();
process.once("SIGTERM", () => ctrl.abort());

await new EnvironmentWorker({
  client,
  environmentId,
  environmentKey,
  workdir: "/workspace",
  signal: ctrl.signal
}).run();
```**自定义工具。** `EnvironmentWorker` 默认运行内置工具集。要添加或替换工具，请将 `AgentToolContext(workdir=, client=, session_id=)` 与 `beta_agent_toolset(env)` / `betaAgentToolset(env)` 结合使用，并将生成的工具传递到较低级别的 `tool_runner()`。在工具调用开始之前，附加到代理的技能将下载到 `{workdir}/skills/<name>/`（当给定 `client` 和 `session_id` 时，`AgentToolContext` 会处理此问题）。下载的技能文件会被CLI和SDK自动标记为可执行；如果您自己实施技能下载，则可以设置权限。

> **运行时依赖：** SDK 帮助程序需要在该确切路径上使用 `/bin/bash`。 TypeScript SDK 还需要 `unzip`、`tar` 和 Node.js 22+。这些在固定路径上解析，并且**不**尊重 `PATH` 覆盖。

## 运行一个worker — `ant` CLI（固定工具）

`ant` CLI 为工人提供固定的内置工具组（`bash`、`read`、`write`、 `edit`、`glob`、`grep`）。按照 `shared/anthropic-cli.md` 安装，然后：```sh
export ANTHROPIC_ENVIRONMENT_KEY=sk-ant-oat01-...
ant beta:worker poll --environment-id env_... --workdir /workspace
```- `--workdir` 是工具运行的目录（默认`.`）；工具调用被沙箱化。
- `--environment-key` 覆盖环境变量。
- `--on-work <script>` 每个工作项运行您的脚本（例如，每个会话旋转一个新容器 - 请参阅下面的容器编排）。
- `--unrestricted-paths`、`--max-idle`（默认 `60s`）、`--log-format` — 请参阅 `ant beta:worker poll --help`。
- 标志回退到环境变量（`ANTHROPIC_ENVIRONMENT_ID`、`ANTHROPIC_ENVIRONMENT_KEY`）。
- 在耗尽正在进行的工作后，在 SIGTERM/SIGINT 上干净地退出。
- **固定工具集** — 对于自定义工具，请使用上面的 SDK 工作器。

在 `--on-work` 容器内，运行 `ant beta:worker run --workdir <dir>` 作为入口点。

## Webhook 驱动的唤醒（而不是始终开启）

注册 `session.status_run_started` 的 Webhook（请参阅 `shared/managed-agents-webhooks.md`），验证交付，然后使用 `.run_one()` 排出一个工作项：```python
import os
import anthropic
from anthropic.lib.environments import EnvironmentWorker

environment_key = os.environ["ANTHROPIC_ENVIRONMENT_KEY"]
environment_id = os.environ["ANTHROPIC_ENVIRONMENT_ID"]
client = anthropic.AsyncAnthropic(
    auth_token=environment_key,
)  # reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env for webhooks.unwrap()


async def handle(raw: bytes, headers: dict[str, str]) -> dict:
    event = client.beta.webhooks.unwrap(raw.decode(), headers=headers)
    if event.data.type != "session.status_run_started":
        return {"status": "ignored"}
    await EnvironmentWorker(
        client,
        environment_id=environment_id,
        environment_key=environment_key,
        workdir="/workspace",
    ).run_one()
    return {"status": "ok"}
```TypeScript：与`client.beta.webhooks.unwrap(body, {headers})`和`new EnvironmentWorker({...}).runOne()`形状相同。

## 容器编排（中级）

`EnvironmentWorker.run()` 在同一进程中轮询和执行工具。要在其**自己的**容器中运行每个会话，请在瘦编排器中使用中级轮询器 - Python `client.beta.environments.work.poller(environment_id=, environment_key=, drain=, block_ms=, reclaim_older_than_ms=, auto_stop=)`；来自 `@anthropic-ai/sdk/helpers/beta/environments` 的 TypeScript `new WorkPoller({client, environmentId, environmentKey, autoStop})` — 并且，对于每个生成的 `work` 项目，启动一个注入这些环境变量的新容器，其入口点运行 `ant beta:worker run` 或`EnvironmentWorker(...).run_one()`。 `block_ms` 为 1–999（或 `None` 对于非阻塞）； `reclaim_older_than_ms` 收回租给死去工人的物品； `drain`一旦队列为空就停止； `auto_stop` 在迭代器退出后发出停止信号（当启动的容器拥有停止调用时设置 `False`）。 **Go 的轮询器没有 `auto_stop` 选择退出** - 当处理程序返回时，它会调用 `work.Stop`，因此会阻塞处理程序，直到会话完成而不是分离。

|环境变量 |价值|
|---|---|
| `ANTHROPIC_SESSION_ID` | `work.data.id` |
| `ANTHROPIC_WORK_ID` | `work.id` |
| `ANTHROPIC_ENVIRONMENT_ID` | `work.environment_id` |
| `ANTHROPIC_ENVIRONMENT_KEY` |穿过|
| `ANTHROPIC_BASE_URL` |穿过|

跳过 `work.data.type != "session"` 的项目。

## 监测与控制

这些是**控制平面**调用 - 使用 `x-api-key`（不是环境密钥）进行身份验证； `managed-agents-2026-04-01` beta 标头。 **从工作主机外部调用它们** — 在工作主机上设置 `ANTHROPIC_API_KEY` 会向代理工具调用公开组织范围的凭据。

| SDK (`client.beta.environments.work.*`) |休息 | CLI |返回|
|---|---|---|---|
| `stats(environment_id)` | `GET /v1/environments/{id}/work/stats` | `ant beta:environments:work stats` | `{type:"work_queue_stats", depth, pending, oldest_queued_at, workers_polling}` |
| `stop(work_id, environment_id=)` | `POST /v1/environments/{id}/work/{work_id}/stop` | `ant beta:environments:work stop` | `work.state` |

## 与 `cloud` 相比有何变化

|关注| `cloud` | `self_hosted` |
|---|---|---|
|容器生命周期、强化、网络 |人择 | **你** — 运行非 root、只读 rootfs、首字下沉；出口是您的 VPC/防火墙允许的任何出口 |
| `file` / `github_repository` 资源安装 |人类安装到容器中 | **您** — 通过 `sessions.create(metadata={...})` 传递指针，并让您的编排器在分派之前获取/克隆 |
| `memory_store` 资源 |支持 | **尚不支持** |
|内置工具|通过 `agent_toolset_20260401` |由您的工人提供（`EnvironmentWorker` 默认 / `beta_agent_toolset(env)` / `ant` CLI 固定套件） |
|技能下载|自动| `EnvironmentWorker` / `AgentToolContext` 获取 `{workdir}/skills/`（需要 `client` + `session_id`）|
| AWS 上的 Claude 平台 |支持 | **不可用** |
| SDK 工人助手|所有 SDK | **Python、TypeScript，仅限 Go**（`EnvironmentWorker` / 轮询器不在 Java、Ruby、PHP 或 C# 中）- 使用这三个之一或 `ant` CLI |

## 凭证

|资质证书 |格式|范围 |
|---|---|---|
| `ANTHROPIC_ENVIRONMENT_KEY` | `sk-ant-oat01-...` |一种环境的工作队列。在控制台中生成（“生成环境密钥”）。在客户端上以 `auth_token=` / `authToken` 的形式传递 **，在 `EnvironmentWorker` 上以 `environment_key=` / `environmentKey` 的形式传递**。存储在机密管理器中；曝光时旋转。 |
| `ANTHROPIC_WEBHOOK_SIGNING_KEY` | `whsec_...` | Webhook 签名验证（如果使用 webhook 驱动的唤醒）。 SDK 自动读取 `client.beta.webhooks.unwrap()` 的此环境变量。 |

## 安全性——你拥有什么

容器硬化；出口限制（没有默认值）； `ANTHROPIC_ENVIRONMENT_KEY` 保管及轮换；运行不受信任的代码时，每个信任边界一个工作区 + 环境；工具进程的最小权限；日志保留和编辑。 **人类不能**：快速撤销泄漏的环境密钥，验证您的图像或供应链，容器内的沙盒工具执行，或在工具输出到达您的基础设施后强制保留。有关完整清单，请参阅 `shared/live-sources.md` 中的自托管沙箱安全页面。
</doc>

<doc path="shared/managed-agents-tools.md">
# 托管代理 — 工具和技能

## 工具

### 服务器工具与客户端工具

|类型 |谁来运营？它是如何运作的 |
|---|---|---|
| **预构建的 Claude Agent 工具** (`agent_toolset_20260401`) | Anthropic，在会话的容器上（对于 `cloud` env；对于 `self_hosted`，**您的** 工作人员提供并运行它们 - 请参阅`shared/managed-agents-self-hosted-sandboxes.md`) |文件操作、bash、网络搜索等。一次性启用全部或使用 `enabled: true/false` 单独配置。 |
| **MCP 工具** (`mcp_toolset`) | Anthropic 的编排层 |连接的 MCP 服务器公开的功能。通过工具集授予每个服务器的访问权限。 |
| **自定义工具** | **您** — 您的应用程序处理调用并返回结果 |代理发出 `agent.custom_tool_use` 事件，会话进入 `idle`，您发回 `user.custom_tool_result` 事件。 |

**建议：** 通过 `agent_toolset_20260401` 启用所有预构建工具，然后根据需要单独禁用。

**版本控制：** 该工具集是版本化的静态资源。当底层工具发生变化时，会创建一个新的工具集版本（因此为 `_20260401`），因此您始终确切地知道您将获得什么。

### 代理工具集

`agent_toolset_20260401` 提供以下内置工具：

|工具|描述 |
| ---------------------- | ---------------------------------------------------- |
| `bash` |在 shell 会话中执行 bash 命令 |
| `read` |从本地文件系统读取文件，包括文本、图像、PDF 和 Jupyter 笔记本 |
| `write` |将文件写入本地文件系统 |
| `edit` |在文件中执行字符串替换 |
| `glob` |使用 glob 模式进行快速文件模式匹配 |
| `grep` |使用正则表达式模式进行文本搜索 |
| `web_fetch` |从 URL 获取内容 |
| `web_search` |搜索网络获取信息 |

启用完整的工具集：```json
{
  "tools": [
    { "type": "agent_toolset_20260401" }
  ]
}
```### 每个工具配置

覆盖各个工具的默认设置。此示例启用除 bash 之外的所有内容：```json
{
  "tools": [
    {
      "type": "agent_toolset_20260401",
      "default_config": { "enabled": true },
      "configs": [
        { "name": "bash", "enabled": false }
      ]
    }
  ]
}
```|领域 |必填 |描述 |
|---|---|---|
| `type` | ✅ | `"agent_toolset_20260401"` |
| `default_config` | ❌ |适用于所有工具。 `{ "enabled": bool, "permission_policy": {...} }` |
| `configs` | ❌ |每个工具覆盖：`[{ "name": "...", "enabled": bool, "permission_policy": {...} }]` |

### 权限策略

控制服务器执行的工具（代理工具集 + MCP）何时自动运行与等待批准。不适用于自定义工具。

|政策 |行为 |
|---|---|
| `always_allow` |工具自动执行（默认）|
| `always_ask` |会话发出 `session.status_idle` 并暂停，直到您发送 `tool_confirmation` 事件 |```json
{
  "type": "agent_toolset_20260401",
  "default_config": {
    "enabled": true,
    "permission_policy": { "type": "always_allow" }
  },
  "configs": [
    { "name": "bash", "permission_policy": { "type": "always_ask" } }
  ]
}
```**响应 `always_ask`：** 从触发 `agent_tool_use`/`mcp_tool_use` 事件发送带有 `tool_use_id` 的 `user.tool_confirmation` 事件：```json
{ "type": "tool_confirmation", "tool_use_id": "sevt_abc123", "result": "allow" }
{ "type": "tool_confirmation", "tool_use_id": "sevt_def456", "result": "deny", "message": "Read .env.example instead" }
```拒绝时的可选 `message` 将传送给代理，以便其可以调整其方法。

要仅启用特定工具，请关闭默认设置并选择每个工具：```json
{
  "tools": [
    {
      "type": "agent_toolset_20260401",
      "default_config": { "enabled": false },
      "configs": [
        { "name": "bash", "enabled": true },
        { "name": "read", "enabled": true }
      ]
    }
  ]
}
```### 自定义工具（客户端）

自定义工具由**您的应用程序**执行，而不是由 Anthropic 执行。流程：

1. 代理决定使用该工具 → 会话发出带有输入的 `agent.custom_tool_use` 事件
2. 会话进行 `idle` 等待您
3. 您的应用程序执行该工具
4. 您发回 `user.custom_tool_result` 事件，并输出
5. 会议恢复 `running`

不需要任何权限策略——您就是执行者。```json
{
  "tools": [
    {
      "type": "custom",
      "name": "get_weather",
      "description": "Fetch current weather for a city.",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": { "type": "string", "description": "City name" }
        },
        "required": ["city"]
      }
    }
  ]
}
```### MCP 服务器

MCP（模型上下文协议）服务器公开标准化的第三方功能（例如 Asana、GitHub、Linear）。 **配置跨代理和保管库分开：**

1. **代理创建**声明要连接到哪些服务器（`type`、`name`、`url` — 无身份验证）。代理的 `mcp_servers` 阵列没有 auth 字段。
2. **Vault** 存储 OAuth 凭证。在会话创建时通过 `vault_ids` 附加。

这可以保护可重用代理定义中的秘密。每个保管库凭证都与一台 MCP 服务器 URL 绑定； Anthropic 通过 URL 将凭据与服务器进行匹配。

**代理端 — 声明服务器（无身份验证）：**

|领域 |必填 |描述 |
|---|---|---|
| `type` | ✅ | `"url"` |
| `name` | ✅ |唯一名称 — 由 `mcp_toolset.mcp_server_name` 引用 |
| `url` | ✅ | MCP 服务器的端点 URL（可流式 HTTP 传输）|```json
{
  "mcp_servers": [
    { "type": "url", "name": "linear", "url": "https://mcp.linear.app/mcp" }
  ],
  "tools": [
    { "type": "mcp_toolset", "mcp_server_name": "linear" }
  ]
}
```**会话端 — 附加保管库：**```json
{
  "agent": "agent_abc123",
  "environment_id": "env_abc123",
  "vault_ids": ["vlt_abc123"]
}
```> 💡 **每工具启用（经验）：** `mcp_toolset` 已被观察到接受 `default_config: {enabled: false}` + `configs: [{name, enabled: true}]` 作为白名单模式。 API 参考仅显示最小的 `{type, mcp_server_name}` 形式。

> 💡 **在正在运行的会话上更改工具/MCP 服务器：** `sessions.update()` 可以在会话运行时替换 `agent.tools`、`agent.mcp_servers` 和 `vault_ids` `idle` — 不触及代理对象的会话本地覆盖。请参阅 `shared/managed-agents-core.md` → 在会话中更新代理配置。

**大量 MCP 工具输出。**如果 MCP 工具返回超过 **100K 令牌**，输出会自动卸载到沙箱中的文件中 — 代理会收到截断的预览和文件路径，并且可以 `read` 获取完整内容。无需配置。

**无效的保管库凭据不会阻止会话创建。** 如果保管库凭据对于声明的 MCP 服务器无效，会话仍会成功创建； `session.error` 事件描述 MCP 身份验证失败，并在下一个 `session.status_idle` → `session.status_running` 转换时重试身份验证。

> ⚠️ **MCP 身份验证令牌 ≠ REST API 令牌。** 托管 MCP 服务器（`mcp.notion.com`、`mcp.linear.app` 等）通常需要**OAuth 不记名令牌**，而不是服务的本机 API 密钥。 Notion `ntn_` 集成令牌根据 Notion 的 REST API 进行身份验证，但**不能**用作 Notion MCP 服务器的保管库凭证。这些是不同的身份验证系统。

### Vaults — MCP 凭证存储

**保管库**存储 OAuth 凭证（访问令牌 + 刷新令牌），Anthropic 通过标准 OAuth 2.0 `refresh_token` 授权代表您自动刷新。这是在启动 SDK 中验证 MCP 服务器的唯一方法。

#### 凭证和沙箱

保险库存储凭证；这些凭证**永远不会进入沙箱**。这是一个故意的安全边界——沙箱中运行的代码（包括代理编写的任何内容）无法读取或泄露保管凭证，即使在提示注入下也是如此。相反，凭据是在请求离开沙箱之后由人类端代理注入的：

- **MCP 工具调用** 通过 Anthropic 端代理进行路由，该代理从保管库获取凭证并将其添加到出站请求中。
- **附加 GitHub 存储库上的 Git 操作**（`git pull`、`git push`、GitHub REST 调用）通过 git 代理进行路由，该代理以相同的方式注入 `github_repository` 资源的 `authorization_token`。

**尚不支持：** 直接在沙箱内运行其他经过身份验证的 CLI（例如 `aws`、`gcloud`、`stripe`）。目前无法设置容器环境变量或向任意进程公开保管库凭据。如果您今天需要其中之一：

- **首选 MCP 服务器**用于该服务（如果存在） - 它获得相同的保险库支持的注入。
- **否则，注册一个自定义工具：** 代理发出 `agent.custom_tool_use`，您的协调器（已持有凭据）执行调用并通过相同的经过身份验证的事件流返回 `user.custom_tool_result`。没有公开端点；沙箱永远看不到秘密。参见 `shared/managed-agents-client-patterns.md` → 模式 9。

**不要在系统提示或用户消息中键入 put API 作为解决方法** — 它们会保留在会话的事件历史记录中。

> 以前在内部称为 TAT（工具/租户访问令牌）。

**流量：**

1. 创建一个保管库 (`client.beta.vaults.create(...)`) — 每个租户/用户一个，或共享一个，具体取决于您的型号
2. 向其中添加 MCP 凭证 (`client.beta.vaults.credentials.create(...)`) — 每个凭证都绑定到一台 MCP 服务器 URL
3. 通过 `vault_ids: ["vlt_..."]` 创建会话时引用保管库
4. 人择在令牌过期前自动刷新令牌；代理在调用 MCP 工具时使用当前访问令牌

**凭证形状**：```json
{
  "display_name": "Notion (workspace-foo)",
  "auth": {
    "type": "mcp_oauth",
    "mcp_server_url": "https://mcp.notion.com/mcp",
    "access_token": "<current access token>",
    "expires_at": "2026-04-02T14:00:00Z",
    "refresh": {
      "refresh_token": "<refresh token>",
      "client_id": "<your OAuth client_id>",
      "token_endpoint": "https://api.notion.com/v1/oauth/token",
      "token_endpoint_auth": { "type": "none" }
    }
  }
}
````refresh` 块是启用自动刷新的功能 - `token_endpoint` 是 Anthropic 发布 `refresh_token` 授权的地方。 `token_endpoint_auth` 是一个受歧视的工会：

| `type` |形状|使用时 |
|---|---|---|
| `"none"` | `{type: "none"}` |公开OAuth客户端（无秘密）|
| `"client_secret_basic"` | `{type: "client_secret_basic", client_secret: "..."}` |机密客户端，通过 HTTP 基本身份验证保密 |
| `"client_secret_post"` | `{type: "client_secret_post", client_secret: "..."}` |机密客户端，请求正文中的秘密 |

如果您只有一个没有刷新功能的访问令牌，则完全省略 `refresh` — 它将一直有效，直到过期，然后代理将失去访问权限。

> 💡 **获取 OAuth 令牌。** 如何获取初始访问和刷新令牌取决于 MCP 服务器 - 请参阅其文档。获得它们后，使用上面的形状将它们存储在保险库凭证中； Anthropic 通过 `refresh.token_endpoint` 从那里自动刷新。

**范围：** Vault 的范围是工作区。在 API 工作区中具有开发人员+角色的任何人都可以创建、读取（仅限元数据 - 机密是只写的）和附加保管库。 `vault_ids` 可以在会话 **创建** 时设置，但不能通过会话更新进行设置（SDK 文档字符串显示“尚不支持；设置此字段的请求被拒绝”）。

---

## 技能

技能是可重用的、基于文件系统的资源，可为您的代理提供特定领域的专业知识：将通用代理转变为专家的工作流程、上下文和最佳实践。与提示（一次性任务的对话级指令）不同，技能按需加载，无需在多个对话中重复提供相同的指导。

两种类型——两者的工作方式相同；当与手头的任务相关时，代理会自动使用它们：

|类型 |它是什么 |
|---|---|
| **预建的人择技能** |常见文档任务（PowerPoint、Excel、Word、PDF）。按名称引用（例如 `xlsx`）。 |
| **自定义技能** |您通过技能 API 在组织中创建的技能。参考 `skill_id` + 可选 `version`。 |

**每个代理最多 20 个技能。** 代理创建使用 `managed-agents-2026-04-01`；单独的技能 API（用于管理自定义技能定义）使用 `skills-2025-10-02`。

### 在会话中启用技能

技能通过 `agents.create()` 附加到 **agent** 定义：```ts
const agent = await client.beta.agents.create(
  {
    name: "Financial Agent",
    model: "claude-opus-4-8",
    system: "You are a financial analysis agent.",
    skills: [
      { type: "anthropic", skill_id: "xlsx" },
      { type: "custom", skill_id: "skill_abc123", version: "latest" },
    ],
  }
);
```Python：```python
agent = client.beta.agents.create(
    name="Financial Agent",
    model="claude-opus-4-8",
    system="You are a financial analysis agent.",
    skills=[
        {"type": "anthropic", "skill_id": "xlsx"},
        {"type": "custom", "skill_id": "skill_abc123", "version": "latest"},
    ]
)
```**技能参考字段：**

|领域 |人择技能 |定制技能|
|---|---|---|
| `type` | `"anthropic"` | `"custom"` |
| `skill_id` |技能名称（例如 `"xlsx"`、`"docx"`、`"pptx"`、`"pdf"`）|来自技能 API 的技能 ID（例如 `"skill_abc123"`）|
| `version` | — | `"latest"` 或特定版本号 |

### 技能 API

|运营|方法|路径|
| -------------------- | -------- | ----------------------------------------------------------- |
|创造技能| `POST` | `/v1/skills` |
|列出技能 | `GET` | `/v1/skills` |
| Get 技能 | `GET` | `/v1/skills/{id}` |
| Delete 技能 | `DELETE` | `/v1/skills/{id}` |
|创建版本 | `POST` | `/v1/skills/{id}/versions` |
|列表版本 | `GET` | `/v1/skills/{id}/versions` |
| Get 版本 | `GET` | `/v1/skills/{id}/versions/{version}` |
| Delete 版本 | `DELETE` | `/v1/skills/{id}/versions/{version}` |
</doc>

<doc path="shared/managed-agents-webhooks.md">
# 托管代理 — Webhooks

当托管代理资源更改状态时，Anthropic 可以将 POST 连接到 HTTPS 端点 - 这是保持 SSE 流或轮询的替代方法。有效负载**薄**（仅事件类型+资源ID）；收到后，获取当前状态的资源。每次交付均经过 HMAC 签名。

> **方向很重要。** 此页面涵盖*人为→您*有关会话/保管库状态的通知。它**不**涵盖*第三方→您*网络挂钩，*触发*会话（例如，调用 `sessions.create()` 的 GitHub 推送处理程序）——这是您这边的普通应用程序代码，没有 Anthropic 特定的有线格式。

---

## 注册端点（仅限控制台）

控制台 → **管理 → Webhooks**。尚无编程端点管理 API。同一页面支持秘密轮换。

|领域 |约束|
|---|---|
| URL |端口 443 上的 HTTPS，可公开解析的主机名 |
|事件类型 |按 `data.type` 订阅 — 您仅收到订阅类型（加上测试事件）|
|签约秘笈 | `whsec_` 前缀，32 字节，**创建时显示一次** — 存储它 |

---

## 验证签名

每次交付均经过 HMAC 签名。 **使用 SDK 的 `client.beta.webhooks.unwrap()`** — 它验证签名，拒绝超过约 5 分钟的有效负载，并返回解析的事件。它从 `ANTHROPIC_WEBHOOK_SIGNING_KEY` 读取 `whsec_` 机密。```python
import anthropic
from flask import Flask, request

client = anthropic.Anthropic()  # reads ANTHROPIC_WEBHOOK_SIGNING_KEY from env
app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        event = client.beta.webhooks.unwrap(
            request.get_data(as_text=True),
            headers=dict(request.headers),
        )
    except Exception:
        return "invalid signature", 400

    if event.id in seen_event_ids:  # dedupe retries — id is per-event, not per-delivery
        return "", 204
    seen_event_ids.add(event.id)

    match event.data.type:
        case "session.status_idled":
            session = client.beta.sessions.retrieve(event.data.id)
            notify_user(session)
        case "vault_credential.refresh_failed":
            alert_oncall(event.data.id)

    return "", 204
```将**原始请求正文**传递给 `unwrap()` — 重新序列化 JSON（Express `.json()`、Flask `.get_json()`）的框架会更改字节并破坏 MAC。对于其他语言，请在 SDK 存储库 (`shared/live-sources.md`) 中查找 `beta.webhooks.unwrap` 绑定；不要手卷验证。

---

## 有效负载信封```json
{
  "type": "event",
  "id": "event_01ABC...",
  "created_at": "2026-03-18T14:05:22Z",
  "data": {
    "type": "session.status_idled",
    "id": "session_01XYZ...",
    "organization_id": "8a3d2f1e-...",
    "workspace_id": "c7b0e4d9-..."
  }
}
```开启`data.type`，通过`data.id`获取资源，返回任意**2xx**来确认。 `created_at` 是“状态转换”发生的时间，而不是 Webhook 触发的时间。

---

## 支持的 `data.type` 值

| `data.type` |何时触发 |
|---|---|
| `session.status_scheduled` |会话已创建并准备好接受事件 |
| `session.status_run_started` |代理执行开始（每次转换到 `running`）|
| `session.status_idled` |代理等待输入（工具批准、自定义工具结果或下一条消息）|
| `session.status_terminated` |会话遇到终端错误 |
| `session.thread_created` | Multiagent：协调器打开了一个新的子代理线程 |
| `session.thread_idled` |多代理：子代理线程正在等待输入 |
| `session.outcome_evaluation_ended` |结果评分者完成了一次迭代 |
| `vault.archived` |保险库已存档 |
| `vault.created` |保险库已创建 |
| `vault.deleted` |保险库已删除 |
| `vault_credential.archived` | Vault 凭证已存档 |
| `vault_credential.created` | Vault 凭证已创建 |
| `vault_credential.deleted` | Vault 凭证已删除 |
| `vault_credential.refresh_failed` | MCP OAuth 保管库凭证刷新失败 |

> 这些是 **webhook** `data.type` 值 - 与 SSE 事件类型（`shared/managed-agents-events.md` 中的 `session.status_idle`、`span.outcome_evaluation_end` 等）不同的命名空间。不要在 webhook 处理程序中重复使用 SSE 常量。

---

## 交付行为和陷阱

- **无订购保证。** 即使评估先完成，`session.status_idled` 也可能在 `session.outcome_evaluation_ended` 之前到达。如果顺序重要，请按信封 `created_at` 排序。
- **重试带有相同的 `event.id`。** 在非 2xx 上至少重试一次。对 `event.id` 进行重复数据删除。
- **3xx 失败。** 不遵循重定向 — 如果您的端点移动，请更新控制台中的 URL。
- **在连续 20 次失败传送后自动禁用**，或者如果主机名解析为私有 IP 或返回重定向，则立即禁用。在控制台中手动重新启用。
- **精简有效负载是有意为之。** 不要指望 Webhook 主体上有 `stop_reason`、`outcome_evaluations`、凭据机密等 - 获取资源。
</doc>

<doc path="shared/model-migration.md">
# 模型迁移指南

> **如果您通过 `/claude-api migrate` 到达：** 这是正确的文件。按顺序执行以下步骤 - 不要将它们总结回给用户。在接触任何文件之前，请从步骤 0（确认范围）开始。

如何将现有代码移动到较新的 Claude 模型。涵盖重大变更、已弃用的参数以及退役型号的直接替代品。

如需最新的权威版本（包含每种受支持语言的代码示例），请从 `shared/live-sources.md` Web 获取 **迁移指南** URL。使用此文件作为综合的技能驻留参考；每当模型发布或重大更改可能改变情况时，就回到实时文档。

**此文件很大。** 使用下面的部分名称进行跳转（或使用 `Grep` 此文件作为标题文本）。首先阅读步骤 0 和步骤 1 — 它们适用于每次迁移。然后仅阅读您要迁移到的模型的每个目标部分。

|部分|当你需要的时候 |
|---|---|
|步骤0：确认迁移范围|始终 - 在任何编辑之前 |
|第1步：对每个文件进行分类 |始终 — 决定是否交换、添加或跳过 |
| Per-SDK 语法参考 |将本指南中的 Python 示例翻译为 TypeScript / Go / Ruby / Java / C# / PHP |
|目的地型号/退役型号替换|选择目标模型|
|源模型的重大变化 |迁移到 Opus 4.6 / Sonnet 4.6 |
|迁移到 Opus 4.7 |迁移到 Opus 4.7（重大更改、静默默认设置、行为转变）|
| Opus 4.7 迁移清单 | 4.7 的必需项目与可选项目，标记为 `[BLOCKS]` / `[TUNE]` |
|迁移到 Opus 4.8 |迁移到 Opus 4.8（没有新的重大更改；会话中系统提示；行为重新调整）|
| Opus 4.8 迁移清单 | 4.8 的必需项目与可选项目，标记为 `[BLOCKS]` / `[TUNE]` |
|验证迁移 |编辑后 — 运行时抽查 |

**TL;DR:** 更改型号 ID 字符串。如果您使用的是 `budget_tokens`，请切换到 `thinking: {type: "adaptive"}`。如果您使用辅助预填充，它们在 Opus 4.6 和 Sonnet 4.6 上均为 400 — 切换到其中一种预填充替代品（最常见的是 `output_config.format`；请参阅按源模型划分的重大更改中的表格）。如果您要从 Sonnet 4.5 迁移到 Sonnet 4.6，请显式设置 `effort` — 4.6 默认为 `high`。删除 `effort-2025-11-24` 和 `fine-grained-tool-streaming-2025-05-14` beta 标头（4.6 上的 GA）；一旦您处于适应性思维状态，请删除 `interleaved-thinking-2025-05-14`（仅在使用过渡 `budget_tokens` 逃生舱口）。然后从 `client.beta.messages.create` 回落到 `client.messages.create`。收回任何激进的“关键：你必须”工具指令； 4.6更加严格遵循系统提示。

---

## 步骤0：确认迁移范围

**在任何写入、编辑或多重编辑调用之前，请确认范围。**如果用户的请求未明确命名单个文件、特定目录或显式文件列表，**首先询问 - 不要开始编辑**。这是不可协商的：即使是像“迁移我的代码库”、“将我的项目移动到 X”、“升级到 Sonnet 4.6”或纯粹的“迁移到 Opus 4.7”这样听起来势在必行的请求，也会使范围变得模糊不清，需要一个澄清的问题。像“我的项目”、“我的代码”、“我的代码库”、“整个事情”、"everywhere" 或“跨存储库”这样的短语**含糊不清，没有指导性**——它们告诉你“做什么”，但不告诉你“在哪里”。做之前先询问。

明确提供通用范围并在接触任何文件之前等待答案：

1.整个工作目录
2.特定子目录（例如`src/`、`app/`、`services/billing/`）
3. 特定文件或文件列表

将其作为一个澄清问题呈现出来，以便用户可以一次性回答。 **仅当范围已经明确时才继续而不询问** — 用户命名了一个确切的文件（“将 `extract.py` 迁移到 Sonnet 4.6”），指向特定目录（“将 `services/billing/` 下的所有内容迁移到 Opus 4.6”），列出了特定文件（“更新`a.py` 和 `b.py`”），或者已经在之前回答过范围问题。如果您可以回答“此更改将触及哪些文件？”的问题仅凭提示中的精确列表即可继续。如果没有，请询​​问。

**工作示例。** 如果用户说“将我的项目移至 Opus 4.6。我希望在任何有意义的地方都采用自适应思维。”* 您不知道“我的项目”是否意味着整个工作目录，只是 `src/`，只是生产代码，还是其他东西 - `everywhere` 使意图明确（更新每个调用站点*在范围内*），但范围本身仍然是未定义。不要开始编辑。回应：

> 在我开始编辑之前，你能确认一下范围吗？我可以迁移：
> 1.工作目录中的每个`.py`文件
> 2.仅`src/`（生产代码）下的文件
> 3. 您指定的特定子目录或文件列表
>
> 哪一个？

然后等待答案。这同样适用于 *“迁移到 Opus 4.7”* 和裸 *“帮助我升级到 Sonnet 4.6”* - 在编辑前询问。

**调整范围问题（大型存储库）。** 在询问之前，get 每个目录的计数，以便用户可以具体选择：```sh
rg -l "<old-model-id>" --type-not md | cut -d/ -f1 | sort | uniq -c | sort -rn
```提供范围问题中的细分（例如*“在 3 个目录中找到 217 个引用：api/ (130)、api-go/ (62)、routing/ (25)。要迁移哪个？”*）。在测量之前还要确认 `git status` 是干净的 - 意外的修改意味着并发过程；在继续之前停止并调查。

---

## 步骤1：对每个文件进行分类

并非每个包含旧型号 ID 的文件都是 API 的**调用者**。在编辑之前，将每个文件分类到以下存储桶之一 - 正确的操作有所不同：

| ＃|桶|看起来像什么 |行动|
|---|---|---|---|
| 1 | **调用 API/SDK** | `client.messages.create(model=…)`、`anthropic.Anthropic()`，请求有效负载 |交换模型 ID **并**应用目标版本的重大更改清单（如下）。 |
| 2 | **定义或服务模型** |模型注册表、OpenAPI 规范、路由/队列配置、模型策略枚举、生成的目录 |旧条目**保留**（模型仍然可用）。询问是否（a）添加新型号，（b）保留，或（c）淘汰旧型号——切勿盲目更换。 **如果您不能询问，则默认为 (a)：在旁边添加新模型并对其进行标记** — 替换将取消注册仍在生产中的模型。 |
| 3 | **将 ID 作为不透明字符串引用** | UI 后备常量、功能门子字符串检查、通用测试装置、标签解析器、环境默认值 |通常交换字符串并验证任何解析器/正则表达式/子字符串匹配是否处理新 ID - 但首先检查下面的子情况。 |
| 4 | **后缀变体 ID** | `claude-<model>-<suffix>` 类似 `-fast`、`-1024k`、`-200k`、`[1m]`，带日期的快照 |这些是部署/路由标识符，而不是公共模型 ID。 **不要假设存在等效的新型号。** 首先在注册表中进行验证；如果不存在，则保留该字符串并对其进行标记。 |

**桶 3 子情况 - 在交换字符串引用之前，检查：**

- **功能门**（例如 `if 'opus-4-6' in model_id:` 启用某项功能）→ **在旁边添加新 ID**，不要替换。旧模型仍然提供服务并且仍然具有该功能，因此替换会默默地禁用仍然流经的任何旧模型流量的该功能。如果您知道旧模型流量不会到达此门（单调用者代码库完全迁移），则替换即可；如果不确定，请添加到旁边。
- **注册表断言测试**（例如 `assert "claude-X" in supported_models`、`test_X_has_N_clusters`）→ **同时为新模型添加断言；保留旧模型。** 旧模型仍然可用，因此其断言仍然有效 - 但注册表还应包含新模型，因此也断言这一点。启发式：如果测试引用列表中的多个模型版本，则这是注册表测试；如果结构中的一个模型仅与其自身进行比较，那么它就是一个通用夹具。
- **冻结/生成的快照** → **重新生成**，不要手动编辑。
- **耦合到定义者**（例如，通过共享 `conftest` 种子列表通过模型授权的集成测试，或对计费层/速率限制组枚举或生成的 SKU/定价目录进行断言）→ **首先验证定义者是否具有新模型条目。** 如果没有，请添加一个种子条目（重用最近的现有层作为占位符）；如果您不能自信地做到这一点，请询问用户如何填充定义器。 **不要跳过测试。** 在不填充定义器的情况下进行交换将使测试在运行时失败。

具体迁移测试时：通常不存在中断参数（`temperature`、`top_p`、`budget_tokens`）——测试夹具很少在占位符模型上设置采样参数。仍然需要进行重大更改扫描，但预计大部分结果都是干净的。

**首先找到有意标记的同步点。** 许多代码库标记点在每次模型启动时都必须使用注释标记进行更改，例如 `MODEL LAUNCH`、`KEEP IN SYNC`、`@model-update` 或类似标记。 Grep 用于存储库*在*广泛的模型 ID grep 之前使用的任何约定 - 这些标记指向承载变化。

---

## Per-SDK 语法参考

本指南中的代码示例为 Python。 **每个官方 Anthropic SDK 中都存在相同的字段** —不锈钢从相同的 OpenAPI 规范生成所有 7 个字段，因此 JSON 字段名称映射 1:1，仅存在大小写约定差异。使用下面的行将 Python 示例转换为您要迁移的 SDK。

> **在将类型和方法名称写入客户代码之前，根据 SDK 源验证类型和方法名称。** Web 从 `shared/live-sources.md` 中的 SDK 源代码表中获取相关存储库（每个 SDK 一行）并确认确切的符号 - 特别是对于类型化 SDK （Go、Java、C#）其中联合/构建器名称可能与 JSON 形状不同。不要猜测下表或 `<lang>/claude-api/README.md` 中没有的类型名称。


### `thinking` — `budget_tokens` → 自适应

| SDK |前|之后 |
|---|---|---|
| Python | `thinking={"type": "enabled", "budget_tokens": N}` | `thinking={"type": "adaptive"}` |
| TypeScript | `thinking: { type: 'enabled', budget_tokens: N }` | `thinking: { type: 'adaptive' }` |
|去 | `Thinking: anthropic.ThinkingConfigParamOfEnabled(N)` | `Thinking: anthropic.ThinkingConfigParamUnion{OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{}}` |
|红宝石 | `thinking: { type: "enabled", budget_tokens: N }` | `thinking: { type: "adaptive" }` |
|爪哇 | `.thinking(ThinkingConfigEnabled.builder().budgetTokens(N).build())` | `.thinking(ThinkingConfigAdaptive.builder().build())` |
| C# | `Thinking = new ThinkingConfigEnabled { BudgetTokens = N }` | `Thinking = new ThinkingConfigAdaptive()` |
| PHP | `thinking: ['type' => 'enabled', 'budget_tokens' => N]` | `thinking: ['type' => 'adaptive']` |

### 采样参数 — `temperature` / `top_p` / `top_k`

（在 Opus 4.7 上完全删除该字段；在 Claude 4.x 上最多保留 `temperature` 或 `top_p` 之一。）

| SDK |要删除的字段 |
|---|---|
| Python | `temperature=…`、`top_p=…`、`top_k=…` |
| TypeScript | `temperature: …`、`top_p: …`、`top_k: …` |
|去 | `Temperature: anthropic.Float(…)`、`TopP: anthropic.Float(…)`、`TopK: anthropic.Int(…)` |
|红宝石 | `temperature: …`、`top_p: …`、`top_k: …` |
|爪哇 | `.temperature(…)`、`.topP(…)`、`.topK(…)` |
| C# | `Temperature = …`、`TopP = …`、`TopK = …` |
| PHP | `temperature: …`、`topP: …`、`topK: …` |

### 预填充替换 — 通过 `output_config.format` 的结构化输出

| SDK |删除（最后一个助手轮）|添加|
|---|---|---|
| Python | `{"role": "assistant", "content": "…"}` | `output_config={"format": {"type": "json_schema", "schema": SCHEMA}}` |
| TypeScript | `{ role: 'assistant', content: '…' }` | `output_config: { format: { type: 'json_schema', schema: SCHEMA } }` |
|去 |尾随 `anthropic.MessageParam{Role: "assistant", …}` | `OutputConfig: anthropic.OutputConfigParam{Format: anthropic.JSONOutputFormatParam{…}}` |
|红宝石 | `{ role: "assistant", content: "…" }` | `output_config: { format: { type: "json_schema", schema: SCHEMA } }` |
|爪哇 |尾随 `Message.builder().role(ASSISTANT)…` | `.outputConfig(OutputConfig.builder().format(JsonOutputFormat.builder()…build()).build())` |
| C# |尾随 `new Message { Role = "assistant", … }` | `OutputConfig = new OutputConfig { Format = new JsonOutputFormat { … } }` |
| PHP |尾随 `['role' => 'assistant', 'content' => '…']` | `outputConfig: ['format' => ['type' => 'json_schema', 'schema' => $SCHEMA]]` |

### `thinking.display` — 选择重新进行归纳推理 (Opus 4.7)

| SDK |添加|
|---|---|
| Python | `thinking={"type": "adaptive", "display": "summarized"}` |
| TypeScript | `thinking: { type: 'adaptive', display: 'summarized' }` |
|去 | `Thinking: anthropic.ThinkingConfigParamUnion{OfAdaptive: &anthropic.ThinkingConfigAdaptiveParam{Display: anthropic.ThinkingConfigAdaptiveDisplaySummarized}}` |
|红宝石 | `thinking: { type: "adaptive", display: "summarized" }`（或直接构造模型类时的 `display_:`）|
|爪哇 | `.thinking(ThinkingConfigAdaptive.builder().display(ThinkingConfigAdaptive.Display.SUMMARIZED).build())` |
| C# | `Thinking = new ThinkingConfigAdaptive { Display = Display.Summarized }` |
| PHP | `thinking: ['type' => 'adaptive', 'display' => 'summarized']` |

对于这些表中没有的任何字段，Python 示例中的 JSON 键直接转换为： `snake_case` for Python/TypeScript/Ruby，对于 PHP，`camelCase` 命名参数；对于 Go/C#，`PascalCase` 结构字段；对于 Java，`camelCase` 构建器方法。

---

## 解释你所做的每一个改变

对于没有阅读过发行说明的用户来说，迁移编辑通常看起来是任意的——删除了 `temperature`、删除了预填充、重写了系统提示语句。 **对于每次编辑，告诉用户您更改了什么以及为什么**，与特定的 API 或激发它的行为变化相关联。在工作时，而不是在最后，在总结中这样做。

特别明确**系统提示编辑**。用户正确地保护他们的提示，提示调整更改是判断调用（不是硬性的 API 要求）。对于任何提示编辑：

- 引用前后文本。
- 说明激发它的行为转变（例如*“Opus 4.7 根据任务复杂性校准响应长度，因此我添加了明确的长度指令”*，或*“4.6 更字面地遵循指令，因此“关键：您必须使用搜索工具”现在将过度触发 - 软化为“在……时使用搜索工具””*）。
- 明确哪些提示编辑是**可选调整**（语气、长度、子代理指导），哪些代码编辑是**需要避免 400**（采样参数、`budget_tokens`、预填充）。切勿将可选的提示更改作为强制性的。

如果您要申请多个立即调整提示编辑，将它们作为简短列表提供，用户可以逐项接受或拒绝，而不是默默地重写系统提示。

---

## 迁移之前

1. **确认目标型号 ID。** 仅使用 `shared/models.md` 中的确切字符串 — 不要将日期后缀附加到别名（`claude-opus-4-6`，而不是 `claude-opus-4-6-20251101`）。猜测 ID 将出现 404。
2. **使用此清单检查您的代码使用了哪些功能**：
   - `thinking: {type: "enabled", budget_tokens: N}` → 迁移到 Opus 4.6 / Sonnet 4.6 上的自适应思维（仍然有效，但已弃用）
   - 助理转预填充（`messages` 以 `role: "assistant"` 结尾）→ 必须在 Opus 4.6 / Sonnet 4.6 上更改（返回 400）
   - `messages.create()` 上的 `output_format` 参数 → 必须在所有型号上更改（已弃用 API 范围）
   - `max_tokens > ~16000` → 必须在任何型号上进行流式传输（超过 ~16K 存在 SDK HTTP 超时的风险）。流式传输时，Sonnet 4.6 / Haiku 4.5 上限为 64K，Opus 4.6 上限为 128K
   - Beta 标头 `effort-2025-11-24`、`fine-grained-tool-streaming-2025-05-14`、`interleaved-thinking-2025-05-14` → 4.6 上的 GA，删除它们并从 `client.beta.messages.create` 切换到 `client.messages.create`
   - 移动 Sonnet 4.5 → Sonnet 4.6，不设置 `effort` → 4.6 默认为 `high`，这可能会改变您的延迟/成本配置文件
   - 系统提示语言为 `CRITICAL`、`MUST`、`If in doubt, use X` → 可能在 4.6 上过度触发（请参阅提示行为更改）
   - 从 3.x / 4.0 / 4.1 开始：还检查采样参数 (`temperature` + `top_p`)、工具版本 (`text_editor_20250728`)、`refusal` + `model_context_window_exceeded` 停止原因，尾随换行符工具参数处理
3. **首先测试单个请求。** 针对新模型运行一次调用，检查响应，然后推出。

---

## 目标模型（推荐目标）

|如果您在... |迁移到|为什么 |
| -------------------------------------------------- | ------------------ | ------------------------------------------------- |
|作品 4.7 | `claude-opus-4-8` |最有能力的模型；与 4.7 相同的 API 表面（没有新的重大变化）——主要是快速重新调整；请参阅迁移到 Opus 4.8 |
|作品 4.6 | `claude-opus-4-8` |应用 Opus 4.7 重大更改，然后重新调整 4.8 |
|作品 4.0 / 4.1 / 4.5 / 作品 3 | `claude-opus-4-8` |按顺序应用 4.6 → 4.7 → 4.8（自适应思维，丢弃采样参数，然后重新调整）|
|十四行诗 4.0 / 4.5 / 3.7 / 3.5 | `claude-sonnet-4-6`|最佳速度/智力平衡；适应性思维； 64K 输出 |
|俳句 3 / 3.5 | `claude-haiku-4-5` |最快、最具性价比|

默认为调用者所在层的最新 Opus，除非他们明确选择了其他方式。 Opus 迁移层：如果您使用的是 Opus 4.6 或更早版本，请按顺序应用每个版本的部分，直至达到您的目标（例如 4.5 → 4.8 表示依次为 4.6、4.7 和 4.8 部分）。 4.7 → 4.8 迁移没有新的重大更改 - 请参阅下面的迁移到 Opus 4.8。

---

## 退役型号替代品

这些模型返回 404 — 立即更新：

|退休模特|退休 |直接更换 |
| -------------------------------------- | ------------- | -------------------- |
| `claude-3-7-sonnet-20250219` | 2026 年 2 月 19 日 | `claude-sonnet-4-6` |
| `claude-3-5-haiku-20241022` | 2026 年 2 月 19 日 | `claude-haiku-4-5` |
| `claude-3-opus-20240229` | 2026 年 1 月 5 日 | `claude-opus-4-8` |
| `claude-3-5-sonnet-20241022` | 2025 年 10 月 28 日 | `claude-sonnet-4-6` |
| `claude-3-5-sonnet-20240620` | 2025 年 10 月 28 日 | `claude-sonnet-4-6` |
| `claude-3-sonnet-20240229` | 2025 年 7 月 21 日 | `claude-sonnet-4-6` |
| `claude-2.1`，`claude-2.0` | 2025 年 7 月 21 日 | `claude-sonnet-4-6` |

## 已弃用的模型（即将退役）

|型号|退休|更换|
| -------------------------------------- | ------------- | -------------------- |
| `claude-3-haiku-20240307` | 2026 年 4 月 19 日 | `claude-haiku-4-5` |
| `claude-opus-4-20250514` | 2026 年 6 月 15 日 | `claude-opus-4-8` |
| `claude-sonnet-4-20250514` | 2026 年 6 月 15 日 | `claude-sonnet-4-6` |

---

## 源模型的重大变化

### 从 Sonnet 4.5 迁移到 Sonnet 4.6（努力默认更改）

Sonnet 4.5 没有 `effort` 参数； Sonnet 4.6 默认为 `high`。如果您只是切换模型字符串而不执行其他操作，您可能会看到明显更高的延迟和令牌使用量。明确设置 `effort`。

**推荐起点：**

|工作量|开始于 |笔记|
| ------------------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------- |
|聊天、分类、内容生成 | `low` |使用 `thinking: {"type": "disabled"}`，您将看到与 Sonnet 4.5 no-thinking 类似或更好的性能 |
|大多数应用程序（平衡）| `medium` |质量与成本的默认最佳点|
|代理编码、工具密集型工作流程 | `medium` |与自适应思维和慷慨的 `max_tokens` 配对（流式传输高达 64K — Sonnet 4.6 的上限）|
|自主多步智能体，长视野循环 | `high` |如果延迟/令牌成为问题，则缩小至 `medium` |
|电脑使用代理| `high` + 自适应 | Sonnet 4.6最好的计算机使用精度是自适应+高 |

特别是对于非思考型聊天工作负载：```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8192,
    thinking={"type": "disabled"},
    output_config={"effort": "low"},
    messages=[{"role": "user", "content": "..."}],
)
```**何时使用 Opus 4.6：** 最困难和最长的问题 - 大型代码迁移、深入研究、扩展自主工作。 Sonnet 4.6 凭借快速周转和成本效率而获胜。

### 迁移到 Opus 4.6 / Sonnet 4.6（从任何旧型号）

**1.不推荐使用手动扩展思维——使用适应性思维。**

`thinking: {type: "enabled", budget_tokens: N}`（具有固定代币预算的手动扩展思维）在 Opus 4.6 和 Sonnet 4.6 上已弃用。将其替换为 `thinking: {type: "adaptive"}`，这让 Claude 可以决定思考的时间和程度。适应性思维还可以自动实现交错思维（不需要 beta 标题）。```python
# Old (still works on older models, deprecated on 4.6)
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 8000},
    messages=[...]
)

# New (Opus 4.6 / Sonnet 4.6)
response = client.messages.create(
    model="claude-opus-4-6",  # or "claude-sonnet-4-6"
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},  # optional: low | medium | high | max
    messages=[...]
)
```适应性思维是长期目标，在内部评估中它优于手动扩展思维。能移动的时候就移动吧。

**过渡逃生舱口：** 手动扩展思考在 Opus 4.6 和 Sonnet 4.6 上仍然“有效”（已弃用，将在未来版本中删除）。如果您在迁移时需要硬性上限（例如，在调整 `effort` 之前限制失控工作负载上的代币支出），您可以将 `budget_tokens` 与显式 `effort` 值一起保留，然后在后续操作中将其删除。 `budget_tokens` 必须严格小于 `max_tokens`：```python
# Transitional only — deprecated, plan to remove
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16384,
    thinking={"type": "enabled", "budget_tokens": 8192},  # must be < max_tokens
    output_config={"effort": "medium"},
    messages=[...],
)
```如果用户要求 4.6 上的“思考预算”，首选答案是 `effort` — 使用 `low`、`medium`、`high` 或 `max` （仅限作品层 - 不是十四行诗或俳句）而不是令牌计数。

**2.努力参数（仅限 Opus 4.5、Opus 4.6、Sonnet 4.6）。**

控制思考深度和总体代币支出。进入`output_config`内部，不是顶层。默认为 `high`。 `max` 仅是 Opus 层（Opus 4.6 及更高版本 - 不是 Sonnet 或 Haiku）。 Sonnet 4.5 和 Haiku 4.5 上的错误。```python
output_config={"effort": "medium"}  # often the best cost / quality balance
```### 迁移到 4.6 系列（Opus 4.6 和 Sonnet 4.6）

**3.助理轮预填充返回 400（Opus 4.6 和 Sonnet 4.6）。**

Opus 4.6 或 Sonnet 4.6 不再支持最后一个助理回合的预填充响应 — 两者都会返回 400。在对话中的*其他地方*添加助理消息（例如，对于少数镜头示例）仍然有效。选择与预填充功能相匹配的替代品：

|预填充用于 |更换|
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
|强制 JSON / YAML / 架构输出 | `output_config.format` 与 `json_schema` — 参见下面的示例 |
|强制分类标签 |具有包含有效标签或结构化输出的枚举字段的工具 |
|跳过序言 (`Here is the summary:\n`) |系统提示说明： *“直接回复，不带序言。不要以‘这里是…’或‘基于…’等短语开头。”* |
|避免不良拒绝 |通常不再需要——4.6 拒绝更合适。简单的用户转向提示就足够了。                                   |
|继续中断的响应 |将延续移动到用户回合：*“您之前的响应被中断并以 `[last text]` 结束。从那里继续。”* |
|注射提醒/情境补水|改为注入用户回合。对于复杂的代理工具，通过工具调用或在压缩期间公开上下文。                      |```python
# Old (fails on Opus 4.6 / Sonnet 4.6) — prefill forcing JSON shape
messages=[
    {"role": "user", "content": "Extract the name."},
    {"role": "assistant", "content": "{\"name\": \""},
]

# New — structured outputs replace the prefill
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    output_config={"format": {"type": "json_schema", "schema": {...}}},
    messages=[{"role": "user", "content": "Extract the name."}],
)
```**4.适用于 `max_tokens > ~16K`（所有型号）的流；仅 Opus 4.6 就达到 128K。**

无论型号如何，非流式请求在高 `max_tokens` 时都会遇到 SDK HTTP 超时 - 对于高于 ~16K 输出的任何流式传输。流媒体上限因型号而异：Sonnet 4.6 和 Haiku 4.5 上限为 64K，仅 Opus 4.6 上限为 128K。```python
with client.messages.stream(model="claude-opus-4-6", max_tokens=64000, ...) as stream:
    message = stream.get_final_message()
```**5.工具调用 JSON 转义可能有所不同（Opus 4.6 和 Sonnet 4.6）。**

两种 4.6 模型都可以生成带有 Unicode 或正斜杠转义的工具调用 `input` 字段。始终使用 `json.loads()` / `JSON.parse()` 进行解析 - 绝不与序列化输入进行原始字符串匹配。

### 所有型号

**6。 `output_format` → `output_config.format`（API 宽）。**

`messages.create()` 上的旧顶级 `output_format` 参数已弃用。请改用 `output_config.format`。这不是 4.6 特有的 — 适用于每个模型。

---

## 在 4.6 上删除的 Beta 标头

4.5 上需要的几个 beta 标头现在在 4.6 上已成为 GA，应该被删除。把它们留在里面是无害的，但会产生误导。删除它们还可以让您从 `client.beta.messages.create(...)` 移回 `client.messages.create(...)`。

|标题 | 4.6 状态 |行动|
| ---------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------- |
| `effort-2025-11-24` |努力参数是 GA |删除 |
| `fine-grained-tool-streaming-2025-05-14` | GA |删除 |
| `interleaved-thinking-2025-05-14` |适应性思维自动实现交错思维 |使用适应性思维时删除；在 Sonnet 4.6 上仍然可以使用*手动扩展思维，但该路径已被弃用 |
| `token-efficient-tools-2025-02-19` |内置于所有 Claude 4+ 型号 |删除（无效果）|
| `output-128k-2025-02-19` |内置于 Claude 4+ 模型 |删除（无效果）|

删除所有这些并完成转向适应性思维后，您可以将 SDK 调用站点从 beta 命名空间切换回常规命名空间：```python
# Before
response = client.beta.messages.create(
    model="claude-opus-4-5",
    betas=["interleaved-thinking-2025-05-14", "effort-2025-11-24"],
    ...
)

# After
response = client.messages.create(
    model="claude-opus-4-6",
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    ...
)
```---

## 来自 3.x / 4.0 / 4.1 → 4.6 时的其他更改

如果您要从 Opus 4.1、Sonnet 4、Sonnet 3.7 或较旧的 Claude 3.x 模型直接跳到 4.6，请应用上面的所有内容*加上*本节中的项目。已经使用 Opus 4.5 / Sonnet 4.5 的用户可以跳过此操作。

**1.采样参数：`temperature` 或 `top_p`，不能同时使用两者。**

在每个 Claude 4+ 模型上通过这两项都会出错：```python
# Old (3.x only — errors on 4+)
client.messages.create(temperature=0.7, top_p=0.9, ...)

# New
client.messages.create(temperature=0.7, ...)  # or top_p, not both
```**2.更新工具版本。**

4+ 不支持旧版工具版本。 **`type` 和 `name` 字段均发生变化** — `text_editor_20250728` 和 `str_replace_based_edit_tool` 是一对；更新其中一个而不需要其他 400。还要从文本编辑器集成中删除 `undo_edit` 命令：

|旧|新 |
| ------------------------------------------------- | ------------------------------------------------------- |
| `text_editor_20250124` + `str_replace_editor` | `text_editor_20250728` + `str_replace_based_edit_tool` |
| `code_execution_*`（早期版本）| `code_execution_20250825` |
| `undo_edit` 命令 | *（不再支持 — delete 调用站点）* |```python
# Before
tools = [{"type": "text_editor_20250124", "name": "str_replace_editor"}]

# After — BOTH fields change
tools = [{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}]
```**3.处理`refusal`停止原因。**

Claude 4+ 可以在响应中返回 `stop_reason: "refusal"`。如果您的代码仅处理 `end_turn` / `tool_use` / `max_tokens`，请添加分支：```python
if response.stop_reason == "refusal":
    # Surface the refusal to the user; do not retry with the same prompt
    ...
```**4.处理 `model_context_window_exceeded` 停止原因 (4.5+)。**

与 `max_tokens` 不同：这意味着模型达到了*上下文窗口*限制，而不是请求的输出上限。处理两者：```python
if response.stop_reason == "model_context_window_exceeded":
    # Context window exhausted — compact or split the conversation
    ...
elif response.stop_reason == "max_tokens":
    # Requested output cap hit — retry with higher max_tokens or stream
    ...
```**5.工具调用字符串参数中保留尾随换行符 (4.5+)。**

4.5 和 4.6 保留旧型号删除的尾随换行符。如果您的工具实现针对工具调用 `input` 值（例如 `if name == "foo"`）进行精确字符串匹配，请验证当模型发送 `"foo\n"` 时它们仍然匹配。在接收端使用 `.rstrip()` 进行标准化通常是最简单的修复方法。

**6。 Haiku：各代之间重置速率限制。**

Haiku 4.5 有自己的速率限制池，与 Haiku 3 / 3.5 分开。如果您在迁移时增加流量，请在 [API 速率限制](https://platform.claude.com/docs/en/api/rate-limits) 中检查您的层级的 Haiku 4.5 限制 — 能够轻松满足 Haiku 3.5 流量的配额可能需要在 4.5 上提高相同流量的层级。

---

## 提示行为更改（Opus 4.5 / 4.6、Sonnet 4.6）

这些不会破坏您的代码，但在 4.5 及更早版本上有效的提示可能会在 4.6 上过度或不足触发。根据需要进行调整。

**1.激进的指令会导致过度触发。** Opus 4.5 和 4.6 比早期型号更严格地遵循系统提示。为“克服”旧的不情愿而写的提示现在过于激进：

|之前（适用于 4.0 / 4.5）|之后（在 4.6 上使用）|
| ------------------------------------------- | ---------------------------------------------------- |
| `CRITICAL: You MUST use this tool when...` | `Use this tool when...` |
| `Default to using [tool]` | `Use [tool] when it would improve X` |
| `If in doubt, use [tool]` | *（delete — 不再需要）* |

如果模型现在过度触发某种工具或技能，解决方法几乎总是回拨语言，而不是添加更多护栏。

**2.过度思考和过度探索 (Opus 4.6)。** 在较高的 `effort` 设置下，Opus 4.6 在回答之前会进行更多探索。如果这会消耗太多的思考代币，请先降低 `effort` （`medium` 通常是最佳点），然后再添加散文指令来限制推理。

**3.过度渴望的子代理生成 (Opus 4.6)。** Opus 4.6 非常倾向于委派给子代理。如果您看到它为直接 `grep` 或 `read` 可以解决的问题生成子代理，请添加指导：*“仅将子代理用于并行或独立工作流。对于单文件读取或顺序操作，请直接工作。”*

**4.过度设计 (Opus 4.5 / 4.6)。** 两种模型都可能添加超出要求的额外文件、抽象或防御性错误处理。如果您想要最小的更改，请明确提示：*“仅进行直接请求的更改。不要为不可能发生的场景添加帮助程序、抽象或错误处理。”*

**5. LaTeX 数学输出 (Opus 4.6)。** Opus 4.6 默认使用 LaTeX (`\frac{}{}`、`$...$`) 来处理数学和技术内容。如果您需要纯文本，请明确指示：*“将所有数学格式设置为纯文本 - 没有 LaTeX、没有 `$`、没有 `\frac{}{}`。使用 `/` 进行除法，使用 `^` 进行指数。”*

**6。跳过口头摘要（4.6 系列）。** 4.6 模型更加简洁，可能会在工具调用后跳过摘要段落，直接跳到下一个操作。如果您依赖这些摘要来获得可见性，请添加：*“完成涉及工具使用的任务后，请提供您所做工作的简短摘要。”*

**7. "Think" 作为触发词（禁用思考的 Opus 4.5）。** 当 `thinking` 关闭时，Opus 4.5 对“思考”一词特别敏感，并且可能会推理出超出您想要的内容。请改用 `consider`、`evaluate` 或 `reason through`。

---

## 模型 ID 重命名快速参考

|旧字符串（迁移源）|新字符串 |
| ------------------------------------------ | ------------------ |
| `claude-opus-4-7` | `claude-opus-4-8` |
| `claude-opus-4-6` | `claude-opus-4-8` |
| `claude-opus-4-5` | `claude-opus-4-8` |
| `claude-opus-4-1` | `claude-opus-4-8` |
| `claude-opus-4-0` | `claude-opus-4-8` |
| `claude-sonnet-4-5` | `claude-sonnet-4-6`|
| `claude-sonnet-4-0` | `claude-sonnet-4-6`|

较旧的别名（`claude-opus-4-7`、`claude-opus-4-6`、`claude-opus-4-5`、`claude-sonnet-4-5` 等）仍然有效，如果您在升级前需要时间，可以固定 — 请参阅 `shared/models.md` 了解完整的旧版别名列表。

### Amazon Bedrock 模型 ID

如果代码使用 `AnthropicBedrockMantle` 客户端（Python `anthropic[bedrock]`、TypeScript `@anthropic-ai/bedrock-sdk`、Java `BedrockMantleBackend`、Go `bedrock.NewMantleClient` 等）或目标 `https://bedrock-mantle.{region}.api.aws/anthropic`，它在 Amazon Bedrock 中的 **Claude** 上运行。本指南中的所有重大更改均保持不变 - 它提供相同的消息 API 形状 - 但模型 ID 带有 `anthropic.` 提供商前缀：

|第一方身份证 |基岩 ID |
|---|---|
| `claude-opus-4-8` | `anthropic.claude-opus-4-8` |
| `claude-opus-4-7` | `anthropic.claude-opus-4-7` |
| `claude-haiku-4-5` | `anthropic.claude-haiku-4-5` |

迁移基岩文件时，应用与第一方相同的重命名表行，然后保留/添加 `anthropic.` 前缀。 **不要**为 Bedrock 客户端生成第一方 `claude-*` ID — 它将是 400。

**跳过 Bedrock：** `code_execution_*` 工具版本清单项和 **任务预算** 部分 — 两者都是仅限第一方的功能（Bedrock 不支持服务器端 Anthropic 工具或 `task-budgets-2026-03-13` beta）。本指南中的其他内容 - `effort`、自适应/扩展思维、`output_config.format`、`thinking.display`、细粒度工具流、令牌计数 - 均可在 Bedrock 上获取。

> **超出范围：** 旧版 Amazon Bedrock 集成（带有 ARN 版本 ID（例如 `anthropic.claude-3-5-sonnet-20241022-v2:0`）的 `InvokeModel` / `Converse` API）使用不同的请求形状和模型 ID 格式。本指南不涉及它；如果用户在两个 Bedrock 集成之间迁移，则在 `shared/live-sources.md` 中 WebFetch Bedrock 页面。

### AWS 上的克劳德平台

如果代码使用 `AnthropicAWS` / `AnthropicAws` / `anthropicaws.NewClient` / `AnthropicAwsClient` （或目标 `https://aws-external-anthropic.{region}.api.aws`），则它在 **Claude Platform on AWS** 上运行 - 人工操作，当日API平价。模型 ID 是**裸第一方**字符串； **逐字**应用上面的重命名表，并且本指南中的每个重大更改部分保持不变。没有什么可以跳过的。 **不要**添加 `anthropic.` 前缀（这是 Amazon Bedrock，一个单独的产品）。有关客户端/身份验证详细信息，请参阅 `shared/claude-platform-on-aws.md`。

---

## 迁移清单

每个项目都被标记为：**`[BLOCKS]`** 项目会导致 400 错误、无限循环、静默超时或错过的工具选择错误 - 将这些应用为代码编辑，而不是建议。 **`[TUNE]`** 项目是质量/成本调整。

对于调用 `messages.create()` / 等效 SDK 方法的每个文件：

- [ ] **[BLOCKS]** 将 `model=` 字符串更新为新别名
- [ ] **[BLOCKS]** 将 `budget_tokens` 替换为 `thinking={"type": "adaptive"}`（在 Opus 4.6 / Sonnet 4.6 上已弃用）
- [ ] **[BLOCKS]** 将 `format` 从顶层 `output_format` 移至 `output_config.format`
- [ ] **[BLOCKS]** 如果针对 Opus 4.6 或 Sonnet 4.6，请删除所有辅助转弯预填充（请参阅预填充替换表）
- [ ] **[BLOCKS]** 如果 `max_tokens > ~16000` 则切换到流式传输（否则 SDK HTTP 超时）
- [ ] **[TUNE]** 验证工具输入处理解析 JSON 而不是原始字符串匹配序列化输入（4.6 可能会以不同方式转义 Unicode/正斜杠；大多数 SDK 已将 `block.input` 公开为解析对象）
- [ ] **[TUNE]** 显式设置 `output_config={"effort": "..."}` — 尤其是在移动 Sonnet 4.5 → Sonnet 4.6 时（4.6 默认为 `high`）
- [ ] **[TUNE]** 删除 GA beta 标头：`effort-2025-11-24`、`fine-grained-tool-streaming-2025-05-14`、`token-efficient-tools-2025-02-19`、`output-128k-2025-02-19`；在适应性思维中删除一次 `interleaved-thinking-2025-05-14`
- [ ] **[TUNE]** 一旦删除所有测试版，切换 `client.beta.messages.create(...)` → `client.messages.create(...)`
- [ ] **[TUNE]** 查看激进工具语言的系统提示（`CRITICAL:`、`MUST`、`If in doubt`）并将其拨回

**来自 3.x / 4.0 / 4.1 的额外项目：**
- [ ] **[BLOCKS]** 删除 `temperature` 或 `top_p`（在 Claude 4+ 上通过两个 400 秒）
- [ ] **[BLOCKS]** 将文本编辑器工具 `type` 更新为 `text_editor_20250728`
- [ ] **[BLOCKS]** 将文本编辑器工具 `name` 更新为 `str_replace_based_edit_tool` — **仅更改 `type` 并保留 `name: "str_replace_editor"` 返回 400**
- [ ] **[BLOCKS]** 将代码执行工具更新为 `code_execution_20250825`
- [ ] **[BLOCKS]** Delete 任何 `undo_edit` 命令调用站点
- [ ] **[TUNE]** 添加对 `stop_reason == "refusal"` 的处理
- [ ] **[TUNE]** 添加对 `stop_reason == "model_context_window_exceeded"` (4.5+) 的处理
- [ ] **[TUNE]** 验证工具参数字符串匹配是否允许尾随换行符（在 4.5+ 上保留）
- [ ] **[TUNE]** 如果迁移到 Haiku 4.5：审查速率限制层（与 Haiku 3.x 分开的池）

**验证：**
- [ ] 运行一个测试请求并检查 `response.stop_reason`、`response.usage` 以及工具使用/思维行为是否符合预期

对于缓存的提示：渲染顺序和哈希输入没有改变，因此现有的 `cache_control` 断点继续工作。但是，**更改模型字符串会使现有缓存无效** - 新模型上的第一个请求将刷新缓存。

---

## 迁移到 Opus 4.7

> **型号 ID `claude-opus-4-7` 具有权威性写在这里。** 当用户要求迁移到 Opus 4.7 时，请准确填写 `model="claude-opus-4-7"`。 **不要**通过 WebFetch 进行验证 - 本指南是迁移目标 ID 的真实来源。相应的条目存在于 `shared/models.md` 中。

Claude Opus 4.7 是 Anthropic 推出时最强大的模型，现在是上一代 Opus（Opus 4.8 是当前版本 - 请参阅下面的迁移到 Opus 4.8）。它具有高度自主性，在长期代理工作、知识工作、视觉任务和记忆任务方面表现异常出色。本节总结了 4.7 发布时的所有新增内容，并且仍然是来自 Opus 4.6 或更早版本的调用者的分层重大更改路径。它位于上面的 4.6 迁移之上 - 如果调用者从 Opus 4.5 或更早版本跳转，请首先应用 4.6 更改，然后应用此部分，然后应用 4.8 部分。

**TL;DR 对于已经使用 Opus 4.6 的人：** 将模型 ID 更新为 `claude-opus-4-7`，删除任何剩余的 `budget_tokens` 和采样参数（Opus 4.7 上均为 400），为 `max_tokens` 提供额外的空间并重新设定基线`count_tokens()` 针对新模型，如果向用户展示推理，则选择返回 `thinking.display: "summarized"`，并重新调整 `effort` — 这在 4.7 上比在任何以前的 Opus 上更重要。

### 重大变更（Opus 4.7 上为 400）

**删除了扩展思维。**

Claude Opus 4.7 或更高版本不再支持 `thinking: {type: "enabled", budget_tokens: N}`，并返回 400 错误。切换到适应性思维（`thinking: {type: "adaptive"}`）并使用努力参数来控制思维深度。自适应思维在 Claude Opus 4.7 上**默认关闭**：没有 `thinking` 字段的请求在不思考的情况下运行，与 Opus 4.6 的行为相匹配。明确设置 `thinking: {type: "adaptive"}` 以启用它。```python
# Before (Opus 4.6)
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=64000,
    thinking={"type": "enabled", "budget_tokens": 32000},
    messages=[{"role": "user", "content": "..."}],
)

# After (Opus 4.7)
client.messages.create(
    model="claude-opus-4-7",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},  # or "max", "xhigh", "medium", "low"
    messages=[{"role": "user", "content": "..."}],
)
```如果调用者没有使用扩展思维，则不需要进行任何更改 - 默认情况下思维处于关闭状态，或者可以使用 `thinking={"type": "disabled"}` 显式设置。

Delete `budget_tokens` 管道完全。有关替换 `effort` 值，请参阅下面的 **在 Opus 4.7 上选择工作级别** - `budget_tokens` 没有精确的 1:1 映射。

**删除了采样参数。**

Claude Opus 4.7 不再接受 `temperature`、`top_p` 和 `top_k` 参数。包含它们的请求会返回 400 错误。从您的请求负载中删除这些字段。提示是在 Claude Opus 4.7 上指导模型行为的推荐方法。如果您使用 `temperature = 0` 来实现确定性，请注意，它永远不会保证先前模型的输出相同。```python
# Before — errors on Opus 4.7
client.messages.create(temperature=0.7, top_p=0.9, ...)

# After
client.messages.create(...)  # no sampling params
```- **如果意图是决定论** — 使用带有更严格提示的 `effort: "low"`。
- **如果意图是创造性差异** - 及时替换取决于用例； **询问用户**他们希望如何引发方差。如果您不能询问，请添加一条适合用例的指令，类似于*“选择一些非发行且有趣的东西”* - 例如对于文本生成，*“改变响应中的措辞和结构”*；对于前端/设计，请使用下面**设计和前端编码**下的提议 4 方向方法。

### 选择 Opus 4.7 的努力级别

`budget_tokens` 控制了“思考”的程度； `effort` 控制思考*和*行动的程度，因此不存在精确的 1:1 映射。 **使用 `xhigh` 可以在编码和代理用例中获得最佳结果，对于大多数智能敏感用例，至少使用 `high`。** 尝试其他级别以进一步调整令牌使用和智能：

|水平|使用时 |笔记|
| --- | --- | --- |
| `max` |值得在天花板上测试的智力要求很高的任务在某些用例中可以带来收益，但可能会因代币使用量的增加而带来收益递减；可能容易想太多|
| `xhigh` | **大多数编码和代理用例** |这些的最佳设置；用作 Claude Code 中的默认值 |
| `high` |一般情报敏感用例 |平衡代币使用和情报；大多数情报敏感工作的建议最低限度|
| `medium` |成本敏感的用例需要减少代币使用，同时牺牲智能 | |
| `low` |短的、有范围的任务和延迟敏感的工作负载，但对智能不敏感 | |

### 无提示默认更改（没有错误，但行为不同）

**思考内容默认省略。**

思考块仍然出现在 Claude Opus 4.7 的响应流中，但除非您明确选择加入，否则它们的 `thinking` 字段为空。这是 Claude Opus 4.6 的无声变化，默认情况下是返回总结的思考文本。要恢复 Claude Opus 4.7 上的总结思维内容，请将 `thinking.display` 设置为 `"summarized"`。 **块字段名称未更改** — 在 `thinking` 类型块上，它仍然是 `block.thinking`；不要重命名它。

**检测此：**从 `thinking` 类型块读取 `block.thinking` （或等效内容）并将其呈现在 UI、日志或跟踪中的任何代码。 **修复的是请求参数，而不是响应处理** — 将 `display: "summarized"` 添加到 `thinking` 参数：```python
thinking={"type": "adaptive", "display": "summarized"}  # "display" is new on Opus 4.7; values: "omitted" (default) | "summarized"
```Claude Opus 4.7 上的默认值为 `"omitted"`。如果思维内容从未在任何地方出现过，那么就不需要改变。如果您的产品向用户流式传输推理，则新的默认设置会在输出开始之前显示为长时间的暂停；设置 `display: "summarized"` 以恢复思考过程中可见的进展。

**更新了令牌计数。**

Claude Opus 4.7 和 Claude Opus 4.6 计算令牌的方式不同。相同的输入文本在 Claude Opus 4.7 上产生的标记计数高于 Claude Opus 4.6，并且 `/v1/messages/count_tokens` 将为 Claude Opus 4.7 返回的标记数量与 Claude Opus 4.6 不同。 Claude Opus 4.7 的代币效率可能因工作负载形状而异。提示干预、`task_budget` 和 `effort` 可以帮助控制成本并确保适当的代币使用。请记住，这些控件可能会牺牲模型智能。 **更新 `max_tokens` 参数以提供额外的空间，包括压缩触发器。** Claude Opus 4.7 以标准 API 定价提供 1M 上下文窗口，没有长上下文溢价。

还需要检查什么：

- 针对 4.6 校准的客户端代币估算器（tiktoken 式近似值）
- 将代币乘以固定的每个代币费率的成本计算器
- 速率限制重试阈值与测量的令牌计数有关

通过在呼叫者提示的代表性示例上针对 `claude-opus-4-7` 重新运行 `client.messages.count_tokens()` 来重新设定基线。不要应用毯子乘数。对于成本敏感的工作负载，请考虑将 `effort` 减少一级（例如 `high` → `medium`）。对于代理循环，请考虑采用任务预算（如下）。

### 新功能：任务预算（测试版）

Opus 4.7 引入了**任务预算**——告诉 Claude 完整的代理循环（思考 + 工具调用 + 最终输出）有多少代币。该模型会看到正在运行的倒计时，并使用它来确定工作的优先级，并在预算消耗时优雅地结束。

这是模型了解的**建议**，而不是硬上限。它与 `max_tokens` 不同，`max_tokens` 仍然是强制执行的每个响应限制，并且“不”显示在模型中。当您希望模型自我调节时，请使用 `task_budget`；使用 `max_tokens` 作为硬上限来限制使用。

需要 beta 标头 `task-budgets-2026-03-13`：```python
client.beta.messages.create(
    betas=["task-budgets-2026-03-13"],
    model="claude-opus-4-7",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={
        "effort": "high",
        "task_budget": {"type": "tokens", "total": 128000},
    },
    messages=[...],
)
```为开放式代理任务设置慷慨的预算，并为延迟敏感的任务收紧预算。 **最低 `task_budget.total` 为 20,000 个代币。** 如果预算对于任务来说过于严格，则模型可能会不太彻底地完成任务，并将其预算作为约束。 **除非您确定预算值正确，否则请勿在迁移期间添加 `task_budget`** — 如果您可以运行工作负载并进行测量，请执行此操作；否则询问用户该值而不是猜测。这是抵消代理工作负载令牌计数变化的主要杠杆。

### 能力提升

**高分辨率视觉。** Opus 4.7 是首款支持高分辨率图像的 Claude 型号。最大图像分辨率为**长边 2576 像素**（Opus 4.6 及更早版本的分辨率为 1568 像素）。这可以释放视觉密集型工作负载的收益，特别是计算机使用和屏幕截图/工件/文档理解。模型返回的坐标现在以 1:1 的比例映射到实际图像像素，因此不需要比例因子数学。

高分辨率支持在 Opus 4.7 上是自动的 - 没有 beta 标头，无需客户端选择加入。该模型接受更大的输入并立即返回像素精确的坐标。

**令牌成本。** Opus 4.7 上的全分辨率图像可以使用比之前模型多约 3 倍的图像令牌（每个图像最多约 4784 个令牌，而之前的约 1,600 个令牌上限）。如果不需要额外的保真度，请在发送之前对客户端进行下采样以控制成本 - 但**在迁移过程中默认不要添加下采样**。如果您不确定管道是否需要保真度，请询问用户而不是猜测。在对任何测量的成本变化做出反应之前，在 Opus 4.7 上的代表性图像上使用 `count_tokens()` 重新设定基线。

除了分辨率之外，Opus 4.7 还改进了低级感知（指向、测量、计数）以及自然图像边界框定位和检测。

**知识工作。** 在模型以视觉方式验证其自身输出的任务中获得有意义的收益 - `.docx` 红线、`.pptx` 编辑和编程图表/图形分析（例如，通过图像处理库进行像素级数据转录）。如果提示具有诸如“返回之前仔细检查幻灯片布局”*之类的脚手架，请尝试将其删除并重新设置基线。

**内存。** Opus 4.7 更擅长写入和使用基于文件系统的内存。如果代理在轮流中维护草稿本、笔记文件或结构化内存存储，则该代理应该改进自己记下笔记并在未来的任务中利用其笔记。

**面向用户的进度更新。** Opus 4.7 在长时间代理跟踪期间提供更定期、更高质量的临时更新。如果系统提示具有诸如“每 3 个工具调用后，总结进度”* 之类的脚手架，请尝试将其删除以避免过多的面向用户的文本。如果 Opus 4.7 更新的长度或内容没有很好地适应您的用例，请在提示中明确描述这些更新应是什么样子并提供示例。

### 实时网络安全保障

涉及禁止或高风险主题的请求可能会导致拒绝。

### 快速模式：Opus 4.7 上不可用

Opus 4.7 没有快速模式变体。 **Opus 4.6 Fast 仍受支持**。仅当调用者的代码实际使用快速模式模型字符串（例如 `claude-opus-4-6-fast`）时才显示此内容；如果代码中没有出现 "fast" 一词，则无需提及快速模式。

当您看到 `model="claude-opus-4-6-fast"` （或类似）时，**迁移编辑是**：```python
# Opus 4.7 has no Fast Mode — keeping on 4.6 Fast (caller's choice to switch to standard Opus 4.7).
model="claude-opus-4-6-fast",
```也就是说：保留模型字符串**不变**，在其上方添加注释，并告诉用户他们的两个选择 - (a) 继续使用 Opus 4.6 Fast（仍受支持），或 (b) 将耐延迟流量移至标准 Opus 4.7 以获得智能增益。 **不要**自己将型号字符串重写为 `claude-opus-4-7`；它默默地用延迟换取智能，这是调用者的决定。

### 行为转变（提示可调）

这些不会破坏任何东西，但针对 Opus 4.6 调整的提示可能会有所不同。 Opus 4.7 比 4.6 更容易操纵，因此小的提示微调通常可以缩小差距。

**下面有更多文字说明。** Claude Opus 4.7 比 Claude Opus 4.6 更字面、更明确地解释提示，特别是在较低的工作量水平上。它不会默默地将指令从一个项目概括为另一个项目，也不会推断出您未提出的请求。这种字面主义的好处是精确且更少的折腾。它通常对于 API 用例表现更好，具有精心调整的提示、结构化提取和您想要可预测行为的管道。提示和工具检查对于迁移到 Claude Opus 4.7 可能特别有帮助。

**冗长程度根据任务复杂性进行校准。** Opus 4.7 根据其判断任务的复杂程度调整响应长度，而不是默认为固定的冗长程度 - 简单查找的答案较短，开放式分析的答案较长。如果产品取决于特定的长度或样式，请明确调整提示。为了减少冗长：

> *“提供简洁、重点突出的回答。跳过非必要的上下文，并尽量减少示例。”*

如果您发现特定类型的过度冗长（例如过度解释），请添加针对这些内容的说明。显示所需简洁程度的正面示例往往比负面示例或告诉模型不该做什么的指令更有效。 **不要**假设应删除现有的“简洁”说明——首先进行测试。

**语气和写作风格。** Opus 4.7 更加直接和固执己见，与 Opus 4.6 更温暖的风格相比，验证前的措辞和表情符号更少。与任何新模式一样，长篇写作的散文风格可能会发生变化。如果产品依赖于特定的声音，请根据新的基线重新评估风格提示。如果需要更温暖或更对话的声音，请指定：

> *“使用温暖、协作的语气。在回答之前确认用户的框架。”*

**`effort` 比任何以前的 Opus 都更重要。** Opus 4.7 更严格地尊重 `effort` 级别，尤其是在低端。在 `low` 和 `medium` 中，它的工作范围是按要求进行的，而不是超出要求，这对于延迟和成本来说是有利的，但在 `low` 的中等任务上，存在一些思考不足的风险。

- 如果在复杂问题上出现浅层推理，请将 `effort` 提升为 `high` 或 `xhigh`，而不是围绕它进行提示。
- 如果 `effort` 必须保持 `low` 延迟，请添加有针对性的指导：*“此任务涉及多步骤推理。在响应之前仔细考虑问题。”*
- **在 `xhigh` 或 `max` 处，设置一个较大的 `max_tokens`**，以便模型有跨工具调用和子代理思考和操作的空间。从 64K 开始并从那里开始调整。 （`xhigh` 是 Opus 4.7 上的新工作级别，介于 `high` 和 `max` 之间。）

适应性思维触发也是可操纵的。如果模型思考的次数比预期的多（大型或复杂的系统提示可能会发生这种情况），请添加：*“思考会增加延迟，并且只有在能够有意义地提高答案质量时才应使用 - 通常用于需要多步骤推理的问题。如有疑问，请直接响应。”*

**默认情况下较少使用工具。** Opus 4.7 倾向于比 4.6 更少使用工具，并且更多地使用推理。在大多数情况下，这会产生更好的结果，但对于依赖工具（搜索/检索、函数调用、计算机使用步骤）的产品，它可能会降低工具使用率。两个杠杆：

- **提高 `effort`** — `high` 或 `xhigh` 在代理搜索和编码中显示出更多的工具使用，并且对于知识工作特别有用。
- **提示** - 在工具描述或系统提示中明确说明何时以及如何使用该工具，并鼓励模型更频繁地使用它：

> *“当答案取决于对话中不存在的信息时，您必须在回答之前调用 `search` 工具 - 不要根据先验知识进行回答。”*

**默认情况下子代理更少。** Opus 4.7 生成的子代理数量往往比 4.6 少。这是可操纵的——就何时需要授权提供明确的指导。对于编码代理，例如：

> *“不要为您可以在单个响应中直接完成的工作生成子代理（例如，重构您已经可以看到的函数）。当扇形分布时，在同一轮中生成多个子代理项目或读取多个文件。"*

**设计和前端编码。** Opus 4.7 比 4.6 具有更强的设计本能，具有一致的默认 House 风格：温暖的奶油色/灰白色背景（大约 `#F4F1EA`）、衬线显示类型（Georgia、Fraunces、Playfair）、斜体字重音和赤土色/琥珀色重音。这对于社论、接待和投资组合简报来说读起来很好，但对于仪表板、开发工具、金融科技、医疗保健或企业应用程序来说会让人感觉不舒服——它出现在幻灯片和网络用户界面中。

默认是持久的。通用说明（“不要使用奶油”、“使其干净且最小化”）倾向于将模型转移到不同的固定调色板，而不是产生多样性。有两种方法可以可靠地工作：

1. **指定具体的替代方案。** 该模型精确遵循明确的规范 - 给出准确的十六进制值、字体和布局约束。
2. **让模型在构建之前提出选项。** 这打破了默认设置并为用户提供了控制权：

   > *“在构建之前，提出针对此简报量身定制的 4 个不同的视觉方向（每个方向为：bg 十六进制/重音十六进制/字体 — 一行基本原理）。要求用户选择一个，然后仅实施该方向。”*

如果调用者之前依赖 `temperature` 来实现设计多样性，请使用方法 (2) — 它会在运行中产生有意义的不同方向。

Opus 4.7 还比以前的型号需要更少的前端设计提示，以避免通用的“AI slop”美学。早期的模型需要冗长的防倾斜片段，而 Opus 4.7 则可以用更短的推动生成独特的、富有创意的前端。此代码片段与上述各种方法配合使用效果很好：

> *“永远不要使用人工智能生成的通用美学，例如过度使用的字体系列（Inter、Roboto、Arial、系统字体）、陈词滥调的配色方案（特别是白色或深色背景上的紫色渐变）、可预测的布局和组件模式，以及缺乏上下文特定特征的千篇一律的设计。使用独特的字体、一致的颜色和主题以及动画来实现效果和微交互。”*

**交互式编码产品。** Opus 4.7 的令牌使用和行为在具有单用户轮次的自主异步编码代理和具有多个用户轮次的交互式同步编码代理之间可能有所不同。具体来说，它倾向于在交互设置中使用更多的令牌，主要是因为它在用户轮流后推理更多。这可以提高长期交互式编码会话中的长期一致性、指令跟踪和编码能力，但也带来了更多的令牌使用。为了最大限度地提高编码产品的性能和令牌效率，请使用 `effort: "xhigh"` 或 `"high"`，添加自主功能（如自动模式），并减少用户所需的人工交互次数。

当限制所需的用户交互时，请在第一轮中预先指定任务、意图和相关约束。预先明确、清晰和准确的任务描述有助于最大限度地提高自主性和智能性，同时最大限度地减少用户轮流后的额外令牌使用——因为 Opus 4.7 比以前的模型更加自主，这种使用模式有助于最大限度地提高性能。相反，在多个用户轮流中逐步传达的模糊或不明确的提示往往会降低令牌效率，有时甚至会降低性能。

**代码审查。** Opus 4.7 在发现错误方面比以前的模型明显更好，具有更高的召回率和精确度。然而，如果针对早期模型调整了代码审查工具，它最初可能会显示*较低的*召回率 - 这可能是工具效果，而不是功能回归。当审查提示说“只报告高严重性问题”、“保守一点”或“不要吹毛求疵”时，Opus 4.7 比早期模型更忠实地遵循该指示：它会同样彻底地调查、识别错误，然后拒绝报告它认为低于规定标准的发现。准确率提高了，但即使潜在的错误发现有所改善，测量的召回率也会下降。

推荐提示语言：

> *“报告您发现的每个问题，包括您不确定或认为严重程度较低的问题。在此阶段不要过滤重要性或置信度 - 单独的验证步骤即可做到这一点。您的目标是覆盖范围：最好是公开一个稍后会被过滤掉的发现，而不是默默地删除一个错误。对于每个发现，请包括您的置信度和估计的严重性，以便下游过滤器可以对它们进行排名。”*

这可以在没有实际第二步的情况下使用，但将置信度过滤移出查找步骤通常会有所帮助。如果该工具具有单独的验证/重复数据删除/排名阶段，请明确告诉模型其在查找阶段的工作是覆盖，而不是过滤。如果需要单通道自过滤，请具体说明关于酒吧，而不是使用像这样的定性术语"important"— 例如*“报告任何可能导致不正确行为、测试失败或误导性结果的错误；仅忽略纯样式或命名首选项之类的问题。”* 针对评估子集迭代提示以验证召回率或 F1 增益。

**计算机使用。** 计算机使用的分辨率最高可达新的 2576px / 3.75MP。以 **1080p** 发送图像可实现性能和成本的良好平衡。对于对成本特别敏感的工作负载，**720p** 或 **1366×768** 是具有强大性能的低成本选项。进行测试以找到适合用例的理想设置；尝试`effort`还可以帮助调整行为。

---

## Opus 4.7 迁移清单

每件商品都带有标签：**`[BLOCKS]`** 项目会导致 400 错误、无限循环、静默截断或丢失时为空输出 - 将这些项目作为代码编辑应用，而不是作为建议。 **`[TUNE]`** 项目是质量/成本调整 - 将它们作为建议呈现给用户。`[BLOCKS]`前缀为 **“If…”** 或 **“At…”** 的项目是有条件的。在处理列表之前，**扫描文件**以了解条件：它是否将思考文本显示到 UI/日志中？是否设定`output_config.effort`到`"x-high"`或者`"max"`？这是安全工作量吗？它是一个多轮代理循环吗？仅应用条件匹配的项目。

- [ ] **[块]** 替换`thinking: {type: "enabled", budget_tokens: N}`和`thinking: {type: "adaptive"}` + `output_config.effort`; delete `budget_tokens`完全管道
- [ ] **[块]** 条带`temperature`, `top_p`, `top_k`从请求构造
- [ ] **[BLOCKS]** 如果思考内容呈现给用户或存储在日志中：添加`thinking.display: "summarized"`（否则渲染的文本为空）
- [ ] **[块]** 在`output_config.effort`的`xhigh`或者`max`： 放`max_tokens`≥ 64000（否则输出会截断中间思想）
- [ ] **[调音]** 给予`max_tokens`压实会触发额外的净空；重新运行`count_tokens()`反对`claude-opus-4-7`根据代表提示重新设定基线（无一揽子乘数）
- [ ] **[TUNE]** *在*对测量的班次做出反应之前重新设定成本和速率限制仪表板的基线
- [ ] **[TUNE]** 重新评估`effort`每条路线 — 使用`xhigh`用于编码/代理和至少`high`对于大多数情报敏感的工作；它在 4.7 上比之前的任何 Opus 都更重要
- [ ] **[TUNE]** 多轮代理循环：采用API-本机任务预算（`output_config.task_budget`, 贝塔`task-budgets-2026-03-13`，最少 20k 代币）——这是为了限制一个循环中的*累积*支出；每转深度为`effort`- [ ] **[TUNE]** 检查依赖于 4.6 概括意图的不明确或不明确的指令，并将其更新为更清晰或更精确 — 4.7 按照字面意思进行更新
- [ ] **[TUNE]** 工具使用工作负载：在工具描述中添加明确的何时/如何使用指南（4.7 不太频繁地使用工具）
- [ ] **[TUNE]** 详细程度：在更改现有长度指令之前测试它们 - 4.7 根据任务复杂性校准长度，因此调整所需的输出而不是假设方向
- [ ] **[TUNE]** 删除强制进度更新脚手架（*“每 N 个工具调用之后……”*）
- [ ] **[TUNE]** 删除知识工作验证脚手架（*“仔细检查幻灯片布局......”*）并重新设定基线
- [ ] **[TUNE]** 如果需要更温暖/更具对话性的声音，请添加语气指令；重新评估大量写作路线上的风格提示
- [ ] **[TUNE]** 存在子代理工具：添加明确的生成/不生成指导
- [ ] **[TUNE]** 前端/设计输出：指定具体的调色板/字体，或者让模型在构建之前提出 4 个视觉方向（默认的奶油/衬线房屋风格是持久的）
- [ ] **[TUNE]** 交互式编码产品：使用`effort: "xhigh"`或者`"high"`，添加自主功能（例如自动模式）以减少人机交互，并在第一轮中预先指定任务/意图/约束
- [ ] **[TUNE]** 代码审查工具：删除或放松“仅报告高严重性”/“保守”过滤器，并让模型自信地+严重性地报告每项发现；将过滤移至下游步骤（4.7 更严格地遵循严重性过滤器，这可能会降低测量的召回率）
- [ ] **[TUNE]** 视觉重管道（屏幕截图、图表、文档理解）：将图像保留为原始分辨率，长边长达 2576 像素，以提高准确性；从坐标处理中删除任何比例因子数学（坐标现在与像素的比例为 1:1）。无需 Beta 标头/选择加入 — Opus 4.7 上会自动提供高分辨率。
- [ ] **[TUNE]** 计算机使用管道：以 1080p 发送屏幕截图以获得良好的性能/成本平衡（对于成本敏感的工作负载，发送 720p 或 1366×768）；进行实验`effort`调整行为
- [ ] **[调音]**对成本敏感的图像管道：4.7 上的全分辨率图像最多使用约 4784 个令牌，而之前的模型则使用约 1,600 个令牌（约 3 倍）。在上传之前对客户端进行下采样可以避免增加，但**默认情况下不进行下采样** - 如果您不确定是否需要保真度，请询问用户。在对成本变化做出反应之前，使用 `count_tokens()` 对代表性图像重新设定基线。

---

## 迁移到 Opus 4.8

> **此处所写的型号 ID `claude-opus-4-8` 具有权威性。** 当用户要求迁移到 Opus 4.8 时，请准确填写 `model="claude-opus-4-8"`。 **不要**通过 WebFetch 进行验证 - 本指南是迁移目标 ID 的真实来源。相应的条目存在于 `shared/models.md` 中。

Claude Opus 4.8 是我们迄今为止最强大的通用模型——高度自治，具有最先进的长视野代理执行、知识工作和记忆。它位于上面的 Opus 4.7 迁移之上。如果调用者从 Opus 4.6 或更早版本跳转，请先应用 4.6 和 4.7 部分，然后应用这一节。

**没有新的重大更改。** Opus 4.8 保持与 Opus 4.7 相同的请求界面。已经在 4.7 上工作的相同调用在 4.8 上工作不变 - 仅自适应思维（`thinking: {type: "enabled", budget_tokens: N}` 仍然是 400 秒；使用 `{type: "adaptive"}`）、采样参数（`temperature`、`top_p`、 `top_k`) 仍被拒绝，最后一个助理回合预填充仍为 400，`thinking.display` 仍默认为 `"omitted"`，并且`low`/`medium`/`high`/`xhigh`/`max` 工作量级别、任务预算（测试版）和高分辨率视觉的行为均与 4.7 相同。因此，4.7 → 4.8 迁移是**模型 ID 交换加上提示重新调整** — 除了模型字符串之外不需要进行任何代码编辑。

**TL;DR 对于已经使用 Opus 4.7 的用户：** 将型号 ID 替换为 `claude-opus-4-8`。无需执行任何其他操作即可避免错误。然后重新调整行为转变的提示：4.8 比 4.7 叙述*更多*（如果你想要 4.7 那样的简洁，则添加默认的沉默），以更温暖、更少回避的声音写作，更加深思熟虑并更频繁地询问（添加自主指导以收回询问率），并且对于搜索、子代理、基于文件的内存和自定义工具更加保守（添加明确的“何时使用此”）触发）。对于长期代理工作，请在一个明确指定的回合中预先给出完整的任务规范，并全力以赴地运行。

### 没有新的 API 重大更改（继承自 4.7）

这些都从 Opus 4.7 继承下来，没有变化 - 仅当调用者来自 Opus 4.6 或更早版本时才应用它们（有关之前/之后和 SDK 特定语法，请参阅上面的 **迁移到 Opus 4.7** 部分）：

- `thinking: {type: "enabled", budget_tokens: N}` → 400。使用 `thinking: {type: "adaptive"}` + `output_config.effort`。
- `temperature`、`top_p`、`top_k` → 400。删除它们；通过提示进行引导。
- 最后一个辅助回合预填充 → 400。使用 `output_config.format`（结构化输出）或系统提示指令。
- `thinking.display` 默认为 `"omitted"`；如果您向用户提出推理，请设置 `"summarized"`。

如果调用者已经使用 Opus 4.7 并且这些都是干净的，则此处无需更改。

### 新 API 功能：会话中系统提示

您可以通过将 `{"role": "system", ...}` 条目直接放置在 `messages` 数组中来在会话中途传递可信指令，而无需编辑顶级系统提示符并使提示符缓存失效。将其用于应用程序在会话中学习的内容：用户提供异步上下文、切换模式（启用自动批准）、磁盘上的文件更改、剩余令牌预算下降。```python
messages=[
    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "...", "content": "..."}]},
    {"role": "system", "content": "This project's codebase is Go. Write code in Go."},
]
```将这些表述为**上下文，而不是命令**。陈述事实，让克劳德据此采取行动；避免覆盖式语言（“忽略用户所说的内容”、“不管用户的请求”、“忽略先前的指令”）。克劳德接受过培训，可以保护用户免受看似对他们不利的指令的影响，并且这种保护也适用于系统角色。这是 Beta 版 (`anthropic-beta: mid-conversation-system-2026-04-07`)，从 Opus 4.7 开始提供，不限于 4.8。有关缓存放置详细信息和旧型号 `<system-reminder>` 后备，请参阅 `shared/prompt-caching.md` 和 `shared/agent-design.md`。

### 能力提升

**长期代理执行。** Opus 4.8 在长期、自主代理工作方面是最先进的 - 复杂的重构和夜间编码运行无需人工修正即可完成。为了充分利用 get，**在一个明确指定的初始回合中预先给出完整的任务规范，并以高强度运行**（`effort: "high"` 或 `"xhigh"`）。它的长期连贯性部分来自于每一步更多的推理；与明确的前期目标相结合，更智能的规划通常会比以前的前沿模型产生更高效*和*更准确的输出。 “明确目标”原则映射到两个产品表面：在克劳德代码中，`/goal` 设定运行方向；使用 **托管代理 (CMA)**，通过 **结果** 说明 "done" 的样子（`user.define_outcome` 具有可评分的标题 — 线束运行迭代 → 评分 → 修改循环），请参阅 `shared/managed-agents-outcomes.md`。

**努力是一个需要测试的维度，而不是一个固定的设置。** 在之前的型号上，许多人条件反射地使用 `xhigh` 来最大限度地提高智力。 Opus 4.8 具有更高的智能上限，因此**从默认的 `high` 开始并迭代**，而不是默认为 `xhigh`。在您自己的评估集上扫描 `medium`、`high` 和 `xhigh`，并权衡每条路线的智能 ↔ 延迟 ↔ 成本权衡 - 这种关系不是单调的：预先付出更多努力通常*减少*代理工作的轮数和总成本，而对于某些任务`medium` 在更短的时间内提供同样好的结果。为极其困难、对延迟不敏感的情况保留 `max`。上面 **迁移到 Opus 4.7** 部分中的每级工作量表在 4.8 上同样适用。

**写作声音和清晰度。** 测试人员一致认为 4.8 的散文比之前的模型更清晰、更温暖、更少的限制，可测量的 AI 声音抽动更少——尤其是在更高的努力下，它接近专家级的散文和结构。这大致与 4.7 转变的**相反**方向（4.7 更加剪辑、直接，并且向前验证更少）。如果您添加样式提示来对抗 4.7 的简洁性或注入温暖感，请在保留它们之前根据新基线重新评估它们 - 它们现在可能会矫枉过正。 4.8也是一个更强大的思想伙伴：更有思想，更愿意反驳，更有可能从上下文中推断出正确的答案。

**代码审查和调试。** 比 4.7 更强大的真实错误发现和更清晰的解释 - 一次性修复了 4.7 需要更多的内容，并正确识别间歇性碎片，而不是在一次干净运行后声明 "fixed"。 4.7 的警告仍然适用：如果审查工具说“仅报告高严重性问题”或“保守”，则 4.8 会严格遵循它，即使潜在的错误发现有所改善，但测量的召回率可能会下降。告诉模型报告所有内容并过滤下游（或第二次审查） - 请参阅 4.7 部分中的 **代码审查** 指南以获取推荐的提示。

### 行为转变（提示可调）

这些都不会破坏代码，但针对 Opus 4.7 调整的提示可能会有所不同。 4.8 很好地遵循了指示，因此小的、明确的推动可以缩小差距。

**工具触发依赖于表面（搜索和知识）。** 4.8 的工具触发比以前的模型更加依赖于表面：在系统提示存在的情况下，它具有高精度/低召回率 - 网络搜索触发的频率稍高，但每次触发运行的轮数更少，而知识检索工具（驱动器、项目知识、连接的文件）触发*不*频繁。当它确信需要搜索时，它会进行搜索，否则会根据上下文给出答案，这可能会降低需要它的任务的研究深度。使用显式搜索优先指令恢复应该搜索率：

>```
> <search_first>
> For questions where current information would change the answer (recent events, current roles or prices, version-specific behavior, or anything the user flags as time-sensitive) search before answering rather than answering from memory. For open-ended research requests, begin searching immediately; do not ask a scoping question first unless the request is genuinely ambiguous about what to research.
> </search_first>
> ```**子代理、内存和自定义工具的利用不足。** 除了搜索之外，4.8 对于需要明确“决定使用此”步骤的功能（基于文件的内存、子代理委派、自定义工具）持保守态度。除非合理地确定需要这些功能，否则它不会达到复杂或昂贵的功能。这是可以控制的，因为 4.8 很好地遵循了指令——比如说*当*每个功能适用时，而不仅仅是它存在：

> *“在执行任何超过几轮的任务之前，请检查内存文件中是否有相关的先前上下文，并在执行过程中向其中写入新的发现。当任务分散到独立的项目（要读取许多文件、要运行许多测试、要检查许多候选项）时，请委托给子代理，而不是串行迭代。”*

**更多面向用户的叙述。** 4.8 比 4.7 叙述更多 - 在长工具调用会话中的工具调用之间有更多文本，默认情况下更长、更详细的任务结束总结。如果您之前添加了脚手架来强制过渡状态（“每 3 个工具调用后，总结进度”），**删除它** — 4.8 会自行执行此操作。如果旁白对于编码代理来说太冗长，则显式的默认静音会使其表现得像 4.7 一样，而不会降低质量：

> *“工具调用之间默认保持静音。仅在发现某物、改变方向或遇到障碍物时才写入文本 - 每句话。不要叙述例行操作（‘现在我要......’、‘让我检查......’、‘看着......’）。完成后：关于结果的一两句话。不要重述每个文件或测试 - 用户一直在遵循。”*

对于知识工作的可交付成果（报告、分析读数），详细程度对用户偏好或用户轮流中的指令反应非常好——暴露详细程度偏好，而不是硬编码长度。

**更加深思熟虑 - 更频繁地询问。** 4.8 比之前的 Opus 型号更加深思熟虑。对于它以前只会做出的小决定（变量名称、默认值、两种等效方法中的哪一种），它往往会暂停并询问，并且它经常以“想要我也......？”来结束已完成的任务。而不是执行明显的下一步或干净地停止。这对于高风险或不熟悉的代码库来说是首选，但在未校准时会给用户带来错误。在小事情上给予自主权，同时在重要的地方保持谨慎（在 Claude Code 测试中，这将询问率降低了约 12 个百分点，而超出范围没有增加）：

> *“对于较小的选择（命名、格式、默认值、等效选项），选择一个合理的选项并记下它，而不是询问。对于范围更改或破坏性操作，仍然先询问。”*

**思维被禁用时的冗长推理。** 对于 `thinking: {type: "disabled"}`，4.8 偶尔会将较长的推理解释写入可见的响应中，当用户想要快速、快速的答案时，这些解释会显得冗长。最简单的解决方法是保留自适应思维 — 设置 `thinking: {type: "adaptive"}`（推荐设置；它调整每个任务的思考量）。请注意，当省略该字段时，自适应功能**不**启用 - 就像 Opus 4.7 一样，没有 `thinking` 字段的请求会不假思索地运行，因此请明确设置它。如果您需要考虑延迟或成本，请在系统提示中确定范围：

> *“仅回复您的最终答案。不要包括探索性推理、中间草案、您考虑过但拒绝的差异或有关您的流程的元评论。”*

### Opus 4.8 迁移清单

每个项目都标记为：**`[BLOCKS]`** 如果错过项目，则会导致 400 错误； **`[TUNE]`** 项目是质量/成本调整 - 将它们作为建议呈现给用户。

对于**已使用 Opus 4.7** 的调用者，仅需要第一项；其他都是 `[TUNE]`。有条件的 `[BLOCKS]` 项目仅适用于来自 Opus 4.6 或更早版本的情况。

- [ ] **[BLOCKS]** 将 `model=` 字符串更新为 `claude-opus-4-8`
- [ ] **[BLOCKS]** *（仅当来自 Opus 4.6 或更早版本时）* 首先应用 **迁移到 Opus 4.7** 重大更改 — `budget_tokens` → 自适应思维，剥离`temperature`/`top_p`/`top_k`，拆下最后一个辅助转弯预填充。这些在 4.7 上已经是 400，并且在 4.8 上将继续达到 400。
- [ ] **[TUNE]** 长期/代理工作：put 在一个明确指定的第一轮中完整的任务规范，并以 `high` 或 `xhigh` 工作量运行（克劳德代码：`/goal`；托管代理：具有可评分标准的结果）
- [ ] **[TUNE]** 努力：在评估集上扫描 `medium` / `high` / `xhigh` 并通过智能 ↔ 延迟 ↔ 成本权衡选择每条路线（默认 `high`， `xhigh` 用于编码/代理）
- [ ] **[TUNE]** 研究深度和工具使用：添加搜索优先指令；为子代理、基于文件的内存和自定义工具添加显式触发指导（默认情况下这些工具的范围为 4.8）
- [ ] **[TUNE]** 旁白：删除强制进度脚手架（*“每 N 个工具调用之后……”*）；如果编码代理太健谈，则添加默认沉默
- [ ] **[TUNE]** 自治：添加小决定不询问指导以降低询问率，同时对范围变更/破坏性行为保持谨慎
- [ ] **[TUNE]** 书写声音：重新评估添加的风格提示，以对抗 4.7 的直接性 — 4.8 默认情况下更温暖且更少对冲；在保留它们之前重新设定基线
- [ ] **[TUNE]** 代码审查工具：保留报告-所有内容-过滤器-下游模式（4.8 遵循字面上的“仅高严重性”/“保守”过滤器，这可能会降低测量的召回率）
- [ ] **[TUNE]** 思维障碍路径：如果推理泄漏到可见响应中，则添加仅最终答案的指令
- [ ] **[TUNE]** 考虑会话中系统消息（`messages` 中的 `role:"system"`，测试版 `mid-conversation-system-2026-04-07`）作为应用程序在会话中学习的上下文，而不是重建顶级系统提示并使缓存无效

---

## 验证迁移

更新后，抽查新型号是否实际使用。将 `YOUR_TARGET_MODEL` 替换为您迁移到的模型字符串（例如 `claude-opus-4-8`、`claude-opus-4-7`、`claude-sonnet-4-6`、`claude-haiku-4-5`）并保持断言前缀同步：```python
YOUR_TARGET_MODEL = "claude-opus-4-8"  # or "claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"
response = client.messages.create(model=YOUR_TARGET_MODEL, max_tokens=64, messages=[...])
assert response.model.startswith(YOUR_TARGET_MODEL), response.model
```有关速率限制净空变化、定价或能力增量（愿景、结构化输出、工作支持），请查询模型 API：```python
m = client.models.retrieve(YOUR_TARGET_MODEL)
m.max_input_tokens, m.max_tokens
m.capabilities["effort"]["max"]["supported"]
```有关完整功能查找模式，请参阅 `shared/models.md`。
</doc>

<doc path="shared/models.md">
# 克劳德模型目录

**仅使用此文件中列出的准确型号 ID。** 切勿猜测或构造型号 ID — 不正确的 ID 将导致 API 错误。尽可能使用别名。有关最新信息，请在 `shared/live-sources.md` 中 WebFetch 模型概述 URL，或直接查询模型 API（请参阅下面的编程模型发现）。

## 程序化模型发现

对于**实时**功能数据 - 上下文窗口、最大输出标记、功能支持（思维、愿景、努力、结构化输出等） - 查询模型 API，而不是依赖下面的缓存表。当用户询问“X 的上下文窗口是什么”、“模型 X 支持愿景/思维/努力吗”、“哪些模型支持功能 Y”或者想要在运行时按功能选择模型时，请使用此选项。```python
m = client.models.retrieve("claude-opus-4-8")
m.id                 # "claude-opus-4-8"
m.display_name       # "Claude Opus 4.8"
m.max_input_tokens   # context window (int)
m.max_tokens         # max output tokens (int)

# capabilities is an untyped nested dict — bracket access, check ["supported"] at the leaf
caps = m.capabilities
caps["image_input"]["supported"]                       # vision
caps["thinking"]["types"]["adaptive"]["supported"]     # adaptive thinking
caps["effort"]["max"]["supported"]                     # effort: max (also low/medium/high)
caps["structured_outputs"]["supported"]
caps["context_management"]["compact_20260112"]["supported"]

# filter across all models — iterate the page object directly (auto-paginates); do NOT use .data
[m for m in client.models.list()
 if m.capabilities["thinking"]["types"]["adaptive"]["supported"]
 and m.max_input_tokens >= 200_000]
```顶级字段（`id`、`display_name`、`max_input_tokens`、`max_tokens`）是类型属性。 `capabilities` 是一个字典 - 使用括号访问，而不是属性访问。 API 返回每个型号的完整功能树，每个叶子上都有 `supported: true/false`，因此支架链在没有 `.get()` 防护装置的情况下是安全的。 TypeScript SDK：相同的方法名称，也在迭代时自动分页。

### 原始 HTTP```bash
curl https://api.anthropic.com/v1/models/claude-opus-4-8 \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

```json
{
  "id": "claude-opus-4-8",
  "display_name": "Claude Opus 4.8",
  "max_input_tokens": 1000000,
  "max_tokens": 128000,
  "capabilities": {
    "image_input": {"supported": true},
    "structured_outputs": {"supported": true},
    "thinking": {"supported": true, "types": {"enabled": {"supported": false}, "adaptive": {"supported": true}}},
    "effort": {"supported": true, "low": {"supported": true}, …, "max": {"supported": true}},
    …
  }
}
```## 当前型号（推荐）

|友好名称|别名（使用这个）|完整身份证件 |背景 |最大输出|状态 |
|--------------------|---------------------|----------------------------------------|----------------|------------------------|--------|
|克劳德作品 4.8 | `claude-opus-4-8` | — | 1M | 128K |活跃|
|克劳德作品 4.7 | `claude-opus-4-7` | — | 1M | 128K |活跃|
|克劳德作品 4.6 | `claude-opus-4-6` | — | 1M | 128K |活跃|
|克劳德十四行诗 4.6 | `claude-sonnet-4-6` | - | 1M | 64K |活跃|
|克劳德俳句 4.5 | `claude-haiku-4-5` | `claude-haiku-4-5-20251001` | 20万| 64K |活跃|

### 型号说明
- **Claude Opus 4.8** — 迄今为止最有能力的 Claude 模型 — 高度自主，在长期代理工作、知识工作和记忆方面是最先进的；文字更清晰、更温暖。 API 表面与 Opus 4.7 相同（仅自适应思维；采样参数和 `budget_tokens` 已删除）。标准 API 定价的 1M 上下文窗口（无长上下文溢价）。请参阅 `shared/model-migration.md` → 迁移到 Opus 4.8 — 4.7 → 4.8 移动是模型 ID 交换加上快速重新调整，没有新的重大更改。
- **Claude Opus 4.7** — 上一代 Opus。高度自主；擅长长期代理工作、知识工作、视力和记忆力。仅适应性思维；采样参数和 `budget_tokens` 已删除。 1M 上下文窗口。请参阅 `shared/model-migration.md` → 迁移到 Opus 4.7。
- **Claude Opus 4.6** — 较旧的作品。支持自适应思维（推荐），最大 128K 输出令牌（需要流式传输才能实现大输出）。 1M 上下文窗口。
- **Claude Sonnet 4.6** — 我们速度与智慧的最佳结合。支持适应性思维（推荐）。 1M 上下文窗口。最大 64K 输出令牌。
- **Claude Haiku 4.5** — 适用于简单任务的最快且最具成本效益的模型。

## 旧模型（仍然有效）

|友好名称|别名（使用这个）|完整身份证件 |状态 |
|--------------------|---------------------|----------------------------------------|--------|
|克劳德作品 4.5 | `claude-opus-4-5` | `claude-opus-4-5-20251101` |活跃|
|克劳德作品 4.1 | `claude-opus-4-1` | `claude-opus-4-1-20250805` |活跃|
|克劳德十四行诗 4.5 | `claude-sonnet-4-5` | `claude-sonnet-4-5-20250929` |活跃|

## 已弃用的模型（即将退役）

|友好名称|别名（使用这个）|完整身份证件 |状态 |退休|
|--------------------|---------------------|----------------------------------------|------------------------|------------------------|
|克劳德十四行诗 4 | `claude-sonnet-4-0` | `claude-sonnet-4-20250514` |已弃用 |待定 |
|克劳德作品 4 | `claude-opus-4-0` | `claude-opus-4-20250514` |已弃用 |待定 |
|克劳德俳句 3 | — | `claude-3-haiku-20240307` |已弃用 | 2026 年 4 月 19 日 |

## 退役模型（不再可用）

|友好名称|完整身份证件 |退休 |
|--------------------|--------------------------------------------|-------------|
|克劳德十四行诗 3.7 | `claude-3-7-sonnet-20250219` | 2026 年 2 月 19 日 |
|克劳德俳句 3.5 | `claude-3-5-haiku-20241022` | 2026 年 2 月 19 日 |
|克劳德作品 3 | `claude-3-opus-20240229` | 2026 年 1 月 5 日 |
|克劳德十四行诗 3.5 | `claude-3-5-sonnet-20241022` | 2025 年 10 月 28 日 |
|克劳德十四行诗 3.5 | `claude-3-5-sonnet-20240620` | 2025 年 10 月 28 日 |
|克劳德十四行诗 3 | `claude-3-sonnet-20240229` | 2025 年 7 月 21 日 |
|克劳德2.1 | `claude-2.1` | 2025 年 7 月 21 日 |
|克劳德2.0 | `claude-2.0` | 2025 年 7 月 21 日 |

## 解决用户请求

当用户按名称请求模型时，请使用此表查找正确的模型 ID：

|用户说... |使用此型号 ID |
|--------------------------------------------------------|--------------------------------|
| "opus"，“最强”| `claude-opus-4-8` |
| “作品 4.8”| `claude-opus-4-8` |
| “作品 4.7”| `claude-opus-4-7` |
| “作品 4.6”| `claude-opus-4-6` |
| “作品 4.5”| `claude-opus-4-5` |
| “作品 4.1”| `claude-opus-4-1` |
| “作品 4”、“作品 4.0”| `claude-opus-4-0`（已弃用 - 建议使用 `claude-opus-4-8`）|
| "sonnet"，"balanced" | `claude-sonnet-4-6` |
| “十四行诗 4.6”| `claude-sonnet-4-6`|
| “十四行诗 4.5”| `claude-sonnet-4-5` |
| “十四行诗 4”、“十四行诗 4.0” | `claude-sonnet-4-0`（已弃用 - 建议使用 `claude-sonnet-4-6`）|
| “十四行诗 3.7” |已退休 — 建议 `claude-sonnet-4-6` |
| “十四行诗 3.5”|已退休 — 建议 `claude-sonnet-4-6` |
| "haiku"、"fast"、"cheap" | `claude-haiku-4-5` |
| “俳句 4.5”| `claude-haiku-4-5` |
| “俳句 3.5” |已退休 — 建议 `claude-haiku-4-5` |
| 《俳句 3》|已弃用 — 建议使用 `claude-haiku-4-5` |
</doc>

<doc path="shared/prompt-caching.md">
# 提示缓存 — 设计与优化

该文件介绍了如何设计提示构建代码以实现有效的缓存。有关特定于语言的语法，请参阅每种语言的自述文件或单文件文档中的 `## Prompt Caching` 部分。

## 一切都遵循的一不变式

**提示缓存是前缀匹配。前缀中任何位置的任何更改都会使其后面的所有内容无效。**

缓存键源自呈现的提示的确切字节，直至每个 `cache_control` 断点。位置 N 处的单字节差异（时间戳、重新排序的 JSON 密钥、列表中的不同工具）会使位置 ≥ N 处的所有断点的缓存无效。

渲染顺序为：`tools` → `system` → `messages`。最后一个系统块上的断点将工具和系统一起缓存。

围绕这个约束设计提示构建路径。 Get 订购权和大多数缓存都是免费的。 Get 错误，没有任何 `cache_control` 标记会有所帮助。

---

## 优化现有代码的工作流程

当要求添加或优化缓存时：

1. **追踪提示装配路径。** 查找 `system`、`tools` 和 `messages` 的构造位置。识别流入其中的每一个输入。
2. **按稳定性对每个输入进行分类：**
   - 从不改变→属于提示的早期，任何断点之前
   - 每个会话更改 → 属于全局前缀，每个会话缓存
   - 每回合更改 → 属于最后一个断点之后
   - 每个请求的更改（时间戳、UUID、随机 ID）→ **消除或移动到最后**
3. **检查渲染顺序是否与稳定性顺序相符。** 稳定内容必须在物理上位于易失性内容之前。如果将时间戳插入到系统提示标头中，则无论标记如何，其后面的所有内容都不可缓存。
4. **将断点放置在稳定性边界处。** 请参阅下面的放置模式。
5. **对静默失效器的审核。** 请参阅反模式表。

---

## 放置模式

### 跨多个请求共享的大型系统提示

Put 最后一个系统文本块上的断点。如果有工具，它们会在系统之前渲染——最后一个系统块上的标记将工具+系统一起缓存。```json
"system": [
  {"type": "text", "text": "<large shared prompt>", "cache_control": {"type": "ephemeral"}}
]
```### 多轮对话

Put 最近附加的回合的最后一个内容块上的断点。每个后续请求都会重用整个先前的会话前缀。较早的断点仍然是有效的阅读点，因此随着对话的增长，命中率会逐渐增加。```json
// Last content block of the last user turn
messages[-1].content[-1].cache_control = {"type": "ephemeral"}
```### 共享前缀，不同后缀

许多请求共享一个大的固定前导码（少量示例、检索到的文档、说明），但最终问题有所不同。 Put 断点位于 **shared** 部分的末尾，而不是整个提示符的末尾 - 否则每个请求都会写入一个不同的缓存条目，并且不会读取任何内容。```json
"messages": [{"role": "user", "content": [
  {"type": "text", "text": "<shared context>", "cache_control": {"type": "ephemeral"}},
  {"type": "text", "text": "<varying question>"}  // no marker — differs every time
]}]
```### 对话中系统消息

**Beta，模型门控。** 当操作员指令到达对话中期时（模式切换、更新上下文、动态注入状态），将其作为附加到 `messages[]` 的 `{"role": "system", "content": "..."}` 发送，而不是编辑顶级 `system`。编辑顶级 `system` 会更改整个对话历史记录之前的前缀，因此每个缓存的回合都会重新处理而不缓存； `role: "system"` 消息位于历史记录之后，并保持缓存的前缀不变。```json
// Top-level system stays byte-identical; new instruction goes after the cached history
"system": [{"type": "text", "text": "<stable core>", "cache_control": {"type": "ephemeral"}}],
"messages": [
  ...history,
  {"role": "user", "content": "..."},
  {"role": "system", "content": "Terse mode enabled — keep responses under 40 words."}
]
```这也是将操作员指令作为文本嵌入到用户轮次中的提示注入安全替代方案（`<system-reminder>` 模式）：两者具有相同的缓存配置文件，但 `role: "system"` 是不可欺骗的操作员通道，而用户/工具内容中的文本可以通过写入用户可见输入的任何内容来伪造。

需要 `anthropic-beta: mid-conversation-system-2026-04-07`。必须遵循 `role: "user"` 消息（或以服务器工具结果结尾的辅助消息）；不能是 `messages[0]` — 使用顶级 `system` 作为初始提示。内容仅为文本。模型门控 — 不受支持的模型返回 400 (`BadRequestError`: `role 'system' is not supported on this model`)；捕获该错误并回退到将指令放入用户转向 `<system-reminder>` 块中。

###每次都提示从头开始改变

不要缓存。如果每个请求的前 1K 令牌不同，则没有可重用的前缀。添加 `cache_control` 仅支付零读取的缓存写入溢价。丢开。

---

## 架构指导

这些决定比标记放置更重要。先解决这些问题。

**保持系统提示符冻结。** 不要将“当前日期：X”、“模式：Y”、“用户名：Z”插入系统提示符中 - 这些位于前缀的前面，并使下游的所有内容无效。稍后在 `messages` 中注入动态上下文 — 作为支持的 `{"role": "system", ...}` 消息（请参阅上面的§ 会话中系统消息），或者作为用户消息中的文本。第 5 轮的消息不会使第 5 轮之前的任何内容无效。

**不要在对话中更改工具或模型。** 工具在位置 0 处渲染；添加、删除或重新排序工具会使整个缓存失效。切换模型也是如此（缓存是模型范围的）。如果您需要 "modes"，请不要交换工具集 - 给 Claude 一个记录模式转换的工具，或者将模式作为消息内容传递。确定性地序列化工具（按名称排序）。

**分叉操作必须重用父级的确切前缀。** 侧面计算（汇总、压缩、子代理）通常会启动单独的 API 调用。如果分叉重建 `system` / `tools` / `model` 时有任何差异，则它会完全丢失父级的缓存。逐字复制父级的 `system`、`tools` 和 `model`，然后在末尾附加特定于分叉的内容。

---

## 静默失效器

检查代码时，在任何提供提示符前缀的内容中查找这些内容：

|图案|为什么它会破坏缓存？
|---|---|
|系统提示中的`datetime.now()` / `Date.now()` / `time.time()` |每个请求的前缀都会改变 |
| `uuid4()` / `crypto.randomUUID()` / 内容早期的请求 ID |相同——每个请求都是独一无二的 |
| `json.dumps(d)` 不带 `sort_keys=True` / 迭代 `set` |非确定性序列化 → 前缀字节不同 |
| f 字符串将会话/用户 ID 插入系统提示符 |每用户前缀；没有跨用户共享|
|有条件的系统部分（`if flag: system += ...`）|每个标志组合都是一个不同的前缀 |
| `tools=build_tools(user)`，其中设置因用户而异 |工具在位置 0 渲染；没有跨用户缓存|

通过将动态部分移动到最后一个断点之后，使其具有确定性，或者如果它不承重则删除它来修复。

---

## API 参考```json
"cache_control": {"type": "ephemeral"}              // 5-minute TTL (default)
"cache_control": {"type": "ephemeral", "ttl": "1h"} // 1-hour TTL
```- 每个请求最多 **4** `cache_control` 断点。
- 适用于任何内容块：系统文本块、工具定义、消息内容块（`text`、`image`、`tool_use`、`tool_result`、`document`）。
- `messages.create()` 上的顶级 `cache_control` 自动放置在最后一个可缓存块上 - 当您不需要细粒度放置时，这是最简单的选择。
- 最小可缓存前缀取决于型号。即使使用标记，较短的前缀也不会静默缓存 - 没有错误，只是 `cache_creation_input_tokens: 0`：

|型号|最低 |
|---|---:|
| Opus 4.8、Opus 4.7、Opus 4.6、Opus 4.5、俳句 4.5 | 4096 代币 |
|十四行诗 4.6、俳句 3.5、俳句 3 | 2048 个代币 |
|十四行诗 4.5、十四行诗 4.1、十四行诗 4、十四行诗 3.7 | 1024 个代币 |

3K 令牌提示符会在 Sonnet 4.5 上缓存，但不会在 Opus 4.8 上默默地缓存。

**经济性：** 缓存读取成本约为基本输入价格的 0.1 倍。缓存写入成本**5 分钟 TTL 为 1.25×，1 小时 TTL 为 2×**。收支平衡取决于 TTL：对于 5 分钟 TTL，两个请求收支平衡（1.25× + 0.1× = 1.35× vs 2× 未缓存）；对于 1 小时 TTL，您至少需要三个请求（2× + 0.2× = 2.2× 与 3× 未缓存）。 1 小时的 TTL 可以使条目在突发流量的间隙中保持活动状态，但双倍的写入成本意味着需要更多的读取才能获得回报。

---

## 验证缓存命中

响应 `usage` 对象报告缓存活动：

|领域 |意义|
|---|---|
| `cache_creation_input_tokens` |写入缓存此请求的令牌（您支付了 ~1.25× 写入溢价）|
| `cache_read_input_tokens` |缓存此请求提供的令牌（您支付了 ~0.1×）|
| `input_tokens` |以全价处理的代币（未缓存）|

如果 `cache_read_input_tokens` 在具有相同前缀的重复请求中为零，则静默无效器正在工作 - 比较两个请求之间呈现的提示字节以找到它。

**`input_tokens` 仅是未缓存的剩余部分。** 总提示大小 = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`。如果您的代理运行了几个小时，但 `input_tokens` 显示 4K，则其余部分是从缓存提供的 - 检查总和，而不是单个字段。

特定于语言的访问：`response.usage.cache_read_input_tokens` (Python/TS/Ruby)、`$message->usage->cacheReadInputTokens` (PHP)、`resp.Usage.CacheReadInputTokens` (Go/C#)、`.usage().cacheReadInputTokens()` (Java)。

---

## 失效层次结构

并非每个参数更改都会使所有内容无效。 API 有 3 个缓存层，更改只会使自己的层及以下层无效：

|改变 |工具缓存 |系统缓存|消息缓存 |
|---|:---:|:---:|:---:|
|工具定义（添加/删除/重新排序）| ❌ | ❌ | ❌ |
|型号开关| ❌ | ❌ | ❌ |
| `speed`，网络搜索，引文切换 | ✅ | ❌ | ❌ |
|系统提示内容 | ✅ | ❌ | ❌ |
| `tool_choice`、图像、`thinking` 启用/禁用 | ✅ | ✅ | ❌ |
|留言内容 | ✅ | ✅ | ❌ |

含义：您可以根据请求更改 `tool_choice` 或切换 `thinking`，而不会丢失工具+系统缓存。不要过度担心这些——只有工具定义和模型更改才会强制完全重建。

---

## 20 块回溯窗口

每个断点向后行走**最多 20 个内容块**以查找先前的缓存条目。如果单回合添加超过 20 个块（常见于具有许多 tool_use/tool_result 对的代理循环），则下一个请求的断点将找不到前一个缓存并默默地错过。

修复：在长回合中每约 15 个区块放置一个中间断点，或者 put 在上一回合最后一个缓存区块 20 以内的区块上放置标记。

---

## 并发请求计时

仅在第一个响应**开始流式传输**后，缓存条目才变得可读。 N 个具有相同前缀的并行请求都需要支付全价——没有人可以读取其他人仍在编写的内容。

对于扇出模式：发送 1 个请求，等待第一个流式令牌（不是完整响应），然后触发剩余的 N−1。他们将读取第一个刚刚写入的缓存。

## 预热缓存

要消除*第一个*实际请求的缓存未命中延迟，请在启动时（或间隔时间）发送 **`max_tokens: 0`** 请求。 API 运行预填充 - 在 `cache_control` 断点处写入缓存 - 并立即返回 `content: []`、`stop_reason: "max_tokens"` 和已填充的 `usage` 块（计费为零； `cache_creation_input_tokens` 上的正常缓存写入费用）。

**何时预热** — 预热会用*现在*的缓存写入费用来换取*下一个*实际请求上的较低 TTFT。当这三个条件都满足时，这是值得的：(a) 首次请求延迟是用户可见的（聊天/语音/交互 - 不是后台作业），(b) 共享前缀足够大，冷写入明显很慢，(c) 在流量触发它之前有一段时间 - 应用程序启动、工作进程启动、post 部署、计划窗口的启动。

|当……时跳过预热因为|
|---|---|
|流量连续（请求 ≤ TTL 间隔）|第一个真正的请求会预热缓存，随后的每个请求都会命中它；单独的热情呼叫纯粹是额外的写入|
|前缀较小或低于可缓存的最小值 |冷写损失可以忽略不计
|前缀因请求/用户而异 |没有分享任何预热|
|您可能会推测性地预热许多不同的前缀 |每个都是 ~1.25× 写入；成本可能超过您节省的延迟|

**计划的重新预热：**仅当流量的间隙长于 TTL 时才需要。如果实际请求到达的频率超过每 5 分钟一次，它们会自行保持缓存预热 — 不要添加重新预热间隔。对于具有较长空闲间隙的突发流量，可以在 TTL 下重新预热，也可以切换到 `ttl: "1h"` 并减少重新预热的频率。```python
client.messages.create(
    model="claude-opus-4-8",
    max_tokens=0,
    system=[{
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
    }],
    messages=[{"role": "user", "content": "warmup"}],
)
```**断点放置：** put `cache_control` 在 **与真实请求共享的最后一个块**（系统提示符或工具定义）上 - **不是**在占位符用户消息上，**不是**通过顶级自动缓存（这会将缓存锁定到占位符）。占位符可以是任何非空白字符串；它在预填充期间被读取但从未得到答复。

**拒绝的组合：** `max_tokens: 0` 是 `invalid_request_error`，其中 `stream: true`、`thinking.type: "enabled"`、`output_config.format`、`tool_choice` `{"type":"tool"}` 或 `{"type":"any"}`，或在消息批次请求内。

**TTL 仍然适用** — 对于默认缓存，至少每 5 分钟重新预热一次，或使用 1 小时 TTL。这取代了旧的 `max_tokens: 1` 解决方法（没有要丢弃的单个令牌回复，没有输出令牌计费，意图明确）。
</doc>

<doc path="shared/tool-use-concepts.md">
# 工具使用概念

该文件涵盖了 Claude API 工具使用的概念基础。有关特定于语言的代码示例，请参阅 `python/`、`typescript/` 或其他语言文件夹。有关公开哪些工具、如何管理长时间运行的代理中的上下文以及缓存策略的决策启发式，请参阅 `agent-design.md`。

## 用户定义的工具

### 工具定义结构

> **注意：** 使用 Tool Runner（测试版）时，工具架构会根据您的函数签名 (Python)、Zod 架构 (TypeScript)、带注释的类 (Java)、`jsonschema` 结构标记 (Go) 或`BaseTool` 子类 (Ruby)。下面的原始 JSON 模式格式适用于手动方法 - 包括 PHP 的 `BetaRunnableTool`，它围绕手写模式包装运行闭包 - 或没有工具运行程序支持的 SDK。

每个工具的输入都需要名称、描述和 JSON 架构：```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City and state, e.g., San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "Temperature unit"
      }
    },
    "required": ["location"]
  }
}
```**工具定义的最佳实践：**

- 使用清晰的描述性名称（例如 `get_weather`、`search_database`、`send_email`）
- 编写详细描述 - 克劳德使用这些来决定何时使用该工具
- 包括每个属性的描述
- 对于具有一组固定值的参数，使用 `enum`
- 在`required`中标记真正需要的参数；将其他选项设置为默认值

---

### 工具选择选项

控制克劳德何时使用工具：

|价值|行为 |
| --------------------------------- | -------------------------------------------------------- |
| `{"type": "auto"}` |克劳德决定是否使用工具（默认）|
| `{"type": "any"}` |克劳德必须使用至少一种工具 |
| `{"type": "tool", "name": "..."}` |克劳德必须使用指定工具|
| `{"type": "none"}` |克劳德不能使用工具 |

任何 `tool_choice` 值还可以包括 `"disable_parallel_tool_use": true`，以强制 Claude 每个响应最多使用一个工具。默认情况下，Claude 可以在单个响应中请求多个工具调用。

---

### 工具运行器与手动循环

**工具运行程序（推荐）：** SDK 的工具运行程序自动处理代理循环 - 它调用 API，检测工具使用请求，执行工具函数，将结果反馈给 Claude，并重复直到 Claude 停止调用工具。适用于 Python、TypeScript、Java、Go、Ruby 和 PHP SDK（测试版）。 Python SDK 还提供 MCP 转换助手 (`anthropic.lib.tools.mcp`)，用于转换 MCP 工具、提示和资源，以便与工具运行程序一起使用 — 请参阅`python/claude-api/tool-use.md` 了解详情。

**手动代理循环：** 当您需要对循环进行细粒度控制时使用（例如，自定义日志记录、条件工具执行、人机交互批准）。循环直到 `stop_reason == "end_turn"`，始终附加完整的 `response.content` 以保留 tool_use 块，并确保每个 `tool_result` 包含匹配的 `tool_use_id`。

**服务器端工具的停止原因：** 使用服务器端工具（代码执行、网页搜索等）时，API 运行服务器端采样循环。如果此循环达到 10 次迭代的默认限制，则响应将为 `stop_reason: "pause_turn"`。要继续，请重新发送用户消息和助理响应，并发出另一个 API 请求 - 服务器将从中断处恢复。不要添加额外的用户消息，如 "Continue." — API 检测到尾部 `server_tool_use` 块并知道自动恢复。```python
# Handle pause_turn in your agentic loop
if response.stop_reason == "pause_turn":
    messages = [
        {"role": "user", "content": user_query},
        {"role": "assistant", "content": response.content},
    ]
    # Make another API request — server resumes automatically
    response = client.messages.create(
        model="claude-opus-4-8", messages=messages, tools=tools
    )
```设置 `max_continuations` 限制（例如 5）以防止无限循环。有关完整指南，请参阅：`https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons`

> **安全性：** 只要 Claude 请求，工具运行程序就会自动执行您的工具功能。对于具有副作用的工具（发送电子邮件、修改数据库、金融交易），请验证工具功能中的输入，并考虑要求确认破坏性操作。如果您需要在每次工具执行之前进行人机交互批准，请使用手动代理循环。

---

### 处理工具结果

当 Claude 使用工具时，响应包含 `tool_use` 块。您必须：

1. 使用提供的输入执行该工具
2. 将结果通过 `tool_result` 消息发回
3. 继续对话

**工具结果中的错误处理：** 当工具执行失败时，设置 `"is_error": true` 并提供信息性错误消息。克劳德通常会承认错误，然后尝试不同的方法或要求澄清。

**多个工具调用：** Claude 可以在单个响应中请求多个工具。在继续之前处理所有这些问题 - 将所有结果通过一条 `user` 消息发回。

---

## 服务器端工具：代码执行

代码执行工具让 Claude 在安全的沙盒容器中运行代码。与用户定义的工具不同，服务器端工具在 Anthropic 的基础设施上运行 - 您无需在客户端执行任何操作。只需包含工具定义，Claude 即可处理剩下的事情。

### 关键事实

- 在隔离容器中运行（1 个 CPU、5 GiB RAM、5 GiB 磁盘）
- 无法访问互联网（完全沙盒）
- Python 3.11 预装数据科学库
- 容器可持续保存 30 天，并且可以跨请求重复使用
- 与网络搜索/网络获取工具一起使用时免费；每个组织每月免费使用 1,550 小时后 0.05 美元/小时

### 工具定义

该工具不需要模式 - 只需在 `tools` 数组中声明它：```json
{
  "type": "code_execution_20260120",
  "name": "code_execution"
}
```Claude 自动获得对 `bash_code_execution`（运行 shell 命令）和 `text_editor_code_execution`（创建/查看/编辑文件）的访问权限。

### 预安装 Python 库

- **数据科学**：pandas、numpy、scipy、scikit-learn、statsmodels
- **可视化**：matplotlib、seaborn
- **文件处理**：openpyxl、xlsxwriter、pillow、pypdf、pdfplumber、python-docx、python-pptx
- **数学**：sympy、mpmath
- **实用程序**：tqdm、python-dateutil、pytz、sqlite3

可以在运行时通过 `pip install` 安装其他软件包。

### 支持上传的文件类型

|类型 |扩展 |
| ------ | ---------------------------------- |
|数据| CSV、Excel (.xlsx/.xls)、JSON、XML |
|图片 | JPEG、PNG、GIF、WebP |
|文字| .txt、.md、.py、.js 等 |

### 容器重复使用

跨请求重用容器来维护状态（文件、已安装的包、变量）。从第一个响应中提取 `container_id` 并将其传递给后续请求。

### 响应结构

响应包含交错文本和工具结果块：

- `text` — 克劳德的解释
- `server_tool_use` — 克劳德在做什么
- `bash_code_execution_tool_result` — 代码执行输出（检查 `return_code` 是否成功/失败）
- `text_editor_code_execution_tool_result` — 文件操作结果

> **安全性：** 在将下载的文件写入磁盘之前，始终使用 `os.path.basename()` / `path.basename()` 清理文件名，以防止路径遍历攻击。将文件写入专用输出目录。

---

## 服务器端工具：Web 搜索和 Web Fetch

Web 搜索和 Web 获取让 Claude 可以搜索 Web 并检索页面内容。它们在服务器端运行 - 只需包含工具定义，Claude 就会自动处理查询、获取和结果处理。

### 工具定义```json
[
  { "type": "web_search_20260209", "name": "web_search" },
  { "type": "web_fetch_20260209", "name": "web_fetch" }
]
```### 动态过滤（Opus 4.8 / Opus 4.7 / Opus 4.6 / Sonnet 4.6）

`web_search_20260209` 和 `web_fetch_20260209` 版本支持**动态过滤** — Claude 编写并执行代码以在搜索结果到达上下文窗口之前对其进行过滤，从而提高准确性和令牌效率。动态过滤内置于这些工具版本中并自动激活；您不需要单独声明 `code_execution` 工具或传递任何 beta 标头。```json
{
  "tools": [
    { "type": "web_search_20260209", "name": "web_search" },
    { "type": "web_fetch_20260209", "name": "web_fetch" }
  ]
}
```不带动态滤波，也可以使用之前的 `web_search_20250305` 版本。

> **注意：** 仅当您的应用程序需要独立于 Web 搜索来执行代码以实现其自身目的（数据分析、文件处理、可视化）时，才包含独立的 `code_execution` 工具。将其与 `_20260209` Web 工具一起创建会创建第二个执行环境，这可能会混淆模型。

---

## 服务器端工具：编程工具调用

使用标准工具时，每个工具调用都是一个往返：Claude 调用，结果进入 Claude 的上下文，Claude 原因，然后调用下一个工具。链式调用会累积延迟和令牌——大部分中间数据不再需要。

编程工具调用让 Claude 将这些调用组成一个脚本。脚本在代码执行容器中运行；当它调用工具时，容器暂停，调用执行，结果返回到正在运行的代码（而不是 Claude 的上下文）。该脚本使用正常的控制流处理它。只有最终的输出返回给克劳德。当链接许多工具调用或中间结果很大且应在到达上下文窗口之前进行过滤时，请使用它。

如需完整文档，请使用 WebFetch：

- URL：`https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling`

---

## 服务器端工具：工具搜索

工具搜索工具使 Claude 能够从大型库中动态发现工具，而无需将所有定义加载到上下文窗口中。当您有很多工具但只有少数工具与任何给定的请求相关时，请使用它。发现的工具架构将附加到请求中，而不是换入 - 这会保留提示缓存（请参阅 `agent-design.md` §代理缓存）。

如需完整文档，请使用 WebFetch：

- URL：`https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool`

---

## 技能

技能包特定于任务的说明，克劳德仅在相关时加载。每个技能都是一个包含 `SKILL.md` 文件的文件夹。默认情况下，该技能的简短描述位于上下文中；当当前任务需要时，克劳德会读取完整的文件。使用技能将专门指令排除在基本系统提示之外，同时又不会失去可发现性。

如需完整文档，请使用 WebFetch：

- URL：`https://platform.claude.com/docs/en/agents-and-tools/skills`

---

## 工具使用示例

您可以直接在工具定义中提供示例工具调用，以演示使用模式并减少参数错误。这有助于 Claude 了解如何正确格式化工具输入，特别是对于具有复杂架构的工具。

如需完整文档，请使用 WebFetch：

- URL：`https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use`

---

## 服务器端工具：计算机使用

计算机的使用让 Claude 能够与桌面环境（屏幕截图、鼠标、键盘）进行交互。它可以是人为托管的（服务器端，如代码执行）或自托管（您提供环境并在客户端执行操作）。

如需完整文档，请使用 WebFetch：

- URL：`https://platform.claude.com/docs/en/agents-and-tools/computer-use/overview`

---

## 上下文编辑

当长期运行的代理累积回合时，上下文编辑可以清除陈旧的工具结果和记录中的思维障碍。与压缩（总结）不同，上下文编辑会修剪——清除的内容被删除，而不是被替换。当旧工具输出不再相关并且您希望保持文字记录简洁而又不丢失对话结构时，请使用它。清除内容的阈值是可配置的。

如需完整文档，请使用 WebFetch：

- URL：`https://platform.claude.com/docs/en/build-with-claude/context-editing`

---

## 服务器端工具：Advisor（测试版）

顾问工具让克劳德在对话期间咨询辅助模型。该顾问程序使用您指定的模型运行自己的 API 调用，并将其分析返回到主模型。当您需要第二意见、专业知识或跨模型验证而无需亲自管理编排时，请使用它。

### 工具定义```json
{
  "type": "advisor_20260301",
  "name": "advisor",
  "model": "claude-sonnet-4-6"
}
````model` 参数是必需的 - 它指定顾问程序使用哪个模型进行自己的推理。可选字段：`caching`、`max_uses`、`allowed_callers`、`defer_loading`、`strict`。

**需要 Beta 标头：** `advisor-tool-2026-03-01`。当 `client.beta.messages.create()` 与顾问工具一起使用时，SDK 会自动设置此项。

---

## 客户端工具：内存

记忆工具使克劳德能够通过记忆文件目录存储和检索对话中的信息。 Claude 可以创建、读取、更新和在会话之间保留的 delete 文件。

### 关键事实

- 客户端工具 — 您可以通过实施来控制存储
- 支持命令：`view`、`create`、`str_replace`、`insert`、`delete`、`rename`
- 操作 `/memories` 目录中的文件
- Python、TypeScript 和 Java SDK 提供用于实现内存后端的帮助程序类/函数

> **安全性：** 切勿将 API 密钥、密码、令牌或其他机密存储在内存文件中。请谨慎对待个人身份信息 (PII) — 在保留用户数据之前检查数据隐私法规（GDPR、CCPA）。参考实现没有内置访问控制；在多用户系统中，在工具处理程序中实现每用户内存目录和身份验证。

有关完整的实现示例，请使用 WebFetch：

- 文档：`https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool.md`

---

## 结构化输出

结构化输出限制 Claude 的响应遵循特定的 JSON 模式，从而保证有效、可解析的输出。这不是一个单独的工具 - 它增强了消息 API 响应格式和/或工具参数验证。

有两个功能可用：

- **JSON 输出** (`output_config.format`)：控制 Claude 的响应格式
- **严格工具使用** (`strict: true`)：保证有效的工具参数模式

**支持的型号：** Claude Opus 4.8、Claude Sonnet 4.6 和 Claude Haiku 4.5。旧模型（Claude Opus 4.5、Claude Opus 4.1）也支持结构化输出。

> **推荐：** 使用 `client.messages.parse()`，它会根据您的架构自动验证响应。直接使用`messages.create()`时，使用`output_config: {format: {...}}`。 `output_format` 便利参数也被一些 SDK 方法（例如 `.parse()`）接受，但 `output_config.format` 是规范的 API 级别参数。

### JSON 架构限制

**支持：**

- 基本类型：对象、数组、字符串、整数、数字、布尔值、null
- `enum`、`const`、`anyOf`、`allOf`、`$ref`/`$def`
- 字符串格式：`date-time`、`time`、`date`、`duration`、`email`、`hostname`、 `uri`、`ipv4`、`ipv6`、`uuid`
- `additionalProperties: false`（所有对象都需要）

**不支持：**

- Recursive schemas
- 数值约束（`minimum`、`maximum`、`multipleOf`）
- 字符串约束（`minLength`、`maxLength`）
- 复杂的数组约束
- `additionalProperties` 设置为 `false` 以外的任何值

Python 和 TypeScript SDK 通过从发送到 API 的架构中删除不支持的约束并在客户端验证它们来自动处理不支持的约束。

### 重要提示

- **首次请求延迟**：新模式会产生一次性编译成本。具有相同架构的后续请求将使用 24 小时缓存。
- **拒绝**：如果 Claude 出于安全原因拒绝 (`stop_reason: "refusal"`)，输出可能与您的架构不匹配。
- **令牌限制**：如果是 `stop_reason: "max_tokens"`，输出可能不完整。增加`max_tokens`。
- **不兼容**：引用（返回 400 错误）、消息预填充。
- **适用于**：批次 API、流式传输、令牌计数、扩展思维。

---

## 有效使用工具的技巧

1. **提供详细描述**：Claude 严重依赖描述来理解何时以及如何使用工具
2. **使用特定工具名称**：`get_current_weather` 优于 `weather`
3. **验证输入**：执行前始终验证工具输入
4. **优雅地处理错误**：返回信息丰富的错误消息，以便 Claude 能够适应
5. **限制工具数量**：太多的工具可能会混淆模型 - 保持集合的重点
6. **测试工具交互**：验证Claude在各种场景下正确使用工具

详细的工具使用文档，请使用WebFetch：

- URL：`https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview`
</doc>

<doc path="typescript/claude-api/README.md">
# 克劳德 API — TypeScript

## 安装```bash
npm install @anthropic-ai/sdk
```## 客户端初始化```typescript
import Anthropic from "@anthropic-ai/sdk";

// Default — resolves credentials from the environment:
// ANTHROPIC_API_KEY, or ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile.
// Prefer this for local dev; don't hardcode a key.
const client = new Anthropic();

// Explicit API key (only when you must inject a specific key)
const client = new Anthropic({ apiKey: "your-api-key" });
```---

## 基本消息请求```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [{ role: "user", content: "What is the capital of France?" }],
});
// response.content is ContentBlock[] — a discriminated union. Narrow by .type
// before accessing .text (TypeScript will error on content[0].text without this).
for (const block of response.content) {
  if (block.type === "text") {
    console.log(block.text);
  }
}
```---

## 系统提示```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  system:
    "You are a helpful coding assistant. Always provide examples in Python.",
  messages: [{ role: "user", content: "How do I read a JSON file?" }],
});
```### 对话中系统消息（测试版，模型门控）

对于在对话中到达的操作员指令（模式切换、注入状态），请将 `{role: "system", ...}` 附加到 `messages`，而不是编辑顶级 `system` — 这会保留缓存的前缀并携带操作员权限。必须遵循用户消息；不能是 `messages[0]`。不受支持的型号返回 400 (`role 'system' is not supported on this model`)。请参阅 `shared/prompt-caching.md` 了解何时使用此与顶级 `system`。```typescript
// SDK types for role:"system" in messages are pending — pass the beta header
// directly until the SDK updates, then switch to client.beta.messages.create
// with betas: ["mid-conversation-system-2026-04-07"].
const response = await client.messages.create(
  {
    model: MODEL_ID, // must support mid-conversation system messages
    max_tokens: 16000,
    system: [
      { type: "text", text: STABLE_SYSTEM, cache_control: { type: "ephemeral" } },
    ],
    messages: [
      ...history,
      { role: "user", content: userMessage },
      // @ts-expect-error — role:"system" pending SDK types
      { role: "system", content: "Terse mode enabled — keep responses under 40 words." },
    ],
  },
  { headers: { "anthropic-beta": "mid-conversation-system-2026-04-07" } },
);
```---

## 愿景（图像）

### URL```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: [
        {
          type: "image",
          source: { type: "url", url: "https://example.com/image.png" },
        },
        { type: "text", text: "Describe this image" },
      ],
    },
  ],
});
```### Base64```typescript
import fs from "fs";

const imageData = fs.readFileSync("image.png").toString("base64");

const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: [
        {
          type: "image",
          source: { type: "base64", media_type: "image/png", data: imageData },
        },
        { type: "text", text: "What's in this image?" },
      ],
    },
  ],
});
```---

## 提示缓存

**缓存是前缀匹配** - 前缀中任何位置的任何字节更改都会使其后面的所有内容无效。有关布局模式、架构指南（冻结系统提示、确定性工具顺序、put 易失性内容的位置）和静默无效器审核清单，请阅读 `shared/prompt-caching.md`。

### 自动缓存（推荐）

使用顶级 `cache_control` 自动缓存请求中的最后一个可缓存块：```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  cache_control: { type: "ephemeral" }, // auto-caches the last cacheable block
  system: "You are an expert on this large document...",
  messages: [{ role: "user", content: "Summarize the key points" }],
});
```### 手动缓存控制

为了进行细粒度控制，请将 `cache_control` 添加到特定内容块：```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  system: [
    {
      type: "text",
      text: "You are an expert on this large document...",
      cache_control: { type: "ephemeral" }, // default TTL is 5 minutes
    },
  ],
  messages: [{ role: "user", content: "Summarize the key points" }],
});

// With explicit TTL (time-to-live)
const response2 = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  system: [
    {
      type: "text",
      text: "You are an expert on this large document...",
      cache_control: { type: "ephemeral", ttl: "1h" }, // 1 hour TTL
    },
  ],
  messages: [{ role: "user", content: "Summarize the key points" }],
});
```### 验证缓存命中```typescript
console.log(response.usage.cache_creation_input_tokens); // tokens written to cache (~1.25x cost)
console.log(response.usage.cache_read_input_tokens);     // tokens served from cache (~0.1x cost)
console.log(response.usage.input_tokens);                // uncached tokens (full cost)
```如果 `cache_read_input_tokens` 在重复的相同前缀请求中为零，则说明静默无效器正在工作 - `Date.now()` 或系统提示中的 UUID、非确定性密钥排序或变化的工具集。有关完整审核表，请参阅 `shared/prompt-caching.md`。

---

## 延伸思考

> **Opus 4.8、Opus 4.7、Opus 4.6 和 Sonnet 4.6：** 使用适应性思维。 `budget_tokens` 在 Opus 4.8 和 4.7 上被删除（如果发送则为 400）；在 Opus 4.6 和 Sonnet 4.6 上已弃用。
> **旧型号：** 使用 `thinking: {type: "enabled", budget_tokens: N}`（必须 < `max_tokens`，最小 1024）。```typescript
// Opus 4.8 / 4.7 / 4.6: adaptive thinking (recommended)
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  thinking: { type: "adaptive" },
  output_config: { effort: "high" }, // low | medium | high | max
  messages: [
    { role: "user", content: "Solve this math problem step by step..." },
  ],
});

for (const block of response.content) {
  if (block.type === "thinking") {
    console.log("Thinking:", block.thinking);
  } else if (block.type === "text") {
    console.log("Response:", block.text);
  }
}
```---

## 错误处理

使用 SDK 的类型化异常类 — 永远不要检查字符串匹配的错误消息：```typescript
import Anthropic from "@anthropic-ai/sdk";

try {
  const response = await client.messages.create({...});
} catch (error) {
  if (error instanceof Anthropic.BadRequestError) {
    console.error("Bad request:", error.message);
  } else if (error instanceof Anthropic.AuthenticationError) {
    console.error("Invalid API key");
  } else if (error instanceof Anthropic.RateLimitError) {
    console.error("Rate limited - retry later");
  } else if (error instanceof Anthropic.APIError) {
    console.error(`API error ${error.status}:`, error.message);
  }
}
```所有类都使用类型化 `status` 字段扩展 `Anthropic.APIError`。从最具体到最不具体进行检查。请参阅 [shared/error-codes.md](../../shared/error-codes.md) 以获取完整的错误代码参考。

---

## 多轮对话

API 是无状态的 — 每次都会发送完整的对话历史记录。使用 `Anthropic.MessageParam[]` 键入消息数组：```typescript
const messages: Anthropic.MessageParam[] = [
  { role: "user", content: "My name is Alice." },
  { role: "assistant", content: "Hello Alice! Nice to meet you." },
  { role: "user", content: "What's my name?" },
];

const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: messages,
});
```**规则：**

- 允许连续的相同角色消息 - API 将它们组合成一个回合
- 第一条消息必须是 `user`
- 对所有 API 数据结构使用 SDK 类型（`Anthropic.MessageParam`、`Anthropic.Message`、`Anthropic.Tool` 等）——不要重新定义等效接口

---

### 压缩（长对话）

> **Beta、Opus 4.8、Opus 4.7、Opus 4.6 和 Sonnet 4.6。** 当对话接近 200K 上下文窗口时，压缩会自动总结服务器端较早的上下文。 API 返回 `compaction` 块；您必须在后续请求中将其传回 - 附加 `response.content`，而不仅仅是文本。```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();
const messages: Anthropic.Beta.BetaMessageParam[] = [];

async function chat(userMessage: string): Promise<string> {
  messages.push({ role: "user", content: userMessage });

  const response = await client.beta.messages.create({
    betas: ["compact-2026-01-12"],
    model: "claude-opus-4-8",
    max_tokens: 16000,
    messages,
    context_management: {
      edits: [{ type: "compact_20260112" }],
    },
  });

  // Append full content — compaction blocks must be preserved
  messages.push({ role: "assistant", content: response.content });

  const textBlock = response.content.find(
    (b): b is Anthropic.Beta.BetaTextBlock => b.type === "text",
  );
  return textBlock?.text ?? "";
}

// Compaction triggers automatically when context grows large
console.log(await chat("Help me build a Python web scraper"));
console.log(await chat("Add support for JavaScript-rendered pages"));
console.log(await chat("Now add rate limiting and error handling"));
```---

## 停止原因

响应中的 `stop_reason` 字段指示模型停止生成的原因：

|价值|意义|
| ---------------- | --------------------------------------------------------------------------- |
| `end_turn` |克劳德很自然地完成了回应|
| `max_tokens` |达到 `max_tokens` 限制 — 增加限制或使用流式传输 |
| `stop_sequence` |按下自定义停止顺序 |
| `tool_use` |克劳德想要调用一个工具——执行它并继续 |
| `pause_turn` |模型已暂停并可以恢复（代理流）|
| `refusal` |克劳德出于安全原因拒绝了 — 检查 `stop_details` |

### 结构化止损详细信息

当 `stop_reason` 为 `"refusal"` 时，响应包括 `stop_details` 对象，其中包含有关拒绝的结构化信息：```typescript
if (response.stop_reason === "refusal" && response.stop_details) {
  console.log(`Category: ${response.stop_details.category}`); // "cyber" | "bio" | null
  console.log(`Explanation: ${response.stop_details.explanation}`);
}
```---

## 成本优化策略

### 1. 对重复上下文使用提示缓存```typescript
// Automatic caching (simplest — caches the last cacheable block)
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  cache_control: { type: "ephemeral" },
  system: largeDocumentText, // e.g., 50KB of context
  messages: [{ role: "user", content: "Summarize the key points" }],
});

// First request: full cost
// Subsequent requests: ~90% cheaper for cached portion
```### 2. 在请求之前使用令牌计数```typescript
const countResponse = await client.messages.countTokens({
  model: "claude-opus-4-8",
  messages: messages,
  system: system,
});

const estimatedInputCost = countResponse.input_tokens * 0.000005; // $5/1M tokens
console.log(`Estimated input cost: $${estimatedInputCost.toFixed(4)}`);
```</doc>

<doc path="typescript/claude-api/batches.md">
# 消息批次 API — TypeScript

批次 API (`POST /v1/messages/batches`) 以标准价格的 50% 异步处理消息 API 请求。

## 关键事实

- 每批最多 100,000 个请求或 256 MB
- 大多数批次在 1 小时内完成；最长24小时
- 结果在创建后 29 天内可用
- 所有代币使用成本降低 50%
- 支持所有消息 API 功能（视觉、工具、缓存等）

---

## 创建一个批次```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const messageBatch = await client.messages.batches.create({
  requests: [
    {
      custom_id: "request-1",
      params: {
        model: "claude-opus-4-8",
        max_tokens: 16000,
        messages: [
          { role: "user", content: "Summarize climate change impacts" },
        ],
      },
    },
    {
      custom_id: "request-2",
      params: {
        model: "claude-opus-4-8",
        max_tokens: 16000,
        messages: [
          { role: "user", content: "Explain quantum computing basics" },
        ],
      },
    },
  ],
});

console.log(`Batch ID: ${messageBatch.id}`);
console.log(`Status: ${messageBatch.processing_status}`);
```---

## 投票完成```typescript
let batch;
while (true) {
  batch = await client.messages.batches.retrieve(messageBatch.id);
  if (batch.processing_status === "ended") break;
  console.log(
    `Status: ${batch.processing_status}, processing: ${batch.request_counts.processing}`,
  );
  await new Promise((resolve) => setTimeout(resolve, 60_000));
}

console.log("Batch complete!");
console.log(`Succeeded: ${batch.request_counts.succeeded}`);
console.log(`Errored: ${batch.request_counts.errored}`);
```---

## 检索结果```typescript
for await (const result of await client.messages.batches.results(
  messageBatch.id,
)) {
  switch (result.result.type) {
    case "succeeded":
      console.log(
        `[${result.custom_id}] ${result.result.message.content[0].text.slice(0, 100)}`,
      );
      break;
    case "errored":
      if (result.result.error.type === "invalid_request") {
        console.log(`[${result.custom_id}] Validation error - fix and retry`);
      } else {
        console.log(`[${result.custom_id}] Server error - safe to retry`);
      }
      break;
    case "expired":
      console.log(`[${result.custom_id}] Expired - resubmit`);
      break;
  }
}
```---

## 取消批次```typescript
const cancelled = await client.messages.batches.cancel(messageBatch.id);
console.log(`Status: ${cancelled.processing_status}`); // "canceling"
```</doc>

<doc path="typescript/claude-api/files-api.md">
# 文件 API — TypeScript

文件 API 上传文件以在消息 API 请求中使用。通过内容块中的 `file_id` 引用文件，避免跨多个 API 调用重新上传。

**测试版：** 在 API 调用中传递 `betas: ["files-api-2025-04-14"]`（SDK 自动设置所需的标头）。

## 关键事实

- 最大文件大小：500 MB
- 总存储空间：每个组织 100 GB
- 文件持续存在直至被删除
- 文件操作（上传、列表、delete）免费；消息中使用的内容按输入令牌计费
- 不适用于 Amazon Bedrock 或 Google Vertex AI

---

## 上传文件```typescript
import Anthropic, { toFile } from "@anthropic-ai/sdk";
import fs from "fs";

const client = new Anthropic();

const uploaded = await client.beta.files.upload({
  file: await toFile(fs.createReadStream("report.pdf"), undefined, {
    type: "application/pdf",
  }),
  betas: ["files-api-2025-04-14"],
});

console.log(`File ID: ${uploaded.id}`);
console.log(`Size: ${uploaded.size_bytes} bytes`);
```---

## 在消息中使用文件

### PDF/文本文档```typescript
const response = await client.beta.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: [
        { type: "text", text: "Summarize the key findings in this report." },
        {
          type: "document",
          source: { type: "file", file_id: uploaded.id },
          title: "Q4 Report",
          citations: { enabled: true },
        },
      ],
    },
  ],
  betas: ["files-api-2025-04-14"],
});

console.log(response.content[0].text);
```---

## 管理文件

### 列出文件```typescript
const files = await client.beta.files.list({
  betas: ["files-api-2025-04-14"],
});
for (const f of files.data) {
  console.log(`${f.id}: ${f.filename} (${f.size_bytes} bytes)`);
}
```### Delete 一个文件```typescript
await client.beta.files.delete("file_011CNha8iCJcU1wXNR6q4V8w", {
  betas: ["files-api-2025-04-14"],
});
```### 下载文件```typescript
const response = await client.beta.files.download(
  "file_011CNha8iCJcU1wXNR6q4V8w",
  { betas: ["files-api-2025-04-14"] },
);
const content = Buffer.from(await response.arrayBuffer());
await fs.promises.writeFile("output.txt", content);
```</doc>

<doc path="typescript/claude-api/streaming.md">
# 流媒体 — TypeScript

## 快速入门```typescript
const stream = client.messages.stream({
  model: "claude-opus-4-8",
  max_tokens: 64000,
  messages: [{ role: "user", content: "Write a story" }],
});

for await (const event of stream) {
  if (
    event.type === "content_block_delta" &&
    event.delta.type === "text_delta"
  ) {
    process.stdout.write(event.delta.text);
  }
}
```---

## 处理不同的内容类型

> **Opus 4.8 / Opus 4.7 / Opus 4.6：** 使用 `thinking: {type: "adaptive"}`。在旧型号上，请改用 `thinking: {type: "enabled", budget_tokens: N}`。```typescript
const stream = client.messages.stream({
  model: "claude-opus-4-8",
  max_tokens: 64000,
  thinking: { type: "adaptive" },
  messages: [{ role: "user", content: "Analyze this problem" }],
});

for await (const event of stream) {
  switch (event.type) {
    case "content_block_start":
      switch (event.content_block.type) {
        case "thinking":
          console.log("\n[Thinking...]");
          break;
        case "text":
          console.log("\n[Response:]");
          break;
      }
      break;
    case "content_block_delta":
      switch (event.delta.type) {
        case "thinking_delta":
          process.stdout.write(event.delta.thinking);
          break;
        case "text_delta":
          process.stdout.write(event.delta.text);
          break;
      }
      break;
  }
}
```---

## 使用工具进行流式传输 (Tool Runner)

使用带有 `stream: true` 的工具运行装置。外循环迭代工具运行器迭代（消息），内循环处理流事件：```typescript
import Anthropic from "@anthropic-ai/sdk";
import { betaZodTool } from "@anthropic-ai/sdk/helpers/beta/zod";
import { z } from "zod";

const client = new Anthropic();

const getWeather = betaZodTool({
  name: "get_weather",
  description: "Get current weather for a location",
  inputSchema: z.object({
    location: z.string().describe("City and state, e.g., San Francisco, CA"),
  }),
  run: async ({ location }) => `72°F and sunny in ${location}`,
});

const runner = client.beta.messages.toolRunner({
  model: "claude-opus-4-8",
  max_tokens: 64000,
  tools: [getWeather],
  messages: [
    { role: "user", content: "What's the weather in Paris and London?" },
  ],
  stream: true,
});

// Outer loop: each tool runner iteration
for await (const messageStream of runner) {
  // Inner loop: stream events for this iteration
  for await (const event of messageStream) {
    switch (event.type) {
      case "content_block_delta":
        switch (event.delta.type) {
          case "text_delta":
            process.stdout.write(event.delta.text);
            break;
          case "input_json_delta":
            // Tool input being streamed
            break;
        }
        break;
    }
  }
}
```---

## 获取最终消息```typescript
const stream = client.messages.stream({
  model: "claude-opus-4-8",
  max_tokens: 64000,
  messages: [{ role: "user", content: "Hello" }],
});

for await (const event of stream) {
  // Process events...
}

const finalMessage = await stream.finalMessage();
console.log(`Tokens used: ${finalMessage.usage.output_tokens}`);
```---

## 流事件类型

|事件类型 |描述 |当它发生时 |
| -------------------- | ------------------------ | | --------------------------------- |
| `message_start` |包含消息元数据 |一次在开始 |
| `content_block_start` |新内容块开始 |当文本/tool_use 块开始时 |
| `content_block_delta` |增量内容更新 |对于每个令牌/块|
| `content_block_stop` |内容块完成 |当一个块完成时 |
| `message_delta` |消息级更新 |包含 `stop_reason`，用法 |
| `message_stop` |留言完毕 |一次在最后|

## 最佳实践

1. **始终刷新输出** — 使用 `process.stdout.write()` 立即显示
2. **处理部分响应** — 如果流中断，您的内容可能不完整
3. **跟踪代币使用情况** — `message_delta` 事件包含使用信息
4. **使用 `finalMessage()`** — 即使在流式传输时，Get 也是完整的 `Anthropic.Message` 对象。不要将 `.on()` 事件包装在 `new Promise()` 中 — `finalMessage()` 在内部处理所有完成/错误/中止状态
5. **Web UI 的缓冲区** — 考虑在渲染之前缓冲一些令牌，以避免过多的 DOM 更新
6. **使用 `stream.on("text", ...)` 进行增量** — `text` 事件仅提供增量字符串，比手动过滤 `content_block_delta` 事件更简单
7. **对于具有流式处理的代理循环** — 请参阅 tool-use.md 中的 [Streaming Manual Loop](./tool-use.md#streaming-manual-loop) 部分，了解如何将 `stream()` + `finalMessage()` 与工具使用循环结合起来

## 原始 SSE 格式

如果使用原始 HTTP（不是 SDK），则流返回服务器发送的事件：```
event: message_start
data: {"type":"message_start","message":{"id":"msg_...","type":"message",...}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":12}}

event: message_stop
data: {"type":"message_stop"}
```</doc>

<doc path="typescript/claude-api/tool-use.md">
# 工具使用 — TypeScript

有关概念概述（工具定义、工具选择、提示），请参阅 [shared/tool-use-concepts.md](../../shared/tool-use-concepts.md)。

## 工具运行程序（推荐）

**测试版：** TypeScript SDK 中的工具运行程序处于测试版状态。

将 `betaZodTool` 与 Zod 模式结合使用，通过 `run` 函数定义工具，然后将它们传递给 `client.beta.messages.toolRunner()`：```typescript
import Anthropic from "@anthropic-ai/sdk";
import { betaZodTool } from "@anthropic-ai/sdk/helpers/beta/zod";
import { z } from "zod";

const client = new Anthropic();

const getWeather = betaZodTool({
  name: "get_weather",
  description: "Get current weather for a location",
  inputSchema: z.object({
    location: z.string().describe("City and state, e.g., San Francisco, CA"),
    unit: z.enum(["celsius", "fahrenheit"]).optional(),
  }),
  run: async (input) => {
    // Your implementation here
    return `72°F and sunny in ${input.location}`;
  },
});

// The tool runner handles the agentic loop and returns the final message
const finalMessage = await client.beta.messages.toolRunner({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  tools: [getWeather],
  messages: [{ role: "user", content: "What's the weather in Paris?" }],
});

console.log(finalMessage.content);
```**工具运行程序的主要优点：**

- 无手动循环 — SDK 负责调用工具并反馈结果
- 通过 Zod 模式进行类型安全的工具输入
- 工具模式根据 Zod 定义自动生成
- 当 Claude 不再有工具调用时迭代会自动停止

---

## 手动代理循环

当您需要细粒度控制（自定义日志记录、条件工具执行、流式传输单个迭代、人机交互批准）时，请使用此选项：```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();
const tools: Anthropic.Tool[] = [...]; // Your tool definitions
let messages: Anthropic.MessageParam[] = [{ role: "user", content: userInput }];

while (true) {
  const response = await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 16000,
    tools: tools,
    messages: messages,
  });

  if (response.stop_reason === "end_turn") break;

  // Server-side tool hit iteration limit; append assistant turn and re-send to continue
  if (response.stop_reason === "pause_turn") {
    messages.push({ role: "assistant", content: response.content });
    continue;
  }

  const toolUseBlocks = response.content.filter(
    (b): b is Anthropic.ToolUseBlock => b.type === "tool_use",
  );

  messages.push({ role: "assistant", content: response.content });

  const toolResults: Anthropic.ToolResultBlockParam[] = [];
  for (const tool of toolUseBlocks) {
    const result = await executeTool(tool.name, tool.input);
    toolResults.push({
      type: "tool_result",
      tool_use_id: tool.id,
      content: result,
    });
  }

  messages.push({ role: "user", content: toolResults });
}
```### 流媒体手动循环

当您需要在手动循环中进行流式传输时，请使用 `client.messages.stream()` + `finalMessage()` 而不是 `.create()`。文本增量在每次迭代中进行流式传输； `finalMessage()` 收集完整的 `Message`，以便您可以检查 `stop_reason` 并提取工具使用块：```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();
const tools: Anthropic.Tool[] = [...];
let messages: Anthropic.MessageParam[] = [{ role: "user", content: userInput }];

while (true) {
  const stream = client.messages.stream({
    model: "claude-opus-4-8",
    max_tokens: 64000,
    tools,
    messages,
  });

  // Stream text deltas on each iteration
  stream.on("text", (delta) => {
    process.stdout.write(delta);
  });

  // finalMessage() resolves with the complete Message — no need to
  // manually wire up .on("message") / .on("error") / .on("abort")
  const message = await stream.finalMessage();

  if (message.stop_reason === "end_turn") break;

  // Server-side tool hit iteration limit; append assistant turn and re-send to continue
  if (message.stop_reason === "pause_turn") {
    messages.push({ role: "assistant", content: message.content });
    continue;
  }

  const toolUseBlocks = message.content.filter(
    (b): b is Anthropic.ToolUseBlock => b.type === "tool_use",
  );

  messages.push({ role: "assistant", content: message.content });

  const toolResults: Anthropic.ToolResultBlockParam[] = [];
  for (const tool of toolUseBlocks) {
    const result = await executeTool(tool.name, tool.input);
    toolResults.push({
      type: "tool_result",
      tool_use_id: tool.id,
      content: result,
    });
  }

  messages.push({ role: "user", content: toolResults });
}
```> **重要提示：** 不要将 `.on()` 事件包装在 `new Promise()` 中来收集最终消息 - 请改用 `stream.finalMessage()`。 SDK 在内部处理所有错误/中止/完成状态。

> **循环中的错误处理：** 使用 SDK 的类型化异常（例如 `Anthropic.RateLimitError`、`Anthropic.APIError`） - 有关示例，请参阅[错误处理](./README.md#error-handling)。不要用字符串匹配来检查错误消息。

> **SDK 类型：** 使用 `Anthropic.MessageParam`、`Anthropic.Tool`、`Anthropic.ToolUseBlock`、`Anthropic.ToolResultBlockParam`、`Anthropic.Message` 等API 相关数据结构。不要重新定义等效接口。

---

## 处理工具结果```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  tools: tools,
  messages: [{ role: "user", content: "What's the weather in Paris?" }],
});

for (const block of response.content) {
  if (block.type === "tool_use") {
    const result = await executeTool(block.name, block.input);

    const followup = await client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 16000,
      tools: tools,
      messages: [
        { role: "user", content: "What's the weather in Paris?" },
        { role: "assistant", content: response.content },
        {
          role: "user",
          content: [
            { type: "tool_result", tool_use_id: block.id, content: result },
          ],
        },
      ],
    });
  }
}
```---

## 工具选择```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  tools: tools,
  tool_choice: { type: "tool", name: "get_weather" },
  messages: [{ role: "user", content: "What's the weather in Paris?" }],
});
```---

## 服务器端工具

版本后缀的 `type` 文字； `name` 对于每个接口都是固定的。传递普通对象文字 - `ToolUnion` 类型在结构上得到满足。 **`name`/`type` 对必须与接口匹配**：将 `str_replace_based_edit_tool`（20250728 名称）与 `text_editor_20250124`（预计为 `str_replace_editor`）混合是TS2322。

**不要键入注释为 `Tool[]`** — `Tool` 只是自定义工具变体。让结构类型从 `tools` 参数推断，或者注释为 `Anthropic.Messages.ToolUnion[]`（如果必须）：```typescript
// ✓ let inference work — no annotation
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  tools: [
    { type: "text_editor_20250728", name: "str_replace_based_edit_tool" },
    { type: "bash_20250124", name: "bash" },
    { type: "web_search_20260209", name: "web_search" },
    { type: "code_execution_20260120", name: "code_execution" },
  ],
  messages: [{ role: "user", content: "..." }],
});

// ✗ this is a TS2352 — Tool is the CUSTOM tool variant only
// const tools: Anthropic.Tool[] = [{ type: "text_editor_20250728", ... }]
```|接口 | `name` | `type` |
|---|---|---|
| `ToolTextEditor20250124` | `str_replace_editor` | `text_editor_20250124` |
| `ToolTextEditor20250429` | `str_replace_based_edit_tool` | `text_editor_20250429` |
| `ToolTextEditor20250728` | `str_replace_based_edit_tool` | `text_editor_20250728` |
| `ToolBash20250124` | `bash` | `bash_20250124` |
| `WebSearchTool20260209` | `web_search` | `web_search_20260209` |
| `WebFetchTool20260209` | `web_fetch` | `web_fetch_20260209` |
| `CodeExecutionTool20260120` | `code_execution` | `code_execution_20260120` |

**不要混合 beta 和非 beta 类型**：如果您调用 `client.beta.messages.create()`，则响应 `content` 是 `BetaContentBlock[]` — 您无法在不缩小每个元素的情况下将其传递给非 beta `ContentBlockParam[]`。

---


## 代码执行

### 基本用法```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content:
        "Calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
    },
  ],
  tools: [{ type: "code_execution_20260120", name: "code_execution" }],
});
```### 读取本地文件（ESM 注释）

ES 模块中不存在 `__dirname`。对于脚本相对路径，请使用 `import.meta.url`：```typescript
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const pdfBytes = readFileSync(join(__dirname, "sample.pdf"));
```或者，如果脚本从已知目录运行，则使用 CWD 相对路径：`readFileSync("./sample.pdf")`。

### 上传文件进行分析```typescript
import Anthropic, { toFile } from "@anthropic-ai/sdk";
import { createReadStream } from "fs";

const client = new Anthropic();

// 1. Upload a file
const uploaded = await client.beta.files.upload({
  file: await toFile(createReadStream("sales_data.csv"), undefined, {
    type: "text/csv",
  }),
  betas: ["files-api-2025-04-14"],
});

// 2. Pass to code execution
// Code execution is GA; Files API is still beta (pass via RequestOptions)
const response = await client.messages.create(
  {
    model: "claude-opus-4-8",
    max_tokens: 16000,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: "Analyze this sales data. Show trends and create a visualization.",
          },
          { type: "container_upload", file_id: uploaded.id },
        ],
      },
    ],
    tools: [{ type: "code_execution_20260120", name: "code_execution" }],
  },
  { headers: { "anthropic-beta": "files-api-2025-04-14" } },
);
```### 检索生成的文件```typescript
import path from "path";
import fs from "fs";

const OUTPUT_DIR = "./claude_outputs";
await fs.promises.mkdir(OUTPUT_DIR, { recursive: true });

for (const block of response.content) {
  if (block.type === "bash_code_execution_tool_result") {
    const result = block.content;
    if (result.type === "bash_code_execution_result" && result.content) {
      for (const fileRef of result.content) {
        if (fileRef.type === "bash_code_execution_output") {
          const metadata = await client.beta.files.retrieveMetadata(
            fileRef.file_id,
          );
          const downloadResponse = await client.beta.files.download(fileRef.file_id);
          const fileBytes = Buffer.from(await downloadResponse.arrayBuffer());
          const safeName = path.basename(metadata.filename);
          if (!safeName || safeName === "." || safeName === "..") {
            console.warn(`Skipping invalid filename: ${metadata.filename}`);
            continue;
          }
          const outputPath = path.join(OUTPUT_DIR, safeName);
          await fs.promises.writeFile(outputPath, fileBytes);
          console.log(`Saved: ${outputPath}`);
        }
      }
    }
  }
}
```### 容器重复使用```typescript
// First request: set up environment
const response1 = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: "Install tabulate and create data.json with sample user data",
    },
  ],
  tools: [{ type: "code_execution_20260120", name: "code_execution" }],
});

// Reuse container
// container is nullable — set only when using server-side code execution
const containerId = response1.container!.id;

const response2 = await client.messages.create({
  container: containerId,
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: "Read data.json and display as a formatted table",
    },
  ],
  tools: [{ type: "code_execution_20260120", name: "code_execution" }],
});
```---

## 记忆工具

### 基本用法```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: "Remember that my preferred language is TypeScript.",
    },
  ],
  tools: [{ type: "memory_20250818", name: "memory" }],
});
```### SDK 内存助手

将 `betaMemoryTool` 与 `MemoryToolHandlers` 实现结合使用：```typescript
import {
  betaMemoryTool,
  type MemoryToolHandlers,
} from "@anthropic-ai/sdk/helpers/beta/memory";

const handlers: MemoryToolHandlers = {
  async view(command) { ... },
  async create(command) { ... },
  async str_replace(command) { ... },
  async insert(command) { ... },
  async delete(command) { ... },
  async rename(command) { ... },
};

const memory = betaMemoryTool(handlers);

const runner = client.beta.messages.toolRunner({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  tools: [memory],
  messages: [{ role: "user", content: "Remember my preferences" }],
});

for await (const message of runner) {
  console.log(message);
}
```有关完整的实现示例，请使用 WebFetch：

- `https://github.com/anthropics/anthropic-sdk-typescript/blob/main/examples/tools-helpers-memory.ts`

---

## 结构化输出

### JSON 输出（Zod — 推荐）```typescript
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const ContactInfoSchema = z.object({
  name: z.string(),
  email: z.string(),
  plan: z.string(),
  interests: z.array(z.string()),
  demo_requested: z.boolean(),
});

const client = new Anthropic();

const response = await client.messages.parse({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content:
        "Extract: Jane Doe (jane@co.com) wants Enterprise, interested in API and SDKs, wants a demo.",
    },
  ],
  output_config: {
    format: zodOutputFormat(ContactInfoSchema),
  },
});

// parsed_output is null if parsing failed — assert or guard
console.log(response.parsed_output!.name); // "Jane Doe"
```### 严格工具使用```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [
    {
      role: "user",
      content: "Book a flight to Tokyo for 2 passengers on March 15",
    },
  ],
  tools: [
    {
      name: "book_flight",
      description: "Book a flight to a destination",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          destination: { type: "string" },
          date: { type: "string", format: "date" },
          passengers: {
            type: "integer",
            enum: [1, 2, 3, 4, 5, 6, 7, 8],
          },
        },
        required: ["destination", "date", "passengers"],
        additionalProperties: false,
      },
    },
  ],
});
```</doc>

<doc path="typescript/managed-agents/README.md">
# 托管代理 — TypeScript

> **此处未显示绑定：** 本自述文件涵盖了 TypeScript 最常见的托管代理流程。如果您需要未显示的类、方法、命名空间、字段或行为，请从 `shared/live-sources.md` Web 获取 TypeScript SDK 存储库**或相关文档页面**，而不是猜测。请勿从 cURL 形状或其他语言的 SDK 进行推断。

> **代理是持久性的 — 创建一次，通过 ID 引用。** 存储 `agents.create` 返回的代理 ID，并将其传递给后续的每个 `sessions.create`；不要在请求路径中调用 `agents.create`。 Anthropic CLI 是从版本控制的 YAML 创建代理和环境的一种便捷方法 - 其 URL 位于 `shared/live-sources.md` 中。为了完整性，下面的示例展示了代码内创建；在生产中，创建调用属于设置，而不是请求路径。

＃＃ 安装```bash
npm install @anthropic-ai/sdk
```## 客户端初始化```typescript
import Anthropic from "@anthropic-ai/sdk";

// Default — resolves credentials from the environment:
// ANTHROPIC_API_KEY, or ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile.
// Prefer this for local dev; don't hardcode a key.
const client = new Anthropic();

// Explicit API key (only when you must inject a specific key)
const client = new Anthropic({ apiKey: "your-api-key" });
```---

## 创建环境```typescript
const environment = await client.beta.environments.create(
  {
    name: "my-dev-env",
    config: {
      type: "cloud",
      networking: { type: "unrestricted" },
    },
  },
);
console.log(environment.id); // env_...
```---

## 创建代理（第一步必填）

> ⚠️ **没有内联代理配置。** `model`/`system`/`tools` 存在于代理对象上，而不是会话上。始终以 `agents.create()` 开始 — 会话仅需要 `agent: { type: "agent", id: agent.id }`。

### 最小```typescript
// 1. Create the agent (reusable, versioned)
const agent = await client.beta.agents.create(
  {
    name: "Coding Assistant",
    model: "claude-opus-4-8",
    tools: [{ type: "agent_toolset_20260401", default_config: { enabled: true } }],
  },
);

// 2. Start a session
const session = await client.beta.sessions.create(
  {
    agent: { type: "agent", id: agent.id, version: agent.version },
    environment_id: environment.id,
  },
);
console.log(session.id, session.status);
```### 带有系统提示和自定义工具```typescript
const agent = await client.beta.agents.create(
  {
    name: "Code Reviewer",
    model: "claude-opus-4-8",
    system: "You are a senior code reviewer.",
    tools: [
      { type: "agent_toolset_20260401", default_config: { enabled: true } },
      {
        type: "custom",
        name: "run_tests",
        description: "Run the test suite",
        input_schema: {
          type: "object",
          properties: {
            test_path: { type: "string", description: "Path to test file" },
          },
          required: ["test_path"],
        },
      },
    ],
  },
);

const session = await client.beta.sessions.create(
  {
    agent: { type: "agent", id: agent.id, version: agent.version },
    environment_id: environment.id,
    title: "Code review session",
    resources: [
      {
        type: "github_repository",
        url: "https://github.com/owner/repo",
        mount_path: "/workspace/repo",
        authorization_token: process.env.GITHUB_TOKEN,
        branch: "main",
      },
    ],
  },
);
```---

## 发送用户消息```typescript
await client.beta.sessions.events.send(
  session.id,
  {
    events: [
      {
        type: "user.message",
        content: [{ type: "text", text: "Review the auth module" }],
      },
    ],
  },
);
```> 💡 **流优先：**在发送消息之前*（或同时）打开流。流仅传递打开后发生的事件 - 发送后流意味着早期事件以一批方式缓冲到达。请参阅[转向模式](../../shared/managed-agents-events.md#steering-patterns)。

---

## 直播活动 (SSE)```typescript
// Stream-first: open stream and send concurrently
const [events] = await Promise.all([
  collectStream(session.id),
  client.beta.sessions.events.send(
    session.id,
    { events: [{ type: "user.message", content: [{ type: "text", text: "..." }] }] },
  ),
]);

// Standalone stream iteration:
const stream = await client.beta.sessions.events.stream(
  session.id,
);

for await (const event of stream) {
  switch (event.type) {
    case "agent.message":
      for (const block of event.content) {
        if (block.type === "text") {
          process.stdout.write(block.text);
        }
      }
      break;
    case "agent.custom_tool_use":
      // Custom tool invocation — session is now idle
      console.log(`\nCustom tool call: ${event.name}`);
      console.log(`Input: ${JSON.stringify(event.input)}`);
      break;
    case "session.status_idle":
      console.log("\n--- Agent idle ---");
      break;
    case "session.status_terminated":
      console.log("\n--- Session terminated ---");
      break;
  }
}
```---

## 提供自定义工具结果```typescript
await client.beta.sessions.events.send(
  session.id,
  {
    events: [
      {
        type: "user.custom_tool_result",
        custom_tool_use_id: "sevt_abc123",
        content: [{ type: "text", text: "All 42 tests passed." }],
      },
    ],
  },
);
```---

## 投票活动```typescript
const events = await client.beta.sessions.events.list(
  session.id,
);
for (const event of events.data) {
  console.log(`${event.type}: ${event.id}`);
}
```---

## 使用自定义工具的完整流媒体循环```typescript
function runCustomTool(toolName: string, toolInput: unknown): string {
  if (toolName === "run_tests") {
    // Your tool implementation here
    return "All tests passed.";
  }
  return `Unknown tool: ${toolName}`;
}

async function runSession(client: Anthropic, sessionId: string) {
  while (true) {
    const stream = await client.beta.sessions.events.stream(
      sessionId,
    );

    const toolCalls: Anthropic.Beta.Sessions.BetaManagedAgentsAgentCustomToolUseEvent[] = [];

    for await (const event of stream) {
      if (event.type === "agent.message") {
        for (const block of event.content) {
          if (block.type === "text") {
            process.stdout.write(block.text);
          }
        }
      } else if (event.type === "agent.custom_tool_use") {
        toolCalls.push(event);
      } else if (event.type === "session.status_idle") {
        break;
      } else if (event.type === "session.status_terminated") {
        return;
      }
    }

    if (toolCalls.length === 0) break;

    // Process custom tool calls
    const results = toolCalls.map((call) => ({
      type: "user.custom_tool_result" as const,
      custom_tool_use_id: call.id,
      content: [{ type: "text" as const, text: runCustomTool(call.name, call.input) }],
    }));

    await client.beta.sessions.events.send(
      sessionId,
      { events: results },
    );
  }
}
```---

## 上传文件```typescript
import fs from "fs";

const file = await client.beta.files.upload({
  file: fs.createReadStream("data.csv"),
  purpose: "agent",
});

// Use in a session
const session = await client.beta.sessions.create(
  {
    agent: { type: "agent", id: agent.id, version: agent.version },
    environment_id: environment.id,
    resources: [{ type: "file", file_id: file.id, mount_path: "/workspace/data.csv" }],
  },
);
```---

## 列出并下载会话文件

列出代理在会话期间写入 `/mnt/session/outputs/` 的文件，然后下载它们。```typescript
import fs from "fs";

// List files associated with a session
const files = await client.beta.files.list({
  scope_id: session.id,
  betas: ["managed-agents-2026-04-01"],
});
for (const f of files.data) {
  console.log(f.filename, f.size_bytes);

  // Download and save to disk
  const resp = await client.beta.files.download(f.id);
  const buffer = Buffer.from(await resp.arrayBuffer());
  fs.writeFileSync(f.filename, buffer);
}
```> 💡 `session.status_idle` 和 `files.list` 中出现的输出文件之间存在短暂的索引滞后（~1–3 秒）。如果列表为空，请重试一次或两次。

---

## 会话管理```typescript
// Get session details
const session = await client.beta.sessions.retrieve("sesn_011CZxAbc123Def456");
console.log(session.status, session.usage);

// List sessions
const sessions = await client.beta.sessions.list();

// Delete a session
await client.beta.sessions.delete("sesn_011CZxAbc123Def456");

// Archive a session
await client.beta.sessions.archive("sesn_011CZxAbc123Def456");
```---

## MCP 服务器集成```typescript
// Agent declares MCP server (no auth here — auth goes in a vault)
const agent = await client.beta.agents.create({
  name: "MCP Agent",
  model: "claude-opus-4-8",
  mcp_servers: [
    { type: "url", name: "my-tools", url: "https://my-mcp-server.example.com/sse" },
  ],
  tools: [
    { type: "agent_toolset_20260401", default_config: { enabled: true } },
    { type: "mcp_toolset", mcp_server_name: "my-tools" },
  ],
});

// Session attaches vault(s) containing credentials for those MCP server URLs
const session = await client.beta.sessions.create({
  agent: agent.id,
  environment_id: environment.id,
  vault_ids: [vault.id],
});
```请参阅 `shared/managed-agents-tools.md` §Vaults 以创建保管库并添加凭据。
</doc>

## 何时使用 WebFetch

在以下情况下使用 WebFetch 获取 get 最新文档：

- 用户询问 "latest" 或 "current" 信息
- 缓存数据似乎不正确
- 用户询问此处未涵盖的功能

实时文档 URL 位于 `shared/live-sources.md` 中。

## 常见陷阱

- 将文件或内容传递到 API 时不要截断输入。如果内容太长而无法放入上下文窗口，请通知用户并讨论选项（分块、摘要等），而不是默默地截断。
- **Opus 4.8 / 4.7 思考：** 仅自适应。 `thinking: {type: "enabled", budget_tokens: N}` 返回 400 — `budget_tokens` 已完全删除（以及 `temperature`、`top_p`、`top_k`）。使用 `thinking: {type: "adaptive"}`。 Opus 4.8 从 4.7 继承了这个表面，没有新的重大变化。
- **Opus 4.6 / Sonnet 4.6 思考：** 使用 `thinking: {type: "adaptive"}` — 不要将 `budget_tokens` 用于新的 4.6 代码（在 Opus 4.6 和 Sonnet 4.6 上已弃用；要逐步迁移现有代码，请参阅 `shared/model-migration.md` 中的过渡逃生舱口 —请注意，此例外情况不适用于 Opus 4.7 或 4.8）。对于较旧的型号，`budget_tokens` 必须小于 `max_tokens`（至少 1024）。如果 get 错误，则会抛出错误。
- **4.6/4.7/4.8 系列预填充已删除：** 助理消息预填充（最后一个助理轮预填充）在 Opus 4.6、Opus 4.7、Opus 4.8 和 Sonnet 4.6 上返回 400 错误。使用结构化输出 (`output_config.format`) 或系统提示指令来控制响应格式。
- **编辑前确认迁移范围：**当用户要求将代码迁移到较新的 Claude 模型而不命名特定文件、目录或文件列表时，**询问首先应用哪个范围** — 整个工作目录、特定子目录或特定文件集。在用户确认之前不要开始编辑。像“迁移我的代码库”、“将我的项目移动到 X”、“升级到 Sonnet 4.6”或简单的“迁移到 Opus 4.8”这样的命令性措辞**仍然不明确**——它们告诉你要做什么，但不告诉你在哪里，所以要问。仅当提示指定确切文件、特定目录或显式文件列表时（“迁移 `app.py`”、“迁移 `services/` 下的所有内容”、“更新 `a.py` 和 `b.py`”），才继续而不询问。请参阅 `shared/model-migration.md` 步骤 0。
- **`max_tokens` 默认值：** 不要低估 `max_tokens` — 达到上限会截断输出，需要重试。对于非流式请求，默认为 `~16000`（在 SDK HTTP 超时下保留响应）。对于流请求，默认为 `~64000`（超时不是问题，因此请给模型空间）。仅当您有硬性原因时才降低：分类 (`~256`)、成本上限、故意短输出或用于缓存预热的 **`max_tokens: 0`**（请参阅 `shared/prompt-caching.md` → 预热）。
- **128K 输出令牌：** Opus 4.6、Opus 4.7 和 Opus 4.8 支持高达 128K `max_tokens`，但 SDK 需要对如此大的值进行流式传输，以避免 HTTP 超时。将 `.stream()` 与 `.get_final_message()` / `.finalMessage()` 一起使用。
- **工具调用 JSON 解析（4.6/4.7/4.8 系列）：** Opus 4.6、Opus 4.7、Opus 4.8 和 Sonnet 4.6 可能会在工具调用 `input` 字段中产生不同的 JSON 字符串转义（例如，Unicode 或正斜杠转义）。始终使用 `json.loads()` / `JSON.parse()` 解析工具输入 — 切勿对序列化输入进行原始字符串匹配。
- **结构化输出（所有型号）：** 使用 `output_config: {format: {...}}` 而不是 `messages.create()` 上已弃用的 `output_format` 参数。这是一般的 API 更改，不是 4.6 特有的。
- **不要重新实现 SDK 功能：** SDK 提供高级帮助程序 - 使用它们而不是从头开始构建。具体来说：使用 `stream.finalMessage()` 而不是将 `.on()` 事件包装在 `new Promise()` 中；使用类型化异常类（`Anthropic.RateLimitError` 等）而不是字符串匹配的错误消息；使用 SDK 类型（`Anthropic.MessageParam`、`Anthropic.Tool`、`Anthropic.Message` 等）而不是重新定义等效接口。
- **不要为 SDK 数据结构定义自定义类型：** SDK 导出所有 API 对象的类型。使用 `Anthropic.MessageParam` 表示消息，使用 `Anthropic.Tool` 表示工具定义，使用 `Anthropic.ToolUseBlock` / `Anthropic.ToolResultBlockParam` 表示工具结果，使用 `Anthropic.Message` 表示响应。定义您自己的 `interface ChatMessage { role: string; content: unknown }` 会重复 SDK 已提供的内容，并且会失去类型安全性。
- **报告和文档输出：** 对于生成报告、文档或可视化的任务，代码执行沙箱具有 `python-docx`、`python-pptx`、`matplotlib`、`pillow` 和 `pypdf`预安装。克劳德可以生成格式化文件（DOCX、PDF、图表）并通过文件 API 返回它们 - 考虑将其用于 "report" 或 "document" 类型请求，而不是纯标准输出文本。