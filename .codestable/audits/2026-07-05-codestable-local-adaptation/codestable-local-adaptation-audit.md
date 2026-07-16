---
doc_type: onboarding-audit
task: refresh-codestable-local-adaptation
status: completed
created: 2026-07-05
updated: 2026-07-05
owner_skill: cs-onboard
---

# CodeStable 本地适配复核审计

## 1. 背景

本次处理基于 2026-07-03 已完成的共享资产刷新，继续补齐两个收尾动作：

- 把 `.codestable/attention.md` 升级到新版骨架
- 复核 `.codestable/` 中剩余目录，区分当前标准目录与历史遗留目录

## 2. 本次已执行适配

| 项目 | 结果 |
|---|---|
| `.codestable/attention.md` | 已补入新版“报告语言”段落，保留原有项目碎片知识分节 |
| `.codestable/tools/` | 延续 2026-07-03 刷新结果，当前已是新版共享工具副本 |
| `.codestable/reference/` | 延续 2026-07-03 刷新结果，当前已是新版共享参考副本 |
| `.codestable/gates/roadmap-goal-gates.yaml` | 已存在，属于当前版本新增 gate 配置 |
| `.codestable/compound/2026-07-05-codestable-architecture-overview.md` | 已承接原 `architecture/ARCHITECTURE.md` 的骨架内容并补充迁移说明 |
| `.codestable/architecture/` | 已完成迁移后删除 |
| `.codestable/config/` | 已按确认删除空目录 |

## 3. 兼容性扫描结论

### 3.1 当前标准或当前运行时所需目录

- `.codestable/requirements/`
- `.codestable/roadmap/`
- `.codestable/goals/`
- `.codestable/features/`
- `.codestable/issues/`
- `.codestable/refactors/`
- `.codestable/audits/`
- `.codestable/brainstorm/`
- `.codestable/compound/`
- `.codestable/tools/`
- `.codestable/reference/`
- `.codestable/tasks/`
- `.codestable/gates/`

说明：`tasks/` 虽不在最早的 onboard 简表里，但已在当前共享约定中明确为强制运行主线；`gates/` 已被最近两次刷新记录实际使用，属于当前版本运行时配置目录，不应按遗留目录处理。

补充说明：`.codestable/brainstorms/` 当前未被 `.codestable/reference/shared-conventions.md` 列为标准骨架目录，因此本次不再把它表述为“当前标准目录”。如果后续确认它仍是现行流程的一部分，应先更新共享约定，再把它升级为标准目录。

### 3.2 已确认并完成清理的历史遗留目录

#### `.codestable/architecture/`

- 原 `ARCHITECTURE.md` 已迁移到 `.codestable/compound/2026-07-05-codestable-architecture-overview.md`
- 旧文档中的有效信息已保留，待补齐部分已改为按当前正式流程维护
- 结论：该历史遗留结构已完成迁移并删除旧目录

后续建议：如需继续维护架构知识，优先通过 `requirements/adrs/` 或 `compound/` 落盘，不再恢复 `.codestable/architecture/` 目录。

#### `.codestable/config/`

- 原目录为空目录
- 结论：已按用户确认删除

后续建议：除非未来重新引入明确的运行时配置约定，否则不再恢复该目录。

## 4. 本次已执行的结构清理动作

本次已执行：

- 已将历史骨架文档迁移到 `.codestable/compound/2026-07-05-codestable-architecture-overview.md`
- 已删除旧文件 `.codestable/architecture/ARCHITECTURE.md`
- 已删除空目录 `.codestable/architecture/`
- 已删除空目录 `.codestable/config/`

原因：用户已明确确认“两个都做”，因此本次按确认执行清理。

## 5. 验证结果

已验证：

- `attention.md` 已包含新版“报告语言”段落
- `.codestable/compound/2026-07-05-codestable-architecture-overview.md` 已存在
- `.codestable/tasks/archived/2026-07-05-refresh-codestable-local-adaptation.md` 已存在
- `.codestable/tasks/active/` 无同名残留 Task
- `.codestable/gates/roadmap-goal-gates.yaml` 存在
- `.codestable/architecture/` 已不存在
- `.codestable/config/` 已不存在

结论：当前仓库 `.codestable/` 已完成本次本地适配与遗留结构清理，相关 Task 已归档；此前识别出的 `architecture/` 与 `config/` 两个遗留目录均已按确认完成迁移或删除，当前目录结构已与现行主线约定对齐。
