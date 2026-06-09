---
name: cs-code-review
description: Code Review 横切质量关卡——在 feature、issue、refactor 或 fastforward 完成后，scoped-commit、PR 或 merge 前，对照 CodeStable 产物和 git diff 做独立代码评审。触发：用户说"code review"、"代码评审"、"合并前审一下"、"准备 PR / merge"，或各流程收尾进入最终质量门禁。
---

# cs-code-review

## 启动必读

开始任何判断或动作前，先读取 `.codestable/attention.md`；缺失则视为骨架不完整，提示先补齐或运行 `cs-onboard`，不要回退到外部 AI 入口文件。

`cs-feat-accept` 验的是"实现有没有按方案落地"，`cs-issue-fix` 验的是"bug 有没有被定点修掉"，`cs-refactor` 验的是"行为是否等价"。这些都不是独立 code review。`cs-code-review` 补的是最后一关：**让一个没有参与实现的 reviewer 对当前 diff 做生产就绪审查**。

核心原则：review 看的是**工作产物**，不是实现者的思考过程。给 reviewer 精确上下文，不把整段会话历史塞过去。

## Task 接入

- 等级：`auto`（最终质量门禁）。本 skill 必须复用当前 feature / issue / refactor 的 Task List；没有关联流程的 ad-hoc review 才创建独立 Task List。
- review 报告落盘、Critical / Important 反馈处理、复审状态变化后，先同步 Task List 的步骤状态和 CodeStable 文档索引，再继续。
- 上游流程一旦把 `owner_skill` 交给 `cs-code-review`，就不再自己发起 commit 询问；review 通过后由本 skill 负责把 Task List 标记 `completed`。如果用户选择本地 `scoped-commit`，由本 skill 按共享规则直接执行；如果用户只是要 PR / merge readiness，本 skill 只给出可继续的结论，不在 CodeStable 内部自动执行外部平台动作。

---

## 什么时候进入

| 来源 | 进入点 | 必读材料 |
|---|---|---|
| `cs-feat-accept` | acceptance 完成、commit 前 | design + checklist + acceptance + 本次代码 diff + 相关 architecture / requirement / decision |
| `cs-feat-ff` | ff-note 落盘、commit 前 | ff-note + 用户原始需求 + 本次代码 diff + 相关 architecture / decision |
| `cs-issue-fix` | fix-note 落盘、commit 前 | report（如有）+ analysis（如有）+ fix-note + 本次代码 diff + 相关 architecture / decision / explore |
| `cs-refactor` | apply-notes 完成、commit 前 | scan + refactor-design + checklist + apply-notes + 本次代码 diff + 相关 architecture / decision |
| `cs-refactor-ff` | 自证通过、commit 前 | 用户确认过的重构范围 + 验证命令 + 本次代码 diff + 相关 architecture / decision |
| ad-hoc / pre-merge | 用户要求 code review | 用户指定范围 / git range / PR 目标 + 相关 architecture / decision（如适用） |

**不是 `cs-audit`**：audit 主动扫一片代码找潜在问题；code review 只审当前变更范围。

---

## Phase 1：锁定 review 范围

1. 读 `.codestable/attention.md`。
2. 判断来源流程和关联目录，读上表材料。
3. 获取 git 证据：
   - 未提交改动：`git status --short` + `git diff --stat` + `git diff` + `git diff --cached`
   - 已提交范围：用户指定 `{base}..{head}`；未指定时用最近一次相关提交到 `HEAD`
   - untracked 文件不会出现在 `git diff`，必须从 `git status --short` 里单独读取
4. 整理一句话范围：`本次 review 审 {来源} 的 {目标}，范围是 {文件/提交/工作区改动}`。

如果当前变更触达系统边界、目录结构、共享约束、模块交互或已有长期规约，必须把相关 `.codestable/architecture/`、`compound/` 里的 `decision` / `explore`、以及 `.codestable/attention.md` 一并加入 reviewer 输入。

范围不清楚时停下来问；范围清楚就继续，不要求用户重复确认。

---

## Phase 2：派发独立 reviewer

优先派发子代理，且不要继承当前会话历史：

- `fork_turns: "none"`
- 给 reviewer 的输入只包含：实现摘要、需求 / spec 路径、git range 或工作区 diff 获取方式、必须检查的清单、输出格式
- reviewer 只读代码和文档，不修改文件

子代理提示模板见 `reference.md`。如果运行环境没有子代理能力，才降级为自审，并在报告里写明：

```markdown
review_mode: self-review
degraded_reason: subagent unavailable
```

