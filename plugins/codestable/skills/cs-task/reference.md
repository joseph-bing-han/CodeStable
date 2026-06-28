# cs-task 参考协议

本文件定义 Task List 的目录、schema、正文和状态机。`SKILL.md` 定义运行流程；本文件定义持久化契约。

## 1. 目录结构

```text
.codestable/tasks/
├── active/
│   └── {task}.md
├── archived/
│   └── YYYY-MM-DD-{task}.md
├── tombstones/
│   └── {task}.json
├── staging/
│   └── {task}.md
├── conflicts/
│   └── {task}-{unique}.md
└── locks/
    └── {task}.lock
```

- active 文件不带日期，archived 文件必须带归档日期。
- active 允许 `active`、`blocked`、`completed`、`cancelled`。
- archived 只允许 `archived`。
- create/update/complete/backfill 必须通过 runtime `write-active`。
- 更新已有 active Task 时必须传入读取正本时计算的 `--expected-sha256`；陈旧快照必须以 compare-and-swap conflict 失败。
- archive/cleanup 必须通过同一个 runtime；禁止手工复制后删除。
- 判断 Task 是否缺失时同时检查 active、archived 和 tombstone。
- `.codestable` 可能被 ignore，扫描必须使用不受 ignore 过滤的文件系统枚举。
- 2026-07-17 之前生成的 archived-only Task 作为历史只读证据兼容；从该日期起的新归档必须具备严格 tombstone。

## 2. Frontmatter schema

```yaml
---
doc_type: task-list
task: restore-local-override-workflow
goal: Restore the local CodeStable override workflow
status: active
workflow: feature
owner_skill: cs-feat-impl
created: YYYY-MM-DD
updated: YYYY-MM-DD
archived: null
related_docs:
  - .codestable/features/YYYY-MM-DD-feature/feature-design.md
---
```

| 字段 | 约束 |
|---|---|
| `doc_type` | 固定 `task-list` |
| `task` | 小写英文连字符，必须与 active 文件名一致 |
| `goal` | 人类可读目标 |
| `status` | `active` / `blocked` / `completed` / `cancelled` / `archived` |
| `workflow` | 当前 workflow 类型 |
| `owner_skill` | 当前负责继续执行的 skill |
| `created` | 创建日期 |
| `updated` | 最近更新日期 |
| `archived` | 未归档为 `null`，归档后为日期 |
| `related_docs` | 当前任务关联的 canonical 产物 |

## 3. 固定正文

每个 Task 必须保留以下章节：

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

没有内容的章节写“无”，不得删除。Agent 同步区和执行步骤必须能映射到当前实现批次，而不是把每个微小编辑拆成独立 review 单元。

## 4. 状态机

合法转换：

```text
active -> blocked
blocked -> active
active -> completed
active -> cancelled
completed -> archived
cancelled -> archived
```

禁止转换：

```text
active -> archived
blocked -> archived
completed -> active
cancelled -> active
archived -> active
```

`completed` 是待归档态，不是 workflow 结束态。

## 5. Runtime 命令

新版工具固定从 cs-onboard skill 目录调用：

```text
python3 <cs-onboard skill 目录>/tools/codestable-task-runtime.py --root . scan
python3 <cs-onboard skill 目录>/tools/codestable-task-runtime.py --root . write-active --task {task} --content-file {path}
python3 <cs-onboard skill 目录>/tools/codestable-task-runtime.py --root . write-active --task {task} --content-file {path} --expected-sha256 {sha256}
python3 <cs-onboard skill 目录>/tools/codestable-task-runtime.py --root . archive --task {task} --date YYYY-MM-DD
python3 <cs-onboard skill 目录>/tools/codestable-task-runtime.py --root . cleanup --task {task}
```

不得新增 `.codestable/tools/codestable-task-runtime.py` 新版入口。

## 6. Tombstone 契约

archive 开始前写入：

```json
{
  "task": "restore-local-override-workflow",
  "state": "archiving",
  "source_status": "completed",
  "source_sha256": "...",
  "archived_path": ".codestable/tasks/archived/YYYY-MM-DD-restore-local-override-workflow.md",
  "archived_date": "YYYY-MM-DD",
  "staging_path": ".codestable/tasks/staging/restore-local-override-workflow.md"
}
```

archive 正本写入完成后，状态改为 `archived` 并记录 `archived_sha256`。

- active 重现内容与 `source_sha256` 一致：runtime 自动清理。
- active 重现内容不同：返回 `divergent-active-residue` 并阻塞。
- archived 正本缺失或 hash 不匹配：阻塞，不得删除 active。
- 无 staging/source snapshot 的 archived-only 中间态不可自动认证，返回 `incomplete-archive`。
- `conflicts/` 中的未解决证据会使 inspect/scan fail closed。
- `locks/` 是同版本 runtime 的协作锁；跨调用一致性仍以 expected SHA、tombstone 状态机和冲突保留为准。

## 7. Review 与归档前置条件

Task 只有在当前 workflow 的 required evidence 齐全时才能 complete：

- feature/refactor checklist 全部完成；
- issue fix-note 或等价实施记录存在；
- 当前完整实现 batch 已由独立 Task agent review；
- blocking/important findings 已集中修复并复审通过；
- workflow 要求的 QA/acceptance 已完成；
- 没有待执行的 `workflow-next` 动作。

归档成功必须同时满足：

1. archived 文件存在且 frontmatter 为 `status: archived`；
2. tombstone 为 `state: archived`；
3. archived hash 与 tombstone 匹配；
4. active 同名文件不存在。

## 8. Agent Native Tasks

Agent Todo/Tasks 是 Task List 的镜像：

- Task 文件先更新，Agent Tasks 后同步；
- Agent Tasks 更新失败不回滚 Task source of truth，但必须报告降级；
- 不允许只更新 Agent Tasks 而不更新 Task 文件；
- Task recovery 从正文第一个未完成步骤恢复 Agent Tasks。

## 9. 用户选择

Task create/recovery 是 L0 自动动作，不询问是否创建。仅以下情况使用结构化选择：

- 多个 active Task 都可能匹配当前诉求；
- archive 目标冲突；
- divergent residue；
- 无法确定 owner skill 或 workflow。

用户选择后仍应在当前 run 自动进入目标 workflow。
