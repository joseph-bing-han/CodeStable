---
name: cs-task
description: CodeStable Task List 运行入口。触发：用户说"cs task"、"继续当前任务"、"任务列表"、"历史任务"、"归档任务"，或任一 CS workflow 需要创建、恢复、同步、完成、归档 Task List 时使用。管理 `.codestable/tasks/active` 与 `.codestable/tasks/archived`，不处理具体 feature/issue 实现。
---

# cs-task

`cs-task` 是 CodeStable 的任务运行账本入口。它不替代 feature checklist、roadmap items 或 issue report，而是提供跨 workflow 的“当前任务 / 中断恢复 / 历史归档”统一入口。

> 详细 schema、状态机和模板看同目录 `reference.md`。共享目录约定看 `.codestable/reference/shared-conventions.md`。

## Task 接入

- 等级：`internal-runtime`。本 skill 负责创建、恢复、更新、完成、归档 Task List 本身，绝不为自己的 task 文件变更递归创建新的 Task List。
- 其他会写项目内文档或代码的 CS skill 一旦进入 Tasks，都通过本 skill 落盘和同步；active / archived 清理、归档残留删除是本 skill 的默认职责，不是可选步骤。
- 只有当别的 workflow 调用本 skill 做 create / update / complete / archive / recovery 时，才更新现有 Task List；`cs-task` 自己不再套一层 Task。

---

## 启动必读

1. 先读 `.codestable/attention.md`；缺失时提示骨架不完整，但如果当前任务正是 Task System bootstrap，可继续读取 `.codestable/tasks/` 与 roadmap 上下文。
2. 读取 `.codestable/tasks/active/*.md`；如果目录不存在，说明还没有 task system 实例，提示先创建 task list 或走 `cs-onboard`。
3. 读取 `.codestable/tasks/archived/*.md`，先清理 active 中已归档任务的残留副本，再进入 recovery / archive。
4. `cs-task` 是 internal runtime：只更新 task 文件本身时，不再为这个更新递归创建新的 Task List。

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

判断不出时，用结构化用户问题让用户选，不要开放式追问。

---

## recovery：恢复当前任务

1. 扫描 `.codestable/tasks/active/*.md` 和 `.codestable/tasks/archived/*.md`。
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

## create：创建 Task List

创建条件：当前 CS skill 会修改项目内文档或代码，且策略要求进入 Tasks。

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
4. 不自动删除 active 文件；归档动作走 archive。

---

## archive / history：归档与历史

归档对象：active 目录中 `status: completed` 或 `status: cancelled` 的 task。

归档动作：

1. 目标路径：`.codestable/tasks/archived/YYYY-MM-DD-{task}.md`。
2. 如果多个可归档 task，使用当前 Agent 提供的结构化用户问答能力选择。
3. 如果目标文件已存在，询问用户改名或取消；不得覆盖。
4. 移动文件到 archived。
5. frontmatter 改为 `status: archived`，`archived: YYYY-MM-DD`。
6. “当前状态”改为 `archived`，归档记录写明目标路径。
7. 归档完成后重新检查 `.codestable/tasks/active/{task}.md`；如果仍存在同名 active 残留，自动删除。归档的退出条件是 active 中不存在同名任务。

查看历史任务时只读 `.codestable/tasks/archived/*.md`，按文件名前缀日期倒序列出。

---

## 用户询问协议

所有选择都通过当前 Agent 提供的结构化用户问答能力完成。选项尽量编号，用户默认只按键盘。

二选一固定格式：

```text
1. 进入 Tasks
2. 跳过 Tasks
3. 自由输入补充信息
```

多选列表也保留一个“自由输入补充信息”。如果自由输入无法消除歧义，重新给编号选项。

---

## 退出条件

- recovery：已明确并自动进入下一步 owner skill，或因真实歧义停在结构化问题；task 路径和未完成步骤已同步。
- create：Task List 已创建并同步运行时任务视图。
- update：Task List 文件先于运行时任务视图更新。
- complete：Task List 状态已改为 `completed`。
- archive：Task List 已移动到 archived 且 frontmatter 状态一致。
- cleanup：已归档任务在 active 中没有同名残留。

---

## 常见错误

- 把 Task List 当成 feature checklist 重写。
- 只更新 Agent Todo，不更新 Task List 文件。
- 多个 active task 时自己猜用户要继续哪个。
- 归档时复制文件，导致 active 和 archived 同时存在同一任务。
- 归档完成后没清理 active 中的同名残留。
- 归档目标存在时直接覆盖。
- 为 `cs-task` 自己的状态更新递归创建 Task List。
