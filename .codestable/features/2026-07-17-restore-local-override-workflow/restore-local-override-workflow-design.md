---
doc_type: feature-design
feature: 2026-07-17-restore-local-override-workflow
status: approved
summary: 在 CodeStable 1.0.4 上恢复本地 Task spine、去 OCR 独立审查门禁与完整自动编排闭环
tags: [codestable, local-override, task, code-review, orchestration]
---

# restore-local-override-workflow design

## 1. 目标与范围

本次改动以当前 CodeStable 1.0.4 为主体，恢复因上游同步丢失的本地 overlay：

- `cs-task` skill 及 guarded Task runtime；
- Task create/recovery/update/complete/archive/cleanup 状态机；
- `cs-code-review` 去 OCR，仅保留独立 Task agent；
- 写入型 workflow 的 Task → implementation batch → review → archive 强制主干；
- direct-entry 在当前 run 自主推进，不要求用户手动输入下一阶段命令；
- review 以完整实现批次为单位，集中修复 findings 后复审。

明确不恢复：旧 `.codestable/tools/` 新版入口、worktree/main publish 工具、旧 stage 手工跳转、browser bridge。

## 2. 关键设计

### 2.1 Task runtime 适配

旧 runtime 的状态机语义保留，但工具迁移到：

```text
plugins/codestable/skills/cs-onboard/tools/codestable-task-runtime.py
```

runtime 提供 `scan`、`write-active`、`archive`、`cleanup`。所有 active 写入采用临时文件 + 原子替换；archive 使用 tombstone、SHA-256 和稳定性复验防止 stale rewrite。

### 2.2 Task spine 接入

`cs-task` 是独立安装单元，不读取 sibling skill。共享约束通过项目 `.codestable/reference/local-override-workflow.md` 和 onboard runtime reference 传播。

入口 skill 继续使用当前 1.0.4 的 `continuing-current-run` 与 `workflow-next`。本地 overlay 只补以下机械门禁：

1. 写入前 create/recovery Task；
2. 实施批次完成前持续更新 Task；
3. 实现全部完成后统一进入 review；
4. review/QA/acceptance 证据齐全后 complete + archive；
5. active 残留不存在才允许最终结束。

### 2.3 Review 去 OCR

移除 review 状态机、protocol、doctor、report template 和 gate 中的 OCR 新流程分支。历史 `subagent+ocr` 证据保持可读兼容，但新流程只生成 `reviewer: subagent`。

独立 Task agent 不可用时 fail closed。不得静默改用 self review、OCR 或第三方 APP。

### 2.4 Review 批次边界

一个 review batch 对应一个已定稿 spec/fix/refactor 范围及其完整实现 diff。实现阶段必须先完成该批次全部 checklist/fix 项，再启动首次 review。review-fix 集中处理本轮全部 blocking/important findings；只有 closure-only diff 才走 focused closure，其它情况完整复审。

## 3. 修改面

- 新增 `plugins/codestable/skills/cs-task/`；
- 新增 `codestable-task-runtime.py` 并注册 runtime capability；
- 更新 `cs-code-review` skill、independent-review protocol、report template；
- 更新 `codestable_common.py`、doctor、workflow-next 的 review 证据规则；
- 更新 `cs`、`cs-feat`、`cs-issue`、`cs-refactor`、`cs-epic`、`cs-goal`、`cs-audit` 的 Task spine/批次门禁表述；
- 增加 runtime、review、skill package 回归测试；
- 同步 onboard references 与项目 `.codestable/reference/`。

## 4. 验收契约

- skill discovery 能发现 `cs-task`；
- Task runtime 的原子写、archive、stale cleanup、divergent residue 阻塞均有测试；
- plugin skill/source 与本地安装同步后均含 `cs-task`；
- `plugins/codestable/` 中不再存在 OCR 运行依赖；
- 新 review 报告只接受/生成 `reviewer: subagent`；
- 入口 workflow 明确执行完整 spine，不把下一阶段命令交还用户；
- review 在实现批次完成后统一触发；
- `pytest`、`git diff --check`、`codestable-runtime-sync.py --check --json` 通过。
