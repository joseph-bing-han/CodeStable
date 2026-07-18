---
doc_type: task-list
task: historical-review-evidence-remediation
goal: 修复历史 CodeStable review 证据合规遗留
status: archived
workflow: issue
owner_skill: cs-issue
created: 2026-07-17
updated: 2026-07-18
archived: 2026-07-18
related_docs:
  - .codestable/issues/2026-07-17-historical-review-evidence-remediation/historical-review-evidence-remediation-report.md
  - .codestable/issues/2026-07-17-historical-review-evidence-remediation/historical-review-evidence-remediation-analysis.md
  - .codestable/issues/2026-07-17-historical-review-evidence-remediation/approval-report.md
  - .codestable/issues/2026-07-17-historical-review-evidence-remediation/historical-review-evidence-remediation-review.md
  - .codestable/features/2026-07-16-cursor-plugin-v104-hardening/cursor-plugin-v104-hardening-acceptance.md
---

# 修复历史 CodeStable review 证据合规遗留

## 1. 任务目标
将 `codestable-doctor.py` 报出的历史 review 证据遗留分类处置，恢复 CodeStable 健康检查可通过状态。

## 2. 当前状态
archived

全部执行步骤已完成：历史 Task 回填、legacy review 兼容、SemVer fail-closed、Cursor Feature 验收与 requirement 回写、剩余 P1 review 证据补齐、本 Issue independent review passed。待 archive。

## 3. Agent 原生 Tasks 同步区
无。

## 4. CodeStable 文档索引
- `.codestable/issues/2026-07-17-historical-review-evidence-remediation/historical-review-evidence-remediation-report.md`（confirmed）
- `.codestable/issues/2026-07-17-historical-review-evidence-remediation/historical-review-evidence-remediation-analysis.md`（confirmed）
- `.codestable/issues/2026-07-17-historical-review-evidence-remediation/approval-report.md`（approved）
- `.codestable/issues/2026-07-17-historical-review-evidence-remediation/historical-review-evidence-remediation-review.md`（passed，round 1）
- `.codestable/features/2026-07-16-cursor-plugin-v104-hardening/cursor-plugin-v104-hardening-acceptance.md`（passed）

## 5. 执行步骤
- [x] 确认 Issue 报告并固定标准处理路径。
- [x] 审计 25 个 P1 finding 的原始 review 证据与可迁移性。
- [x] 回填 14 个缺失的历史 Task archive，并保留 1 个既有旧格式归档。
- [x] 实现历史 Issue `*-code-review.md` 兼容识别并添加回归测试。
- [x] 派发并完成 16 个独立 focused review。
- [x] owner 确认将 10 个实现/验收 blocker 集中并入当前 Issue。
- [x] 对通过的 6 个单元写入独立 review evidence；为修复批次启动复审。
- [x] 收敛 reviewer 契约到用户意图：优先独立 subagent；不可用时当前主模型最高档 `reviewer: self`（非 Explore/Fast）。
- [x] 完成 Cursor Feature 的 canonical review、acceptance 和 requirement delta 机械回写。
- [x] 处理剩余历史 P1 evidence 与旧 archive compatibility findings。
- [x] 运行 targeted tests、源码 doctor、runtime sync 与 `git diff --check`。
- [x] 通过本 Issue 的独立 code review 后完成并归档 Task。

## 6. 中断恢复提示
本 Task 已 completed，下一步 archive。

## 7. 完成与归档记录
- 2026-07-18：review passed；doctor findings 0；Cursor Feature 闭环；准备 archive。
