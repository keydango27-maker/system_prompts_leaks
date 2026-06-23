<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run-skill-generator/SKILL.md -->
<!-- source-sha256: 6196bcdf8104fe2812b43bef56107908d4d71c828eed0b178ca1d21d09280d21 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: run-skill-generator
description: Teach /run and /verify how to build and launch your project by creating a per-project run skill with a driver script.
---
您的工作是在 `<unit>/.claude/skills/run-<unit-name>/` 培养 **技能**
让未来的代理构建、启动并**驱动**该项目
一台干净的机器。

该技能由两个共同组成的部分组成：```
<unit>/.claude/skills/run-<unit-name>/
  SKILL.md      ← agent-facing instructions — SHORT. Points at the driver.
  driver.mjs    ← (or driver.py, smoke.sh, … — or none: web apps use
                   chromium-cli off-the-shelf, and the heredoc in
                   SKILL.md is the script)
```这几乎总是意味着**编写代码**，而不仅仅是散文。如果应用程序
具有任何交互界面（GUI、TUI、长时间运行的服务器、REPL），
未来的智能体需要一种编程方式来戳它。一个 Markdown 文件
本身无法单击按钮 - 但有时按钮单击器
已经存在：对于网络应用程序，它是 `chromium-cli`，对于服务器，它是
`curl`。您现在构建（或编写脚本）该工具，并一起提交
该技能，以及 `SKILL.md` 文档如何使用它。

## 完成的定义

当**所有**都为真时，您就完成了：

1. **您在此容器中启动了应用程序并与其交互** —
   不是它的测试套件，而是实际运行的应用程序。对于任何带有 GUI 的东西，
   这意味着您在磁盘上有一个您拍摄的屏幕截图文件。
2. **交互工具被提交**在技能旁边。一名司机
   脚本、REPL 包装器、冒烟测试或 `chromium-cli` 此处文档
   `SKILL.md` 中的内联 — 无论您在步骤 1 中用于驱动应用程序的内容。
   （毕业为 `scripts/`/`e2e/`？ - 好吧，指向它。Web 应用程序
   `chromium-cli` 现货？ — 内联脚本是工具；不
   单独的文件。）
3. **`SKILL.md` 将线束**记录为主要代理路径 —
   未来的代理首先阅读的部分是“运行此驱动程序/管道
   这些命令是 `chromium-cli`，而不是“运行 `npm start` 和一个窗口
   打开。”
4. **`SKILL.md` 中的每个代码块都是您运行的有效命令。**
   本次会议。这个容器。不是从 README 中，不是推断出来的。

如果您要编写技能但没有 (1)，**停止。** 您
即将解释现有文档。该文件已经存在 -
它被称为自述文件，您来到这里的全部原因是它
还不够。

## 可交付成果是代码和文档

典型的输出是包含以下两者的技能目录：```
<unit>/.claude/skills/run-<unit>/
  SKILL.md         ← SHORT. Points at the driver. Has the frontmatter
                     that lets Claude auto-load it when someone asks
                     to "run <unit>" or "screenshot <unit>".
  driver.mjs       ← (or driver.py, smoke.sh, … — or none: web apps
                     use chromium-cli off-the-shelf, and the heredoc
                     in SKILL.md is the script)
```默认情况下，驱动程序位于**技能目录**内。他们是一个
对——技能的指令和实现它们的代码。一个
住在这里的驱动程序可以比生产环境更混乱一些
代码；这是代理工具，而不是产品表面。

**毕业：**如果驱动程序成长为项目自己的东西
测试套件想要重用——共享启动助手，真正的 e2e 工具——
将其移动到 `scripts/` 或 `e2e/` 并更新 `SKILL.md` 以引用
新路径。技能保留；司机找到了更好的家。

确切的形状取决于项目，但原则是不变的：
**驱动程序是可交付的。** `SKILL.md` 是其手册页。对于
Web 应用程序，驱动程序已存在 — `chromium-cli`
([examples/playwright.md](examples/playwright.md)) — 技能是
运行它的脚本。对于桌面应用程序
([examples/electron.md](examples/electron.md))，驱动程序是自定义的
tmux 下的 REPL 公开了 `launch`/`ss`/`click`/`eval`。对于服务器来说，
驱动程序是`curl`。无论它采取什么形状，没有任何东西
进入正在运行的应用程序，技能是一个窗口的描述
没有人可以碰。

## 技能去向

