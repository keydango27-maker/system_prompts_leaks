<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run.md -->
<!-- source-sha256: 9f3484b671b9ff27d3e2fbac8df5254eccde435007a0160941968bfcd5ee5481 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: run
description: Launch and drive this project's app to see a change working.
---
# 奔跑技能

**运行意味着启动实际的应用程序并与其交互** —
不是测试套件，不是内部函数的 `import` 和
`console.log`。该应用程序作为用户（人类或程序化）会满足
它：CLI 在其命令上，服务器在其套接字上，GUI 在其上
窗口。

## 首先：项目技能是否已经涵盖了这一点？

启动此应用程序的项目技能是存储库的验证路径 -
它的作者已经从 Linux 容器冷启动并承诺
什么有效：确切的 `apt-get` 行、环境变量、补丁、
司机。使用它而不是重新发现。```bash
d=$PWD; while :; do
  grep -Hm1 '^description:' "$d"/.claude/skills/*/SKILL.md 2>/dev/null
  [ -e "$d/.git" ] || [ "$d" = / ] && break
  d=$(dirname "$d")
done
```- **其中描述了启动/驱动此应用程序** → 阅读 SKILL.md
  并逐字遵循。不要转述；不要跳过补丁。
- **大型仓库，几个看似合理的，没有明确匹配** →询问用户
  运行哪个单元。
- **陈旧**（与你的任务无关的机制失败）→告诉
  用户；提供通过 `/run-skill-generator` 刷新它。
- **与跑步无关** → 回到下面的模式。

## 否则：匹配形状，使用模式

选择最接近您的项目的行。每个示例都经过
启动+首次互动；忽略任何结尾的“写技能”
部分 - 您正在使用食谱，而不是创作食谱。

|项目类型 |手柄|示例|
|---|---|---|
| CLI 工具 |直接调用、退出代码、stdin/stdout |示例/cli.md |
|网络服务器/API |背景发射+`curl` 烟雾|示例/server.md |
| TUI/交互终端| tmux `send-keys` / `capture-pane` |示例/tui.md |
|电子/桌面 GUI | xvfb 下的剧作家 `_electron` REPL |示例/电子.md |
|浏览器驱动|开发服务器 + `chromium-cli` 脚本 |示例/playwright.md |
|库 / SDK |在包边界导入并调用烟雾脚本 |示例/library.md |

如果没有合适的，请从最接近的匹配开始并进行调整。对于一个网络
app, example/playwright.md — 使用 `chromium-cli` 驱动它，无自定义
需要司机。对于桌面应用程序，examples/electron.md — 它具有
`_electron` REPL 驱动程序框架和 tmux 包装。

## 驱动它，而不仅仅是启动它

在没有交互的情况下启动证明入口点已解析。那是
不运行应用程序 - 它是通过额外步骤进行类型检查。驾驶它到
用户会看到某些内容的点：

- CLI → 输入代表性命令，检查退出代码和输出。
- 服务器→用`curl`点击diff接触的路线，阅读正文。
- TUI → `send-keys` 导航，`capture-pane` 结果。
- GUI → 单击按钮，截屏窗口。 **看看
  屏幕截图。** 空白框表示启动失败。

如果回退模式无法立即使用 - 您必须这样做
安装软件包、设置环境变量、patch 配置或编写驱动程序 —
在您的报告中推荐 `/run-skill-generator`，以便工作得到
捕获为项目技能。如果它只是有效，那就不要。

---

# 示例/cli.md — CLI 工具

CLI 是最简单的情况 — 通常没有后台进程
管理，没有端口，没有生命周期。技能重点是**安装**，
**代表性调用**和**测试**。

## 重要的是

- **如何 get `PATH` 上的二进制文件。** 全局安装？运行通过
  `npx`/`uv run`？建于`./target/release/foo`？明确一点。
- **两个或三个示例调用**，涵盖主要用例。
  包括预期的输出，以便读者可以知道它有效。
- **退出代码**，如果它们有意义（例如 linter 在发现结果时返回 1）。
- **标准输入行为**（如果工具从标准输入读取）。

