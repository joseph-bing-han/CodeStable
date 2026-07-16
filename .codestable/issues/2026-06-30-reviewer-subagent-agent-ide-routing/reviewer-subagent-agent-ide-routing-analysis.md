---
doc_type: issue-analysis
issue: 2026-06-30-reviewer-subagent-agent-ide-routing
status: analyzed
created: 2026-06-30
updated: 2026-06-30
---

# reviewer-subagent-agent-ide-routing 根因分析

## 1. 根因

`cs-code-review` 的规则曾经只描述“应该按当前 Agent IDE 配置 subagent”，但没有可执行脚本负责：

- 识别当前 Agent IDE；
- 读取 `.codestable/config/code-review-subagent.yaml`；
- 写入 Cursor / Claude Code / Codex 对应的官方 custom subagent 文件；
- 拒绝覆盖未带 CodeStable managed marker 的用户文件；
- 用独立测试锁定这些行为。

因此人工 review 时不会自动生成当前 Agent IDE 的 managed reviewer 配置。

后续人工复测又暴露第二层根因：即使脚本已经存在，`cs-code-review` 的执行顺序仍允许在运行 `configure-review-subagent.py` 之前直接询问 owner 是否接受 local-only / current-conversation fallback。实际结果是 `.cursor/agents/cs-code-reviewer.md` 还不存在时，流程已经进入 fallback 决策，导致 `cs-code-reviewer` 根本没有被真正创建，自然也不可能被启动。

## 2. 相关风险

- 如果继续复用 Explore、general-purpose 或其他内置 subagent，reviewer 模型和思考预算可能偏离 owner 配置。
- 如果 agent 名称过于通用或接近官方内置名称，可能与官方或用户自定义 agent 冲突。
- 如果脚本路径按业务仓库根目录解析，会在任何非 skill 根目录运行时失败。

## 3. 修复方案

采用可执行脚本 + contract test + 独立测试三层约束：

1. 新增 `cs-code-review/scripts/configure-review-subagent.py`。
2. 统一 CodeStable managed reviewer 名称为 `cs-code-reviewer`。
3. Cursor 写入 `.cursor/agents/cs-code-reviewer.md`。
4. Claude Code 写入 `.claude/agents/cs-code-reviewer.md`。
5. Codex 写入 `.codex/agents/cs-code-reviewer.toml`。
6. `cs-code-review/SKILL.md` 要求先按 `SKILL_DIR` 运行检测脚本，再运行配置脚本。
7. 测试覆盖 IDE 识别、三类输出、marker、路径、覆盖保护和脚本绝对路径运行。
8. `cs-code-review/SKILL.md` 增加硬性顺序：必须先运行配置脚本并确认 managed agent 文件存在且带 marker，之后才允许进入 custom subagent 调用或 fallback 判断。

## 4. 决策

使用 `cs-code-reviewer` 作为唯一 managed reviewer 名称，避免与官方内置 agent 或常见用户 agent 名称冲突。
