---
doc_type: task-list
task: task-archive-ignored-active-scan
goal: Prevent cs-task archive from missing active tasks hidden by ignored .codestable paths
status: archived
workflow: issue
owner_skill: cs-task
created: 2026-06-30
updated: 2026-06-30
archived: 2026-06-30
related_docs:
  - .codestable/issues/2026-06-30-task-archive-ignored-active-scan/task-archive-ignored-active-scan-fix-note.md
  - .codestable/issues/2026-06-30-task-archive-ignored-active-scan/task-archive-ignored-active-scan-code-review.md
---

# Prevent cs-task archive from missing active tasks hidden by ignored .codestable paths

## 1. 任务目标

修复 `cs-task` 归档盘点会因 `.codestable/` 被 ignore 而漏扫 active task 的协议缺陷。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 记录归档漏扫问题与根因
- [x] 更新 `cs-task` 启动和 recovery 扫描规则
- [x] 更新 `cs-task/reference.md` 归档残留清理规则
- [x] 增加合同测试
- [x] 运行验证并完成 review / archive

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| fix-note | `.codestable/issues/2026-06-30-task-archive-ignored-active-scan/task-archive-ignored-active-scan-fix-note.md` | cs-task 归档漏扫修复记录 |
| code-review | `.codestable/issues/2026-06-30-task-archive-ignored-active-scan/task-archive-ignored-active-scan-code-review.md` | issue 代码审查报告，状态 passed |

## 5. 执行步骤

### 1. 记录归档漏扫问题与根因

- 状态：done
- 来源：用户截图与 active task 事实
- 完成信号：fix-note 落盘

### 2. 更新 `cs-task` 启动和 recovery 扫描规则

- 状态：done
- 来源：issue fix
- 完成信号：技能明确要求使用不受 ignore 过滤的目录枚举交叉确认 active / archived

### 3. 更新 `cs-task/reference.md` 归档残留清理规则

- 状态：done
- 来源：issue fix
- 完成信号：reference 明确禁止只凭 Glob / rg 的 0 结果判断目录为空

### 4. 增加合同测试

- 状态：done
- 来源：issue fix
- 完成信号：workflow contracts 覆盖 ignore 过滤风险和目录枚举要求

### 5. 运行验证并完成 review / archive

- 状态：done
- 来源：workflow gate
- 完成信号：测试通过，code review passed，Task 已归档且 active 原件已清理

## 6. 中断恢复提示

已归档，无需续跑。

## 7. 完成与归档记录

- 2026-06-30：issue fix、code review 和 Task archive 已完成；active 同名原件已删除。
