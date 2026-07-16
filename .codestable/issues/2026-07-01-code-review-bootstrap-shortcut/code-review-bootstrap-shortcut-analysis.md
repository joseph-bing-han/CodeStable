---
doc_type: issue-analysis
issue: 2026-07-01-code-review-bootstrap-shortcut
status: confirmed
root_cause_type: logic
related: [code-review-bootstrap-shortcut-report.md]
tags: [workflow, code-review, subagent]
---

# cs-code-review bootstrap 短路根因分析

## 1. 问题定位

| 关键位置 | 说明 |
|---|---|
| `cs-code-review/SKILL.md` 启动检查 | 已有 review 报告的 `blocked` / `changes-requested` 分支早于明确的 reviewer bootstrap gate，容易让 agent 把旧报告状态当成当前事实。 |
| `cs-code-review/SKILL.md` 独立 reviewer 增强项 | “独立 reviewer 是增强项，不是硬依赖”的旧语义与 Cursor / Claude Code / Codex 下必须先配置 `cs-code-reviewer` 的新规则混在一起，降低了硬性顺序的优先级。 |
| `tests/test_workflow_contracts.py` | 测试覆盖了配置脚本存在和路径文本，但没有锁定每次 review 都必须重新执行 reviewer bootstrap、不能用旧 blocked 报告短路。 |

## 2. 失败路径还原

**正常路径**：用户触发 `/cs-code-review` → 读取当前 Task/spec/diff → 执行 reviewer bootstrap → 运行 `configure-review-subagent.py` → 验证 managed agent 文件 → 尝试调用 `cs-code-reviewer` → 根据真实当轮结果写 review verdict。

**失败路径**：用户触发 `/cs-code-review` → 读取旧 `{slug}-code-review.md` → 看到 `status: blocked` → 复述旧 blocker → 没有运行配置脚本，也没有验证 `.cursor/agents/cs-code-reviewer.md` 当前是否存在。

**分叉点**：`cs-code-review/SKILL.md` 启动检查 — 旧报告状态检查没有被 reviewer bootstrap gate 包围，导致旧结论可以短路当轮事实验证。

## 3. 根因

**根因类型**：logic

**根因描述**：`cs-code-review` 的规则把“读取旧 review 报告”写成启动检查的一部分，但没有明确要求旧报告只能作为历史输入，不能替代当轮 reviewer bootstrap。虽然后续章节已经写了必须运行 `configure-review-subagent.py`，但该要求没有被提升为启动检查里的不可跳过阶段，所以执行时可以先沿用旧 blocked verdict。

**是否有多个根因**：是。主因是启动检查顺序缺口；次因是测试只断言文本存在，未断言旧报告不能短路配置脚本。

## 4. 影响面

- **影响范围**：所有已经存在 `blocked` / `pending` review 报告并再次触发 `/cs-code-review` 的场景。
- **潜在受害模块**：`cs-code-review`、`cs-issue-fix` 的收尾 review gate，以及依赖 review evidence 的 Task archive 流程。
- **数据完整性风险**：无直接数据损坏风险，但会让 CodeStable 产物记录与当前文件系统事实不一致。
- **严重程度复核**：维持 P1。该问题会破坏独立审查链路可信度，但不直接修改业务数据。

## 5. 修复方案

### 方案 A：在启动检查中新增不可跳过 Reviewer bootstrap
- **做什么**：把 reviewer config、配置脚本运行、managed agent 文件验证、旧报告不可替代当轮事实等规则提升到 `cs-code-review/SKILL.md` 的启动检查顶部。
- **优点**：直接修复短路路径，符合用户要求，改动集中。
- **缺点 / 风险**：仍是文档型 workflow 约束，需要 contract test 锁定关键句。
- **影响面**：`cs-code-review/SKILL.md`、`tests/test_workflow_contracts.py`。

### 方案 B：只加强独立 reviewer 增强项章节
- **做什么**：在原独立 reviewer 章节继续追加禁止旧报告短路的说明。
- **优点**：改动更小。
- **缺点 / 风险**：仍可能被前面的启动检查旧报告分支短路，修复不彻底。
- **影响面**：`cs-code-review/SKILL.md`。

### 推荐方案

**推荐方案 A**，理由：问题发生在启动顺序，必须在启动检查阶段设置不可跳过 gate；只改后续增强项章节无法阻止旧报告 verdict 提前生效。
