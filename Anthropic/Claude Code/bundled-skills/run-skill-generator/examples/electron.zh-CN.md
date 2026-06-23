<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run-skill-generator/examples/electron.md -->
<!-- source-sha256: 28cdf599c62baef276f3ef1381aab638e3a2a4e918d9809b8b2a8bf13c4c34cf -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

# 示例：Electron / 桌面 GUI 应用程序

Electron 应用程序有一个窗口。无头容器中的未来特工
看不到窗户。所以你的交付物不是一个 Markdown 文件
上面写着“`npm start` 打开一个窗口”——这是一个 **驱动程序脚本**
在 xvfb 下启动应用程序，公开命令的 REPL（单击、键入、
屏幕截图），并让代理通过发送文本行来戳 UI。

然后，该技能的 `SKILL.md` 就成为该驾驶员的简短手册。

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
在 `.claude/skills/run-desktop/`；司机找到了更好的家。

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
    // Electron has no clean "loaded" signal — this sleep is a blind guess.
    // Replace with a poll once you know what ready looks like for this app:
    // wait until windows() includes the expected URL, or waitForSelector on firstWindow().
    await new Promise(r => setTimeout(r, 8_000));
    // Find the real UI page. Often NOT firstWindow() — may be a
    // splash screen, or the real content is in a BrowserView overlay.
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

  // Click via evaluate(), NOT locator.click(). If the content lives in a
  // BrowserView layered over the main window, Playwright's coordinate
  // math hits the wrong layer. DOM .click() always works.
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

  // Introspection: essential for figuring out which window/webContents
  // actually has the UI. Electron apps often spawn several.
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

// Stop Electron from stealing stdin — use the raw fd.
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
您将添加特定于应用程序的命令：导航到特定的
查看，关注奇怪的输入类型，绕过身份验证门，等等。那些
命令编码来之不易的知识——保留它们。

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

继续——点击主要功能，填写表格，查看结果
出现，截图。驱动程序会增长您需要的任何命令
（`focus-input`、`goto-settings`、`login-as-test-user`…）。当一个真正的
流程端到端地工作，您已经完成构建并准备好编写。

## 步骤 4 — 编写 SKILL.md

保持简短。司机就是肉； `SKILL.md` 是手册。
有效的结构：

