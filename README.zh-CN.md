<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: README.md -->
<!-- source-sha256: 8e96d926672570a879f233fd496afd411b9fe8c2e7304a2d63812fff6d9c8e35 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

> **正如华盛顿 Post 中所见：** [查看人工智能背后的隐藏规则。然后用它们重写这篇文章。](https://wapo.st/49t4gSb)（2026年5月11日）
# 系统提示泄漏
此存储库的目的是记录所有 AI 聊天机器人（Claude、ChatGPT、Gemini 等）的系统提示指令。

<img alt="ChatGPT leaking its system prompt after being asked to repeat all of the above" src="https://github.com/user-attachments/assets/0037a6c5-2ae4-4d34-8be0-0d679773172b" />

[![GitHub 每周浏览量](https://raw.githubusercontent.com/asgeirtj/system_prompts_leaks/traffic/traffic-system_prompts_leaks/views_per_week.svg)](https://github.com/asgeirtj/system_prompts_leaks)
![上次提交](https://img.shields.io/github/last-commit/asgeirtj/system_prompts_leaks?style=flat)
[![欢迎 PR](https://img.shields.io/badge/PRs-welcome-brightgreen)](http://makeapullrequest.com)

> 🆕 **[差异：Claude Opus 4.8 → Claude Fable 5](https://www.diffchecker.com/QJn9jFNk/)** — 准确查看 Anthropic 最新模型的 claude.ai 系统提示中发生的变化





## 最近更新

|什么 |日期 |链接 |
|------|------|------|
| **适用于 macOS 的 GitHub Copilot（应用程序）** | 2026 年 6 月 18 日 | [系统提示](Microsoft/copilot-macos-app.md) |
| **克劳德设计（完整的内置技能）** | 2026 年 6 月 18 日 | [系统提示](Anthropic/claude-design.md) |
| **GPT-5.5 Codex（完整提示）** | 2026 年 6 月 18 日 | [系统提示](OpenAI/Codex/gpt-5.5.md) |
| **克劳德寓言5** | 2026 年 6 月 9 日 | [系统提示](Anthropic/claude-fable-5.md) · [Diff vs Opus 4.8](https://www.diffchecker.com/QJn9jFNk/) |
| **克劳德作品 4.8** | 2026 年 6 月 9 日 | [系统提示](Anthropic/claude-opus-4.8.md) · [官方](Anthropic/Official/2026-05-28-claude-opus-4.8.md) |
| **Claude Code Glob 和 Grep 工具** | 2026 年 6 月 9 日 | [Glob](Anthropic/Claude%20Code/glob-tool.md) · [Grep](Anthropic/Claude%20Code/grep-tool.md) |
| **克劳德·代码（作品 4.8）** | 2026 年 5 月 28 日 | [系统提示](Anthropic/Claude%20Code/claude-code-opus-4.8.md) |
| **克劳德代码与合作** | 2026 年 5 月 28 日 | [克劳德代码](Anthropic/Claude%20Code/claude-code-opus-4.6.md) · [Cowork](Anthropic/claude-cowork.md) · [Cowork Dispatch](Anthropic/claude-cowork-dispatch.md) |
| **GPT-5.5** | 2026 年 5 月 24 日 | [思考](OpenAI/gpt-5.5-thinking.md) · [即时](OpenAI/gpt-5.5-instant.md) · [API](OpenAI/gpt-5.5-api.md) · [Pro API](OpenAI/gpt-5.5-pro-api.md) |
| **困惑计算机** | 2026 年 5 月 21 日 | [系统提示](Perplexity/perplexity-computer.md) |
| **VS Code Copilot 代理** | 2026 年 5 月 21 日 | [系统提示](Microsoft/vscode-copilot-agent.md) |
| **码头工人戈登人工智能** | 2026 年 5 月 21 日 | [系统提示](Misc/docker-gordon-ai.md) |
| **双子座 3.5 闪存** | 2026 年 5 月 20 日 | [系统提示](Google/gemini-3.5-flash.md) · [AI Studio](Google/gemini-3.5-flash-ai-studio.md) · [工具](Google/gemini-3.5-flash-tools.json) |
| **反重力 CLI** | 2026 年 5 月 20 日 | [系统提示](Google/反重力-cli.md) |
| **Zed 人工智能** | 2026 年 5 月 16 日 | [系统提示](Misc/zed.md) |
| **格洛克专家** | 2026 年 5 月 11 日 | [系统提示](xAI/grok-expert.md) |

---
![人择](https://shieldcn.dev/badge/Anthropic-D97757.svg?logo=anthropic&logoColor=fff&variant=secondary&mode=light)

## 人类 — 克劳德

|型号|提示|
|--------|--------|
| **克劳德寓言5** | [**系统提示**](Anthropic/claude-fable-5.md) |
| **克劳德作品 4.8** | [**系统提示**](Anthropic/claude-opus-4.8.md) |
| **克劳德·代码（作品 4.8）** | [**系统提示**](Anthropic/Claude%20Code/claude-code-opus-4.8.md) |
| **克劳德作品 4.7** | [**系统提示**](Anthropic/claude-opus-4.7.md) |
| **克劳德·代码（作品 4.6）** | [**系统提示**](Anthropic/Claude%20Code/claude-code-opus-4.6.md) |
| **克劳德作品 4.6** | [**系统提示**](Anthropic/claude-opus-4.6.md) |
| **克劳德十四行诗 4.6** | [**系统提示**](Anthropic/claude-sonnet-4.6.md) |
|克劳德.ai | [人智提醒](人智/anthropic_reminders.md) |

<details><summary>集成、官方提示和旧版本</summary>

| | |
|--|--|
|集成 | [Cowork](Anthropic/claude-cowork.md) · [Cowork 调度](Anthropic/claude-cowork-dispatch.md) · [桌面代码](Anthropic/claude-desktop-code.md) · [设计](Anthropic/claude-design.md) · [移动 iOS](Anthropic/claude-mobile-ios.md) · [在Chrome](Anthropic/claude-in-chrome.md) · [对于 Excel](Anthropic/claude-for-excel.md) · [对于 Word](Anthropic/claude-for-word.md) · [在 PowerPoint 中](Anthropic/claude-in-powerpoint.md) · [默认样式](Anthropic/default-styles.md) |
|克劳德·代码额外资料 | [全局工具](Anthropic/Claude%20Code/glob-tool.md) · [Grep 工具](Anthropic/Claude%20Code/grep-tool.md) · [延迟工具](Anthropic/Claude%20Code/deferred-tools.md) · [文档助手](Anthropic/Claude%20Code/claude-code-docs-assistant.md) · [捆绑技能](Anthropic/Claude%20Code/bundled-skills/) |
|已发布（发布日期为 `claude_behavior`，未更新）| [作品 4.8](人类/官方/2026-05-28-claude-opus-4.8.md) · [作品 4.7](人类/官方/2026-04-16-claude-opus-4.7.md) · [作品4.6](Anthropic/Official/2026-02-05-claude-opus-4.6.md) · [Sonnet 4.6](Anthropic/Official/2026-02-17-claude-sonnet-4.6.md) · [所有版本](Anthropic/Official/) |
|无需工具| [作品4.6](Anthropic/claude-opus-4.6-no-tools.md) · [十四行诗 4.6](Anthropic/claude-sonnet-4.6-no-tools.md) |
|原始提示| [Opus 4.6](Anthropic/raw/claude-opus-4.6-raw.md) · [Opus 4.6 (无工具)](Anthropic/raw/claude-opus-4.6-no-tools-raw.md) · [Sonnet 4.6](Anthropic/raw/claude-sonnet-4.6-raw.md) · [Sonnet 4.6 (无)工具)](Anthropic/raw/claude-sonnet-4.6-no-tools-raw.md) |
|可视化 | [可视化](Anthropic/visualize.md) |
|作品 4.5 | [系统提示](Anthropic/old/claude-opus-4.5.md) |
|十四行诗 4.5 | [系统提示](Anthropic/old/claude-4.5-sonnet.md) |
|十四行诗 4 | [系统提示](Anthropic/old/claude-sonnet-4.md) |
| Opus 4.1 思考 | [系统提示](Anthropic/old/claude-4.1-opus-thinking.md) |
|十四行诗 3.7 | [系统提示](Anthropic/old/claude-3.7-sonnet.md) · [附带工具](Anthropic/old/claude-3.7-sonnet-w-tools.md) · [完整w/工具](Anthropic/old/claude-3.7-full-system-message-with-all-tools.md) · [人类可读](Anthropic/old/claude-3.7-sonnet-full-system-message- humansensitive.md) |

</details>

![OpenAI](https://shieldcn.dev/badge/OpenAI-412991.svg?logo=ri%3ASiOpenai&variant=secondary&mode=light)

## OpenAI — ChatGPT

|型号|提示|
|--------|--------|
| **GPT-5.5** | [**思考**](OpenAI/gpt-5.5-thinking.md) · [**即时**](OpenAI/gpt-5.5-instant.md) · [API](OpenAI/gpt-5.5-api.md) · [Pro API](OpenAI/gpt-5.5-pro-api.md) · [**Codex**](OpenAI/Codex/gpt-5.5.md) · [友好](OpenAI/Codex/personality_friendly_gpt-5.5.md) · [实用](OpenAI/Codex/personality_pragmatic_gpt-5.5.md) |
| **GPT-5.4** | [**API**](OpenAI/gpt-5.4-api.md) · [**Thinking**](OpenAI/gpt-5.4-thinking.md) · [**Codex**](OpenAI/Codex/gpt-5.4.md) · [Codex Mini](OpenAI/Codex/gpt-5.4-mini.md) |
| **GPT-5.3** | [**Codex**](OpenAI/Codex/gpt-5.3-codex.md) · [Spark](OpenAI/Codex/gpt-5.3-codex-spark.md) · [Codex API](OpenAI/gpt-5.3-codex-api.md) · [聊天API](OpenAI/gpt-5.3-chat-api.md) · [即时](OpenAI/gpt-5.3-instant.md) |
| **法典 CLI** | [按模型提示](OpenAI/Codex/) · [Spark](OpenAI/Codex/gpt-5.3-codex-spark.md) · [计划模式](OpenAI/Codex/plan_mode.md) · [角色](OpenAI/Codex/personality_friendly.md) · [自动审查](OpenAI/Codex/codex-auto-review.md) |
| **工具** | [网页搜索](OpenAI/tool-web-search.md) · [深度研究](OpenAI/tool-deep-research.md) · [Python](OpenAI/tool-python.md) · [Python代码](OpenAI/tool-python-code.md) · [画布](OpenAI/tool-canvas-canmore.md) · [图像生成](OpenAI/tool-create-image-image_gen.md) · [内存](OpenAI/tool-memory-bio.md) · [高级[内存](OpenAI/tool-advanced-memory.md) · [文件搜索](OpenAI/tool-file_search.md) |
| **政策**| [图像安全](OpenAI/prompt-image-safety-policies.md) · [自动化上下文](OpenAI/prompt-automation-context.md) |

<details><summary>旧型号和变体</summary>

| | |
|--|--|
| GPT-5.2 | [迷你（免费）](OpenAI/gpt-5.2-mini-free-account.md) · [思考](OpenAI/gpt-5.2-thinking.md) · [Codex](OpenAI/Codex/gpt-5.2-codex.md) |
| o4-迷你 | [系统提示](OpenAI/o4-mini.md) · [高](OpenAI/o4-mini-high.md) |
| o3 | [系统提示](OpenAI/o3.md) |
| ChatGPT 图集 | [系统提示](OpenAI/chatgpt-atlas.md) |
| GPT-5.1 人物 | [默认](OpenAI/gpt-5.1-default.md) · [友好](OpenAI/gpt-5.1-friend.md) · [专业](OpenAI/gpt-5.1-professional.md) · [坦率](OpenAI/gpt-5.1-candid.md) · [愤世嫉俗](OpenAI/gpt-5.1-cynical.md) · [高效](OpenAI/gpt-5.1-efficient.md) · [书呆子](OpenAI/gpt-5.1-nerdy.md) · [古怪](OpenAI/gpt-5.1-quirky.md) |
| GPT-5 | [代理模式](OpenAI/chatgpt-gpt-5-agent-mode.md) · [思考](OpenAI/gpt-5-thinking.md) · [愤世嫉俗](OpenAI/gpt-5-cynic-personality.md) · [监听器](OpenAI/gpt-5-listener-personality.md) · [书呆子](OpenAI/gpt-5-nerdy-personality.md) · [机器人](OpenAI/gpt-5-robot-personality.md) · [Codex](OpenAI/Codex/gpt-5-codex.md) · [Codex Mini](OpenAI/Codex/gpt-5-codex-mini.md) |
| GPT-4.5 | [系统提示](OpenAI/gpt-4.5.md) |
| GPT-4.1 | [完整](OpenAI/gpt-4.1.md) · [迷你](OpenAI/gpt-4.1-mini.md) |
| GPT-4o | [系统提示](OpenAI/gpt-4o.md) · [WhatsApp](OpenAI/gpt-4o-whatsapp.md) · [高级语音](OpenAI/gpt-4o-advanced-voice-mode.md) · [传统语音](OpenAI/gpt-4o-legacy-voice-mode.md) |
|星期一 GPT | [系统提示](OpenAI/monday-gpt.md) |
| GPT-4o新个性| [系统提示](OpenAI/4o-2025-09-03-new-personality.md) |
|学习学习| [系统提示](OpenAI/study-and-learn.md) |
|图像安全政策 | [系统提示](OpenAI/image-safety-policies.md) |
| API 变体 | [GPT-5推理（高）](OpenAI/API/gpt-5-reasoning-effort-high-api.md) · [o3高](OpenAI/API/o3-高-api.md) · [o3 中](OpenAI/API/o3-中-api.md) · [o3低](OpenAI/API/o3-low-api.md) · [o4-mini 高](OpenAI/API/o4-mini-high.md) · [o4-mini med](OpenAI/API/o4-mini-medium-api.md) · [o4-mini low](OpenAI/API/o4-mini-low-api.md) |
|老款o4-mini | [系统提示](OpenAI/Old/chatgpt.com-o4-mini.md) |
|法典（较旧）| [GPT-5](OpenAI/Codex/gpt-5.md) · [GPT-5.1](OpenAI/Codex/gpt-5.1.md) · [GPT-5.1 Codex](OpenAI/Codex/gpt-5.1-codex.md) · [GPT-5.1 Mini](OpenAI/Codex/gpt-5.1-codex-mini.md) · [GPT-5.1 Max](OpenAI/Codex/gpt-5.1-codex-max.md) · [GPT-5.2](OpenAI/Codex/gpt-5.2.md) · [5.2友好](OpenAI/Codex/personality_friendly_gpt-5.2-codex.md) · [5.2 实用](OpenAI/Codex/personality_pragmatic_gpt-5.2-codex.md) |

</details>

![谷歌双子座](https://shieldcn.dev/badge/Google%20Gemini-8E75B2.svg?logo=googlegemini&logoColor=fff&variant=secondary&mode=light)

## 谷歌 — 双子座

|型号|提示|
|--------|--------|
| **双子座 3.5 闪存** | [**系统提示**](Google/gemini-3.5-flash.md) · [AI Studio](Google/gemini-3.5-flash-ai-studio.md) · [工具](Google/gemini-3.5-flash-tools.json) |
| **双子座 3.1 专业版** | [**系统提示**](Google/gemini-3.1-pro.md) · [API](Google/gemini-3.1-pro-api.md) |
|双子座 CLI | [系统提示](Google/gemini-cli.md) |
|反重力 CLI | [系统提示](Google/反重力-cli.md) |
|朱尔斯 | [系统提示](Google/jules.md) |

<details><summary>旧型号和变体</summary>

| | |
|--|--|
|双子座3 | [Flash](Google/gemini-3-flash.md) · [Pro](Google/gemini-3-pro.md) |
|双子座扩散 | [系统提示](Google/gemini-diffusion.md) |
|谷歌搜索AI模式| [系统提示](Google/google-search-ai-mode.md) |
|双子座 YouTube | [系统提示](Google/gemini-youtube.md) |
| Chrome 中的双子座 | [系统提示](Google/gemini-in-chrome.md) |
|双子座工作空间 | [系统提示](Google/gemini-workspace.md) |
|双子座2.5 Pro | [API](Google/gemini-2.5-pro-api.md) · [Webapp](Google/gemini-2.5-pro-webapp.md) · [引导学习](Google/gemini-2.5-pro-guided-learning.md) |
|双子座2.5闪存| [图片预览](Google/gemini-2.5-flash-image-preview.md) |
|双子座2.0闪存| [Web应用程序](Google/gemini-2.0-flash-webapp.md) |
| AI Studio 构建 | [系统提示](Google/ai-studio-build.md) |
|纳米/香蕉2 | [系统提示](Google/nano-banana-2-api.md) |
|笔记本LM | [聊天](Google/notebooklm-chat.md) |

</details>

## xAI — Grok

|型号|提示|
|--------|--------|
| **Grok 构建** | [**系统提示符（CLI 代理）**](xAI/grok-build.md) |
| **Grok 4.3 测试版** | [系统提示](xAI/grok-4.3-beta.md) |
| **格洛克 4.2** | [**系统提示**](xAI/grok-4.2.md) |
| Grok 专家 | [系统提示](xAI/grok-expert.md) |

<details><summary>旧版本</summary>

| | |
|--|--|
| Grok 4.1 测试版 | [系统提示](xAI/grok-4.1-beta.md) |
|格洛克 4 | [系统提示](xAI/grok-4.md) · [API](xAI/grok-api.md) |
|格洛克 3 | [系统提示](xAI/grok-3.md) |
|格罗克帐户| [系统提示](xAI/grok-account.md) |
| Grok 角色 | [角色](xAI/grok-personas.md) |
|安全须知| [Post-new](xAI/grok.com-post-new-safety-instructions.md) |

</details>

## 困惑

|型号|提示|
|--------|--------|
| **困惑计算机** |[**系统提示**](Perplexity/perplexity-computer.md) |
|彗星浏览器 | [系统提示](Perplexity/comet-browser-assistant.md) |
|语音助手| [系统提示](Perplexity/voice-assistant.md) |

## 微软 — 副驾驶

|产品 |提示|
|---------|--------|
| GitHub 副驾驶 | [系统提示](Microsoft/github-copilot.md) |
| VS Code 副驾驶代理 | [系统提示](Microsoft/vscode-copilot-agent.md) |
|副驾驶 CLI | [系统提示](Microsoft/copilot-cli.md) |
| **macOS 版副驾驶（应用程序）** | [**系统提示**](Microsoft/copilot-macos-app.md) |
| Word 中的副驾驶 | [系统提示](Microsoft/copilot-in-microsoft-word.md) |

## 光标

|产品 |提示|
|---------|--------|
|光标| [系统提示](Cursor/cursor.md) |

## 元数据

|产品 |提示|
|---------|--------|
|元人工智能 | [系统提示](Meta/meta-ai.md) |

## 米斯特拉尔

|产品 |提示|
|---------|--------|
|乐聊 | [系统提示](Mistral/le-chat.md) |

## 概念

|产品 |提示|
|---------|--------|
|概念人工智能 | [系统提示](Notion/notion-ai.md) |

## 奎文

|产品 |提示|
|---------|--------|
| Qwen 3.6 Plus | [系统提示](Qwen/qwen-3.6-plus.md) |

## 其他

|产品 |提示|
|---------|--------|
|放大器代码（源图）| [系统提示](Misc/amp-code.md) |
| Docker Gordon 人工智能 | [系统提示](Misc/docker-gordon-ai.md) |
| ElevenLabs 语音代理 | [系统提示](Misc/elevenlabs-voice-agent.md) |
|开放代码 | [系统提示](Misc/opencode.md) |
| Reddit 答案 | [系统提示](Misc/reddit-answers.md) |
|扭曲 2.0 代理 | [系统提示](Misc/warp-2.0-agent.md) |
|泽德人工智能 | [系统提示](Misc/zed.md) |

<details><summary>更多产品</summary>

| | |
|--|--|
|勇敢寻找| [系统提示](Misc/brave-search.md) |
|角色AI | [系统提示](Misc/character-ai.md) |
|授予| [系统提示](Misc/confer.md) |
|费卢浏览器 | [系统提示](Misc/fellou-browser.md) |
|小发明人工智能 | [系统提示](Misc/gizmo-ai.md) |
|爱马仕 | [系统提示](Misc/hermes.md) |
|梧桐人工智能| [系统提示](Misc/indus-ai.md) |
|卡吉助理| [系统提示](Misc/kagi-assistant.md) |
|迷你最大 M2.5 | [系统提示](Misc/minimax-m2.5.md) |
|质子 Lumo AI | [系统提示](Misc/proton-lumo-ai.md) |
|光线投射人工智能 | [系统提示](Misc/raycast-ai.md) |
|芝麻人工智能玛雅| [系统提示](Misc/sesame-ai-maya.md) |
| t3.聊天 | [系统提示](Misc/t3.chat.md) |
| t3 代码 | [系统提示](Misc/t3-code.md) |

</details>

---


## 联系方式

![a](https://badgen.net/email/asgeirtj/gmail.com)[![X](https://img.shields.io/badge/@asgeirtj-black?logo=x&logoColor=white)](https://x.com/asgeirtj)


## 成长

[![明星历史图](https://api.star-history.com/svg?repos=asgeirtj/system_prompts_leaks&type=Date)](https://www.star-history.com/#asgeirtj/system_prompts_leaks&Date)

<p align="center">
<a href="https://trendshift.io/repositories/14577" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14577" alt="asgeirtj%2Fsystem_prompts_leaks | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
 <a href="https://www.star-history.com/asgeirtj/system_prompts_leaks">
  <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/badge?repo=asgeirtj/system_prompts_leaks&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/badge?repo=asgeirtj/system_prompts_leaks" />
   <img alt="Star History Rank" src="https://api.star-history.com/badge?repo=asgeirtj/system_prompts_leaks" />
  </picture>
 </a>
</p>

<img alt="Claude confirming an extracted system prompt is authentic" src="https://github.com/user-attachments/assets/444e3fcc-9374-4964-afd3-069222713dc0" />