## 示例片段

> ---
> 名称：运行-mytool
> 描述：构建、安装和运行 mytool。当要求运行 mytool、测试它或验证它是否正确安装时使用。
> ---
>
> ## 设置
>
>```bash
> pip install -e .
> ```>
> 这会将 `mytool` 置于 PATH 上。验证：
>
>```bash
> mytool --version
> # → mytool 0.3.1
> ```>
> ## 运行
>
> 处理单个文件：
>
>```bash
> mytool process input.json
> # → Processed 42 records, wrote output.json
> ```>
> 从 stdin 读取，写入 stdout：
>
>```bash
> cat input.json | mytool process -
> ```>
> Lint 目录（出现问题时退出非零）：
>
>```bash
> mytool lint ./src
> echo $?  # 0 if clean, 1 if issues found
> ```>
> ## 测试
>
>```bash
> pytest
> ```## 保持简短

CLI的跑动技能可以非常紧凑。不要用每个标志来填充它 -
`--help` 输出涵盖了这一点。只需展示足够的信息即可让代理商可以
(a) 构建它，(b) 确认它有效，(c) 运行测试。

---

# example/server.md — Web 服务器 / API

服务器的显着关注点是**生命周期**：代理需要
在后台启动服务器，验证它是否已启动，与其交互，然后
干净地关闭它。阻塞 shell 的前台 `npm start` 是
对代理没用。

## 遵循的结构

良好的服务器运行技能具有：

1. **先决条件和设置** — 与任何项目相同。
2. **运行** — 后台启动模式（如下），而不是阻塞命令。
3. **验证** — `curl` 或类似内容，确认服务器确实已启动。
4. **停止** — 如何干净地终止后台进程。

如果后台启动+就绪轮询+烟雾卷曲序列更多
比几行，put它在技能目录中的`smoke.sh`中
并让 `SKILL.md` 说“运行烟雾脚本”。一条命令，退出代码
告诉您服务器是否健康。

## 后台启动模式

不要写：

>```bash
> npm start
> ```那会阻塞。相反，展示如何在后台启动，等待
准备就绪，稍后查找 PID：

>```bash
> npm start &> /tmp/server.log &
> SERVER_PID=$!
>
> # Wait for the server to come up (adjust timeout/port as needed)
> for i in {1..30}; do
>   curl -sf http://localhost:3000/health > /dev/null && break
>   sleep 1
> done
> ```然后是验证步骤：

>```bash
> curl http://localhost:3000/health
> # → {"status":"ok"}
> ```并停止：

>```bash
> kill $SERVER_PID
> # or, if you've lost the PID:
> pkill -f "node.*server.js"
> ```## 值得记录的细节

- **哪个端口。** 明确并说明如何覆盖它 (`PORT=4000 npm start`)。
- **"ready" 是什么样的。** 要命中的特定日志行或运行状况端点。
- **必需的环境变量。** 数据库 URL、API 密钥等 — 使用模板 `.env`
  如果清单很长。
- **热重载与生产模式。** 如果它们有显着差异，请说明是哪一个
  使用以及何时使用。
- **依赖服务。** 如果服务器需要Redis/Postgres/等，则
  指向启动它们的 docker-compose，或者包含 `docker run`
  直接命令。

## 示例片段

典型节点 API 的运行部分可能如下所示：

> ## 运行
>
> 在后台启动开发服务器：
>
>```bash
> npm run dev &> /tmp/api.log &
> ```>
> 服务器侦听端口 3000。等待其准备就绪，然后验证：
>
>```bash
> for i in {1..20}; do
>   curl -sf http://localhost:3000/health && break
>   sleep 0.5
> done
> curl http://localhost:3000/health
> # → {"status":"ok","version":"1.2.3"}
> ```>
> 日志位于 `/tmp/api.log`。停止：
>
>```bash
> pkill -f "tsx watch src/index.ts"
> ```>
> ### 环境
>
> |变量|必填|默认|笔记|
> |---|---|---|---|
> | `DATABASE_URL` |是的 | — | Postgres 连接字符串 |
> | `PORT` |没有 | `3000` | |
> | `LOG_LEVEL` |没有 | `info` | `debug` / `info` / `warn` / `error` |

