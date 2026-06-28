---
doc_type: issue-fix
issue: 2026-07-01-code-review-bootstrap-shortcut
status: completed
related: [code-review-bootstrap-shortcut-report.md, code-review-bootstrap-shortcut-analysis.md]
tags: [workflow, code-review, subagent]
---

# cs-code-review bootstrap 短路 Fix Note

## 1. 修复范围

本次修复 `cs-code-review` 在已有 blocked review 报告存在时，未重新执行 reviewer bootstrap 就直接沿用旧结论的问题。

改动文件：

- `cs-code-review/SKILL.md`
- `tests/test_workflow_contracts.py`
- `.codestable/issues/2026-07-01-code-review-bootstrap-shortcut/*`
- `.codestable/tasks/active/code-review-bootstrap-shortcut.md`

## 2. 修复内容

- 在 `cs-code-review/SKILL.md` 的启动检查顶部新增 `Reviewer bootstrap（不可跳过）` 阶段。
- 明确每次执行 `cs-code-review` 都必须重新验证当前事实，不能用旧 review 报告的 `blocked` / `pending` / `passed` 结论替代当轮执行。
- 明确旧 review 报告只能作为历史输入，managed agent 是否存在、是否已启动、actual reviewer 是否返回，都必须用当前文件系统和当轮执行结果重新验证。
- 明确在 Cursor / Claude Code / Codex runtime 下，输出新 verdict、询问 local-only fallback、或沿用旧 blocker 前，必须先读取 reviewer config、运行 `configure-review-subagent.py`、验证 `managed_agent_path` 对应文件和 marker / model。
- 明确当前文件系统读取 managed agent 返回 fileNotFound 时，必须立即运行配置脚本修复，禁止复述旧 blocked 结论。
- 在 `tests/test_workflow_contracts.py` 中新增 contract assertions，锁住上述不可跳过规则。
- 在 `configure-review-subagent.py` 生成的 managed reviewer 内容中加入 self-bootstrap guard：当 `.codestable/config/code-review-subagent.yaml` 存在但 `.cursor/agents/cs-code-reviewer.md` / `.claude/agents/cs-code-reviewer.md` / `.codex/agents/cs-code-reviewer.toml` 缺失时，reviewer 不能直接汇报 invocation blocked，必须先运行配置脚本生成或修复自身文件，并重新验证 marker / name / model。
- 在 `tests/test_configure_review_subagent.py` 和 `tests/test_workflow_contracts.py` 中补充 self-bootstrap guard 断言，确保 Cursor / Claude Code / Codex 三种 managed reviewer 文件都带有自修复指令。

## 3. 验证计划

- 运行 `python3 -m py_compile tests/test_workflow_contracts.py`。
- 运行目标 workflow contract 测试，确认新增断言通过。
- 运行 `python3 -m py_compile cs-code-review/scripts/configure-review-subagent.py tests/test_configure_review_subagent.py tests/test_workflow_contracts.py`。
- 运行 `tests/test_configure_review_subagent.py` 和 `tests/test_workflow_contracts.py` 的目标测试，确认 self-bootstrap guard 断言通过。
- 下一轮 `/cs-code-review` 必须实际执行 reviewer bootstrap，而不是直接读取旧 blocked 报告后结束。

## 4. 剩余风险

- 本次修复把 workflow 规则和契约测试补强，但是否能在当前 Cursor runtime 中真正按项目 custom agent 名称启动 `cs-code-reviewer`，仍取决于 runtime 是否暴露该调用入口。
- 如果 runtime 无法直接调用项目 custom subagent，新的正确行为应该是在配置脚本执行并 managed agent 验证通过后，再报告 invocation blocked。