---

## Phase 3：判定反馈

严重度口径：

- **Critical**：会导致功能错误、安全问题、数据损坏、迁移失败、严重回归；必须修。
- **Important**：需求遗漏、架构偏离、错误处理缺口、测试缺口、明显可维护性债；合并前应修。
- **Minor**：命名、局部可读性、非阻塞文档补充；可记录后续。

结论只能三种：

| 结论 | 条件 | 后续 |
|---|---|---|
| `changes-required` | Critical ≥ 1 或 Important ≥ 1 | 回到上游实现 / 修复 / apply 阶段处理，处理后复审 |
| `approved-with-notes` | 无 Critical / Important，仅有 Minor | 可进入 commit，Minor 进报告"后续项" |
| `approved` | 无阻塞项，验证证据完整 | 可进入 commit / PR / merge |

reviewer 说错时可以反驳，但必须用代码、测试或 spec 证据说明，并把反驳写进报告。

---

## Phase 4：落盘 review 报告

报告放在关联流程目录里：

```
.codestable/features/{feature}/{slug}-code-review.md
.codestable/issues/{issue}/{slug}-code-review.md
.codestable/refactors/{refactor}/{slug}-code-review.md
```

ad-hoc review 没有关联目录时，只在当前回复给出报告；用户明确要求留档再创建合适的 feature / issue / refactor 入口。

补充：

- 来源是 `refactor-ff` 且还没有 `.codestable/refactors/{YYYY-MM-DD}-{slug}/` 时，先创建这个最小目录，再写 `{slug}-code-review.md`
- 来源是 `feature-ff` 时，报告仍落在对应 feature 目录；`ff-note` 不替代 `code-review`

frontmatter：

```yaml
---
doc_type: code-review
scope_type: feature | issue | refactor | ad-hoc
scope: {YYYY-MM-DD-slug 或 git range}
status: changes-required | approved-with-notes | approved
review_mode: subagent | self-review
base: {sha 或 HEAD}
head: {sha 或 WORKTREE}
reviewed_at: YYYY-MM-DD
---
```

正文模板见 `reference.md`。

---

## Phase 5：处理结果

- `changes-required`：不要进入 commit。把 Critical / Important 转成上游流程的待办：
  - 标准 feature → 回到 `cs-feat-impl`，并把 Task List `owner_skill` 切回 `cs-feat-impl`
  - feature fastforward → 仍在原范围内就回 `cs-feat-ff` 并把 `owner_skill` 切回 `cs-feat-ff`；超出原轻量范围就升级到 `cs-feat` / `cs-feat-impl`
  - issue → 回到 `cs-issue-fix`，并把 `owner_skill` 切回 `cs-issue-fix`
  - 标准 refactor → 回到 `cs-refactor`，并把 `owner_skill` 切回 `cs-refactor`
  - refactor fastforward → 仍在原范围内就回 `cs-refactor-ff` 并把 `owner_skill` 切回 `cs-refactor-ff`；超出原轻量范围就升级到 `cs-refactor`
  修完重新跑 `cs-code-review`；只要结论还是 `changes-required`，`owner_skill` 就不能停在 `cs-code-review`。
- `approved-with-notes`：Minor 写进报告"后续项"；如果有关联 Task List，本 skill 将其标记 `completed`，然后统一询问：是立即执行本地 `scoped-commit`，还是仅把 review 结果作为后续 PR / merge 的前置结论。
- `approved`：如果有关联 Task List，本 skill 将其标记 `completed`，然后统一询问：是立即执行本地 `scoped-commit`，还是仅把 review 结果作为后续 PR / merge 的前置结论。

---

## 退出条件

- [ ] review 范围明确，包含 untracked 文件核对
- [ ] reviewer 读取了对应 CodeStable 产物和 git diff
- [ ] Critical / Important / Minor 分类完成
- [ ] review 报告已落盘（ad-hoc 且用户不要求留档除外）
- [ ] `changes-required` 已回到上游阶段；或 `approved` / `approved-with-notes` 后允许上游继续收尾

---

## 容易踩的坑

- 把用户 review / acceptance 当成 code review
- 把整段会话历史塞给 reviewer，导致 reviewer 被实现者思路污染
- 只看测试是否通过，不读 diff
- 忽略 untracked 文件
- 只审代码不对照 design / report / apply-notes
- Critical / Important 没修就进入 commit
- 把 `cs-audit` 当 code review 用——audit 是主动发现清单，不是当前 diff 质量门禁
