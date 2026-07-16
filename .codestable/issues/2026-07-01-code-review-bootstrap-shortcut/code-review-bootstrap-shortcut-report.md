---
doc_type: issue-report
issue: 2026-07-01-code-review-bootstrap-shortcut
status: confirmed
severity: P1
summary: cs-code-review reuses stale blocked reports without rerunning reviewer bootstrap
tags: [workflow, code-review, subagent]
---

# cs-code-review bootstrap 短路 Issue Report

## 1. 问题现象

用户在当前对话中触发 `/cs-code-review` 后，流程直接读取既有 `blocked` review 报告并复述结论，没有重新运行 reviewer 配置脚本，没有验证 `.cursor/agents/cs-code-reviewer.md` 当前是否存在，也没有尝试启动 `cs-code-reviewer`。

## 2. 复现步骤

1. 在已有 `{slug}-code-review.md` 且状态为 `blocked` 的 CodeStable issue 上再次触发 `/cs-code-review`。
2. 当前文件系统中 `.cursor/agents/cs-code-reviewer.md` 读取结果为 fileNotFound。
3. 观察到：流程仍沿用旧报告里的 blocked 原因，未先运行 `configure-review-subagent.py` 修复或确认 managed reviewer。

复现频率：当前对话中稳定复现一次，规则缺口具备重复风险。

## 3. 期望 vs 实际

**期望行为**：每次执行 `cs-code-review` 都先重新执行 reviewer bootstrap：读取配置、运行配置脚本、验证 managed agent 文件，再尝试调用 `cs-code-reviewer` 或记录真实 runtime 阻塞。

**实际行为**：流程读取旧 review 报告后直接沿用旧 `blocked` 结论，跳过当轮 reviewer bootstrap。

## 4. 环境信息

- 涉及模块 / 功能：`cs-code-review` workflow gate
- 相关文件 / 函数：`cs-code-review/SKILL.md`、`tests/test_workflow_contracts.py`
- 运行环境：Cursor / CodeStable 本地仓库
- 其他上下文：`.gitignore` 忽略 `.cursor/`，旧报告中的 managed agent 状态不能代表当前文件系统事实。

## 5. 严重程度

**P1** — 会让 code review gate 在关键 reviewer evidence 未重新验证时直接给出结论，破坏独立审查链路可信度。

## 备注

用户已明确指出这是流程草率：没有自动配置 reviewer subagent，也没有执行 code-reviewer subagent 的 Review。
