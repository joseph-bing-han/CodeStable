---
doc_type: issue-report
issue: 2026-07-16-epic-goal-dispatch-authorization-regression
status: confirmed
issue_path: standard
severity: P1
summary: Epic 统一确认设计后被两个串行授权门阻断，无法通过一次 goal 确认立即开始实现
tags: [cs-epic, goal, authorization, regression]
---

# Epic Goal 派发授权交互回归 Issue Report

## 1. 问题现象

`cs-epic` 完成全部子 feature design-review 并取得统一 design 确认后，会先生成 goal package，
然后停在 `goal-acceptance` 授权门；批准后还会再次停在 `goal-commits` 授权门。用户无法查看并
确认一条完整的 `/goal` 指令后立即开始实现。

## 2. 复现步骤

1. 使用 `cs-epic` 完成 roadmap review 和全部子 feature design-review。
2. 统一确认所有 feature design。
3. 等待 skill 生成 goal package。
4. 观察到 skill 先询问 `goal-acceptance`，并声明批准后还会单独询问 `goal-commits`，未派发实现。

复现频率：稳定复现；CodeStable `1.0.4` 状态机和 runtime 路由均编码了该路径。

## 3. 期望 vs 实际

**期望行为**：全部 design 统一确认后生成并展示完整 `/goal` 指令；用户确认该指令一次后，
系统记录该 goal 的执行和 scoped-commit 授权并立即派发 Goal driver 开始实现。

**实际行为**：goal package 生成后先后出现 `goal-acceptance`、`goal-commits` 两个串行授权门，
`/goal` 指令与实现派发被延后到两次确认之后。

## 4. 环境信息

- 涉及模块 / 功能：`cs-epic` GoalPackage、`codestable-workflow-next.py epic`、goal authorization artifacts
- 相关文件 / 函数：`plugins/codestable/skills/cs-epic/SKILL.md`、`references/goal/protocol.md`、`epic_next`
- 运行环境：CodeStable `1.0.4`，Paseo agent `241a549c-b7e8-4e8d-810d-7253b8c14f7f`
- 其他上下文：Paseo agent 按当前契约执行；不是 provider 临场误判

## 5. 严重程度

**P1** - Epic 核心长程执行被额外人工门阻断；可以通过连续批准绕过，但违背一次 goal 确认即开工的主流程。

## 备注

`push`、registry publish、release、deployment、stable promotion 和 production cutover 不属于本次
合并授权，继续由各自协议保留独立 owner confirmation。
