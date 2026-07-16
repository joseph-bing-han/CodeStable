---
doc_type: issue-analysis
issue: 2026-07-10-reviewer-model-fallback-regression
status: confirmed
root_cause_type: logic
related: [reviewer-model-fallback-regression-report.md]
tags: [workflow, code-review, design-review, roadmap-review, subagent, model-routing, regression]
---

# 审核子代理模型降级回归根因分析

## 1. 问题定位

| 关键位置 | 说明 |
|---|---|
| `plugins/codestable/skills/cs-feat-design-review/SKILL.md:55-71` | 仍使用旧 Paseo / 检测脚本分流，并引用实际不存在的 `scripts/detect-review-agent.py`；没有定义专用 design reviewer，也没有禁止用内置 Explore 补位。 |
| `plugins/codestable/skills/cs-roadmap-review/SKILL.md:54-70` | 复制了同一套旧 reviewer 分流，具备相同的 Explore/Fast 降级风险。 |
| `plugins/codestable/skills/cs-code-review/SKILL.md:35-41,102-108` | 允许无法固定模型的 `generalPurpose` bridge 继续执行，只要求记录 `model fallback / unknown`，把模型质量不确定的输出仍记作 subagent review evidence。 |
| `plugins/codestable/skills/cs-code-review/code-reviewer.md:8,57-59` | task 模板重复声明：不能使用固定 reviewer 模型时仍运行 bridge，只记录 residual risk。 |
| `plugins/codestable/skills/cs-onboard/tools/resolve-task-agent-dispatch.py:126-137` | 当 runtime 支持通用只读 subagent、但不支持模型选择时，仍返回 `native_subagent_bridge`，并把 `model_handling` 标为 `runtime_fallback`。 |
| `plugins/codestable/agents/code-reviewer.md:5` | 实际 agent frontmatter 只写 `model: gpt-5.5`，没有技能、模板和测试宣称的 `fast=false` 与高思考参数。 |
| `tests/test_resolve_task_agent_dispatch.py:94-112` | 测试主动断言“无法选择模型时仍使用 native bridge + runtime_fallback”，因此把不安全行为固化为预期。 |
| `tests/test_workflow_contracts.py:94-118` | 只检查禁止 Explore 名称和删除旧 managed config，没有约束 Fast、模型未知、父模型继承或专用 reviewer 的真实模型参数。 |

Cursor 官方 subagent 文档说明，内置 Explore 为提高搜索吞吐默认使用更快模型；custom subagent 支持通过 frontmatter 固定具体模型和参数，`model: inherit` 则继承父 agent。当前实现没有把这些运行时事实转化为硬性审核合同。

## 2. 失败路径还原

**正常路径**：进入审核 gate → 优先启动对应的 CodeStable 命名 reviewer → reviewer 使用 frontmatter 中预定义的非 Fast、高思考预算模型 → reviewer 只读返回结果 → 主 agent 核验并落审核报告。命名 reviewer 不可调用但 runtime 明确支持父模型继承时，通用只读 bridge 使用当前主模型；否则主 agent 本地 self review。

**截图中的失败路径**：进入 `cs-feat-design-review` → skill 要求运行不存在的检测脚本 → 外部 Paseo reviewer 不可用 → skill 没有专用 design reviewer 路由，也没有禁止 Explore → 主 agent 为“增强审查”选择内置 Explore → Cursor 按内置策略使用 Fast 模型执行审核。

**代码审核的潜在失败路径**：进入 `cs-code-review` → 无法显式启动 `codestable-code-reviewer` → runtime 暴露通用 Subagent 但不能选择固定 reviewer 模型 → resolver 仍返回 `generalPurpose` bridge → 实际模型可能是默认、Fast 或未知 → 报告只记录 residual risk，但仍把结果记作 `reviewer: subagent`。

**分叉点**：

- `cs-feat-design-review/SKILL.md:55-71`：没有专用 reviewer 路由时，合同从“本地 review”旁逸为任意独立 subagent。
- `resolve-task-agent-dispatch.py:126-137`：无法保证模型质量时仍判定 bridge 可用，而不是切换到父模型继承或 self review。

## 3. 根因

**根因类型**：logic

**根因描述**：2026-06-30 的历史修复曾禁止 Explore 并要求稳定 reviewer 模型，但后续 SuperPowers-style reviewer 迁移删除了旧 managed config / 检测链路，只为 `cs-code-review` 增加了命名 reviewer，同时保留“模型不可控也可继续 bridge”的兼容策略。`cs-feat-design-review` 和 `cs-roadmap-review` 没有同步迁移，继续引用已删除的检测脚本与 Paseo 规则。结果是三个审核 gate 使用了两套不一致且都不完整的路由合同。

