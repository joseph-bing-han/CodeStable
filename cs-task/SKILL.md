---
name: cs-task
description: CodeStable Task List 运行入口。触发：用户说"cs task"、"继续当前任务"、"任务列表"、"历史任务"、"归档任务"、"缺少 task"、"补建 task"、"backfill task"，或任一 CS workflow 需要创建、恢复、同步、完成、归档 Task List 时使用。管理 `.codestable/tasks/active` 与 `.codestable/tasks/archived`，不处理具体 feature/issue 实现。
---

# cs-task

`cs-task` 是 CodeStable 的任务运行账本入口。它不替代 feature checklist、roadmap items 或 issue report，而是提供跨 workflow 的“当前任务 / 中断恢复 / 历史归档”统一入口。

Task List 不是可选配件，而是所有会落盘 workflow 的强制主线：结束分析、准备首次修改项目内文档或代码时，必须先 create / recovery；`completed` 只是待归档态，archive 完成且 active 无残留才算真正闭环。

> 详细 schema、状态机和模板看同目录 `reference.md`。共享目录约定看 `.codestable/reference/shared-conventions.md`。

## Task 接入

- 等级：`internal-runtime`。本 skill 负责创建、恢复、更新、完成、归档 Task List 本身，绝不为自己的 task 文件变更递归创建新的 Task List。
- 其他会写项目内文档或代码的 CS skill 一旦准备首次落盘，必须自动调用本 skill 做 create / recovery；active / archived 清理、归档残留删除是本 skill 的默认职责，不是可选步骤。
- 只有当别的 workflow 调用本 skill 做 create / update / complete / archive / recovery 时，才更新现有 Task List；`cs-task` 自己不再套一层 Task。

---

## 启动必读

1. 先读 `.codestable/attention.md`；缺失时提示骨架不完整，但如果当前任务正是 Task System bootstrap，可继续读取 `.codestable/tasks/` 与 roadmap 上下文。
2. 读取 `.codestable/tasks/active/*.md`；如果目录不存在，说明还没有 task system 实例，提示先创建 task list 或走 `cs-onboard`。
3. 读取 `.codestable/tasks/archived/*.md`，先清理 active 中已归档任务的残留副本，再进入 recovery / archive。
4. `cs-task` 是 internal runtime：只更新 task 文件本身时，不再为这个更新递归创建新的 Task List。

### Task 目录扫描硬约束

`.codestable/` 可能被 `.gitignore` 忽略；因此 recovery / archive / history / cleanup 不能只用会受 ignore 过滤的 Glob、rg 或文件搜索结果判断 active / archived 是否为空。每次盘点 Task 目录时，必须使用不受 ignore 过滤的目录枚举方式读取 `.codestable/tasks/active` 和 `.codestable/tasks/archived` 下的 `*.md` 文件名，再逐个读取 frontmatter。若 Glob / rg 返回 0，也必须用未过滤目录枚举交叉确认后，才能报告“当前没有 active task”。

---

## 核心定位

### Task List 是 source of truth

- Task List 文件记录任务目标、步骤、关联 CodeStable 文档索引、当前状态和归档记录。
- Agent Native Tasks / TodoWrite / Claude todo 等只是运行时镜像。
- 每完成一步，先更新 Task List 文件，再同步 Agent 运行时任务视图。

### Task List 不替代这些东西

- feature / refactor 的 `{slug}-checklist.yaml`
- roadmap 的 `{slug}-items.yaml`
- issue 的 report / analysis / fix-note
- acceptance report

Task List 只负责“任务恢复和跨 workflow 进度账本”。

---

## 模式分流

| 用户意图 | 模式 |
|---|---|
| `cs task` / 继续任务 / 当前任务 | recovery |
| 创建 Task List | create |
| 当前步骤完成 / 更新进度 | update |
| 所有步骤完成 | complete |
| 归档完成任务 / 查看历史任务 | archive / history |
| 用户说“缺少 task”或发现已有 CodeStable 产物 / 代码改动但无 Task | backfill |

判断不出时，用结构化用户问题让用户选，不要开放式追问。

---

## recovery：恢复当前任务

1. 用不受 ignore 过滤的目录枚举扫描 `.codestable/tasks/active/*.md` 和 `.codestable/tasks/archived/*.md`；不得只凭 Glob / rg 的 0 结果判断无任务。
2. 先执行归档残留清理：如果 active 中的 `{task}.md` 已有对应 archived 文件 `YYYY-MM-DD-{task}.md`，且 archived 文件 frontmatter 为 `status: archived`，自动删除 active 副本并记录本次清理；不要把它列为可恢复任务。
3. 解析剩余 active frontmatter：
   - `active` / `blocked`：可恢复任务
   - `completed`：待归档任务
   - `cancelled`：可归档任务
   - `archived`：位置错误，正常不应在 active 目录
