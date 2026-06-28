---
doc_type: task-list
task: cs-code-review-reviewer-subagent-routing
goal: Harden cs-code-review's Cursor subagent routing so the main agent dispatches a configured code-review custom subagent (name flexible) instead of the default Explore subagent or generic generalPurpose agent, and sync the change across all installed copies
status: archived
workflow: feature-ff
owner_skill: cs-code-review
created: 2026-07-04
updated: 2026-07-04
archived: 2026-07-04
related_docs:
  - plugins/codestable/skills/cs-code-review/SKILL.md
  - plugins/codestable/skills/cs-code-review/references/code-reviewer-prompt.md
  - plugins/codestable/skills/cs-code-review/references/report-template.md
  - ~/.agents/plugins/CodeStable/plugins/codestable/skills/cs-code-review/SKILL.md
  - ~/.agents/plugins/CodeStable/plugins/codestable/skills/cs-code-review/references/code-reviewer-prompt.md
  - ~/.agents/plugins/CodeStable/plugins/codestable/skills/cs-code-review/references/report-template.md
  - ~/.cursor/plugins/local/codestable/skills/cs-code-review/SKILL.md
  - ~/.cursor/plugins/local/codestable/skills/cs-code-review/references/code-reviewer-prompt.md
  - ~/.cursor/plugins/local/codestable/skills/cs-code-review/references/report-template.md
---

# Harden cs-code-review reviewer subagent routing

## 1. 任务目标

修复 `cs-code-review` 在实际执行时被 Cursor 主 agent 错误路由到默认 Explore subagent（高速低思考模型）的问题。原 SKILL.md 只写“启动 reviewer subagent”和 `generalPurpose` 泛化描述，未按 Cursor 官方 sub-agents 语义把“调用哪个 custom subagent”写成明确路由约束，导致主 agent 未选中用户在 Cursor Settings 里配置的代码审查型 custom subagent。

修复口径：不硬编码任何单一名字，接受名称或 description 明确指向 code review 的一组候选（reviewer / review / code-review / code-reviewer / pr-review / review-agent 等）；禁止 Explore / explorer / explore / generalPurpose 代替；找不到符合条件的 review custom subagent 时降级 self review 并在报告写明降级原因。三处安装路径保持一致。

## 2. 当前状态

archived

## 3. Agent 原生 Tasks 同步区

- [x] 参考 Cursor 官方 sub-agents 文档定位路由偏差根因（generalPurpose / 缺明确路由约束）
- [x] 在 `SKILL.md` 增加 Cursor subagent 选择规则章节，明确匹配集合与 forbidden substitutes
- [x] 修正 Dispatch 步骤 3 / 5、退出条件、常见坑，去掉 `generalPurpose` 默认入口
- [x] 修正 `references/code-reviewer-prompt.md`：Dispatch contract + CodeStable Context 里的 Required / Forbidden 字段
- [x] 修正 `references/report-template.md`：Runtime agent / Runtime params 不再硬编码具体名字
- [x] 同步 `/Users/joseph/.agents/plugins/CodeStable/plugins/codestable/skills/cs-code-review/`
- [x] 同步 `/Users/joseph/.cursor/plugins/local/codestable/skills/cs-code-review/`
- [x] 用 rg 交叉验证三处路径无 `reviewer` 硬编码残留
- [~] 对本次 skill 改动执行 `cs-code-review` gate（源目录）—— 用户明示跳过 review gate，直接归档
- [~] review passed 后标记 completed 并立即 archive，active 无残留 —— 归档时无 review evidence，按 user-override 完成 archive

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| skill | `plugins/codestable/skills/cs-code-review/SKILL.md` | 新增 Cursor subagent 选择规则、Dispatch / 退出条件 / 坑同步改造 |
| prompt | `plugins/codestable/skills/cs-code-review/references/code-reviewer-prompt.md` | Dispatch contract + Required/Forbidden 字段 |
| template | `plugins/codestable/skills/cs-code-review/references/report-template.md` | Runtime agent 改为选中的 review custom subagent 名字占位 |
| installed-copy | `~/.agents/plugins/CodeStable/plugins/codestable/skills/cs-code-review/` | 与源目录三文件一致 |
| installed-copy | `~/.cursor/plugins/local/codestable/skills/cs-code-review/` | Cursor local plugin 副本，与源目录三文件一致 |

## 5. 执行步骤

### 1. 根因定位

- 状态：done
- 来源：user-report + Cursor 官方 sub-agents 文档
- 完成信号：确认原描述使用 `generalPurpose` 与泛化“启动 subagent”表述，未把“调用哪个 Cursor custom subagent”写成路由约束，导致主 agent 匹配到默认 Explore subagent。

### 2. 修复 SKILL.md 路由规则

- 状态：done
- 来源：manual
- 完成信号：源 `SKILL.md` 新增 “Cursor subagent 选择规则”，候选集合覆盖 reviewer / review / code-review / code-reviewer / pr-review / review-agent 及等价 review agent；Dispatch / 退出条件 / 坑同步更新。

### 3. 修复 prompt 模板

- 状态：done
- 来源：manual
- 完成信号：`references/code-reviewer-prompt.md` 顶部新增 Dispatch contract；CodeStable Context 写入 Required Cursor subagent（configured code-review custom subagent，记录实际选中名字）与 Forbidden substitutes。

### 4. 修复 report 模板

- 状态：done
- 来源：manual
- 完成信号：`references/report-template.md` 的 Runtime agent / Runtime params 改为“selected Cursor custom review subagent name / settings”，不再硬编码 reviewer 或 generalPurpose。

### 5. 同步三处路径

- 状态：done
- 来源：manual
- 完成信号：源 `/Users/joseph/code/CodeStable/plugins/codestable/skills/cs-code-review/`、`~/.agents/plugins/CodeStable/plugins/codestable/skills/cs-code-review/`、`~/.cursor/plugins/local/codestable/skills/cs-code-review/` 三处的 `SKILL.md` / `references/code-reviewer-prompt.md` / `references/report-template.md` 内容一致；rg 交叉验证不再残留 `reviewer` 硬编码措辞（`Required Cursor subagent: reviewer` / `Cursor custom subagent reviewer` / `reviewer custom agent settings` / `named \`reviewer\``）。

### 6. 执行代码审查 gate

- 状态：skipped
- 来源：user-override
- 完成信号：用户明示跳过 `cs-code-review` gate，直接归档；未产出 `{slug}-review.md`。

### 7. 完成与归档

- 状态：done
- 来源：user-override
- 完成信号：`.codestable/tasks/active/cs-code-review-reviewer-subagent-routing.md` 已移动到 `.codestable/tasks/archived/2026-07-04-cs-code-review-reviewer-subagent-routing.md`，frontmatter `status: archived`、`archived: 2026-07-04`；active 目录无同名残留。

## 6. 中断恢复提示

任务已归档。若后续想为本次改动补 review 证据，重新起独立 ad-hoc task 单独跑 `cs-code-review`。

## 7. 完成与归档记录

- 完成日期：2026-07-04
- 归档日期：2026-07-04
- review evidence：none（用户显式跳过 review gate）
- 结论：`cs-code-review` reviewer subagent 路由修复已在三处路径同步完成；code review gate 按用户 override 跳过，无 review 报告；本 task 按 user-override 直接归档。