该技能位于 `<unit>/.claude/skills/run-<unit-name>/`，其中
`<unit>` 是 **一个可部署的东西** 的目录 - 一个应用程序、一个
服务，图书馆。

Claude Code **从嵌套 `.claude/skills/` 中本地发现**技能
目录：在 `<unit>` 内任何地方工作的特工都会看到
`/run-<unit-name>` 作为可用技能，当
请求与其描述相符（例如“运行桌面应用程序”、“采取
账单截图”）。

- **单项目存储库：** `.claude/skills/run-<repo-name>/` 位于存储库根目录。
- **包含许多应用程序的大型存储库：** 每个应用程序一个，位于同一位置 —
  `apps/billing/.claude/skills/run-billing/`，
  `apps/desktop/.claude/skills/run-desktop/`。
- **具有多个二进制文件的应用程序：**仍然是应用程序的**一项**技能
  每个二进制文件的根目录。他们共享设置。从
  最接近的单二进制示例并添加 `## Run: <name>` 部分
  每个二进制文件。

如果您不确定单元边界在哪里，**询问用户。**

Slugify 目录名称：小写，破折号表示空格，没有斜杠
（`run-billing-api`，而不是 `run-billing/api`）。目录名称和
frontmatter `name:` 应该匹配 - 这就是斜杠命令。

## 流程

### 0. 查找有关运行此应用程序的任何现有技能

列出项目的技能及其描述（相同探针 `/run`
使用——用户对这些名称有不同的命名，因此匹配描述，而不是名称）：```bash
d=$PWD; while :; do
  grep -Hm1 '^description:' "$d"/.claude/skills/*/SKILL.md 2>/dev/null
  [ -e "$d/.git" ] || [ "$d" = / ] && break
  d=$(dirname "$d")
done
```如果一个人想要启动/驱动这个应用程序——无论它叫什么名字——
**精炼，不要重写**：验证其声明，修复错误，添加
缺少什么，保留有效的。如果有则重新运行驱动程序
一。保留其现有名称。

（另请检查旧版 `.claude/run.md` — 此版本的早期版本
工具产生了那些。如果你找到了，就迁移它：身体变成
该技能的 `SKILL.md` 内容，任何引用的脚本都会移至
技能目录，delete 旧文件。）

如果不存在，请决定在哪里创建它（见上文）并继续。

### 1. 发现并对待每一个主张都是不可证伪的

弄清楚您创作的目的：

- 清单就在这里（`package.json`、`go.mod`、`pyproject.toml`…）和
  这是一个独立的东西 → 这是一个单元。
- 看起来像一个大型仓库根（`apps/`，`packages/`，`services/`）→
  **问哪一个。** 列出候选人，让他们挑选，`cd` 在那里。
- 确实模棱两可→询问。

调查常用的地方：`README.md`、`package.json`脚本、
`Dockerfile`、`Makefile`、`.github/workflows/`、`CONTRIBUTING.md`。 CI
配置通常比自述文件更准确。

**现有文档中的每个主张都是一个假设。**尤其是
消极的：

|当文档说... |你做什么|
|---|---|
| “需要 macOS/Windows” |无论如何在 Linux 上启动它。应用程序很少拒绝启动 - 它们会在丢失的 `.so` 上崩溃，而 `apt-get` 已修复该问题。 *您的主机的*钥匙串/通知的本机模块可能无操作；核心通常运行。 |
| “需要 GPU”|尝试软件渲染。 Electron/Chrome 使用 `--disable-gpu` 进行回退。 |
| “需要付费帐户/功能标志” |门是您可以阅读的代码。找到它（环境变量？构建定义？SSR嵌入的JSON？）和patch它用于本地运行。记录 patch。 |
| “运行`npm start`” |这就是人类的道路（产生一个窗口，永远等待）。查找或构建“编程”路径 — `electron-forge start` 进行构建，然后通过 Playwright 或同等工具启动。 |

macOS 开发人员编写的自述文件中显示“Linux 上不支持”
意思是“我从未尝试过”。你正要尝试一下。 **如果你在这里放弃，
您编写的技能是带有额外步骤的自述文件。**

### 2. 执行 — 并构建您需要的工具

您处于无头 Linux 容器中。该应用程序将与你战斗。
那战斗就是技能的内容。

随时保持运行的 `NOTES.md`。每个错误→每个修复→每个
命令终于起作用了。该暂存器成为
故障排除部分。

**进行真正的互动：**

- **安装 + 构建。** 当缺少某些内容时，请记下确切的内容
  `apt-get` / `npm install` 修复了它。
