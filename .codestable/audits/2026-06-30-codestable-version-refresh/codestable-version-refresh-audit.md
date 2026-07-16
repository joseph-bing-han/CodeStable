# CodeStable 版本刷新审计

## 1. 任务背景

本次工作用于把当前仓库的 `.codestable/` 目录刷新到最新 `cs-onboard` 骨架，并适配当前项目已经存在的本地扩展内容。

## 2. 扫描结论

当前仓库在刷新前已存在以下结构：

- 已存在：`attention.md`、`requirements/`、`roadmap/`、`features/`、`issues/`、`compound/`、`tasks/`、`tools/`、`reference/`
- 非标准但已有内容：`architecture/`、`config/`
- 缺失标准骨架：`goals/`、`refactors/`、`audits/`、`brainstorms/`、`brainstorm/`

判断结果：本仓库属于 `cs-onboard` 的迁移路径，不是空仓库初始化路径。

## 3. 已执行刷新动作

### 3.1 共享目录刷新

已用当前技能包版本覆盖刷新：

- `.codestable/tools/`
- `.codestable/reference/`

刷新来源：

- `/Users/joseph/.agents/skills/cs/cs-onboard/tools/`
- `/Users/joseph/.agents/skills/cs/cs-onboard/reference/`

### 3.2 骨架补齐

已补齐以下标准聚合根：

- `.codestable/goals/`
- `.codestable/refactors/`
- `.codestable/audits/`
- `.codestable/brainstorms/`
- `.codestable/brainstorm/`

其中空目录已补 `.gitkeep`，审计目录已用于落盘本报告。

## 4. 保留原位的现有内容

以下内容不属于最新标准骨架的最小集合，但当前项目仍有明确用途，因此本次保留原位，不做迁移或删除：

| 路径 | 处理结果 | 原因 |
|---|---|---|
| `.codestable/architecture/ARCHITECTURE.md` | 保留原位 | 当前项目已有架构入口内容，属于历史资产，未与新版骨架冲突 |
| `.codestable/config/code-review-subagent.yaml` | 保留原位 | 被 `cs-code-review` 与测试契约直接引用，属于当前有效配置 |
| `.codestable/reference/branch-guard-hooks.md` | 保留原位 | 该文件不在当前技能包 reference 清单中，但现有项目副本仍可作为本地扩展参考，不影响新版 reference 覆盖刷新 |

## 5. 兼容性结论

本次刷新后，项目已满足当前 `cs-onboard` 的核心要求：

- `.codestable/` 标准聚合根已齐全
- `.codestable/attention.md` 已存在
- `.codestable/tools/` 已刷新到当前技能包版本
- `.codestable/reference/` 已刷新到当前技能包版本
- 当前项目依赖的历史扩展内容未被误删

另外确认：当前技能包不存在 `.codestable/hooks/` 目录，因此本次无需同步 hooks。

## 6. 未执行的迁移动作

本次没有移动、重命名或删除任何已有业务性文档，原因如下：

- 当前目标是版本刷新与骨架适配，不是重构历史文档信息架构
- 现有非标准路径均未形成阻塞
- 对历史资产做归位迁移会引入额外判断成本，不适合在无明确指令下自动执行

## 7. 最终状态

当前仓库的 `.codestable/` 已完成版本刷新，可按当前 CodeStable 工作流继续使用。
