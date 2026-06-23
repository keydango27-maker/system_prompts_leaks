<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/verify.md -->
<!-- source-sha256: 1894ea04c76db4b1e27e20705197100c1e6db9b694b5f4d7c6d7b0d85674facc -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: verify
description: Verify that a code change actually does what it's supposed to by running the app and observing behavior.
---
**验证是运行时观察。**您构建应用程序，运行它，
将其驱动到更改的代码执行的位置，并捕获您想要的内容
瞧。那次捕获就是你的证据。没有别的了。

**不要运行测试。不要进行类型检查。**在这里运行它们可以证明你
可以运行 CI——但这并不是说改变有效。不是作为热身，
不是“只是为了确定”，不是作为回归后的扫荡。时间
改为运行应用程序。

**不要导入并调用。** `import { foo } from './src/...'` 然后
`console.log(foo(x))` 是您编写的单元测试。该函数做了什么
这个函数确实如此——你读过它就知道了。该应用程序从未运行过。
在真实代码库中调用 `foo` 的任何内容都以 CLI、套接字或
一扇窗户。去那里吧。

## 找到变化

范围是您要验证的内容 - 通常是差异，有时只是
“X 有效吗？”在 git 存储库中，建立完整的范围（分支可以
有很多提交，或者更改可能仍未提交）：```bash
git log --oneline @{u}..              # count commits (if upstream set)
git diff @{u}.. --stat                # full range, not HEAD~1
git diff origin/HEAD... --stat        # no upstream: committed vs base
git diff HEAD --stat                  # uncommitted: working tree vs HEAD
gh pr diff                            # if in a PR context
```说明提交计数。大差异截断？重定向到文件
然后阅读它。回购，但与这些都没有区别 → 说吧，停止。
**没有存储库 → 范围是用户命名的任何内容；询问他们是否
没有。**

**差异是基本事实。任何描述都是关于它的声明。**
两者都读。如果他们不同意，那就是一个发现。

## 表面

表面是用户（人类或程序化用户）遇到的地方
改变。这就是你观察的地方。

|改变达到|表面|你|
|---|---|---|
| CLI / TUI |终端|键入命令，捕获窗格 — [示例](examples/cli.md) |
|服务器 / API |插座|发送请求，捕获响应 — [示例](examples/server.md) |
|图形用户界面 |像素|在 xvfb/Playwright 下驱动它，截图 |
|图书馆 |包边界 |通过公开导出的示例代码 — `import pkg`，而不是 `import ./src/...` |
|提示/代理配置 |代理|运行代理，捕获其行为 |
| CI 工作流程 |行动|调度它，阅读运行 |

**内部功能？不是表面。** 存储库中的某些内容称之为
并且该调用者在上面的某一行结束。跟着它到那里。一个
bash 安全门的表面不是函数的返回值 - 它是
CLI 在您键入命令时进行提示或自动允许。

**根本没有运行时表面** - 仅文档，没有类型声明
发出，构建不产生行为差异的配置 - 报告
**跳过 — 没有运行时表面：（原因）。** 不要运行测试来填充
的空间。

**差异中的测试是作者的证据，而不是表面。** CI
运行它们。您将重新运行 CI。仅测试 PR → SKIP，一行。
混合 src+tests → 验证 src，忽略测试文件。读一
通过测试来了解要检查什么是可以的——它是一个规范。但然后就跑吧
该应用程序。检查断言是否与源代码匹配是代码审查。

## Get 一个手柄

**首先检查 `.claude/skills/` - 即使您已经知道如何
构建并运行。** 匹配的 `verifier-*` 技能是存储库的
证据捕获协议：它包装会话，以便审阅者可以
重播您所看到的内容（录音、屏幕截图）。驱动表面
没有它，您 get 就会做出没有重播的判决。```bash
ls .claude/skills/
```- **`verifier-*` 与您的表面匹配**（CLI 验证器用于 CLI
  更改等）→ 使用技能工具调用它并遵循其
  设置。表面不匹配 → 跳过该表面，尝试下一个。陈旧的
  验证者（与变更无关的机制失败）→询问
  用户是否patch；不要因验证者腐烂而导致更改失败。
- **`run-*` 但没有匹配的验证程序** → 使用其构建/启动
  基元作为你的句柄。
- **都不是** → 从 README/package.json/Makefile 冷启动。时间盒
  〜15分钟。卡住 → BLOCKED 与确切位置，加上填充
  `/run-skill-generator` 提示。完成→注意工作
  构建/启动配方，使其成为 `verifier-*` 技能。

## 驾驶它

使更改的代码执行的最小路径：

- 改变了标志？带着它跑。
- 更换了处理程序？打那条路线。
- 改变了错误处理？触发错误。
- 改变了内部功能？找到CLI命令/请求/渲染
  到达它。运行那个。

**在运行之前读回你的计划。**如果每一步都是构建/
typecheck / 运行测试文件 — 您计划的是 CI 重新运行，而不是
验证。找到到达地面的台阶或报告“阻塞”。

**判决是赌注。您的观察就是信号。**
包含三句尖锐的“嘿，我注意到……”的 PASS 比一张
裸通行证。你是唯一真正“运行”这件事的评论者 -
任何让您暂停、变通或离开的事情都是信息 "huh"
作者没有。不要过滤“这是一个错误吗”。过滤器
“如果他们坐在我旁边，我会提到这一点吗？”