---

# example/tui.md — TUI / 交互式终端应用程序

交互式终端应用程序（文本编辑器、REPL、基于curses的UI）不能
由代理的 bash 工具直接驱动 - 他们接管终端。
该技能必须显示如何将它们包装在 `tmux` 中，以便代理可以发送
输入、捕获输出并截取屏幕截图。

## tmux 模式

这是标准方法：

1. 在分离的 tmux 会话中启动 TUI
2. 使用 `tmux send-keys` 发送击键
3.使用`tmux capture-pane`读取屏幕内容
4.用`tmux kill-session`清理

该技能的 `SKILL.md` 应将其呈现为主要的驾驶方式
该应用程序。封装启动+附加序列的小 `driver.sh` 可以
位于技能目录中，但对于大多数 TUI，原始 tmux 命令位于
技能本体就够了。

## 示例片段

> ## 运行（交互式，针对代理）
>
> 在 tmux 内启动 TUI：
>
>```bash
> tmux new-session -d -s app -x 120 -y 40 './myapp'
> ```>
> 轮询直到出现就绪标记（比固定睡眠更快+更可靠 —
> 在应用程序启动时立即返回，如果没有启动，则会失败）：
>
>```bash
> timeout 10 bash -c 'until tmux capture-pane -t app -p | grep -q "Ready"; do sleep 0.2; done'
> tmux capture-pane -t app -p
> ```>
> 发送输入（此示例导航至“设置”屏幕并切换
> 一个选项）：
>
>```bash
> tmux send-keys -t app 's'
> timeout 5 bash -c 'until tmux capture-pane -t app -p | grep -q "Settings"; do sleep 0.2; done'
> tmux send-keys -t app 'Down' 'Down' 'Space'  # navigate + toggle
> timeout 5 bash -c 'until tmux capture-pane -t app -p | grep -qF "[x]"; do sleep 0.2; done'
> tmux capture-pane -t app -p
> ```>
> 如果您发现自己写了不止几行这样的民意调查，请拉
> 他们变成了一个`wait_for()` 助手在一个`driver.sh` 技能旁边。
>
> 退出：
>
>```bash
> tmux send-keys -t app 'q'
> tmux kill-session -t app 2>/dev/null || true
> ```>
> ### 关键参考
>
> |关键|行动|
> |---|---|
> | `j` / `k` 或 `Down` / `Up` |导航列表 |
> | `Enter` |选择 |
> | `s` |设置 |
> | `q` |退出 |

## 值得记录的细节

- **终端尺寸。** 某些 TUI 会破坏或隐藏小宽度的内容。
  在 `tmux new-session -x -y` 参数中指定已知良好的大小。
- **启动时间。** 轮询就绪标记 (`until tmux capture-pane | grep -q X`)
  而不是固定的 `sleep N` — 在应用程序启动并失败时立即返回
  当它从不这样做时很有用。说出什么字符串表示准备就绪。
- **键绑定参考。** 主键表。这是 "API"
  TUI 的一部分 — 代理需要它来驱动应用程序。
- **干净地退出。** 显示退出击键 * 和 * `tmux kill-session` 为
  后备。
- **颜色/unicode 怪癖。** 如果 `capture-pane` 输出难以阅读，
  注意有助于的标志（`-e` 用于转义序列，`-J` 用于加入包装
  行）。

## 还记录直接调用

对于以交互方式运行应用程序的人来说，tmux 太过分了。包括
也是单行：

> ## 运行（直接，对于人类）
>
>```bash
> ./myapp
> ```>
> 按 `q` 退出。

---

# example/electron.md — Electron / 桌面 GUI 应用程序

