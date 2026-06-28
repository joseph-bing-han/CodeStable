---
name: cs-issue
description: 修 bug 的子流程入口，把"发现问题"自动编排到修复验证、code review 与 Task 归档，留下 report / analysis / fix-note / code-review 产物。触发：用户说"修 bug"、"有个问题"、"修复 XX"。根据已有产物自动进入 report / analyze / fix / code-review。简单问题走快速通道。
---

# cs-issue

## 启动必读

开始任何判断或动作前，先读取 `.codestable/attention.md`；缺失则视为骨架不完整，提示先补齐或运行 `cs-onboard`，不要回退到外部 AI 入口文件。

修 bug 直觉是"找到错的地方改了完事"，但这个直觉路径反复制造同样的麻烦：

1. 问题描述只在脑子里改完就忘——三个月后 bug 再现没复现步骤留存
2. 根因没分析就动手——改了表面现象深层问题等下次爆发
3. 修复范围扩散——发现一个 bug 顺手改五处引入新问题，无法追溯
4. 没验收闭环——怎么判断改好了？改好了什么？没记录

issue 工作流在"看到问题"和"动手改代码"之间塞缓冲：

```
发现问题 → 清晰记录（report）→ 根因分析（analyze）→ 定点修复 + 验证（fix）→ code review
```

本技能不替阶段技能写 issue 文档或代码；它负责判断当前 issue 走到哪步，并自动进入对应子技能。只有路径选择、方案 review 或风险操作才停下来用结构化问题确认。

**这是 issue 的完整入口，不是只帮你挑 report / analyze / fix 的局部工具**：direct entry 和从 `cs` 路由过来等价，后续必须沿同一条 issue 主线继续到 `cs-code-review`、`cs-task archive` 和收尾建议。

**禁止降级为建议入口**：本技能判出下一阶段后，当前 agent 必须继续读取并执行目标子技能；不能只说“建议使用 / 下一步运行 `cs-issue-analyze`”。阶段 review 需要用户拍板时，必须给结构化选项；用户选“通过并继续”后立即续跑下游。

## Task 接入

- 等级：`route-only`。本 skill 自己不写 issue 文档或代码，不直接创建 Task List。
- 一旦自动编排到 `cs-issue-report` / `cs-issue-analyze` / `cs-issue-fix`，由对应下游 skill 在首次落盘前自动创建或复用 Task List，并按 `modify -> update -> accept/review -> archive` 闭环。
- **硬性守卫**：本 skill 只做阶段判定。没有当前 issue Task List 时，不允许直接改代码、改配置或给"已完成修改"式最终报告；必须先自动进入 `cs-issue-report`，由下游创建 / 复用 Task List。
- 快速通道也不是裸改：它只能由 `cs-issue-report` 正式判定，并且必须先有 issue 目录、Task List 和后续 `{slug}-fix-note.md`。缺任一项就不能进入 `cs-issue-fix`。

---

## 文件放哪儿

```
.codestable/issues/{YYYY-MM-DD}-{slug}/
├── {slug}-report.md           ← 阶段 1 问题报告
├── {slug}-analysis.md         ← 阶段 2 根因分析
├── {slug}-fix-note.md         ← 阶段 3 修复记录（必出产物）
└── {slug}-code-review.md      ← 阶段 4 最终代码评审
```

日期取**发现 / 提报问题当天**定了不动。slug 能一眼看出是什么问题（`auth-token-leak`、`null-pointer-on-empty-list`）。

`{slug}-fix-note.md` 是阶段 3 **必出产物**——无论修复简单还是复杂都要写。它不是仪式，是回溯凭证：没有它下次类似问题来你只能从 git log 反推。

所有 issue 文档带 YAML frontmatter（`doc_type` 分别为 `issue-report` / `issue-analysis` / `issue-fix`）便于 `search-yaml.py` 按 severity / tags / status 检索。

---

## 两条路径

### 标准路径（问题复杂或根因不明）

| 阶段 | 子技能 | 主导 | 产出 |
|---|---|---|---|
| 1 问题报告 | `cs-issue-report` | 用户描述，AI 引导 | `{slug}-report.md` |
| 2 根因分析 | `cs-issue-analyze` | AI 读代码分析，用户确认 | `{slug}-analysis.md` |
| 3 修复验证 | `cs-issue-fix` | AI 按分析定点修复，用户验证 | 代码 + `{slug}-fix-note.md` |
| 4 最终质量门禁 | `cs-code-review` | 独立 reviewer 审当前 diff | `{slug}-code-review.md` |

阶段间有 L2 review checkpoint——让用户在每阶段结束有一次明确把关；用户选择“通过并继续”后，自动进入下一阶段，不要求重新输入 skill 名，也不能把下一阶段写成 chat-only 推荐。

### 快速通道（问题简单、根因一眼确定）

下面**同时满足**才进：

1. AI 读完代码后对根因高度有把握（能明确指出 file:line + 原因）
2. 修复改动很小（1-2 处）
3. 无跨模块影响风险

流程压缩成：AI 读代码 → 直接告知根因 + 修复方案 → 用户确认 → AI 修复 → 用户验证通过 → AI 写 `{slug}-fix-note.md`。只产出一份 `fix-note.md`，省掉 report 和 analysis。

**判定口径**：是否进快速通道由 `cs-issue-report` 的启动检查做唯一正式判定。一旦进标准路径默认不再二次改判——避免三个阶段对路径各说各话。

**不能**走快速通道：根因有多个候选 / 修复范围涉及多模块 / 需要先复现才能定位 / 用户希望留完整分析存档。

---

## 路由

进入本技能先 Glob `.codestable/issues/`，自己读已有文件才有数。

| 当前状态 | 自动进入哪个子技能 |
|---|---|
| 刚发现问题，没有任何文件 | `cs-issue-report`（那里判断走标准还是快速） |
| `report.md` 已存在，没 `analysis.md` | `cs-issue-analyze` |
| `analysis.md` 已存在，代码还没改 | `cs-issue-fix` |
| 代码已改，还没修复验证记录 | `cs-issue-fix`（走验证） |
| fix-note 已完成、准备 commit / PR / merge | `cs-code-review` |
| 不确定 | 自己读已有文件按上表对号 |

用户描述的是**新功能需求而不是 bug** → 自动交接 `cs-feat`。

用户描述包含"参考项目改配置 / 切换存储 / 清理硬编码 / 迁移到另一种实现"时，先判断是不是现有行为错误：如果只是目标状态变化，交接 `cs-feat` 或 `cs-feat-ff`；如果当前行为本应如此却坏了，才留在 issue。无论路由到哪边，都不能绕过 Task List。

---

## 与 feature 工作流的边界

- issue：本来应该好的东西坏了——已有代码里的 bug / 异常行为 / 文档错误 / 性能问题
- feature：从来没有的东西要加进来——新功能 / 新能力

灰色地带：修 issue 过程中发现需要新增能力才能真正解决——**先用 issue 工作流把记录和分析做完，再视情况开 feature**。不在 issue 里偷偷做新功能，理由跟 feature 不在 PR 里偷偷修 bug 一样：混着改分不清这次到底改了什么范围。

---

## 相关文档

- `.codestable/reference/system-overview.md` — CodeStable 体系总览
- `.codestable/reference/shared-conventions.md` — 跨阶段共享口径
- `.codestable/attention.md` — CodeStable 启动注意事项和项目硬约束
- `.codestable/requirements/CONTEXT.md` + `requirements/adrs/` — 根因分析时可能要查的领域术语与拍板决策
