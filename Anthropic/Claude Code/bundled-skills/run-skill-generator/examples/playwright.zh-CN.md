<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run-skill-generator/examples/playwright.md -->
<!-- source-sha256: 889db4132f2f5be3877c9fdad91735987b33d9c300a1eef67e4207cffb18d4b4 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

# 示例：浏览器驱动的 Web 应用程序

您有一个开发服务器，为浏览器提供 HTML 服务。代理人在一个
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
```不要 `sleep 5` — 轮询端口。停止与
`kill $(cat /tmp/dev.pid)`（或 `pkill -f 'npm run dev'`）之前
重新启动，或者下一次运行会出现 `EADDRINUSE`。

## 驾驶

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
```截图登陆`chromium_cli/sessions/app/screenshots/`（最新
符号链接为 `screenshot.png`)。这就是整个循环：`nav` →
`wait-for` 您需要的元素 → 执行 (`click` / `fill` / `type` /
`press`) → `screenshot` → `console --errors` 检查没有抛出任何东西。
完整命令参考：`chromium-cli` 技能，或出现提示时 `help`。

对于迭代调试，在 tmux 和 `send-keys` 一条命令下运行
一次 - 相同的命令，相同的会话。

**如果 `chromium-cli` 不可用：** 适应
[ Electron.md](Electron.md) 的 REPL 驱动程序 — 结构和命令
传输，但它是 `_electron` 特定的：
改为导入 `{ chromium }`，启动
`chromium.launch({ args: ['--no-sandbox'] })`，通过以下方式获取页面
`(await app.newContext()).newPage()` 然后 `goto()` 您的开发 URL，以及
删除仅 Electron 窗口内省
（`.windows()`/`.firstWindow()`/`windows` 命令）。

##技能中的put是什么

仅项目特定位。 `chromium-cli` 负责机械操作。

- **Dev 命令 + 端口 + stop。** 确切的起始行，任何环境变量
  需要，并且 `kill`/`pkill` 来停止它。
- **Auth.** 任何获得登录会话的内容 — `set-cookie` 行、
  `fill`/`click` 登录序列，或执行 API 的帮助程序脚本
  跳舞并发出饼干。
- **一次有代表性的交互。**不是整个应用程序 - 一条路径
  证明它正在运行，以屏幕截图结束。
- **特定于应用程序的陷阱。** 只有您实际遇到的陷阱。

## 重复出现的问题

- **反应控制输入。** `eval el.value = '…'` 不触发
  React 的 onChange。使用 `fill` / `type` — 它们经过剧作家的
  输入管道。
- **Websockets /长轮询。** `wait-idle` 永远不会解决。 `wait-for`
  您实际需要的元素。
- **第一次绘制速度慢。** Vite/Next 按需编译路线；第一个
  `nav` 可能需要 10 秒以上。 `wait-for` 处理它；原始 `sleep` 没有。
- **`screenshot-element <sel>`** 裁剪为一个元素 - 当
  diff 位于特定组件中，而不是整个页面中。
- **在声明成功之前检查 `console --errors`。** 页面可以
  每次获取数据时渲染其外壳 500 秒。