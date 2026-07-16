---
doc_type: task-list
task: code-review-subagent-model-config
goal: Prevent cs-code-review from using Explore subagent model for independent code review
status: archived
workflow: issue
owner_skill: cs-task
created: 2026-06-30
updated: 2026-06-30
archived: 2026-06-30
related_docs:
  - .codestable/issues/2026-06-30-code-review-subagent-model-config/code-review-subagent-model-config-fix-note.md
  - .codestable/issues/2026-06-30-code-review-subagent-model-config/code-review-subagent-model-config-code-review.md
---

# Prevent cs-code-review from using Explore subagent model for independent code review

## 1. 任务目标

修复 `cs-code-review` 在 Cursor 中启动独立 reviewer 时可能使用 Explore subagent 快速模型预设的问题，改为项目本地配置优先、当前对话模型兜底。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 记录问题与修复范围
- [x] 更新 `cs-code-review` 子代理模型配置规则
- [x] 更新 review 报告模板
- [x] 增加合同测试
- [x] 运行验证并完成 review / archive

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| fix-note | `.codestable/issues/2026-06-30-code-review-subagent-model-config/code-review-subagent-model-config-fix-note.md` | cs-code-review 独立 reviewer 模型配置修复记录 |
| code-review | `.codestable/issues/2026-06-30-code-review-subagent-model-config/code-review-subagent-model-config-code-review.md` | issue 代码审查报告，状态 passed |

## 5. 执行步骤

### 1. 记录问题与修复范围

- 状态：done
- 来源：用户截图与说明
- 完成信号：fix-note 落盘

### 2. 更新 `cs-code-review` 子代理模型配置规则

- 状态：done
- 来源：issue fix
- 完成信号：技能明确要求 `.codestable/config/code-review-subagent.yaml`、首次询问 owner、配置不可用时继承当前对话模型

### 3. 更新 review 报告模板

- 状态：done
- 来源：issue fix
- 完成信号：Independent Review 区记录 Cursor config

### 4. 增加合同测试

- 状态：done
- 来源：issue fix
- 完成信号：workflow contracts 覆盖禁止 Explore subagent 预设兜底，并覆盖 report-template 与配置字段结构

### 5. 运行验证并完成 review / archive

- 状态：done
- 来源：workflow gate
- 完成信号：合同测试通过，code review passed，Task 已归档

## 6. 中断恢复提示

已归档，无需续跑。

## 7. 完成与归档记录

- 2026-06-30：issue fix、code review 和 Task archive 已完成。