4. 没有可恢复任务：
   - 有 completed / cancelled：询问要归档哪个
   - 没有：报告“当前没有 active task”
5. 只有一个可恢复任务：读取全文，提取第一个未完成步骤，同步 Agent Native Tasks。
6. 多个可恢复任务：使用当前 Agent 提供的结构化用户问答能力让用户选择。

选择格式：

```text
检测到多个进行中的 Tasks，请选择要继续的任务：

1. {task-a-goal}
2. {task-b-goal}
3. 自由输入补充信息
```

用户选择后，读取对应 task，构造 handoff 并自动进入 owner skill；只有 owner skill 缺失、目标不明确或存在风险操作时，才停在结构化问题。

---

## backfill：补建缺失 Task 并续跑缺失 gate

触发：用户指出缺少 task，或任一 workflow 发现 issue / feature / refactor 产物、代码改动、fix-note / ff-note / apply-notes 已存在，但 active 与 archived 都没有对应 Task spine。仅 `.codestable/tasks/active/{slug}.md` 缺失不等于缺少 task；必须先检查 `.codestable/tasks/archived/YYYY-MM-DD-{slug}.md`。

动作：

1. 根据 unit 目录或产物 frontmatter 推断 `workflow`、`task`、`goal`、`owner_skill`。
2. 先用不受 ignore 过滤的目录枚举检查 archived：若已存在 `YYYY-MM-DD-{task}.md` 且 frontmatter 为 `status: archived`，说明该 Task 已闭环，禁止创建新的 active Task；若 active 中又出现同名文件，只按归档残留清理处理。
3. active 与 archived 都不存在时，才创建 active Task，`related_docs` 登记已存在的 report / analysis / fix-note / ff-note / review 等产物。
4. 推断下一 gate：有 fix-note / ff-note / apply-notes 但无 passed review → `owner_skill=cs-code-review`；有 passed review 且无后续 QA → `status=completed` 后立即 archive；report 后无 analysis → `cs-issue-analyze`；analysis 后无 fix-note → `cs-issue-fix`。
5. backfill 完不能只汇报“已补建”：若 `owner_skill` 指向下一 workflow skill，立即构造 handoff 并执行；若可归档，立即 archive。

backfill 是修复 spine 断裂的恢复动作，不是正常流程的替代。后续仍必须按原 workflow 的 review / archive gate 收口。

---

## create：创建 Task List

创建条件：当前 CS skill 会修改项目内文档或代码，且当前 workflow 准备首次落盘。

动作：

1. 生成 task slug：小写英文连字符，表达任务主目标。
2. 写入 `.codestable/tasks/active/{task}.md`。
3. frontmatter 至少包含 `doc_type` / `task` / `goal` / `status` / `workflow` / `owner_skill` / `created` / `updated` / `archived` / `related_docs`。
4. 正文必须包含 7 个固定节，见 `reference.md`。
5. 同步 Agent Native Tasks。

如果 active 目录下已存在同名文件，先询问用户覆盖、复用还是改 slug；不得静默覆盖。

---

## update：更新步骤状态

每完成一个执行步骤：

1. 把 Task List 中对应 checklist 项改为完成。
2. 把“执行步骤”里的状态改为 `done`。
3. 更新 frontmatter `updated`。
4. 如果新增 CodeStable 文档，追加到“CodeStable 文档索引”。
5. 再同步 Agent Native Tasks。

如果实际执行拆出新步骤，只能追加到 Task List；不能改写历史已完成步骤。

---

## complete：完成任务

完成条件：

- Agent 同步区所有条目完成
- 执行步骤没有 `pending` / `in-progress`
- 关联 workflow 的必须产物已落盘

动作：

1. frontmatter `status: completed`。
2. “当前状态”改为 `completed`。
3. 完成与归档记录写入完成日期和验证结果。
4. 立即把下一步交给 archive；不允许把 `completed` 当成真正结束态长期留在 active。

---

## archive / history：归档与历史

归档对象盘点同样必须遵守「Task 目录扫描硬约束」：先用不受 ignore 过滤的目录枚举读取 active / archived 文件名，再判断哪些任务可归档。

归档对象：active 目录中 `status: completed` 或 `status: cancelled` 的 task。上游 workflow 写着“进入 `cs-task archive`”时，即表示当前 agent 必须执行本节归档动作，而不是把它转述成下一步建议；只有存在多个可归档任务、目标文件冲突或状态不一致时才停下来询问。