Electron 应用程序有一个窗口。无头容器中的未来特工
看不到窗户。所以你的交付物不是一个 Markdown 文件
上面写着“`npm start` 打开一个窗口”——这是一个 **驱动程序脚本**
在 xvfb 下启动应用程序，公开命令的 REPL（单击、键入、
屏幕截图），并让代理通过发送文本行来戳 UI。

该技能的 `SKILL.md` 随后成为该驾驶员的简短手册。

## 你正在构建什么```
apps/desktop/
  .claude/skills/run-desktop/
    SKILL.md               ← short. "run the driver, here are the commands"
    driver.mjs             ← REPL: stdin commands → Playwright actions
```驱动程序就是产品。如果没有它，该技能将描述一个 GUI
代理永远无法触及。

**毕业路径：**如果驱动程序增长了项目的启动帮助程序
真正的e2e套件想要共享，将其移至`e2e-playwright/driver.mjs`
（或 `scripts/drive.mjs`）并更新技能的路径。技能保持不变
在`.claude/skills/run-desktop/`；司机找到了更好的家。

## 步骤 1 — get 在 xvfb 下启动的应用程序

这通常是最难的部分，并且会产生大部分问题。的
自述文件将显示“仅限 macOS/Windows”。忽略这一点。安装 xvfb +
Chromium 共享库，找到 Electron 二进制文件，然后启动它：```bash
apt-get install -y xvfb libnss3 libgbm1 libasound2t64 libgtk-3-0 \
  libxss1 libxkbcommon0 libatk-bridge2.0-0 libcups2 libdrm2

# Build the app first. Often the "dev" script is electron-forge which
# does a Vite/webpack build THEN launches. You want just the build:
npm install
npx electron-forge start &   # builds .vite/build/ or dist/
sleep 20 && kill %1          # kill it once built — you'll launch yourself

# Now try the raw launch
xvfb-run -a node -e "
  const { _electron } = require('playwright-core');
  _electron.launch({
    executablePath: './node_modules/electron/dist/electron',
    args: ['--no-sandbox', '.'],
    timeout: 30000,
  }).then(app => {
    console.log('launched, windows:', app.windows().map(w => w.url()));
    return app.close();
  });
"
```迭代直至启动。每个缺失 `.so` → 多一个 `apt-get`
包 → 先决条件中多一行。每次启动超时→检查
`nodeCliInspect` 保险丝未禁用，请检查构建输出是否存在。

**容器中几乎总是需要 `--no-sandbox`。** Electron 的
沙箱需要 CAP_SYS_ADMIN 或用户命名空间。默认情况下都不是。

## 步骤 2 — 构建 REPL 驱动程序

一旦您可以启动它，请将一次性脚本转换为 REPL。开始
最小化——您可以根据需要添加命令。 **REPL 是
正确的形状**，因为代理可以在 tmux 内运行它并迭代
无需在每次交互时重新启动（缓慢的）应用程序。```javascript
// .claude/skills/run-<unit>/driver.mjs
// REPL driver for <app>. Run under xvfb on headless Linux.
// Designed for agents: wrap in tmux, send-keys commands, capture-pane output.
import { _electron as electron } from 'playwright-core';
import * as readline from 'node:readline';
import * as fs from 'node:fs';
import * as path from 'node:path';

const APP_DIR = path.resolve(import.meta.dirname, '../../..');
const SHOT_DIR = process.env.SCREENSHOT_DIR || '/tmp/shots';
fs.mkdirSync(SHOT_DIR, { recursive: true });

let app = null;
let page = null;   // the window/page you actually interact with

const electronBin = process.platform === 'darwin'
  ? path.join(APP_DIR, 'node_modules/electron/dist/Electron.app/Contents/MacOS/Electron')
  : path.join(APP_DIR, 'node_modules/electron/dist/electron');