- **启动app.** 不是测试套件 - 应用程序。桌面图形用户界面
  （Electron，原生）需要 `xvfb-run` 和少量 `lib*`
  包裹；由 `chromium-cli` 驱动的 Web 应用程序无头运行
  两者都不需要。启动超时和神秘崩溃是正常的
  这个阶段。阅读堆栈跟踪，安装缺少的东西，尝试
  再次。
- **制作一个安全带来驱动它。** 你需要一个跑步手柄
  应用程序可让您以编程方式发送输入并观察输出。
  形状取决于项目（见下表）。

  **覆盖 PR 实际接触的层。** 戳戳的 tmux 驱动程序
  CLI 的用户界面是 UI 更改的正确手柄 - 并且
  对于涉及一项内部功能的 PR 来说是错误的。对于
  后者代理想要 `NODE_ENV=test bun run script.ts` （或
  等价）：导入函数，调用它，观察。如果大多数 PR
  这里触摸内部，直接调用路径是驱动程序的
  主要入口点，tmux 启动是次要的。看看最近的
  合并的 PR：它们触及哪一层？盖住那个。

  对于 **web** 应用程序，`chromium-cli` 是驱动程序 - 您可以编写脚本，
  你不写它（参见[examples/playwright.md](examples/playwright.md)）。
  对于 **桌面** GUI (Electron)，编写 REPL 驱动程序 (stdin
  命令 → 单击/输入/屏幕截图），在 tmux 中运行它，然后使用
  `send-keys` / `capture-pane`。您将迭代该驱动程序 - 它
  启动最小（`launch`、`ss`、`quit`）并增长任何命令
  您需要到达应用程序的有趣部分。
- **端到端执行一个真实的用户流。** 单击按钮。填写
  形式。在 DOM 中查看结果。截图一下。 **实际上看
  在屏幕截图中。** 如果它是空白或显示错误页面，则您是
  没有完成。
- **然后运行测试。** 单元测试是健全性检查，而不是主要的
  事件。
- **干净地停下来。**

**障碍就是内容。**你会遇到奇怪的障碍——坐标系
不排队，在此 Electron 版本上返回空的 API，
隐藏您需要测试的内容的功能门。其中每一个都得到
陷阱中的一颗子弹和（通常）驱动程序中的助手。黄金
标准是一个陷阱部分，里面充满了没人能猜到的东西。

**驱动程序脚本与技能一起提交。**它不是
脚手架。这是未来智能体（和人类）推动这一发展的方式
应用程序。它默认位于技能目录中（对于网络应用程序
使用 `chromium-cli`，这意味着 `SKILL.md` 中的内联 — 此处文档
是脚本）。如果它超出了这个范围——如果该项目是真正的考验
套件想要从中导入 - 将其移动到 `scripts/` 或 `e2e/` 并
将 `SKILL.md` 更新为指向那里。

### 3.编写SKILL.md

短。指着司机。使用 [template.md](template.md) 作为
起始结构——它具有 frontmatter 形状。

**前面的内容很重要。** `name:` 成为斜杠命令
（`/run-billing`）。 `description:` 是克劳德扫描确定的
是否自动加载此技能 - put 代理将使用的**动词
实际上在其中输入**：“运行”、“开始”、“构建”、“测试”"screenshot."
通用描述（“计费实用程序”）不匹配。

车身结构：

1. 一段介绍：这个应用程序是什么，它是如何驱动的 —
   `<driver-path>` 在 xvfb/tmux 下用于桌面，`chromium-cli` 用于
   web，`curl` 用于服务器。
2. **先决条件** — 您运行的确切 `apt-get install` 行。
3. **构建** — 确切的命令（按顺序）。包括您的任何补丁
   必须使用确切的 `sed` 来应用（功能门、配置覆盖）
   或编辑。
4. **运行（代理路径）** — 首先。如何启动驱动程序，什么
   它接受的命令是屏幕截图所在的位置。如果是 REPL，则显示
   tmux 包装。这是下一个代理实际上将要执行的部分
   使用。
5. **运行（人类路径）** — 第二，如果不同的话。 `npm start` → 窗口
   打开 → Ctrl-C。简短的。请注意，无头是没有用的。
6. **陷阱**——战斗的伤痕。那些看起来像它们的东西
   应该有效但无效，以及解决方法。如果这部分是
   很一般，你战斗的不够努力。
7. **故障排除** — 症状 → 修复。仅显示您实际遇到的错误。

保持**验证**（您运行了它），**规定性**（一条路径，而不是
选项），**诚实**（不稳定？慢？这么说）。

**SKILL.md 中的路径是相对于 `<unit>/`，** 与技能无关
目录。如果有任何歧义，请在顶部说明。当
驱动程序位于技能内，其从 `<unit>` 的路径是
`.claude/skills/run-<unit-name>/driver.mjs` — 它很长，但很明确。

### 4. 验证

新鲜贝壳，`cd`入单位，跟随技能的`SKILL.md`
逐行不偏离。任何即兴发挥=差距。修复它。

## 项目类型模式

为您的一号木选择一个起始形状。这些例子分享给
`/run` 技能（使用与每个项目类型相同的模式
当不存在特定于项目的运行技能时的后备） - 如果您
创作一个新模板，该示例是您的起始模板。

|项目类型 |驾驶员形状 |示例|
|---|---|---|
|网络服务器/API |后台启动+基于`curl`的烟雾脚本| [示例/服务器.md](示例/服务器.md) |
| CLI 工具 |代表-args烟雾脚本，检查退出代码+输出| [示例/cli.md](示例/cli.md) |
| TUI/交互终端| tmux 包装器：`send-keys` / `capture-pane` | [示例/tui.md](示例/tui.md) |
|电子/桌面 GUI |剧作家 `_electron` xvfb 下的 REPL 驱动程序、屏幕截图、tmux 包装 | [示例/电子.md](示例/电子.md) |
|浏览器驱动 |开发服务器 + `chromium-cli` 脚本 | [示例/playwright.md](示例/playwright.md) |
|库 / SDK |导入并调用烟雾脚本| [示例/library.md](示例/library.md) |

对于网络应用程序，请从 [examples/playwright.md](examples/playwright.md) 开始
— 使用 `chromium-cli` 驱动它，无需自定义驱动程序。对于一个
桌面应用程序，从 [examples/electron.md](examples/electron.md) 开始
— 它具有完整的 `_electron` REPL 驱动程序框架、tmux 包装、
以及您将遇到的障碍的目录。

## 包含哪些内容

- **先决条件** — 操作系统包、运行时、工具。 Ubuntu `apt-get`
  线。确切的那些。
- **安装** — 安装 deps、配置、任何补丁。
- **构建** — 编译/捆绑。
- **运行（代理路径）** — 驱动程序。命令。截图位置。
- **直接调用** — 如果可调用：如何导入和运行内部
  没有完整应用程序的代码。绕过 init 的环境变量/标志
  警卫。很多 PR 只需要这个。
- **运行（人类路径）** - 如果有意义的不同。
- **测试** — 测试套件命令。
- **陷阱** — 你遇到的不明显的陷阱。
- **故障排除** — 错误 → 修复。
- **驱动程序本身** — 在技能目录中提交（或已毕业
  到 `scripts/`/`e2e/`)，或内联在 `SKILL.md` 中用于 `chromium-cli`
  网络应用程序；无论哪种方式，都可以从 `SKILL.md` 引用。