归档动作：

1. 目标路径：`.codestable/tasks/archived/YYYY-MM-DD-{task}.md`。
2. 如果多个可归档 task，使用当前 Agent 提供的结构化用户问答能力选择。
3. 如果目标文件已存在，询问用户改名或取消；不得覆盖。
4. 对 active 原文件执行移动 / 重命名，首选命令：`mv ".codestable/tasks/active/{task}.md" ".codestable/tasks/archived/YYYY-MM-DD-{task}.md"`。这一步必须消耗原始 active 文件；禁止用“读取 active 内容 → 写入 archived 新文件 → 稍后再删 active”的复制式归档。
5. 移动后，active 源路径视为失效路径；禁止再对 `.codestable/tasks/active/{task}.md` 使用 ApplyPatch / Edit / Write / 保存旧 buffer。若编辑器或工具仍持有移动前的 active 文件上下文，必须丢弃该上下文，后续所有读取和修改只指向 archived 目标文件。
6. 只在移动后的 archived 目标文件上更新 frontmatter：`status: archived`、`archived: YYYY-MM-DD`。
7. 只在移动后的 archived 目标文件上把“当前状态”改为 `archived`，归档记录写明目标路径。
8. 所有写入完成后、最终回复用户前，必须重新用当前文件系统事实验证归档状态：用不受 ignore 过滤的目录枚举或精确读取确认 archived 目标存在且 frontmatter 为 `status: archived`，并确认 active 源路径不可读 / 不存在。不能只依赖一次 shell `test ! -e active && test -e archived` 的历史 exit code。若 active 源路径重新出现且 archived 目标已是 `status: archived`，必须立即删除 active 残留并再次执行最终验证；如果无法删除或再次验证仍失败，归档失败，不得报告成功。

归档成功的判定标准必须把“移动到 archived”和“清理 active 原始文件”视为同一个结果：只有当归档目标已写入、active 中同名原件已删除，且 frontmatter 状态一致时，才算真正归档成功；归档后的 active 同名源不存在是硬退出条件，不是可选善后；最终回复前的当前文件系统验证通过才允许报告成功；任一条件未满足，都视为归档失败或未完成。

### Gate 机制

`cs-task` 不实现 Gate，本身只消费各 workflow 已落盘的证据作为任务推进和归档前置条件。只要某个 workflow 需要阶段证据，相关证据就必须先在对应 unit 中落盘，Task 才能进入 `completed`。

常见 Gate 输入：

- 路由 / 授权 / 风险接受：`approval-report.md`
- 实现批次：checklist / fix-note / ff-note / apply-notes / validation evidence
- 代码评审 / QA：review / QA 报告
- 收尾归档：acceptance report / completed Task spine

Gate 证据缺失时，Task 只能停留在 `blocked` 或 `active`，不能直接 `completed`。若发现已有代码改动或阶段产物但 Task spine 断裂，先 backfill Task，再按当前 workflow 需要的 review / QA / acceptance 证据继续收口。

查看历史任务时只读 `.codestable/tasks/archived/*.md`，按文件名前缀日期倒序列出。

---

## 用户询问协议

所有选择都通过当前 Agent 提供的结构化用户问答能力完成。选项尽量编号，用户默认只按键盘。

Task 创建 / 恢复属于 L0 自动编排：进入会写文件的 workflow 后，只要准备首次落盘，就直接 create / recovery，不再询问是否接入 Task。

多选列表也保留一个“自由输入补充信息”。如果自由输入无法消除歧义，重新给编号选项。

---

## 退出条件

- recovery：已明确并自动进入下一步 owner skill，或因真实歧义停在结构化问题；task 路径和未完成步骤已同步。
- create：Task List 已创建并同步运行时任务视图。
- update：Task List 文件先于运行时任务视图更新。
- complete：Task List 状态已改为 `completed`，并准备立即进入 archive。
- archive：Task List 已移动到 archived、frontmatter 状态一致，且 active 中没有同名残留。
- cleanup：已归档任务在 active 中没有同名残留。

---

## 常见错误

- 把 Task List 当成 feature checklist 重写。
- 只更新 Agent Todo，不更新 Task List 文件。
- 多个 active task 时自己猜用户要继续哪个。
- 归档时复制 / 重写 archived 文件，导致 active 和 archived 同时存在同一任务。
- 归档完成后没清理 active 中的同名残留。
- 归档目标存在时直接覆盖。
- 为 `cs-task` 自己的状态更新递归创建 Task List。