**是否有多个根因**：是。

1. **主因**：审核有效性的判定只看“是否启动了 subagent”，没有把“是否为专用 reviewer、是否非 Fast、是否具备足够思考预算”作为硬条件。
2. **次因**：feature design 与 roadmap review 未随 code review 一起迁移到命名 reviewer 架构，旧脚本已删除但技能说明仍引用它。
3. **次因**：resolver 和测试把 `runtime_fallback / unknown` 固化为合法 subagent review evidence。
4. **次因**：实际 code reviewer frontmatter 与技能、模板和测试宣称的模型参数不一致，配置只是文案承诺，没有落到真实 agent 定义。

## 4. 影响面

- **影响范围**：不仅影响截图中的 feature design review，也影响最终 code review、roadmap review，以及所有通过这些 gate 进入 QA、acceptance 或归档的 feature / issue / refactor / fastforward 流程。
- **潜在受害模块**：`cs-code-review`、`cs-feat-design-review`、`cs-roadmap-review`、Subagent Runtime Mapping、self-hosted resolver 副本、审核报告模板、插件安装副本与相关合同测试。
- **数据完整性风险**：无直接数据库写入风险；但低质量 reviewer 可能漏掉权限、迁移、并发和数据完整性缺陷，形成错误的 `passed` 证据。
- **严重程度复核**：维持 **P1**。该问题破坏跨 workflow 的核心质量 gate，影响面广，但本身不直接造成业务数据损坏。

## 5. 修复方案

### 方案 A：统一专用 reviewer + 模型安全 fallback 合同

- **做什么**：
  - 将 `codestable-code-reviewer` 的真实 frontmatter 固定为非 Fast、高思考预算模型。
  - 新增只读的 `codestable-design-reviewer` 与 `codestable-roadmap-reviewer`，同样使用预定义高思考预算模型。
  - 把 feature design / roadmap review 从旧 Paseo 检测脚本迁移到命名 reviewer + task template + native bridge。
  - resolver 只有在能固定 reviewer 模型，或 runtime 明确保证继承当前主模型时才允许通用 bridge；禁止 Fast、Explore 和模型未知 bridge 成为有效 reviewer evidence。
  - 无法满足上述条件时直接由当前主模型 self review，而不是启动低预算子代理。
  - 同步 skills、openai prompts、报告模板、runtime mapping、自托管副本、安装副本和回归测试。
- **优点**：完整满足“优先预定义高思考 reviewer，次选当前模型”的目标；三类审核 gate 统一；可通过 resolver 单元测试和 workflow contract test 防回归。
- **缺点 / 风险**：改动文件较多，需要新增两个专用 agent 和 task 模板，并同步插件安装副本。
- **影响面**：CodeStable 审核基础设施，不改业务代码和数据库。

### 方案 B：只保留 code reviewer，设计与 roadmap 固定使用当前主模型

- **做什么**：修紧 `cs-code-review` 的模型 fallback；删除 feature design / roadmap review 的旧独立 reviewer 逻辑，两个规划类 gate 永远由当前主模型本地审核。
- **优点**：改动较小，能立即消除 Explore/Fast 风险。
- **缺点 / 风险**：设计与 roadmap 审核失去独立上下文和独立 reviewer；不完全满足优先使用预定义高思考预算模型的目标。
- **影响面**：三个审核 skill、resolver、模板和测试。

### 方案 C：恢复项目级 managed reviewer 配置体系

- **做什么**：恢复 `.codestable/config/code-review-subagent.yaml`、配置生成脚本和 IDE-specific managed agent 文件，并扩展到 design / roadmap reviewer。
- **优点**：owner 可逐项目选择模型与预算。
- **缺点 / 风险**：重新引入刚被移除的复杂 bootstrap、配置漂移和多 IDE 同步链路；历史上已经多次因脚本路径、配置文件和 invocation 能力产生回归。
- **影响面**：最大，涉及 onboarding、配置生成、多个 IDE 路径和更多测试。

### 推荐方案

**推荐方案 A**。它直接把审核质量写成可执行的 runtime 合同：优先专用高思考 reviewer，无法调用时只允许明确继承当前主模型，否则 self review。相较恢复 managed config，它更简单；相较纯本地审核，它保留独立 reviewer 的价值，并能一次修复 code、design、roadmap 三个同源入口。
