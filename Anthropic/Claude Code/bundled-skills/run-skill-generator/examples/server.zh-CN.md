<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run-skill-generator/examples/server.md -->
<!-- source-sha256: 0ea8b8a2d3f65ecb4310bfebf89d6b03a3e0765d2731dcc24f3c35d2546835a4 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

# 示例：Web 服务器 /API

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
> |变量|必填 |默认 |笔记|
> |---|---|---|---|
> | `DATABASE_URL` |是的 | — | Postgres 连接字符串 |
> | `PORT` |没有 | `3000` | |
> | `LOG_LEVEL` |没有 | `info` | `debug` / `info` / `warn` / `error` |