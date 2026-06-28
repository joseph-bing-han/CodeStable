## 背景

在维护 CodeStable 自身技能时，`cs-code-review` 曾经把 `Use Task tool with codestable:code-reviewer type` 当成可直接执行的运行时能力，并把完整排障记录写进了 `docs/2026-07-04-18-51-cs-code-review-subagent-bridge-fix.md`。但当前仓库已经接入 CodeStable，这类维护结论不应继续留在 `docs/` 里做阶段记录，而应沉淀到 `.codestable/compound/` 作为可复用知识。

## 结论

1. `Task tool` / `Task agent` 在 CodeStable 中只是逻辑派发合约，不保证当前 runtime 暴露同名字面工具；真实执行必须遵循共享的 `Subagent Runtime Mapping`。
2. `cs-code-review` 的正确执行顺序是：优先命名 reviewer `codestable:code-reviewer`，否则桥接到只读 `generalPurpose` subagent，并把 `plugins/codestable/agents/code-reviewer.md` 与 `plugins/codestable/skills/cs-code-review/code-reviewer.md` 合并成真实审查消息；只有两条 subagent 路径都不可用时才允许 self review。
3. 这套约束已经扩展到仓库中其他仍写 `Task tool` / `Task agent` 的技能，并通过 `resolve-task-agent-dispatch.py`、`validate-implementation-review.py`、`check-plugin-package.py` 和对应测试显式防回归。
4. 仅更新插件模板还不够，CodeStable 源仓自带的 `.codestable/tools/resolve-task-agent-dispatch.py` 与 `.codestable/reference/tools.md` 也必须同步到最新模板；否则插件测试可能通过，但当前仓库自己的 review gate 仍会因骨架缺失而失败。
5. 所有 reviewer 相关模型口径现已统一为 `gpt-5.5[fast=false,reasoning=xhigh]`；模板、agent prompt、review skill 文案与测试断言都必须引用同一字符串，避免 helper 读取真实 frontmatter 后与测试期望分叉。

## 证据

- 关键实现文件：
  - `.codestable/tools/resolve-task-agent-dispatch.py`
  - `.codestable/reference/tools.md`
  - `plugins/codestable/skills/cs-code-review/SKILL.md`
  - `plugins/codestable/skills/cs-code-review/code-reviewer.md`
  - `plugins/codestable/skills/cs-code-review/agents/openai.yaml`
  - `plugins/codestable/skills/cs-code-review/references/report-template.md`
  - `plugins/codestable/skills/cs-onboard/reference/tools.md`
  - `plugins/codestable/skills/cs-onboard/tools/resolve-task-agent-dispatch.py`
  - `plugins/codestable/skills/cs-onboard/tools/validate-implementation-review.py`
  - `tools/check-plugin-package.py`
- 关键测试文件：
  - `tests/test_resolve_task_agent_dispatch.py`
  - `tests/test_workflow_contracts.py`
  - `tests/test_validate_implementation_review.py`
  - `tests/test_plugin_package.py`
- 新增的自举同步断言：`tests/test_workflow_contracts.py::test_self_hosted_runtime_mapping_tool_stays_synced`
- 验证命令：

```bash
uv run --with pytest pytest "tests/test_resolve_task_agent_dispatch.py" "tests/test_workflow_contracts.py" "tests/test_validate_implementation_review.py" "tests/test_plugin_package.py" -q
```

- 验证结果：`42 passed in 2.62s`
- 额外验证：`python3 .codestable/tools/resolve-task-agent-dispatch.py --help` 可正常输出 CLI 帮助，说明当前仓库自带 helper 可执行。
- 已移除旧的 `docs/2026-07-04-18-51-cs-code-review-subagent-bridge-fix.md`，避免继续把 CodeStable 内部维护记录留在面向外部读者的 `docs/` 目录。
