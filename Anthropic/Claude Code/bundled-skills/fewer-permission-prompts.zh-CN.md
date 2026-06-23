<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Anthropic/Claude Code/bundled-skills/fewer-permission-prompts.md -->
<!-- source-sha256: 2f1a4e61995998fd3c77a73c43051b77847ce633c0a48bfdf3054172be4831b3 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

---
name: fewer-permission-prompts
description: Scan your transcripts for common read-only Bash and MCP tool calls, then add a prioritized allowlist to project .claude/settings.json to reduce permission prompts.
---
# 更少的权限提示

查看我的成绩单 MCP 和 bash 工具调用，并基于这些内容，制定一个模式的优先级列表，我应该将其添加到我的权限允许列表中，以减少权限提示。重点关注只读命令。

权限的格式为：`Bash(foo*)`、`Bash(foo)`、`Bash(foo bar *)`、`mcp__slack__slack_read_thread`等。

然后，将它们添加到 `permissions.allow` 下的项目 `.claude/settings.json` 中。

## 步骤

1. **查找记录。** 会话记录位于 `~/.claude/projects/<sanitized-cwd>/*.jsonl`。每行都是一个 JSON 对象。工具调用显示为 `assistant` 消息，其中包含 `message.content[]` 条目 `type: "tool_use"`。 `name` 字段标识工具（例如 `"Bash"`、`"mcp__slack__slack_read_thread"`）；对于 Bash，`input.command` 是 shell 字符串。

   扫描用户项目目录中的最新记录（而不仅仅是当前项目），以便允许列表反映他们的实际使用情况。将扫描限制在合理数量的最近会话（例如 50 个最近修改的 JSONL 文件），以便保持快速。

2. **提取工具调用频率。**
   - 对于 `Bash` 调用：解析 `input.command`，获取前导命令令牌（处理 `sudo`、`timeout`、管道、`&&`、env-var 前缀）。记录命令 + 第一个子命令对（例如 `git status`、`gh pr view`、`ls`、`cat`）。
   - 对于 MCP 调用：记录完整的工具名称（例如 `mcp__slack__slack_read_thread`）。
   - 计算扫描记录中的出现次数。

3. **过滤为只读。** 仅保留不会改变状态的命令。只读示例：`ls`、`cat`、`pwd`、`git status`、`git log`、`git diff`、 `git show`、`git branch`、`rg`、`grep`、`find`、`head`、 `tail`、`wc`、`file`、`which`、`echo`、`date`、 `gh pr view`、`gh pr list`、`gh pr diff`、`gh issue view`、`gh issue list`、`gh run list`、 `gh run view`、`gh api` (GET)、`bun run typecheck`、`bun run lint`、`bun run test`（适用于不突变），`docker ps`，`docker logs`，`kubectl get`，`kubectl describe`，`ps`，`top`， `df`、`du`、`env`、`printenv`、任何 MCP 工具其名称为 `read`/`get`/`list`/`search`/`view`。

   删除任何写入、删除、重命名、推送、合并、安装或运行具有副作用的构建/测试的内容。如有疑问，请将其排除。

   **切勿将允许任意代码执行的模式列入白名单。** 其中任何一个的通配符规则（例如 `Bash(python3:*)`）相当于允许任意代码执行。此列表并不详尽 - 将相同的规则应用于同一类别中的任何内容：
   - 口译员：`python`/`python3`、`node`、`bun`、`deno`、`ruby`、`perl`、`php`、`lua` 等
   - 外壳：`bash`、`sh`、`zsh`、`fish`、`eval`、`exec`、 `ssh`等
   - 封装类型：`npx`、`bunx`、`uvx`、`uv run` 等
   - 任务运行程序通配符：`npm run *`、`yarn run *`、`pnpm run *`、`bun run *`、`make *`、`just *`、 `cargo run *`、`go run *` 等 — 精确的 `Bash(bun run typecheck)` 就可以，`Bash(bun run *)` 则不然
   - `gh api *`、`docker run`/`exec`、`kubectl exec`、`sudo` 及类似产品

