---
name: cs-task
description: "CodeStable Task List 运行入口。创建、恢复、更新、完成和原子归档所有写入型 workflow 的强制 Task spine。"
argument-hint: "[create|resume|update|complete|archive|history|backfill] [task]"
contracts:
  - grep: "Task List 是 source of truth"
  - grep: "codestable-task-runtime.py"
  - grep: "`completed` 不是最终状态"
  - grep: "active 同名文件不存在"
  - grep: "backfill"
  - not-grep: ".codestable/tools/codestable-task-runtime.py"
---

# cs-task

## 启动必读

动作前先读 `.codestable/attention.md`。Task schema 和状态机见同目录 `reference.md`；项目级完整 workflow 契约见 `.codestable/reference/local-override-workflow.md`。

`cs-task` 是跨 workflow 的强制运行账本，不替代 feature checklist、roadmap items、issue 产物或 acceptance。它只管理 Task 生命周期，不直接实现 feature、issue 或 refactor。

Task List 是 source of truth；Agent Native Tasks / TodoWrite 只是运行时镜像。所有会修改项目文档或代码的 CodeStable workflow，在首次落盘前必须创建或恢复 Task。`completed` 不是最终状态；只有 archived 正本有效且 active 同名文件不存在，任务才闭环。

## 工具边界

Task create/update/complete/archive/cleanup 必须调用：

```text
python3 <cs-onboard skill 目录>/tools/codestable-task-runtime.py --root . <command>
```

不得新增或默认调用 `.codestable/tools/`。Task runtime 是唯一 active 写入与 archive 入口；禁止直接写 `.codestable/tasks/active/{task}.md` 绕过 tombstone。

## 模式

| 意图 | 模式 |
|---|---|
| 当前任务、继续任务 | `resume` |
| 首次进入写入型 workflow | `create` |
| 执行批次完成、更新进度 | `update` |
| 所有实现与 required gates 完成 | `complete` |
| 完成任务归档 | `archive` |
| 查看历史 | `history` |
| 已有产物或代码但缺 Task | `backfill` |

参数为空时扫描 `.codestable/tasks/active/*.md`。目录可能被 ignore，扫描必须使用不受 ignore 过滤的文件系统枚举，不能只凭 Glob/rg 的空结果判断没有任务。

## create / recovery gate

写入型 workflow 准备首次落盘时：

1. 同时检查 active 与 archived；archived 已有同 task 时禁止重建 active。
2. active 已有匹配 Task 时恢复，并同步第一个未完成步骤。
3. 都不存在时创建 Task，frontmatter 和固定正文节按 `reference.md`。
4. 将 `owner_skill` 指向当前负责阶段，并把已有 spec 产物加入 `related_docs`。
5. Task 落盘后立即在当前 run 继续 owner skill，不把下一条 `/cs-*` 命令交还用户。

多个 active Task 导致真实目标歧义时，使用结构化选择；单个匹配 Task 不询问。

## update

每个可观察实施批次结束后：

1. 生成完整新 Task 内容到临时文件。
2. 读取当前 active 正本并计算 SHA-256。
3. 更新 frontmatter `updated`、步骤状态、文档索引和 `owner_skill`。
4. 调用 runtime `write-active --expected-sha256 {sha256}` 执行 compare-and-swap 原子替换。
5. 若 SHA 已变化，停止并重新读取正本合并，不得用陈旧快照重试覆盖。
6. Task 文件成功后再同步 Agent Native Tasks。
7. 继续剩余实现；不得因为一个小步骤完成就提前进入 review。

## review batch handoff

Task 的实现步骤全部完成后，才把 `owner_skill` 转给 `cs-code-review`。一个 review batch 必须覆盖当前 design/checklist/fix 范围的完整实现，不得把未完成的其它实现项留在 batch 外。

Review 返回 changes-requested 时，把 owner 转回来源实现 skill，集中修复本轮全部 blocking/important findings，再进入 focused closure 或完整复审。review passed 前 Task 不得 complete。

## backfill

发现 spec、fix-note、ff-note、apply-notes 或代码实现已存在但 Task 缺失时：

1. 先检查 archived，防止已闭环 Task 被重新激活。
2. 从 unit frontmatter 和产物推断 `workflow`、`goal`、`owner_skill` 与 `related_docs`。
3. 创建 active Task，已完成步骤如实标记 done。
4. 根据证据推断缺失 gate：实现已完成但无 passed review 时进入 `cs-code-review`；review passed 后进入 QA/acceptance 或 complete。
5. backfill 后自动续跑缺失 gate，不能只补账本后结束。

## complete

只有同时满足以下条件才能标记 `completed`：

- Task 同步区和执行步骤全部完成；
- 当前实现 batch 的 review 已 passed；
- workflow 要求的 QA/acceptance 已完成；
- required spec/gate/evidence 已落盘；
- 没有 blocking/important finding 未处理。

生成完整新内容并通过 runtime `write-active --expected-sha256 {sha256}` 写入 `status: completed`，然后在当前 run 立即进入 archive。

## archive / cleanup

归档仅接受 `completed` 或 `cancelled`：

```text
python3 <cs-onboard skill 目录>/tools/codestable-task-runtime.py \
  --root . archive --task {task} --date YYYY-MM-DD
```

runtime 会：

1. 写 `archiving` tombstone 和归档前 SHA-256；
2. 原子移动 active 正本；
3. 更新 archived frontmatter/body；
4. 完成 tombstone；
5. 在稳定性窗口内清理内容相同的 stale rewrite；
6. 对内容分叉的 active residue fail closed。

最终回答前再次执行：

```text
python3 <cs-onboard skill 目录>/tools/codestable-task-runtime.py \
  --root . cleanup --task {task}
```

并以当前文件系统确认 archived 正本有效、active 同名文件不存在。任一条件失败都不能报告完成。

## 自动编排

- Task create/recovery/update、确定性的 owner handoff、review gate 和 archive 属于机械继续。
- 只有多个匹配 Task、archive 冲突、divergent residue 或状态无法推断时才进入 HumanCheckpoint。
- `cs-task` 自己更新 Task 文件时不递归创建新的 Task。
- Task 归档完成前，不允许 workflow 最终答复声称完整闭环。

## 退出条件

- `resume`：已恢复 Task 并自动进入 owner skill，或因真实歧义停在结构化选择。
- `create/update`：runtime 原子写成功，Agent Tasks 已同步。
- `complete`：状态已写为 completed，当前 run 继续 archive。
- `archive`：archived 正本有效、tombstone 完成、active 同名文件不存在。
- `history`：只读 archived，按日期倒序返回。
