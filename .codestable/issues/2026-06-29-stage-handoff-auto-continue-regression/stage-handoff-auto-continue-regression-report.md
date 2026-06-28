---
doc_type: issue-report
issue: 2026-06-29-stage-handoff-auto-continue-regression
status: confirmed
severity: P1
summary: 阶段 handoff 在新版技能中仍可能退化成推荐用户手动运行下一 skill
tags: [workflow, handoff, checkpoint, direct-entry]
---

# 阶段 Handoff 自动续跑回归 Issue Report

## 1. 问题现象

用户从 `cs`、`cs-issue`、`cs-brainstorm` 等独立入口进入新版 CodeStable 时，流程仍可能在阶段边界停成“建议下一步使用某个 skill”，而不是在用户确认后由当前 agent 自动读取并执行下游 skill。

## 2. 复现步骤

1. 直接从 `cs-issue` 入口提出一个 bug。
2. 观察 report 或初步分析阶段完成后的出口文案。
3. 观察到：agent 可能推荐用户使用 `cs-issue-analyze`，而不是把 report review 做成结构化 checkpoint，并在用户选择通过后自动进入分析阶段。

复现频率：新版技能中可复现，尤其出现在阶段 review / handoff 边界。

## 3. 期望 vs 实际

**期望行为**：所有用户可直达入口都等价于完整入口。目标 skill 已确定且没有开放问题时，当前 agent 继续读取并执行目标 `SKILL.md`；需要阶段 review 时，用结构化选项让用户选择，选择继续后自动续跑下游。

**实际行为**：部分技能虽然写了“自动进入”，但出口仍包含“下一步阶段 / 推荐使用某 skill”的弱表述，容易被 runtime 解释为 chat-only 建议，导致 Task、分析文档、实现、review 与归档主线断开。

## 4. 环境信息

- 涉及模块 / 功能：CodeStable workflow skill 文档与共享协议。
- 相关文件 / 函数：`cs/SKILL.md`、`cs-issue/SKILL.md`、`cs-issue-report/SKILL.md`、`cs-issue-analyze/SKILL.md`、`cs-brainstorm/SKILL.md`、`cs-feat/SKILL.md`、`cs-refactor/SKILL.md`、`cs-roadmap/SKILL.md`、`cs-audit/SKILL.md`、`.codestable/reference/shared-conventions.md`、`cs-onboard/reference/shared-conventions.md`、`.codestable/reference/system-overview.md`、`cs-onboard/reference/system-overview.md`
- 运行环境：CodeStable skill runtime / Markdown workflow contract。
- 其他上下文：2026-06-21 已修过 direct-entry 完整入口问题，但新版源码中的共享协议压缩后弱化了“不能停在建议”和“当前 agent 必须执行目标 skill”的硬约束。

## 5. 严重程度

**P1** — 这是 CodeStable 的主流程契约问题，会直接破坏“入口 > 分析文档落地 > 创建 Task > 实施 > review > Task 归档”的连续性。

## 备注

用户已明确要求在 CodeStable 项目中修复，不能只在对话里解释或让用户改用别的入口。
