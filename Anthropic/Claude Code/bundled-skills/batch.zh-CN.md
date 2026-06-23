<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/batch.md -->
<!-- source-sha256: 3c2cbfcfa465e88caf6b4854b2cea6d88cd485e62e3f102d9911cacd228676c9 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: batch
description: Orchestrate a large, parallelizable change across the codebase by decomposing it into independent units and spawning parallel worker agents in isolated worktrees.
---
# Batch：并行工作编排

您正在整个代码库中协调一个大型的、可并行的更改。

## 用户说明

$参数

## 第一阶段：研究与计划（计划模式）

现在调用`EnterPlanMode`工具进入计划模式，然后：

1. **了解范围。** 启动一个或多个子代理（在前台 - 您需要他们的结果）来深入研究该指令所涉及的内容。查找所有需要更改的文件、模式和调用站点。了解现有约定，以便迁移保持一致。

2. **分解为独立的单元。** 将工作分解为 5-30 个独立的单元。每个单位必须：
   - 可在隔离的 git 工作树中独立实现（不与兄弟单元共享状态）
   - 可自行合并，无需先依赖其他单位的 PR 着陆
   - 大小大致一致（分割大单元，合并小单元）

   将计数扩展到实际工作：很少的文件 → 接近 5；数百个文件 → 接近 30 个。与任意文件列表相比，更喜欢按目录或按模块切片。

3. **确定 e2e 测试方案。** 弄清楚工作人员如何验证其更改是否真正端到端地工作 - 而不仅仅是单元测试通过。寻找：
   - `claude-in-chrome` 技能或浏览器自动化工具（对于 UI 更改：单击受影响的流程，对结果进行屏幕截图）
   - `tmux` 或 CLI 验证者技能（对于 CLI 更改：以交互方式启动应用程序，练习更改后的行为）
   - 开发服务器+curl模式（对于API更改：启动服务器，命中受影响的端点）
   - 工作人员可以运行的现有 e2e/集成测试套件

   如果找不到具体的 e2e 路径，请使用 `AskUserQuestion` 工具询问用户如何端到端验证此更改。根据您发现的内容提供 2-3 个特定选项（例如，“通过 chrome 扩展进行屏幕截图”、“运行 `bun run dev` 并卷曲端点”、“无 e2e — 单元测试就足够了”）。不要跳过这一点——工作人员不能自己询问用户。

   将配方编写为工人可以自主执行的一组简短而具体的步骤。包括任何设置（启动开发服务器，首先构建）和要验证的确切命令/交互。

4. **编写计划。** 在您的计划文件中，包括：
   - 您在研究过程中发现的内容的摘要
   - 工作单元的编号列表 - 每个工作单元：一个简短的标题、它涵盖的文件/目录列表以及更改的一行描述
   - e2e 测试配方（或“跳过 e2e 因为……”，如果用户选择）
   - 您将向每个代理提供的确切工作指示（共享模板）

5. 打电话`ExitPlanMode` 提交计划供批准。

## 第 2 阶段：生成工人（计划批准后）

计划获得批准后，使用 `Agent` 工具为每个工作单元生成一个后台代理。 **所有代理必须使用 `isolation: "worktree"` 和 `run_in_background: true`。** 在单个消息块中全部启动它们，以便它们并行运行。

对于每个代理，提示必须是完全独立的。包括：
- 总体目标（用户的指示）
- 该单元的具体任务（标题、文件列表、更改描述 - 从您的计划中逐字复制）
- 您发现工作人员需要遵循的任何代码库约定
- 您计划中的 e2e 测试配方（或“跳过 e2e 因为……”）
- 以下工人指示，逐字复制：```
After you finish implementing the change:
1. **Code review** — Invoke the `Skill` tool with `skill: "code-review"` to find correctness bugs (it reports findings; it does not edit code). Fix any findings it surfaces before continuing.
2. **Run unit tests** — Run the project's test suite (check for package.json scripts, Makefile targets, or common commands like `npm test`, `bun test`, `pytest`, `go test`). If tests fail, fix them.
3. **Test end-to-end** — Follow the e2e test recipe from the coordinator's prompt (below). If the recipe says to skip e2e for this unit, skip it.
4. **Commit and push** — Commit all changes with a clear message, push the branch, and create a PR with `gh pr create`. Use a descriptive title. If `gh` is not available or the push fails, note it in your final message.
5. **Report** — End with a single line: `PR: <url>` so the coordinator can track it. If no PR was created, end with `PR: none — <reason>`.
```除非适合更具体的代理类型，否则请使用 `subagent_type: "general-purpose"`。

## 第 3 阶段：跟踪进度

启动所有worker后，渲染一个初始状态表：

| ＃|单位|状态 |公关 |
|---|------|--------|----|
| 1 | <title> |跑步| — |
| 2 | <title> |跑步| — |

当后台代理完成通知到达时，从每个代理的结果中解析 `PR: <url>` 行，并使用更新的状态 (`done` / `failed`) 和 PR 链接重新呈现表。为任何未产生 PR 的代理保留简短的失败记录。

当所有代理都报告后，呈现最终表格和一行摘要（例如，“22/24 单位作为 PR 登陆”）。