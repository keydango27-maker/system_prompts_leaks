<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/simplify.md -->
<!-- source-sha256: e4f91c409146b7f352528fd097154ed1d2d71bbdbad4b261e6e2e18974dfac8b -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: simplify
description: Review the changed code for reuse, simplification, efficiency, and altitude cleanups, then apply the fixes.
---
`/simplify → 4 cleanup agents in parallel → apply the fixes`

您正在提高更改后的代码的质量，而不是寻找错误。评论
其目的是为了重用、简化、效率和高度问题，然后修复您所需要的
找到。不要寻找正确性错误——这就是 `/code-review` 的用途。

## 阶段 0 — 收集差异

运行 `git diff @{upstream}...HEAD` （或 `git diff main...HEAD` / `git diff HEAD~1`
如果没有上游）到 get 正在审查的统一差异。如果有
未提交的更改，或者范围差异为空，也运行 `git diff HEAD` 并
包括范围内的工作树更改——审查通常在
提交。如果 PR 编号、分支名称或文件路径作为参数传递，
相反，请检查该目标。将此差异视为审核范围。

## 第 1 阶段 — 审查（并行 4 个清理代理）

通过代理工具启动 **4 个独立审查代理**，所有这些都在一个
单个消息，因此它们同时运行。向每个代理传递 diff 和其中之一
下面的四个角。每个都返回其结果 `file`、`line`、
一行 `summary`，以及具体成本（重复的、浪费的或
更难维护）。

### 重复使用

标记重新实现代码库某些内容的新代码
已经有 — Grep 共享/实用模块和与更改相邻的文件，
并命名现有的助手来调用。

### 简化

标记 diff 添加的不必要的复杂性：冗余或可导出状态，
复制粘贴略有变化，深层嵌套，留下死代码。名称
完成相同工作的更简单的形式。

### 效率

标记 diff 引入的浪费工作：冗余计算或重复 I/O，
独立操作按顺序运行，阻止添加到启动或
热路径。说出更便宜的替代方案。

### 海拔高度

检查每个更改是否在正确的深度实施，而不是作为脆弱的
创可贴。共享基础设施上的特殊情况是修复的标志
不够深入——更喜欢概括底层机制而不是添加
特殊情况。

## 第 2 阶段 — 应用修复

等待所有四个代理完成，删除指向相同的结果
线或机构，并直接修复剩余的每一个。跳过任何发现
修复会改变预期的行为，需要远远超出审查范围的更改
diff，或者您判断为误报 - 请注意跳过而不是
与它争论。最后简要总结一下已修复的内容和已修改的内容
跳过（或确认代码已经干净）。