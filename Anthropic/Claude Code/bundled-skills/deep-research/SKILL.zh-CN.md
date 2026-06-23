<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/deep-research/SKILL.md -->
<!-- source-sha256: a1987c4de027bc6c39b66b04aebaab754e5b5a587b814727e21fb5394358ddf4 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: deep-research
description: Deep research harness — fan-out web searches, fetch sources, adversarially verify claims, synthesize a cited report.
when_to_use: When the user wants a deep, multi-source, fact-checked research report on any topic. BEFORE invoking, check if the question is specific enough to research directly — if underspecified (e.g., "what car to buy" without budget/use-case/region), ask 2-3 clarifying questions to narrow scope. Then pass the refined question as args, weaving the answers in.
---
运行 "deep-research" 工作流程。

深度研究利用——扇出网络搜索、获取来源、对抗性验证主张、综合引用的报告。

当用户想要关于任何主题的深入、多源、经过事实核查的研究报告时。在调用之前，检查问题是否足够具体以供直接研究 - 如果未指定（例如，“买什么车”而没有预算/用例/区域），请提出 2-3 个澄清问题以缩小范围。然后将经过提炼的问题作为参数传递，将答案编织进去。

阶段：
- 范围：将问题（来自参数）分解为 5 个搜索角度
- 搜索：5 个并行 WebSearch 代理，每个角度一个
- 获取：URL-dedup，获取前 15 个来源，提取可伪造的声明
- 验证：每个主张进行 3 票对抗性验证（需要 2/3 反驳才能杀死）
- 综合：合并语义欺骗、按置信度排名、引用来源

调用：工作流({ name: "deep-research" })

## 工作流程脚本

[脚本/workflow-script.js](脚本/workflow-script.js)