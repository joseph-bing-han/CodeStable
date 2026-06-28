---
doc_type: issue-fix
issue: 2026-06-30-code-review-subagent-model-config
status: fixed
severity: medium
created: 2026-06-30
updated: 2026-06-30
---

# code-review-subagent-model-config fix note

## 1. 问题

`cs-code-review` 默认启动独立 subagent 做审查时，Cursor 会使用 Explore subagent model 预设。该预设面向快速浏览文档，思考预算低，不适合作为代码审查 reviewer。

## 2. 根因

`cs-code-review/SKILL.md` 只规定了独立 reviewer 的审查职责和 Paseo / 外部 agent 优先级，没有规定 Cursor subagent 的模型和思考预算来源，也没有项目本地配置文件作为稳定选择依据。运行时因此可能落到 Cursor 的 Explore subagent 默认配置。

## 3. 修复

- 在 `cs-code-review/SKILL.md` 增加 Cursor subagent 模型配置规则。
- 固定项目本地配置路径为 `.codestable/config/code-review-subagent.yaml`。
- 首次运行配置缺失时要求用结构化问题询问 owner，并记录 `model`、`thinking_budget`、`fallback_policy`。
- 配置不可用时要求继承当前对话模型与思考等级，禁止回退到 Explore subagent 或低思考快速预设。
- 在 `cs-code-review/references/report-template.md` 增加 Cursor config 记录行。
- 在 `tests/test_workflow_contracts.py` 增加合同测试锁定该行为。

## 4. 验证

- 合同测试覆盖：`test_code_review_subagent_uses_project_model_config_not_explore_preset`。
- 预期命令：`uvx --with pytest pytest tests/test_workflow_contracts.py`。

## 5. 风险

- 本次只更新 CodeStable 技能约定和文档合同，不实现 Cursor 运行时模型枚举器；真实可用模型仍由运行时在首次询问时由 owner 选择。
