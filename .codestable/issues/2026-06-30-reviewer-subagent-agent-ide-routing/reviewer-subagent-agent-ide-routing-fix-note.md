---
doc_type: issue-fix
issue: 2026-06-30-reviewer-subagent-agent-ide-routing
status: fixed
created: 2026-06-30
updated: 2026-06-30
---

# reviewer-subagent-agent-ide-routing 修复记录

## 1. 修复内容

- 新增 `cs-code-review/scripts/configure-review-subagent.py`。
- 脚本支持 `--agent-ide auto|cursor|claude-code|codex`。
- 脚本读取 `.codestable/config/code-review-subagent.yaml` 并生成 `cs-code-reviewer` managed reviewer。
- Cursor / Claude Code / Codex 分别写入官方 custom subagent 路径。
- 对已有未带 CodeStable managed marker 的同名文件直接拒绝覆盖。
- `cs-code-review/SKILL.md` 明确按 `SKILL_DIR` 运行检测脚本和配置脚本。
- `cs-code-review/references/subagent-config.md` 与 report template 同步 `cs-code-reviewer` 路径。
- `cs-onboard/SKILL.md` 增加初始化 reviewer 配置的要求。
- 新增 `tests/test_configure_review_subagent.py`，并扩展 `tests/test_workflow_contracts.py`。
- 修复 `cs-code-review` 的执行顺序：禁止在运行 `configure-review-subagent.py` 并确认 managed agent 文件前询问 owner 是否接受 local-only fallback。
- 当前仓库已实际运行配置脚本，生成 `.cursor/agents/cs-code-reviewer.md`，确认 marker 和 model 均正确。

## 2. 验证

已执行并通过：

```bash
python3 -m py_compile "cs-code-review/scripts/configure-review-subagent.py" "/Users/joseph/.agents/skills/cs/cs-code-review/scripts/configure-review-subagent.py" "tests/test_configure_review_subagent.py" "tests/test_workflow_contracts.py"
```

已执行并通过 fixture 模拟测试，覆盖 `tests/test_*.py` 中的直接测试函数，包括新增的 reviewer 配置测试。

已执行 `--agent-ide auto --dry-run`，返回 0，证明当前环境下自动识别路径可运行。

## 3. 剩余限制

当前工具环境还没有暴露“按项目 custom subagent 名称直接调用 `cs-code-reviewer`”的能力，因此 code review gate 仍需要真实 custom subagent 回执，或由 owner 明确接受 local-only fallback。
