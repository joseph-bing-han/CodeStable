---
doc_type: roadmap
slug: codestable-task-system
status: active
created: 2026-05-30
last_reviewed: 2026-05-30
tags: [task, workflow, recovery, agent-sync]
related_requirements: []
related_architecture: []
---

# CodeStable Task System

## 1. 背景

CodeStable 当前缺少跨工作流的任务列表入口。feature、issue、refactor 等流程虽然各自有局部产物，例如 checklist、analysis、fix-note、roadmap items，但没有一个统一位置能回答“当前正在做什么、做到哪一步、关联了哪些 CodeStable 文档、任务中断后从哪里继续”。

Task System 的目标是补齐这一层：用 `.codestable/tasks/` 作为跨 workflow 的任务运行账本，用 `cs-task` 作为恢复、同步、完成和归档入口，并让所有涉及项目内文档或代码变更的 CS skill 都有明确接入策略。

## 2. 范围与明确不做

### 本 roadmap 覆盖

- 新增 `.codestable/tasks/active/` 与 `.codestable/tasks/archived/` 目录约定。
- 新增 `cs-task` 技能，负责查找、恢复、选择、同步、完成和归档任务。
- 定义 task list 文件格式、状态机、CodeStable 文档索引、归档命名规则。
- 定义 task list 与 Agent 原生 Tasks/Todo 工具的同步协议。
- 定义所有 CS skill 的接入等级：重要变更自动进入 Tasks；次要变更结构化询问后进入或跳过。
- 接入所有能接入的、会修改项目内文档或代码的 CS skill。
- 更新 shared conventions、onboard 模板、根入口和相关技能表述。

### 明确不做

- 不用 task list 替代 feature/refactor 的 `{slug}-checklist.yaml`。
- 不用 task list 替代 roadmap 的 `{slug}-items.yaml`。
- 不让 task list 绕过 design、analyze、review 等人工 checkpoint。
- 不把 task 写入 requirements 或 architecture；requirements 仍记能力愿景，architecture 仍只记现状。
- 不做跨项目全局任务中心；任务范围限定在当前项目的 `.codestable/tasks/`。
- 不为每个 Agent 工具实现私有 SDK；第一版定义通用协议和降级行为。

## 3. 模块拆分（概设）

```text
CodeStable Task System
├── Task Storage Model：定义 tasks 目录、文件命名、frontmatter、正文结构和状态机
├── cs-task Runtime：负责查找 active tasks、选择任务、恢复任务、完成任务和归档任务
├── Task Integration Policy：定义所有 CS skill 的接入等级、触发方式、跳过规则和防递归规则
├── Agent Sync Adapter：把 task list 映射到 Agent 原生任务视图
├── Workflow Integration Layer：让所有可接入的变更型 skill 自动或询问接入 Task 流程
└── Onboard & Shared Conventions：把 Task System 写入共享约定、onboard 模板和入口文档
```

### Task Storage Model · 任务存储模型

- **职责**：定义 `.codestable/tasks/active/` 和 `.codestable/tasks/archived/` 的目录结构、文件命名、task list frontmatter、正文固定章节、状态机和归档规则。
- **承载的子 feature**：`task-core-storage-runtime`
- **触碰的现有模块**：新增 `cs-task/reference.md`，更新 `cs-onboard/reference/shared-conventions.md`

### cs-task Runtime · 任务运行入口

- **职责**：提供 `cs task` 行为规范：扫描任务、处理多个 active task、恢复上下文、识别 completed 未归档任务、执行归档。
- **承载的子 feature**：`task-core-storage-runtime`
- **触碰的现有模块**：新增 `cs-task/SKILL.md`，更新 `cs/SKILL.md`

### Task Integration Policy · 技能接入策略

- **职责**：定义每个 CS skill 的 task 接入等级，确保所有涉及项目内文档或代码变更的 skill 都有策略。
- **承载的子 feature**：`task-integration-policy`
- **触碰的现有模块**：`cs-task/reference.md`、`cs-onboard/reference/shared-conventions.md`、所有会落盘或改代码的 CS skill

### Agent Sync Adapter · Agent 原生任务同步

- **职责**：定义 CodeStable task list 到 Cursor、Claude Code、Codex、OpenCode 等 Agent 原生任务视图的映射协议。task list 是 source of truth，Agent 原生 Tasks 是运行时镜像。
- **承载的子 feature**：`task-agent-sync-protocol`
- **触碰的现有模块**：`cs-task/reference.md`、核心 workflow 技能中关于 Agent task tool 的表述

### Workflow Integration Layer · 工作流接入层

