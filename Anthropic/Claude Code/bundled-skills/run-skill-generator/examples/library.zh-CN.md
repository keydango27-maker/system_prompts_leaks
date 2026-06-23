<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/run-skill-generator/examples/library.md -->
<!-- source-sha256: f8786bf38002ab96380297ea2c5b789a3a1a801480a5ce1754f51516ed2897f8 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

# 示例：库/SDK

图书馆在流程意义上没有 "run" 步骤 - 没有
服务器启动，没有 CLI 调用。对于库来说，运行技能大约是：

1. **从源代码构建**库
2. **运行测试套件**
3. **一个最小的工作示例**，用于练习库并证明
   安装正确

保持简短。模板的构建和测试部分完成大部分工作。

## 冒烟测试示例

主要的库特定添加是一个小程序（或 REPL 片段）
导入库并做一件真正的事情。代理是这样的
确认“是的，该库可用”：

> ## 验证
>
>```bash
> python -c '
> from mylib import Client
> c = Client()
> print(c.ping())
> '
> # → pong
> ```或者对于编译语言：

>```bash
> cat > /tmp/smoke.go <<GO
> package main
> import "example.com/mylib"
> func main() { println(mylib.Version()) }
> GO
> go run /tmp/smoke.go
> # → v1.2.3
> ```## 示例片段

> ---
> 名称：run-mylib
> 描述：从源代码构建、安装和测试 mylib。当要求验证 mylib 是否工作、运行其测试或构建发行版时使用。
> ---
>
> `mylib` 是一个 Python 库 — "running" 意味着从源代码构建
> 并执行测试套件。
>
> ## 设置
>
>```bash
> pip install -e '.[dev]'
> ```>
> ## 验证
>
>```bash
> python -c 'import mylib; print(mylib.__version__)'
> # → 2.1.0
> ```>
> ## 测试
>
>```bash
> pytest
> ```>
> 测试子集：`pytest tests/unit/`。覆盖范围：`pytest --cov=mylib`。
>
> ## 构建（分发）
>
>```bash
> pip install build
> python -m build
> # → dist/mylib-2.1.0-py3-none-any.whl
> ```## 需要考虑记录的事项

- **开发模式与安装模式。** `pip install -e .` 与
  `pip install .` — 如果行为不同，请说明使用哪个。
- **可选依赖项。** `[dev]`、`[test]`、`[docs]` 附加项以及何时
  每一个都是需要的。
- **生成的代码。** 如果有代码生成步骤（protobuf、OpenAPI 客户端），
  记录它——自述文件中几乎总是缺少它。