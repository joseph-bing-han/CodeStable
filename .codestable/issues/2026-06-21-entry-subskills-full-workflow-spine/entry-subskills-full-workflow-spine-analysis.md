---
doc_type: issue-analysis
issue: 2026-06-21-entry-subskills-full-workflow-spine
status: confirmed
root_cause_type: missing-guard
related:
  - entry-subskills-full-workflow-spine-report.md
tags: [workflow, entry-skill, orchestration]
---

# 子入口缺少完整工作流闭环根因分析

## 1. 问题定位

| 关键位置 | 说明 |
|---|---|
| `.codestable/reference/shared-conventions.md:177` | 只定义了“自动编排 / handoff / 结构化提问”，没有显式定义“所有用户可直达入口都等价于完整入口” |
| `.codestable/reference/system-overview.md:12` | 总览把 `cs` 描述成统一入口，但没有把 direct-entry 等价原则推广到其它入口技能 |
| `cs-brainstorm/SKILL.md:18` | 只约束了本 lane 的讨论 / 落盘 / Task 行为，没有明确规定进入下游后仍属于同一条完整 workflow 主线 |
| `cs-issue/SKILL.md:29` | 说明了本地路由和 Task 守卫，但没有把“直接从这里进入也必须闭环到 review / archive / 收尾建议”提升成入口级规则 |

## 2. 失败路径还原

**正常路径**：用户从 `cs` 进入 → `cs` 先识别场景 → 自动 handoff 给 `cs-feat` / `cs-issue` / `cs-roadmap` 等下游 → 下游继续按 Task、阶段 review、code review 与 archive 规则推进到闭环。

**失败路径**：用户直接从某个子入口进入 → 该 skill 只强调本地分诊、本地阶段或本地落盘 → 共享协议没有补上一条“这也是完整入口，后续必须继续沿下游 workflow 跑到底” → direct entry 被解释成局部入口，闭环语义弱化。

**分叉点**：共享 reference 和多个入口 skill 都缺少“入口等价”守卫，导致是否继续完整闭环取决于局部文案而不是统一协议。

## 3. 根因

**根因类型**：missing-guard

**根因描述**：CodeStable 已经有自动编排协议和 Task 主线协议，但它们主要约束“下一步怎么继续”和“首次落盘前必须有 Task”，没有单独固化“所有用户可直接触发的入口 skill 都必须被当作完整入口，而不是局部入口”。因此 `cs` 根入口被自然理解为完整 orchestrator，子入口却只剩局部阶段语义，形成 direct-entry 行为漂移。

**是否有多个根因**：有。主根因是共享协议缺守卫；次根因是 system-overview 与多个入口 skill 没把 direct-entry 完整闭环写成统一口径。

## 4. 影响面

- **影响范围**：所有用户可直接进入的 workflow 入口，尤其是 `cs-brainstorm`、`cs-issue`、`cs-feat`、`cs-refactor`、`cs-roadmap`、`cs-audit`
- **潜在受害模块**：runtime 读取 `.codestable/reference/system-overview.md` 的路径、未来新增入口 skill、onboard 模板副本
- **数据完整性风险**：无业务数据风险，但有流程数据风险——Task、review、archive 可能被错误弱化
- **严重程度复核**：维持 P1；这是核心 workflow 契约漂移，不是单点文案问题

## 5. 修复方案

### 方案 A：只补 `cs-issue` 与 `cs-brainstorm`

- **做什么**：在两个最明显出问题的入口 skill 里补充“direct entry 也要完整闭环”的说明
- **优点**：改动少、落地快
- **缺点 / 风险**：其它入口仍可能继续漂移；共享协议没有真正修复
- **影响面**：2 个 skill，无法防止未来继续分裂

### 方案 B：先补共享协议，再同步入口技能与总览

- **做什么**：在 shared-conventions / system-overview 里新增“入口等价 + 完整主线”规则，再同步 `cs`、`cs-feat`、`cs-issue`、`cs-brainstorm`、`cs-refactor`、`cs-roadmap`、`cs-audit`
- **优点**：统一约束、直接修复 direct-entry 语义、未来新增入口也有参照
- **缺点 / 风险**：需要改多个文件并保持文案一致
- **影响面**：共享 reference、当前项目副本、入口 skill 包

### 方案 C：收缩能力，只保留 `cs` 为唯一完整入口

- **做什么**：把子入口全部降级成局部工具，要求用户总是先走 `cs`
- **优点**：定义简单
- **缺点 / 风险**：违背用户现在的目标，也削弱 direct-entry 体验
- **影响面**：所有子入口定位都会改变

### 推荐方案

**推荐方案 B**，理由：问题根源是缺少共享入口守卫，不是单个 skill 写漏一句话；必须先补统一协议，再把关键入口同步到同一口径，才能真正保证 direct-entry 的完整闭环。