- **职责**：让所有会修改项目内文档或代码的 CS skill 都遵守 Task 接入策略；重要变更自动进入，次要变更结构化询问。
- **承载的子 feature**：`task-core-workflow-integration`、`task-optional-workflow-integration`
- **触碰的现有模块**：feature、issue、refactor、audit、roadmap、req、arch、guide、libdoc、compound、brainstorm、onboard 等技能

### Onboard & Shared Conventions · 共享约定与模板传播

- **职责**：把 Task System 变成 CodeStable 正式实体，确保新项目 onboard 后自动带有 tasks 目录、共享规则和恢复说明。
- **承载的子 feature**：`task-onboard-docs-consistency`
- **触碰的现有模块**：`cs-onboard/SKILL.md`、`cs-onboard/reference/*`、README、根入口文档

## 4. 模块间接口契约 / 共享协议（架构层详设）

### 4.1 Task File Layout Contract

**方向**：Workflow Integration Layer → Task Storage Model  
**形式**：文件协议

```text
.codestable/tasks/
├── active/
│   └── {task-goal}.md
└── archived/
    └── YYYY-MM-DD-{task-goal}.md
```

**约束**：active 文件不带日期；archived 文件用归档日期前缀；归档时移动文件不复制；归档目标存在时必须询问用户，不能覆盖。

### 4.2 Task List Frontmatter Schema

**方向**：所有 CodeStable workflow → Task Storage Model  
**形式**：Markdown frontmatter schema

```yaml
---
doc_type: task-list
task: codestable-task-system
goal: Add CodeStable task list workflow
status: active
workflow: roadmap
owner_skill: cs-roadmap
created: 2026-05-30
updated: 2026-05-30
archived: null
related_docs: []
---
```

`status` 取值：`active | blocked | completed | archived | cancelled`。

### 4.3 Task Status State Machine

```text
active → blocked
blocked → active
active → completed
active → cancelled
completed → archived
cancelled → archived
```

不合法跃迁：`archived → active`、`completed → active`、`cancelled → active`、`blocked → archived`、`active → archived`。

### 4.4 Task Body Section Protocol

```markdown
# {Goal}

## 1. 任务目标
## 2. 当前状态
## 3. Agent 原生 Tasks 同步区
## 4. CodeStable 文档索引
## 5. 执行步骤
## 6. 中断恢复提示
## 7. 完成与归档记录
```

`CodeStable 文档索引` 必须列出本任务相关的 design、checklist、report、analysis、fix-note、acceptance、roadmap、requirement、architecture 等文档。每完成一步，必须先更新 task list 文件，再同步 Agent 原生 Tasks。

### 4.5 Skill Task Integration Classification Protocol

**方向**：所有 CS skill → Task Integration Policy  
**形式**：技能接入分级表

```yaml
skill_task_policy:
  mode: auto | ask | route-only | internal
  reason: string
  applies_when: string
```

**自动进入 Tasks 的重要变更**：

```text
cs-onboard
cs-roadmap
cs-req
cs-arch
cs-feat-design
cs-feat-impl
cs-feat-accept
cs-feat-ff
cs-issue-report
cs-issue-analyze
cs-issue-fix
cs-refactor
cs-refactor-ff
cs-audit
```

**询问是否进入 Tasks 的次要变更**：

```text
cs-brainstorm
cs-note
cs-learn
cs-trick
cs-decide
cs-explore
cs-guide
cs-libdoc
```

**不直接创建 task 的入口或内部技能**：

```text
cs
cs-feat
cs-issue
cs-task
```

约束：只要 skill 会修改项目内文档或代码，就必须有 Task 接入策略。没有接入策略的 skill 不允许修改项目文件。

### 4.6 User Question Protocol

**方向**：cs-task Runtime / Workflow Integration Layer → Agent 工具  
**形式**：结构化用户选择协议

所有询问用户的地方都必须调用 Agent 工具的 `user_question_answer` 类能力，尽量让用户只按键盘编号选择。

二选一决策固定形式：

```text
1. 进入 Tasks
2. 跳过 Tasks
3. 自由输入补充信息
```

约束：不允许用开放式长问题替代编号选择；选项数量控制在 2-5 个；固定保留“自由输入补充信息”；如果用户选择自由输入但没有解决当前决策，必须再次给编号选项。

### 4.7 cs-task Discovery Protocol

```text
1. 扫描 .codestable/tasks/active/*.md
2. active 或 blocked 任务视为可恢复任务
3. completed 任务视为待归档任务
4. 单个可恢复任务直接读取并同步 Agent 原生 Tasks
5. 多个可恢复任务使用 user_question_answer 询问用户选择
6. 多个 completed 任务使用 user_question_answer 询问用户归档哪个
7. 没有任何任务时报告当前无 active task
```

