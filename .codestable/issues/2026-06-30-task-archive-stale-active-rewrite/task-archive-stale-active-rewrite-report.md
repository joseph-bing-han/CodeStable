---
doc_type: issue-report
issue: 2026-06-30-task-archive-stale-active-rewrite
status: confirmed
severity: P1
summary: cs-task archive can report success even when the active source path is rewritten after mv
tags:
  - cs-task
  - archive
  - workflow-spine
---

# task-archive-stale-active-rewrite Issue Report

## 1. 问题现象

`cs-task archive` 执行了将 active task 移动到 archived 的 `mv` 命令后，后续仍可能在 `.codestable/tasks/active/{task}.md` 重新出现同名 active 文件；如果只依赖一次 shell `test ! -e active && test -e archived` 的结果，会误报归档成功。

## 2. 复现步骤

1. 创建 `.codestable/tasks/active/task-archive-move-original.md`，内容为 `status: completed`、`archived: null`。
2. 执行类似命令：`mv .codestable/tasks/active/task-archive-move-original.md .codestable/tasks/archived/2026-06-30-task-archive-move-original.md`。
3. 只更新 archived 目标文件为 `status: archived`、`archived: 2026-06-30`。
4. 观察到：active 路径之后又出现旧内容版本，且 archived 目标文件也存在。

复现频率：已在本次对话中稳定观察到一次；触发条件疑似与旧 active 路径写入上下文、编辑器 buffer 或最终验证时机有关。

## 3. 期望 vs 实际

**期望行为**：`mv` 后所有后续写入只能指向 archived 目标文件，最终回复前必须重新确认 active 源路径不存在；如果 active 源路径仍存在，归档必须失败并清理。

**实际行为**：归档流程曾用一次 shell `test` 结果报告成功，但用户随后在同一仓库同一分支执行 `ll .codestable/tasks/active/task-archive-move-original.md`，证明 active 源路径仍存在。

## 4. 环境信息

- 涉及模块 / 功能：CodeStable `cs-task archive` workflow
- 相关文件 / 函数：`cs-task/SKILL.md`、`cs-task/reference.md`、`tests/test_workflow_contracts.py`
- 运行环境：本地 Cursor / macOS，项目 `.codestable/` 可能被 ignore
- 其他上下文：同一 task 的 archived 文件为 `status: archived`，active 残留为旧的 `status: completed` 内容。

## 5. 严重程度

**P1** — Task archive 是 CodeStable workflow spine 的收尾 gate；误报成功会导致 active 和 archived 同时存在，破坏后续 recovery / history / archive 可信度。

## 备注

本次走快速修复：根因边界已经明确，改动范围限定为 `cs-task` archive 协议、reference 和 workflow contract test。
