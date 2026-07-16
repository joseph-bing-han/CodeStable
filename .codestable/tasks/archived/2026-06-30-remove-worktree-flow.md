---
doc_type: task-list
task: remove-worktree-flow
goal: Remove all worktree-specific tools, calls, hooks, tests, and workflow documentation from CodeStable
status: archived
workflow: feature
owner_skill: cs-task
created: 2026-06-30
updated: 2026-06-30
archived: 2026-06-30
related_docs:
  - .codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-design.md
  - .codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-checklist.yaml
  - .codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-design-review.md
  - .codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-review.md
---

# Remove all worktree-specific tools, calls, hooks, tests, and workflow documentation from CodeStable

## 1. 任务目标

去除当前 CodeStable 项目中所有 worktree 相关功能、调用和流程，同时保留 review evidence、Task spine、YAML 校验等非 worktree 质量门禁。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 创建 feature 设计、checklist 与 Task 账本
- [x] 执行 design review 并修正方案阻塞项
- [x] 删除 worktree 工具、hook、流程调用与相关测试
- [x] 更新 README、技能文档、参考文档中的 worktree 表述
- [x] 运行验证并修复新增问题
- [x] 执行 cs-code-review 代码审查

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| design | `.codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-design.md` | worktree flow 移除方案 |
| checklist | `.codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-checklist.yaml` | 实现步骤和验收检查项 |
| design-review | `.codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-design-review.md` | 人审前方案审查，状态 passed |
| review | `.codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-review.md` | 代码审查报告，状态 passed |

## 5. 执行步骤

### 1. 创建 feature 设计、checklist 与 Task 账本

- 状态：done
- 来源：cs-feat-design
- 完成信号：design、checklist、active Task 均已落盘

### 2. 执行 design review 并修正方案阻塞项

- 状态：done
- 来源：cs-feat-design-review
- 完成信号：`remove-worktree-flow-design-review.md` 状态为 passed，且无 blocking finding

### 3. 删除 worktree 工具、hook、流程调用与相关测试

- 状态：done
- 来源：design
- 完成信号：worktree 专属脚本、hook 与对应测试已删除或改写

### 4. 更新 README、技能文档、参考文档中的 worktree 表述

- 状态：done
- 来源：design
- 完成信号：用户可见流程不再要求或推荐 worktree

### 5. 运行验证并修复新增问题

- 状态：done
- 来源：design
- 完成信号：pytest、YAML 校验、关键词残留扫描完成并记录结果

### 6. 执行 cs-code-review 代码审查

- 状态：done
- 来源：workflow gate
- 完成信号：`remove-worktree-flow-review.md` 落盘且 status 为 passed

## 6. 中断恢复提示

已归档，无需续跑。

## 7. 完成与归档记录

- 2026-06-30：feature review passed，Task 已归档到 `.codestable/tasks/archived/2026-06-30-remove-worktree-flow.md`。
