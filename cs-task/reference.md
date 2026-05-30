# cs-task 参考协议

本文件定义 Task List 的机器可读字段、人类可读正文和状态流转。`SKILL.md` 保留流程骨架；具体格式以本文件为准。

---

## 1. 目录结构

```text
.codestable/tasks/
├── active/
│   └── {task}.md
└── archived/
    └── YYYY-MM-DD-{task}.md
```

规则：

- `active/` 存放 `active`、`blocked`、`completed`、`cancelled` 状态的任务。
- `archived/` 只存放 `archived` 状态的任务。
- active 文件不带日期前缀；archived 文件必须用归档日期前缀。
- 归档是移动文件，不复制文件。
- 如果 archived 中已经存在 `YYYY-MM-DD-{task}.md` 且状态为 `archived`，active 中同名 `{task}.md` 视为归档残留，`cs-task` 必须自动清理。

---

## 2. frontmatter schema

```yaml
---
doc_type: task-list
task: task-core-storage-runtime
goal: Implement the core CodeStable task storage and recovery runtime
status: active
workflow: feature
owner_skill: cs-feat-impl
created: YYYY-MM-DD
updated: YYYY-MM-DD
archived: null
related_docs:
  - .codestable/features/YYYY-MM-DD-task/task-design.md
---
```

字段：

| 字段 | 规则 |
|---|---|
| `doc_type` | 固定 `task-list` |
| `task` | 小写英文连字符，必须和 active 文件名一致 |
| `goal` | 人类可读任务目标 |
| `status` | `active` / `blocked` / `completed` / `cancelled` / `archived` |
| `workflow` | `feature` / `issue` / `refactor` / `roadmap` / `req` / `arch` / `audit` / `compound` / `guide` / `libdoc` / `onboard` / `task` |
| `owner_skill` | 当前负责推进的 skill，如 `cs-feat-impl` |
| `created` | 创建日期 |
| `updated` | 最近更新日期 |
| `archived` | 未归档为 `null`，归档后为日期 |
| `related_docs` | 关联 CodeStable 文档路径列表 |

---

## 3. 正文模板

```markdown
# {Goal}

## 1. 任务目标

{一句话说明本任务要完成什么。}

## 2. 当前状态

active

## 3. Agent 原生 Tasks 同步区

- [ ] {task item}

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| design | `.codestable/features/...` | 方案 |

## 5. 执行步骤

### 1. {Step title}

- 状态：pending
- 来源：{design / checklist / roadmap / issue / manual}
- 完成信号：{可观察退出信号}

## 6. 中断恢复提示

下次运行 `cs task` 时，从第一个 pending 步骤继续。

## 7. 完成与归档记录

尚未完成。
```

固定节不能删除；没有内容时写“无”。

---

## 4. 状态机

合法跃迁：

```text
active -> blocked
blocked -> active
active -> completed
active -> cancelled
completed -> archived
cancelled -> archived
```

不合法跃迁：

```text
archived -> active
completed -> active
cancelled -> active
blocked -> archived
active -> archived
```

语义：

- `active`：可以继续执行。
- `blocked`：等待用户或外部条件，正文必须写阻塞原因。
- `completed`：任务内容已完成，等待归档。
- `cancelled`：用户明确取消，等待归档。
- `archived`：历史记录，不能恢复执行。

---

## 5. 用户询问协议

所有需要用户选择的地方，优先使用当前 Agent 提供的结构化用户问答能力。不要用开放式长问题。

### 是否进入 Tasks

```text
这次会修改项目内文档或代码，是否进入 Tasks 流程？

1. 进入 Tasks
2. 跳过 Tasks
3. 自由输入补充信息
```

### 多任务选择

```text
检测到多个进行中的 Tasks，请选择要继续的任务：

1. {task-a-goal}
2. {task-b-goal}
3. 自由输入补充信息
```

### 多个完成任务归档

```text
检测到多个已完成但未归档的 Tasks，请选择要归档的任务：

1. {task-a-goal}
2. {task-b-goal}
3. 自由输入补充信息
```

选项数量尽量 2-5 个；自由输入不能消除歧义时，再给编号选项。

---

## 6. Agent Native Tasks 同步

同步输入从“Agent 原生 Tasks 同步区”提取：

```yaml
task_list_path: .codestable/tasks/active/task-core-storage-runtime.md
task_items:
  - id: create-skill
    content: 新增 cs-task skill
    status: pending
active_step: create-skill
```

适配规则：

- Cursor：用 TodoWrite 同步。
- Claude Code：用原生 todo/task 工具同步。
- Codex / OpenCode：有原生任务工具就同步，否则降级为 Markdown checklist。
- 未知 Agent：跳过同步，但不能阻塞 Task List 文件更新。

同步失败时，在回复中说明降级方式。

---

## 7. 完成与归档规则

完成任务前必须满足：

- Agent 同步区所有条目已勾选。
- 执行步骤无 `pending` / `in-progress`。
- 关联 workflow 的必须文档已落盘。

归档步骤：

1. 确认 task `status` 是 `completed` 或 `cancelled`。
2. 计算目标路径：`.codestable/tasks/archived/YYYY-MM-DD-{task}.md`。
3. 如果目标存在，询问用户改名或取消。
4. 移动文件。
5. 更新 frontmatter：`status: archived`、`archived: YYYY-MM-DD`。
6. 更新正文“当前状态”和“完成与归档记录”。
7. 复查 active 目录，同名 `{task}.md` 如果仍存在则删除。

归档后 active 目录不应保留同名任务。

## 8. 归档残留清理

每次 recovery / archive / history 前先执行清理：

1. 扫描 `active/*.md` 和 `archived/*.md`。
2. 对每个 active `{task}.md`，查找 archived 中是否存在 `YYYY-MM-DD-{task}.md`。
3. 如果 archived 文件 frontmatter 是 `status: archived`，删除 active 副本。
4. 如果 archived 文件存在但状态不是 `archived`，停下报告状态不一致，不自动删除。
5. 清理后再计算 active / completed / cancelled 任务列表。

清理规则只删除已确认归档的同名 active 残留，不删除没有 archived 对应文件的 active task。
