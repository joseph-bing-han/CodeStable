---
doc_type: issue-report
issue: 2026-06-30-reviewer-subagent-agent-ide-routing
status: reported
severity: medium
created: 2026-06-30
updated: 2026-06-30
---

# reviewer-subagent-agent-ide-routing 问题报告

## 1. 现象

`cs-code-review` 已经要求读取 `.codestable/config/code-review-subagent.yaml`，但实际 review 流程仍不会自动为当前 Agent IDE 创建可调用的 CodeStable 专属 reviewer subagent 配置。

人工测试还暴露过脚本路径问题：review 流程曾从业务仓库根目录执行 `scripts/detect-review-agent.py`，导致找不到 skill 包内脚本。

## 2. 期望行为

- `cs-code-review` 必须按已加载 `SKILL.md` 所在目录解析自带脚本路径。
- 当前 Agent IDE 支持 custom subagent 时，必须根据 IDE 类型创建或更新 `cs-code-reviewer` managed agent。
- Cursor、Claude Code、Codex 使用各自官方配置文件路径和字段。
- 不覆盖官方内置 agent 或用户已有未标记为 CodeStable managed 的 agent 文件。
- 有独立测试验证 IDE 识别、配置文件生成和覆盖保护。

## 3. 影响

如果不修复，旧项目或新项目即使有 `.codestable/config/code-review-subagent.yaml`，也可能只停留在“配置文件存在”的文档层，实际 review 仍无法稳定使用 owner 指定的 reviewer 模型与思考预算。

## 4. 复现线索

- `/cs-code-review` 人工测试不会自动创建当前 Agent IDE 的 subagent 配置。
- 错误路径示例：`/Users/joseph/code/CodeStable/scripts/detect-review-agent.py`。
- 期望路径应是已加载 skill 包内的 `cs-code-review/scripts/`。

## 5. 范围

本 issue 只修复 `cs-code-review` reviewer subagent 配置与调用前置链路，不修改业务代码，也不改变 CodeStable 其他 workflow 的核心状态机。