const COMMANDS = {
  async launch() {
    if (app) return console.log('already launched');
    app = await electron.launch({
      executablePath: electronBin,
      args: ['--no-sandbox', APP_DIR],
      env: { ...process.env, DISPLAY: process.env.DISPLAY || ':99' },
      timeout: 30_000,
    });
    await new Promise(r => setTimeout(r, 8_000));
    page = app.windows().find(w => !w.url().startsWith('devtools://'))
        ?? await app.firstWindow();
    console.log('launched.', app.windows().length, 'windows:');
    for (const w of app.windows()) console.log(' ', w.url());
  },

  async ss(name) {
    if (!page) return console.log('ERROR: launch first');
    const f = path.join(SHOT_DIR, (name || `ss-${Date.now()}`) + '.png');
    await page.screenshot({ path: f });
    console.log('screenshot:', f);
  },

  async click(sel) {
    if (!page) return console.log('ERROR: launch first');
    const r = await page.evaluate(s => {
      const el = document.querySelector(s);
      if (!el) return 'NOT_FOUND';
      el.click(); return 'OK';
    }, sel);
    console.log('click', sel, '→', r);
  },

  async 'click-text'(text) {
    if (!page) return console.log('ERROR: launch first');
    const r = await page.evaluate(t => {
      const els = [...document.querySelectorAll('button, a, [role="button"]')];
      const el = els.find(e => e.textContent?.trim() === t)
              ?? els.find(e => e.textContent?.includes(t));
      if (!el) return 'NOT_FOUND';
      el.click(); return 'OK: ' + el.tagName;
    }, text);
    console.log('click-text', JSON.stringify(text), '→', r);
  },

  async type(text)  { if (page) await page.keyboard.type(text, { delay: 30 }); },
  async press(key)  { if (page) await page.keyboard.press(key); },

  async wait(sel) {
    if (!page) return console.log('ERROR: launch first');
    try { await page.waitForSelector(sel, { timeout: 10_000 }); console.log('found:', sel); }
    catch { console.log('TIMEOUT:', sel); }
  },

  async eval(expr) {
    if (!page) return console.log('ERROR: launch first');
    try { console.log(JSON.stringify(await page.evaluate(expr))); }
    catch (e) { console.log('ERROR:', e.message); }
  },

  async text(sel) {
    if (!page) return console.log('ERROR: launch first');
    console.log(await page.evaluate(
      s => (s ? document.querySelector(s) : document.body)?.innerText ?? '(null)',
      sel || null));
  },

  async windows() {
    if (!app) return console.log('ERROR: launch first');
    for (const w of app.windows()) console.log(' ', w.url());
    const wcs = await app.evaluate(({ webContents }) =>
      webContents.getAllWebContents().map(w => ({ id: w.id, type: w.getType(), url: w.getURL() })));
    console.log('webContents:');
    for (const w of wcs) console.log(` [${w.id}] ${w.type}: ${w.url}`);
  },

  async quit() { if (app) await app.close().catch(()=>{}); app = null; page = null; },
  help() { console.log('commands:', Object.keys(COMMANDS).join(', ')); },
};

const stdin = fs.createReadStream(null, { fd: fs.openSync('/dev/stdin', 'r') });
const rl = readline.createInterface({ input: stdin, output: process.stdout, prompt: 'driver> ' });

rl.on('line', async line => {
  const [cmd, ...rest] = line.trim().split(/\s+/);
  if (!cmd) return rl.prompt();
  const fn = COMMANDS[cmd];
  if (!fn) { console.log('unknown:', cmd, '— try: help'); return rl.prompt(); }
  try { await fn(rest.join(' ')); } catch (e) { console.log('ERROR:', e.message); }
  if (cmd === 'quit') { rl.close(); process.exit(0); }
  rl.prompt();
});
rl.on('close', async () => { await COMMANDS.quit(); process.exit(0); });