4. **删除命令 Claude Code 已自动允许。** 这些不需要允许列表条目 - 它们从不提示。如果您在文字记录中看到其中任何内容，请跳过它们；不要向用户推荐它们。

   - **始终自动允许（任何参数）：** `cal`、`uptime`、`cat`、`head`、`tail`、 `wc`、`stat`、`strings`、`hexdump`、`od`、`nl`、 `id`、`uname`、`free`、`df`、`du`、`locale`、 `groups`、`nproc`、`basename`、`dirname`、`realpath`、`cut`、 `paste`、`tr`、`column`、`tac`、`rev`、`fold`、 `expand`、`unexpand`、`fmt`、`comm`、`cmp`、`numfmt`、 `readlink`、`diff`、`true`、`false`、`sleep`、`which`、 `type`、`expr`、`test`、`getconf`、`seq`、`tsort`、 `pr`、`echo`、`printf`、`ls`、`cd`、`find`。
   - **仅自动允许零参数：** `pwd`、`whoami`、`alias`。
   - **自动允许的精确形式：** `claude -h`、`claude --help`、`node -v`、`node --version`、`python --version`、 `python3 --version`、`ip addr`。
   - **仅使用安全标志自动允许（已验证）：** `xargs`、`file`、`sed`（只读表达式）、`sort`、`man`、 `help`、`netstat`、`ps`、`base64`、`grep`、`egrep`、 `fgrep`、`sha256sum`、`sha1sum`、`md5sum`、`tree`、`date`、 `hostname`、`info`、`lsof`、`pgrep`、`tput`、`ss`、 `fd`、`fdfind`、`aki`、`rg`、`jq`、`uniq`、 `history`、`arch`、`ifconfig`、`pyright`。
   - **所有 git 只读子命令：** `git status`、`git log`、`git diff`、`git show`、`git blame`、 `git branch`、`git tag`、`git remote`、`git ls-files`、`git ls-remote`、`git config --get`、 `git rev-parse`、`git describe`、`git stash list`、`git reflog`、`git shortlog`、`git cat-file`、 `git for-each-ref`、`git worktree list`等
   - **所有 gh 只读子命令：** `gh pr view`、`gh pr list`、`gh pr diff`、`gh pr checks`、`gh pr status`、 `gh issue view`、`gh issue list`、`gh issue status`、`gh run view`、`gh run list`、`gh workflow list`、 `gh workflow view`、`gh repo view`、`gh release view`、`gh release list`、`gh api` (GET)、 `gh auth status`等
   - **Docker 只读子命令：** `docker ps`、`docker images`、`docker logs`、`docker inspect`。

   事实来源：`src/tools/BashTool/readOnlyValidation.ts`（`READONLY_COMMANDS`、`READONLY_NOARGS`、`READONLY_EXACT`、`COMMAND_ALLOWLIST`) 和 `src/utils/shell/readOnlyCommandValidation.ts` (`GIT_READ_ONLY_COMMANDS`、`GH_READ_ONLY_COMMANDS`、`DOCKER_READ_ONLY_COMMANDS`、 `RIPGREP_READ_ONLY_COMMANDS`、`PYRIGHT_READ_ONLY_COMMANDS`）。如果用户在此存储库中并且您不确定命令是否被覆盖，请 grep 这些文件而不是猜测。

5. **选择模式形式。** 使用仍能覆盖观察到的用法的最窄模式：
   - 如果用户运行多个变体（`git log`、`git log --oneline`、`git log main..HEAD`）：使用 `Bash(git log *)` — 请注意 `*` 之前的空格，这是前缀匹配正常工作所必需的。
   - 如果单个精确调用很常见：使用不带通配符的 `Bash(foo)`。
   - 对于 MCP：逐字使用完整的工具名称（不需要通配符；它们已经是特定的）。
   - 切勿将模式扩大到与上述规则冲突的程度（没有任意代码执行，没有突变/副作用）。

6. **优先级。** 按计数降序排列。删除出现次数少于 3 次的任何内容 — 不值得列入许可名单。将列表限制在顶部~20，以便用户可以浏览它。

7. **以降价表的形式向用户呈现优先级列表**，其中包含以下列：排名、模式、计数、单行描述。示例：

   | ＃|图案|计数|笔记|
   |---|---------|--------|--------|
   | 1 | `Bash(git status *)` | 142 | 142回购状态检查 |
   | 2 | `Bash(gh pr view *)` | 87 | 87公关检查|
   | 3 | `mcp__slack__slack_read_thread` | 54 | 54 Slack 线程读取 |

8. **合并到当前项目中的`.claude/settings.json`**（不是`~/.claude/settings.json`，不是`.claude/settings.local.json`）。如果该文件不存在，则创建该文件。保留 `permissions.allow` 中的现有密钥和现有条目；对已有内容进行重复删除；不要删除任何东西；不要对不相关的字段重新排序。

9. **报告回来。** 告诉用户您添加了哪些内容（计数+一些示例）、白名单中已有哪些内容、您跳过了哪些内容以及原因（例如“删除了 `rm` 和 `git push` - 不是只读的；删除了`cat`/`ls`/`git status` — 已自动允许，无需规则”）。

请勿向 `permissions.deny` 或 `permissions.ask` 添加任何内容。不要触摸任何其他设置字段。