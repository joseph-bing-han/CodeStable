---
doc_type: issue-report
issue: 2026-07-11-task-archive-runtime-guard-regression
status: confirmed
severity: P1
summary: Task 归档完成后旧 active 路径被异步写入重新创建
tags:
  - cs-task
  - archive
  - concurrency
  - workflow-spine
---

# Task 归档后 active 文件重现回归 Issue Report

## 1. 问题现象

执行 CodeStable `cs-task archive` 后，Task 已从 `.codestable/tasks/active/` 移入 `.codestable/tasks/archived/`，归档目标状态为 `archived`，即时检查也确认 active 源文件不存在。后续对话或工具调用期间，部分旧 active 源路径却被重新创建，导致同一 Task 同时存在 active 与 archived 两份文件。

本次三个连续归档 Task 中有两个发生重现。重新出现的文件最终通过显式删除恢复一致性。

## 2. 复现步骤

1. 打开并多次编辑 `.codestable/tasks/active/{task}.md`。
2. 在部分编辑调用 interrupted、延迟返回或旧 buffer 仍可能存在时执行 `mv` 归档。
3. 只更新 archived 目标，把状态改为 `archived`。
4. 确认 archived 目标存在且 active 源路径不存在。
5. 继续处理其他 Task 或等待先前工具结果返回。
6. 再次枚举 `.codestable/tasks/active/`。
7. 观察到部分已归档 Task 的旧 active 路径重新出现。

复现频率：本次三个 Task 中出现两个，尚未在独立最小仓库稳定复现。

## 3. 期望 vs 实际

**期望行为**：归档是受控状态迁移。active 文件移动到 archived 后，旧 active 路径永久失效；任何延迟编辑或旧 buffer 写回都必须被拒绝、识别为 stale rewrite，或者在归档稳定性验证中安全清理。

**实际行为**：当前只有技能文字协议要求 Agent 不再写旧路径，没有可执行归档器或写入守卫。底层延迟写入仍可重新创建 active 文件，破坏 Task source-of-truth。

## 4. 环境信息

- 涉及模块 / 功能：CodeStable `cs-task archive`、Task recovery/history
- 相关文件 / 函数：`plugins/codestable/skills/cs-task/SKILL.md`、`plugins/codestable/skills/cs-task/reference.md`、`tests/test_workflow_contracts.py`
- 运行环境：Cursor IDE coding agent、macOS、`.codestable/` 可能被 `.gitignore` 忽略
- 现场项目：KCPortal
- 其他上下文：工具调用曾先显示 interrupted，后续又返回 `Prior tool result`；该现象说明中断不一定等于底层写入已取消。

## 5. 严重程度

**P1** — 问题破坏 CodeStable Task source-of-truth 和归档状态机，可能导致已完成任务被错误恢复、重复执行 gate 或重复归档。

## 备注

- 关联历史 Issue：`.codestable/issues/2026-06-30-task-archive-stale-active-rewrite/`。
- 历史修复明确未引入可执行归档器，只增加了文字协议和字符串契约测试。
- 本次按新回归 Issue 处理，目标是把一致性要求落实到可执行 runtime 和行为测试。
