<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run-skill-generator/examples/cli.md -->
<!-- source-sha256: 0d6fc899ae53b5aad1f905622ce8e419062d975c87daed0a42072fafde701557 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

# 示例：CLI 工具

CLI 是最简单的情况 — 通常没有后台进程
管理，没有端口，没有生命周期。技能重点是**安装**，
**代表性调用**和**测试**。

## 重要的是

- **如何 get `PATH` 上的二进制文件。** 全局安装？运行通过
  `npx`/`uv run`？构建为 `./target/release/foo`？明确一点。
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