### 4.8 Agent Native Sync Protocol

```text
sync_agent_tasks(task_list_path, task_items, active_step) -> sync_result
```

适配规则：Cursor 使用 `TodoWrite`；Claude Code 使用原生 todo/task 工具；Codex、OpenCode 有原生任务工具则同步，否则降级为 Markdown task block；未知 Agent 跳过同步但不阻塞文件更新。

### 4.9 Workflow Task Hook Protocol

```text
ensure_task_list(workflow, owner_skill, goal, related_docs) -> task_list_path
update_task_step(task_list_path, step_id, status, note) -> task_list_path
append_task_doc_index(task_list_path, doc_type, path, description) -> task_list_path
complete_task(task_list_path, completion_note) -> task_list_path
archive_task(task_list_path, archive_date) -> archived_path
```

## 5. 子 feature 清单

1. **task-core-storage-runtime** — 新增 tasks 目录模型、task list 文件格式、状态机、`cs-task` 技能入口和恢复归档流程。
   - 所属模块：Task Storage Model / cs-task Runtime
   - 依赖：无
   - 状态：done
   - 对应 feature：2026-05-30-task-core-storage-runtime
   - 备注：最小闭环

2. **task-integration-policy** — 定义所有 CS skill 的 auto / ask / route-only / internal 接入等级和防递归规则。
   - 所属模块：Task Integration Policy
   - 依赖：task-core-storage-runtime
   - 状态：planned
   - 对应 feature：未启动

3. **task-agent-sync-protocol** — 定义并接入 Agent 原生 Tasks/Todo 同步协议。
   - 所属模块：Agent Sync Adapter
   - 依赖：task-core-storage-runtime
   - 状态：planned
   - 对应 feature：未启动

4. **task-core-workflow-integration** — 接入所有自动进入 Tasks 的重要变更技能。
   - 所属模块：Workflow Integration Layer
   - 依赖：task-integration-policy, task-agent-sync-protocol
   - 状态：planned
   - 对应 feature：未启动

5. **task-optional-workflow-integration** — 接入所有询问是否进入 Tasks 的次要变更技能，并统一 user_question_answer 交互。
   - 所属模块：Workflow Integration Layer
   - 依赖：task-integration-policy, task-agent-sync-protocol
   - 状态：planned
   - 对应 feature：未启动

6. **task-onboard-docs-consistency** — 更新 onboard 模板、共享约定、系统总览、维护说明、根入口和 README。
   - 所属模块：Onboard & Shared Conventions
   - 依赖：task-core-workflow-integration, task-optional-workflow-integration
   - 状态：planned
   - 对应 feature：未启动

**最小闭环**：第 1 条 `task-core-storage-runtime` 做完后，用户可以在项目中拥有 `.codestable/tasks/active/*.md`，运行 `cs task` 找到当前任务、恢复任务，并在完成后归档到 `.codestable/tasks/archived/YYYY-MM-DD-{task-goal}.md`。

## 6. 排期思路

先做 `task-core-storage-runtime`，因为它定义正式实体和恢复入口。第二步做 `task-integration-policy`，先把所有 skill 的接入等级定死，避免后续改一半漏一半。第三步做 `task-agent-sync-protocol`，让任务文件能映射到 Agent 原生任务工具。第四步接入自动进入 Tasks 的重要变更技能。第五步接入询问进入 Tasks 的次要变更技能。最后做 onboard、README、共享约定和一致性收口。

## 7. 观察项

- 当前仓库原本没有项目级 `.codestable/attention.md`，本次按用户确认先落盘 roadmap 和 bootstrap task 文件。
- `cs-onboard/reference/shared-conventions.md` 当前目录树使用 `.codestable/brainstorm/`，而 `cs-brainstorm/SKILL.md` 和 `cs-brainstorm/reference.md` 使用 `.codestable/brainstorms/`，后续一致性收口应修正。
- `requment.md` 是当前需求草稿，文件名存在拼写问题；实现后应迁移为正式 requirement 或 roadmap 关联材料。
- 文档单文件不能超过 300 行，`cs-task/reference.md` 和 shared conventions 更新时需要控制篇幅，必要时拆分 reference 子文档。

## 8. 变更日志

- 2026-05-30：创建 roadmap 初版，纳入所有可接入技能必须接入 Task 流程、auto/ask 分级，以及 user_question_answer 编号选择协议。
