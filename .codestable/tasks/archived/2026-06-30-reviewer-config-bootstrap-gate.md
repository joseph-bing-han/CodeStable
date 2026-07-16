---
doc_type: task-list
task: reviewer-config-bootstrap-gate
goal: Ensure reviewer model configuration is initialized during cs-onboard and cannot be silently skipped by cs-code-review
status: archived
workflow: issue
owner_skill: cs-code-review
created: 2026-06-30
updated: 2026-06-30
archived: 2026-06-30
related_docs:
  - cs-code-review/SKILL.md
  - cs-onboard/SKILL.md
  - tests/test_workflow_contracts.py
  - .codestable/issues/2026-06-30-reviewer-config-bootstrap-gate/reviewer-config-bootstrap-gate-code-review.md
---

# Ensure reviewer model configuration is initialized during cs-onboard and cannot be silently skipped by cs-code-review

## 1. 任务目标

修复 CodeStable 在新项目与旧项目两种场景下都可能漏掉 reviewer 模型初始化的问题：新初始化项目要在 `cs-onboard` 阶段先配置 `.codestable/config/code-review-subagent.yaml`，旧项目或漏迁移项目则由 `cs-code-review` 的配置 gate 阻止静默落入 `self review`。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 复盘本次 session 中 reviewer 配置缺失为何没有触发询问
- [x] 收紧 `cs-code-review` 的缺配置 gate，禁止静默 local-only fallback
- [x] 在 `cs-onboard` 中加入 reviewer 配置初始化
- [x] 更新 workflow contract 测试覆盖 onboard + code-review 双层防线
- [x] 同步已安装 skill 副本
- [x] 运行验证
- [x] 执行 CodeStable code review gate

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| skill | `cs-code-review/SKILL.md` | 增加 reviewer 配置存在性启动检查与缺配置禁止静默回退 |
| skill | `cs-onboard/SKILL.md` | 新增 reviewer 配置初始化，要求在初始化 `.codestable/` 时先询问 owner |
| test | `tests/test_workflow_contracts.py` | 增加强制覆盖 onboard 初始化与 code-review 缺配置 gate 的契约断言 |

## 5. 执行步骤

### 1. 复盘缺陷触发条件与根因

- 状态：done
- 来源：issue
- 完成信号：已确认根因是旧 `cs-code-review` 规则把“缺少 config 目录/文件”误并入 local-only fallback 路径，未把配置初始化提升为启动前置门禁。

### 2. 收紧 `cs-code-review` 缺配置 gate

- 状态：done
- 来源：issue
- 完成信号：`cs-code-review/SKILL.md` 明确在 Cursor runtime 下必须先检查 `.codestable/config/code-review-subagent.yaml`，缺父目录、缺文件、空文件、缺字段都先询问 owner 并创建配置。

### 3. 在 `cs-onboard` 前置 reviewer 配置初始化

- 状态：done
- 来源：issue
- 完成信号：`cs-onboard/SKILL.md` 已把 `config/code-review-subagent.yaml` 纳入标准骨架、启动检查、空仓库路径和迁移路径，并要求初始化 `.codestable/` 前先询问 owner。

### 4. 更新测试与同步安装副本

- 状态：done
- 来源：issue
- 完成信号：`tests/test_workflow_contracts.py` 已覆盖 onboard + code-review 双层防线，且已同步 `/Users/joseph/.agents/skills/cs/` 下对应 skill 副本。

### 5. 运行验证

- 状态：done
- 来源：workflow
- 完成信号：已通过直接导入方式执行 `tests/test_workflow_contracts.py` 中全部 `test_` 函数，结果为 `workflow contract tests passed`；`ReadLints` 为 0 diagnostics。

### 6. 执行 CodeStable code review gate

- 状态：done
- 来源：workflow
- 完成信号：已落盘 `.codestable/issues/2026-06-30-reviewer-config-bootstrap-gate/reviewer-config-bootstrap-gate-code-review.md`，独立 reviewer 完成且最终 verdict 为 `passed`。

## 6. 中断恢复提示

已归档，无需续跑。

## 7. 完成与归档记录

2026-06-30：已补建缺失 Task spine，完成 `cs-code-review` 并通过 review gate；已归档到 `.codestable/tasks/archived/2026-06-30-reviewer-config-bootstrap-gate.md`。
