---
doc_type: issue-report
issue: 2026-06-21-entry-subskills-full-workflow-spine
status: confirmed
severity: P1
summary: direct entry 进入子入口时无法稳定承接完整 CodeStable 工作流闭环
tags: [workflow, entry-skill, orchestration]
---

# 子入口缺少完整工作流闭环 Issue Report

## 1. 问题现象

当前仓库里，只有根入口 `cs` 被稳定理解为“会把分析、文档、Task、实施、进度回填、Code Review、Task 归档和收尾串成一条完整主线”的入口；当用户直接从 `cs-issue`、`cs-brainstorm` 等子入口进入时，流程更容易停在局部阶段说明、局部交接或局部落盘，缺少“继续沿下游 workflow 跑到闭环”的明确约束。

## 2. 复现步骤

1. 直接从 `cs` 根入口发起一个需要完整实施的诉求，观察 AI 会把诉求路由到下游并继续强调 Task、review 与归档闭环。
2. 改为直接从 `cs-issue`、`cs-brainstorm` 等子入口发起同类诉求。
3. 观察到：子入口虽然描述了本地分诊或本地阶段规则，但没有把“这也是完整入口、后续仍要沿同一条主线继续到最终闭环”作为统一强约束表达出来。

复现频率：稳定

## 3. 期望 vs 实际

**期望行为**：无论用户是从 `cs` 根入口，还是直接点名某个用户可直达的子入口进入，只要诉求属于同一类 workflow，就应承接同样的完整闭环：该写文档就写文档、该建 Task 就建 Task、该实施就实施、该 review 就 review、该归档就归档，不要求用户退回根入口重启。

**实际行为**：只有 `cs` 根入口明确承担了“完整入口”的角色；多个子入口更像“局部入口”或“局部阶段入口”，导致 direct entry 的闭环语义不稳定，容易在说明、分诊、建议下一步或局部落盘后停住。

## 4. 环境信息

- 涉及模块 / 功能：CodeStable skill 文档本身，重点是 `cs`、`cs-issue`、`cs-brainstorm` 及共享 reference
- 相关文件 / 函数：`/Users/joseph/.agents/skills/cs/*.md`、`.codestable/reference/system-overview.md`、`.codestable/reference/shared-conventions.md`
- 运行环境：repo 文档协议 / skill runtime 语义
- 其他上下文：当前仓库已有自动编排与 Task 主线协议，但 direct-entry 等价原则没有被统一固化

## 5. 严重程度

**P1** — 这会破坏 CodeStable 对用户的核心承诺：入口不同会影响 workflow 是否完整闭环，进而造成 Task、review 或归档被弱化。

## 备注

用户已明确指出：目前只有 `cs` 总入口能稳定承接“分析 → 写文档 → 建 task → 实施修改 → Task 进度回填 → Code Review → Task 归档 → 总结”这条主线，子入口存在缺口。
