---
doc_type: issue-fix
issue: 2026-07-10-reviewer-model-fallback-regression
path: standard
fix_date: 2026-07-10
related: [reviewer-model-fallback-regression-analysis.md]
tags: [workflow, code-review, design-review, roadmap-review, subagent, model-routing]
---

# 审核子代理模型降级回归修复记录

## 1. 实际采用方案

采用根因分析中经用户确认的方案 A：统一专用高思考 reviewer，并建立模型安全的 fallback 合同。

三类审核 gate 现在分别优先使用：

- `cs-code-review` -> `codestable-code-reviewer`
- `cs-feat-design-review` -> `codestable-design-reviewer`
- `cs-roadmap-review` -> `codestable-roadmap-reviewer`

三个 reviewer 都声明 `readonly: true`，并固定模型为用户最终确认的 `gpt-5.6-sol[reasoning=max]`。

通用 `generalPurpose` bridge 只有在以下任一条件成立时才合法：

1. runtime 能显式请求预定义高思考 reviewer 模型；
2. runtime 明确保证未指定模型的通用 subagent 继承当前主模型。

两个条件都不成立时，resolver 和技能合同都会切换到当前主模型 self review。Explore、Fast、`model: fast` 和模型未知 bridge 均不能作为审核证据。

## 2. 改动文件清单

### Reviewer agent 与 task 模板

- `plugins/codestable/agents/code-reviewer.md`
- `plugins/codestable/agents/design-reviewer.md`
- `plugins/codestable/agents/roadmap-reviewer.md`
- `plugins/codestable/skills/cs-code-review/code-reviewer.md`
- `plugins/codestable/skills/cs-feat-design-review/design-reviewer.md`
- `plugins/codestable/skills/cs-roadmap-review/roadmap-reviewer.md`

### 审核技能与报告合同

- `plugins/codestable/skills/cs-code-review/SKILL.md`
- `plugins/codestable/skills/cs-code-review/agents/openai.yaml`
- `plugins/codestable/skills/cs-code-review/references/report-template.md`
- `plugins/codestable/skills/cs-feat-design-review/SKILL.md`
- `plugins/codestable/skills/cs-feat-design-review/agents/openai.yaml`
- `plugins/codestable/skills/cs-roadmap-review/SKILL.md`
- `plugins/codestable/skills/cs-roadmap-review/agents/openai.yaml`

### Runtime mapping 与测试

- `plugins/codestable/skills/cs-onboard/reference/tools.md`
- `plugins/codestable/skills/cs-onboard/tools/resolve-task-agent-dispatch.py`
- `tests/test_resolve_task_agent_dispatch.py`
- `tests/test_workflow_contracts.py`

### Self-hosted 与安装副本

- `.codestable/reference/tools.md`
- `.codestable/tools/resolve-task-agent-dispatch.py`
- `/Users/joseph/.cursor/plugins/local/codestable`
- `/Users/joseph/.agents/plugins/CodeStable/plugins/codestable`

源码、当前 Cursor local plugin 和 Agents plugin 的 reviewer agents、三个审核 skill、runtime resolver 与 runtime mapping 文档均已同步。

## 3. 验证结果

### 复现路径验证

- `cs-feat-design-review` 和 `cs-roadmap-review` 已移除 Paseo 与不存在的 `scripts/detect-review-agent.py` 分流。
- 两个规划类 gate 都有专用命名 reviewer 和 task 模板，并明确禁止 Explore、Fast 与模型未知 bridge。
- `cs-code-review` 不再允许把 unknown-model generic bridge 记录为有效 subagent evidence。

### Resolver 行为验证

- reviewer 固定模型采用精确 allowlist；wrong-base、旧模型、Fast 或冲突参数均被拒绝。
- 安全的命名 reviewer -> `named_task_agent` + `plugin_model_honored`。
- runtime 支持模型选择 -> `native_subagent_bridge` + 固定高思考 reviewer 模型。
- runtime 明确保证父模型继承 -> `native_subagent_bridge` + `parent_model_inherited`。
- 模型不可固定且父模型继承无保证 -> `self_review_fallback` + `self_review_current_model`。
- reviewer 模型为 Fast 或低思考预算 -> 不允许作为命名 reviewer 或固定模型 bridge。

### 自动化验证

```text
uvx --with pytest pytest
60 passed in 3.39s
```

```text
python3 -m py_compile plugins/codestable/skills/cs-onboard/tools/resolve-task-agent-dispatch.py .codestable/tools/resolve-task-agent-dispatch.py /Users/joseph/.cursor/plugins/local/codestable/skills/cs-onboard/tools/resolve-task-agent-dispatch.py tests/test_resolve_task_agent_dispatch.py tests/test_workflow_contracts.py
exit code 0
```

IDE linter 结果：0 diagnostics。

合同测试同时覆盖三类 reviewer 的固定模型、pinned bridge、父模型继承 fallback、self review fallback、模板占位符替换、wrong-base / 旧模型 / Fast / 冲突参数拒绝、禁止旧 Paseo/Explore 路由，以及相关 Markdown 不超过 300 行。

## 4. 遗留事项

- 代码与安装副本已完成修复；Cursor 是否立即重新加载新增 custom reviewer 取决于当前会话的插件缓存。下一次真实运行 `cs-feat-design-review` 或 `cs-code-review` 时，应观察 runtime agent 和 model handling 记录是否符合新合同。
- 本次未修改数据库、业务代码或公开 API。
- 没有分析范围外的顺手重构。
