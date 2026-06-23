<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/review.md -->
<!-- source-sha256: 5700f30d3f06706ee56c099adceec222fef26dbcf82817ff604962634e246b2e -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/PRD asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
---
# 回顾

对 `HEAD` 和用户提供的固定点之间的差异进行两轴检查：

- **标准** — 代码是否符合此存储库记录的编码标准？
- **规范** — 代码是否忠实地实现了原始问题/PRD/规范？

两个轴都作为**并行子代理**运行，因此它们不会污染彼此的上下文，然后此技能会聚合他们的发现。

问题跟踪器应该已提供给您 - 如果 `docs/agents/issue-tracker.md` 丢失，请运行 `/setup-matt-pocock-skills`。

## 流程

### 1. 固定固定点

用户所说的都是固定点——提交 SHA、分支名称、标签、`main`、`HEAD~5` 等。通过它。如果他们没有指定，请询问：“根据什么进行审查 - 分支、提交还是 `main`？”在获得之前不要继续。

捕获一次 diff 命令：`git diff <fixed-point>...HEAD`（三点，因此比较是针对合并基础的）。另请注意通过 `git log <fixed-point>..HEAD --oneline` 提交的列表。

### 2. 确定规范来源

按以下顺序查找原始规范：

1. 提交消息中的问题引用（`#123`、`Closes #45`、GitLab `!67` 等） — 通过 `docs/agents/issue-tracker.md` 中的工作流程获取。
2. 用户作为参数传递的路径。
3. `docs/`、`specs/` 或 `.scratch/` 下与分支名称或功能匹配的 PRD/spec 文件。
4. 如果没有找到任何内容，请询问用户规格在哪里。如果他们说没有，**规格**子代理将跳过并报告“没有可用的规格”。

### 3. 确定标准来源

存储库中记录如何编写代码的任何内容。常见地点：

- `CLAUDE.md`、`AGENTS.md`
- `CONTRIBUTING.md`
- `CONTEXT.md`、`CONTEXT-MAP.md`、每个上下文 `CONTEXT.md` 文件
- `docs/adr/`（架构决策是标准）
- `.editorconfig`、`eslint.config.*`、`biome.json`、`prettier.config.*`、`tsconfig.json`（机器强制标准 - 记下它们，但不要重新检查工具已检查的内容）
- 任何 `STYLE.md`、`STANDARDS.md`、`STYLEGUIDE.md` 或存储库根目录下或 `docs/` 下的类似内容

收集文件列表。 **标准**子代理将阅读它们。

### 4. 并行生成两个子代理

使用两个 `Agent` 工具调用发送一条消息。两者均使用 `general-purpose` 子代理。

**标准子代理提示** — 包括：

- 完整的 diff 命令和提交列表。
- 您在步骤 3 中找到的标准源文件列表。
- 简介：“阅读标准文档。然后阅读差异。报告 - 每个文件/块（如果相关） - 差异违反记录的每个地方标准。引用标准（文件+规则）。区分严重违规行为和判断要求。跳过工具强制执行的任何内容。 400字以内。”

**规格子代理提示** — 包括：

- diff 命令和提交列表。
- 规范的路径或获取的内容。
- 简介：“阅读规范。然后读取差异。报告：(a) 规范要求的要求缺失或不完整； (b) diff 中未要求的行为（范围蔓延）； (c) 看似已实施但实施看起来有问题的要求。引用每个发现的规格行。 400字以内。”

如果缺少规格，请跳过规格子代理并在最终报告中注明这一点。

### 5. 聚合

在 `## Standards` 和 `## Spec` 标题下逐字或稍加清理地呈现两份报告。 **不要**合并或重新排列结果 - 两个轴故意分开，以便用户可以独立地看到它们。

以一行摘要结束：每个轴的总发现结果，以及标记的最糟糕的单个问题（如果有）。

## 为什么有两个轴

更改可以通过一个轴而使另一个轴失败：

- 遵循每个标准但实现了错误的代码 → **标准通过，规范失败。**
- 代码完全按照问题要求执行，但违反了项目约定 → **规范通过，标准失败。**

单独报告它们可以防止一个轴掩盖另一个轴。