console.log('<app> driver — "help" for commands, "launch" to start');
rl.prompt();
```**这是一个起始骨架。** 当您尝试到达有趣的部分时
您将添加应用程序特定的命令。

## 步骤 3 — 通过 tmux 自己使用

以与下一个代理相同的方式运行驱动程序：```bash
tmux new-session -d -s app -x 200 -y 50
tmux send-keys -t app 'cd /workspace/apps/desktop && xvfb-run -a node .claude/skills/run-desktop/driver.mjs' Enter
timeout 20 bash -c 'until tmux capture-pane -t app -p | grep -q "driver>"; do sleep 0.2; done'
tmux send-keys -t app 'launch' Enter
timeout 60 bash -c 'until tmux capture-pane -t app -p | grep -q "launched"; do sleep 0.2; done'
tmux send-keys -t app 'ss 01-landing' Enter
timeout 10 bash -c 'until tmux capture-pane -t app -p | grep -q "screenshot:"; do sleep 0.2; done'
tmux send-keys -t app 'windows' Enter    # which page has the real UI?
tmux capture-pane -t app -p
```然后实际打开`/tmp/shots/01-landing.png`。是应用程序吗？是吗
空白？这是登录屏幕吗？其中每一个都会告诉您下一步该做什么。

## 步骤 4 — 编写 SKILL.md

保持简短。司机就是肉； `SKILL.md` 是手册。

## 你会遇到的障碍（它们会遇到陷阱）

- **`firstWindow()` 为您提供启动/加载屏幕，** 而不是应用程序。
- **真正的 UI 位于 BrowserView 中，而不是 BrowserWindow。**
- **`locator.click()` 点击错误的内容。** 使用 `page.evaluate(el => el.click())`。
- **功能门会阻止您需要测试的东西。**
- **内容可编辑输入**（ProseMirror、Tiptap、Slate）不是 `<textarea>`。
- **Electron 窃取标准输入。** `fs.openSync('/dev/stdin', 'r')` 技巧可以保护您的 REPL 的输入。
- **本机模块无法加载**（钥匙串、通知等）。

---

# example/playwright.md — 浏览器驱动的 Web 应用程序

您有一个向浏览器提供 HTML 的开发服务器。代理人在一个
无头容器无法打开浏览器窗口 - 所以“运行应用程序”意味着
启动开发服务器，驱动一个无头 Chromium 来对抗它，以及
生成证明页面呈现的屏幕截图。

不要编写浏览器驱动程序。使用 `chromium-cli`。

## 开发服务器

找到 dev 命令（`package.json` `scripts.dev`、`Makefile`、
README），在后台启动它，并等待它实际运行：```bash
npm run dev &   # or yarn dev, pnpm dev, make serve, ./dev.sh
echo $! > /tmp/dev.pid
timeout 30 bash -c 'until curl -sf http://localhost:3000 >/dev/null; do sleep 1; done'
```## 驾驶

`chromium-cli` 是一个无头 Chromium REPL。将脚本通过管道传输到标准输入：```bash
chromium-cli --session app <<'EOF'
nav http://localhost:3000
wait-for text=Dashboard
screenshot
click button:has-text("New item")
fill input[name="title"] Smoke test
press Enter
wait-for text=Smoke test
screenshot
console --errors
EOF
```##技能中的put是什么

仅项目特定位。 `chromium-cli` 负责机械操作。

- **开发命令+端口+停止。**
- **授权**
- **一次代表性互动。**
- **特定于应用程序的陷阱。**

## 重复出现的问题

- **反应控制输入。** 使用 `fill` / `type`，而不是 `eval el.value = '…'`。
- **Websockets /长轮询。** `wait-idle` 永远不会解决。 `wait-for` 您实际需要的元素。
- **第一次绘制速度慢。** Vite/Next 按需编译路线；第一个 `nav` 可能需要 10 秒以上。
- **`screenshot-element <sel>`** 裁剪为一个元素。
- **在宣布成功之前检查 `console --errors`。**

---

# 示例/library.md — 库/SDK

库在流程意义上没有 "run" 步骤。对于库来说，运行技能大约是：

1. **从源代码构建**库
2. **运行测试套件**
3. **一个最小的工作示例**，用于练习该库

## 冒烟测试示例

>```bash
> python -c '
> from mylib import Client
> c = Client()
> print(c.ping())
> '
> # → pong
> ```## 需要考虑记录的事项

- **开发模式与安装模式。**
- **可选依赖项。**
- **生成的代码。**