> ---
> 名称：运行桌面
> 描述：构建、运行和驱动 <app> Electron 桌面应用程序。当要求启动桌面应用程序、对其进行屏幕截图、构建它或与其 UI 交互时使用。
> ---
>
> <App> 是一个 Electron 桌面应用程序。对于代理/自动化使用，驱动它
> 通过剧作家 REPL `.claude/skills/run-desktop/driver.mjs`
> 在 xvfb 下。启动速度很慢（约 10 秒），有趣的 UI 位于
> BrowserView，而不是主窗口——驱动程序处理两者。
>
> 所有路径均相对于 `apps/desktop/`。
>
> ## 先决条件
>
>```bash
> apt-get install -y xvfb libnss3 libgbm1 libasound2t64 libgtk-3-0 \
>   libxss1 libxkbcommon0 libatk-bridge2.0-0 libcups2 libdrm2
> ```>
> ## 构建
>
>```bash
> npm install
> npx electron-forge start   # builds .vite/build/ — Ctrl-C once built
> # <any patch you had to apply: sed a feature gate, etc.>
> ```>
> ## 运行（代理路径）
>
>```bash
> cd apps/desktop
> xvfb-run -a node .claude/skills/run-desktop/driver.mjs
> ```>
> 封装在 tmux 中以供交互使用：
>
>```bash
> tmux new-session -d -s app -x 200 -y 50
> tmux send-keys -t app 'cd apps/desktop && xvfb-run -a node .claude/skills/run-desktop/driver.mjs' Enter
> timeout 20 bash -c 'until tmux capture-pane -t app -p | grep -q "driver>"; do sleep 0.2; done'
> tmux send-keys -t app 'launch' Enter
> timeout 60 bash -c 'until tmux capture-pane -t app -p | grep -q "launched"; do sleep 0.2; done'
> tmux send-keys -t app 'ss landing' Enter
> tmux capture-pane -t app -p
> ```>
> 屏幕截图位于 `/tmp/shots/`（覆盖：`SCREENSHOT_DIR`）。
>
> ### 命令
>
> |命令 |它是做什么的 |
> |---|---|
> | `launch` |启动应用程序，等待 Windows |
> | `ss [name]` |屏幕截图 → `/tmp/shots/<name>.png` |
> | `click <css-sel>` |单击元素（通过 DOM，而不是坐标 — 请参阅陷阱）|
> | `click-text <text>` |单击包含文本的按钮/链接 |
> | `type <text>` / `press <key>` |键盘输入|
> | `wait <css-sel>` |等待元素，10秒超时|
> | `eval <js>` |在页面中评估，打印 JSON |
> | `text [css-sel]` |打印内部文本 |
> | `windows` |列出所有窗口+ webContents（找到真正的UI）|
> | `quit` |关闭应用程序，退出 |
>
> 加上您构建的任何特定于应用程序的命令：`<your-command>` — <what it does>。
>
> ## 运行（人类路径）
>
>```bash
> npm start   # opens a window; useless headless. Ctrl-C to quit.
> ```>
> ## 陷阱
>
> - **<the specific weird thing you hit>** — <why> → <fix/workaround>
> - <etc. — only things you actually hit, not generic advice>
>
> ## 故障排除
>
> - **启动超时（30 秒）：** 构建输出丢失？ → 重新运行构建
> 步骤。 `nodeCliInspect` 保险丝禁用？ → 剧作家无法附加；
> 不要在开发版本中禁用该保险丝。
> - **“缺少 X 服务器”：** 忘记了 `xvfb-run`。无头 Linux 需要它。
> - **过时的 Xvfb 锁：** `rm -f /tmp/.X*-lock; pkill Xvfb`
> - <anything else you actually hit>

## 你会遇到的障碍（它们会遇到陷阱）

这些是来自真实 Electron 应用程序的真实模式。你会遇到一些子集：

- **`firstWindow()` 为您提供启动/加载屏幕，** 而不是应用程序。
  等待更长的时间，或者通过URL找到正确的页面，或者等待特定的
  仅当应用程序实际准备就绪时才会出现的选择器。

- **真正的 UI 位于 BrowserView 中，而不是 BrowserWindow。** Playwright
  将其视为具有不同 URL 的单独 "window"。 `windows`
  命令的存在正是为了解决这个问题。 `getBrowserViews()`
  在较新的 Electron 上也可能返回空——使用
  改为 `webContents.getAllWebContents()`。

- **`locator.click()` 点击了错误的东西。** 剧作家计算
  单击相对于主窗口的坐标。如果您的内容位于
  BrowserView 覆盖层，这些坐标会击中其后面的窗口。
  驱动程序骨架为此使用 `page.evaluate(el => el.click())`
  原因 - DOM 点击完全绕过坐标。

- **功能门会阻止您需要测试的内容。** 该应用程序会检查
  计划层，或环境标志，或烘焙到 SSR HTML 中的功能标志。
  找到检查发生的位置（grep 门的构建输出
  名称）和 patch 用于本地运行 - 构建输出上的 `sed`，
  环境变量覆盖，或者（对于 SSR 嵌入标志）拦截
  通过 CDP `Fetch.enable` 响应并在运行中重写它。文件
  到底你修补了什么以及为什么。

- **内容可编辑输入**（ProseMirror、Tiptap、Slate）不是
  `<textarea>`。 `fill()` 不起作用。聚焦元素，然后使用
  `keyboard.type()`。如果应用程序有这些命令，请添加 `focus <sel>` 命令。

- **Electron 窃取标准输入。** `fs.openSync('/dev/stdin', 'r')` +
  `createReadStream` 骨架中的技巧可以保护您的 REPL 的输入。

- **本机模块无法加载**（钥匙串、通知等）。
  通常是非致命的——核心应用程序运行，这些功能是无操作的。注意它
  并继续前进。