## 省略什么

- **您未运行的任何内容。** 如果自述文件显示 `yarn start:prod` 并且
  你从来没有跑过它，这不属于技能范围。句号。
- **记录了您不在的平台上的快乐路径。**您处于一个
  Linux 容器。您无法验证的仅限 macOS 的部分是
  猜测。提及它的存在；不详细说明。
- **详尽的选项。** 一条工作路径。
- **建筑散文。** 那是其他文档。
- **一般故障排除。**“如果构建失败，请检查您的节点
  版本”——没用。仅包含您实际遇到并修复的错误。

## 危险信号 — 您将要运送错误的东西

如果出现以下情况，请停止并重新考虑：

- **您尚未截取 GUI 应用程序的屏幕截图**。你没有运行它。
- **你的技能没有驱动程序/烟雾脚本**可以指向，并且应用程序
  是互动的。下一个特工没有办法驾驶它。 （网络应用程序
  使用`chromium-cli`？ — `SKILL.md` 中的heredoc是驱动程序；
  不需要单独的文件。）
- **你的技能读起来就像自述文件。** 相同的结构，相同的
  命令，相同的警告。你转述了。
- **您的故障排除部分是通用的。** 实际执行会产生
  具体的、奇怪的错误。一般错误 = 你没有执行。
- **您写了“此平台不支持”**，但没有尝试
  启动它。 README 作者使用的是 Mac。你不是。尝试。
- **第一次尝试一切正常。** 这个项目要么微不足道
  很简单，或者您运行测试套件并称其完成。