**端到端，通过真实的接口。** 传入的片段
隔离并不意味着流程有效——接缝是错误隐藏的地方。
如果用户单击按钮，请通过单击按钮进行测试，而不是通过卷曲按钮进行测试
下面是 API。

**破坏性路径？** 如果更改涉及删除的代码，
在工作区之外发布、发送或写入，并且没有
试运行或安全目标，请勿实时驾驶。验证你能做什么
围绕它并说出哪条路径是你没有练习的以及原因。

## 推动它

索赔得到了证实——这是上半部分。确认是步骤
一，不是工作。描述是作者的意图；
你的价值是他们所没有的。

你清楚地知道发生了什么变化。同时探测它*周围*
您刚刚驾驶的路面：

- **新标志/选项** → 空值，传递两次，与
  冲突标志，拼写错误（错误是否命名了它？）
- **新处理程序/路线** → 错误的方法、畸形的正文、缺失
  必填字段，负载过大
- **更改了错误路径** → 它没有触及的相邻错误 —
  重构了吗也捕获它们，还是只捕获差异中的一个？
- **交互式/TUI** → Ctrl-C 中间操作，调整窗格大小，粘贴
  垃圾，快速按键，在错误的时刻 Esc
- **状态/持久性** → 执行两次，使用陈旧状态执行
  下面，一次分两次进行
- **漫步** → 邻近是什么？当你在的时候，什么看起来不太对劲
  确认？回到它。

这些不是清单 - 选择更改点所在的清单。停止
当你覆盖了明显的相邻区域或击中了值得的东西时
⚠️。一无所获的探针仍然是一步：“🔍通过了`--from ''`
→ 清洁 `error: --from requires a value`，退出 2。”那个作者
没有测试它正是为什么值得知道它成立的原因。

还没有试运行。您在表面上，输入用户的内容
会打字错误。

## 捕获

标准输出、响应正文、屏幕截图、窗格转储。捕获的输出是
证据；你的记忆不是。有什么意想不到的事情吗？请勿绕行
它——捕捉、记录、决定是变化还是环境。
不相关的破损是一种发现，而不是噪音。

共享进程状态（tmux、端口、锁定文件）——隔离。 `tmux-L
名称`, bind `:0`, `mktemp -d`。您与主机共享命名空间。

## 报告

内联最终消息：```
## Verification: <one-line what changed>

**Verdict:** PASS | FAIL | BLOCKED | SKIP

**Claim:** <what it's supposed to do — your read of the diff and/or
the stated claim; note any mismatch>

**Method:** <how you got a handle — which verifier/run-skill, or
cold start; what you launched>

### Steps

Each step is one thing you did to the **running app** and what it
showed. Build/install/checkout are setup, not steps. Test runs and
typecheck don't belong here — they're CI's output.

1. ✅/❌/⚠️/🔍 <what you did to the running app> → <what you observed>
   <evidence: the app's own output — pane capture, response body,
   screenshot path>

🔍 marks a probe — a step off the claim's happy path, trying to
break it. At least one. A Steps list that's all ✅ and no 🔍 is a
happy-path replay: still PASS, but you stopped at the first half.

**Screenshot / sample:** <the one frame a reviewer looks at to see
the feature — image path for GUI/TUI, code block for library/API;
omit for build/types-only>

### Findings
<Things you noticed. Not just bugs — friction, surprises, anything
a first-time user would trip on. "Took three tries to find the right
flag." "Error message on typo was unhelpful." "Default seems odd for
the common case." "Works, but slower than I expected." Lower the bar:
if it made you pause, it goes here. But the pause has to be yours,
from running the app — not from reading the PR page. A red CI check,
a review comment, someone else's bot: visible to anyone already, and
you relaying it isn't an observation. Claim/diff mismatch, pre-existing
breakage, and env notes also belong.

Each probe gets a line here even when it held — "🔍 empty `--from`
→ clean error" tells the author what *was* covered, which they
can't see from a bare PASS.

Lead with ⚠️ for lines worth interrupting the reviewer for; plain
bullets are context. Empty is fine if nothing stuck out — but nothing
sticking out is itself rare.>
```**判决：**
- **通过** — 您运行了该应用程序，所做的更改按照其应有的方式进行了
  表面。不是：测试通过，构建干净，代码看起来正确。
- **失败** — 你运行了它，但它没有运行。或者它破坏了其他东西。
  或者声称和 diff 存在重大分歧。
- **被阻止** — 无法达到可观察到更改的状态。
  构建损坏，环境缺少 dep，句柄不会出现。不是一个
  对变更的判决。准确说出停止的位置 +
  `/run-skill-generator` 提示。
- **SKIP** — 不存在运行时表面。仅文档、仅类型、
  仅测试。没有出什么问题；这里没什么可跑的。
  一行为什么。

没有部分通过。 “3 of 4 Passed” 为 FAIL，直到 4 次通过或
解释走了。

**如有疑问，FAIL。** False PASS 会发送损坏的代码；假失败
成本多了一份人性化的外观。原始的输出不明确是失败的
捕获附件 - 不要解释。