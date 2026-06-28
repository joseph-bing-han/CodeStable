---
doc_type: issue-report
issue: 2026-07-10-reviewer-model-fallback-regression
status: confirmed
severity: P1
summary: CodeStable 审核 gate 会选择 Explore 或其他低思考预算快速子代理执行审核
tags: [workflow, code-review, design-review, subagent, model-routing, regression]
---

# 审核子代理模型降级回归 Issue Report

## 1. 问题现象

在使用 Claude Opus 作为当前主模型执行 CodeStable feature 流程时，`cs-feat-design-review` 未能使用专用高思考预算 reviewer，而是启动了 Explore subagent，并由带 Fast 预设的模型执行独立审核。

`cs-code-review` 当前虽然明确禁止 Explore，但仍允许在 runtime 无法固定 reviewer 模型时使用通用 `generalPurpose` subagent，并仅记录模型降级或未知状态。该规则不能保证最终审核由预定义高思考预算模型或当前主模型完成，因此与截图暴露的问题属于同一类审核模型降级风险。

## 2. 复现步骤

1. 在 Cursor 3.8.24 中使用 Claude Opus 主模型运行标准 `/cs-feat` 流程。
2. 完成 feature design 与 checklist，进入 `cs-feat-design-review` gate。
3. skill 声明的 `scripts/detect-review-agent.py` 不存在，外部 Paseo reviewer 链路不可用。
4. 主 agent 为增强审查自行启动 Explore subagent。
5. 观察到独立审查由带 Fast 预设的快速模型执行，而不是专用高思考预算 reviewer 或当前 Claude Opus 主模型。

复现频率：当前会话证据中稳定复现一次；技能合同允许同类路径再次发生。

## 3. 期望 vs 实际

**期望行为**：CodeStable 的代码审核和设计审核必须优先使用预定义、只读、高思考预算 reviewer。若 runtime 无法显式启动该 reviewer 或无法保证其模型与思考预算，则应由当前主模型执行本地审核，或明确阻塞；不得使用 Explore、Fast 或模型未知的通用子代理完成质量 gate。

**实际行为**：`cs-feat-design-review` 在外部 reviewer 不可用时自行选择 Explore subagent；`cs-code-review` 的 native bridge 规则仍允许在无法固定模型时继续使用通用 subagent，只把模型未知记为 residual risk。

## 4. 环境信息

- 涉及模块 / 功能：`cs-code-review`、`cs-feat-design-review`、Subagent Runtime Mapping、审核报告模板与 workflow contract tests
- 相关文件：
  - `plugins/codestable/skills/cs-code-review/SKILL.md`
  - `plugins/codestable/skills/cs-code-review/code-reviewer.md`
  - `plugins/codestable/skills/cs-code-review/references/report-template.md`
  - `plugins/codestable/skills/cs-feat-design-review/SKILL.md`
  - `plugins/codestable/skills/cs-onboard/reference/tools.md`
  - `tests/test_workflow_contracts.py`
- 运行环境：Cursor 3.8.24，Claude Opus 主模型，CodeStable Cursor local plugin
- 会话证据：`/Users/joseph/Downloads/cursor_notifications_mark_read_feature.md`
- 历史上下文：2026-06-30 已修复同类 `cs-code-review` Explore 模型问题；后续 reviewer subagent 迁移删除了项目模型配置链路并重新允许模型未知的通用 subagent bridge。

## 5. 严重程度

**P1** — 问题不直接修改业务数据，但会破坏 CodeStable 最终质量 gate 的可信度，使低思考预算模型可能漏掉功能、安全、权限和数据完整性问题，并让报告错误地把该结果记录为独立 reviewer 证据。

## 备注

- 截图实际发生在 `cs-feat-design-review`，不是最终 `cs-code-review`；修复必须同时检查两个审核 gate，不能只修改截图对应技能或只修改用户点名技能。
- 这是已修问题的回归，应该新建本次 regression issue，保留 2026-06-30 历史 issue 作为对照，而不是改写已归档记录。
- 修复目标不是恢复已删除的旧 Paseo managed reviewer 体系，而是建立简单、可执行、可测试的 reviewer 路由硬约束。
