---
doc_type: feature-acceptance
feature: 2026-05-30-task-core-storage-runtime
status: accepted
summary: 验收 cs-task 核心技能和 task list 存储恢复协议
tags: [task, workflow, recovery]
accepted_at: 2026-05-30
---

# task-core-storage-runtime 验收报告

> 阶段：阶段 3（验收闭环）
> 验收日期：2026-05-30
> 关联方案 doc：`.codestable/features/2026-05-30-task-core-storage-runtime/task-core-storage-runtime-design.md`

## 1. 接口契约核对

**名词层“现状 → 变化”逐项核对**：

- [x] 新增 `cs-task/SKILL.md`：已定义 recovery / create / update / complete / archive / history 模式，并覆盖 active、completed、cancelled、archived task 的发现和处理流程。
- [x] 新增 `cs-task/reference.md`：已定义目录结构、frontmatter schema、正文模板、状态机、用户询问协议、Agent Native Tasks 同步和归档规则。
- [x] 更新 `cs/SKILL.md`：体系图已包含 `tasks/`；路由表已将“当前任务 / 继续任务 / 任务列表 / 历史任务 / 归档任务”指向 `cs-task`。
- [x] 更新 `cs-onboard/reference/shared-conventions.md`：onboard 骨架和命名规则已包含 `.codestable/tasks/active` 与 `.codestable/tasks/archived`。

**流程图核对**：

- [x] `cs-task/SKILL.md` 的 recovery、complete、archive 节覆盖设计图里的扫描 active、任务数量分支、编号选择、同步运行时任务视图、完成和归档节点。

## 2. 行为与决策核对

**需求摘要逐项验证**：

- [x] 新增 task 存储入口：`cs-task/reference.md` 定义 `.codestable/tasks/active/{task}.md` 和 `.codestable/tasks/archived/YYYY-MM-DD-{task}.md`。
- [x] 新增恢复入口：`cs-task/SKILL.md` 明确 `cs task` / 继续任务 / 当前任务进入 recovery。
- [x] 根入口识别 task 实体：`cs/SKILL.md` 已加入 `tasks/` 体系图和 `cs-task` 路由。
- [x] 共享约定识别 task 实体：`shared-conventions.md` 已加入 tasks 目录树、命名规则和共享边界。

**明确不做逐项核对**：

- [x] 未接入所有现有 skill 的 auto / ask 分级；本次只定义核心 runtime，后续由 `task-integration-policy` 处理。
- [x] 未实现各 Agent 私有 SDK；只定义通用同步和降级规则。
- [x] 未替代 feature checklist 或 roadmap items；`cs-task` 与 shared conventions 均明确 Task List 不替代它们。
- [x] 未做跨项目 task 中心；路径限定在当前项目 `.codestable/tasks/`。

**关键决策落地**：

- [x] Markdown + frontmatter：`cs-task/reference.md` 给出 frontmatter schema 和固定正文模板。
- [x] active / archived 分目录：`cs-task/reference.md` 和 shared conventions 均已固化。
- [x] 防递归：`cs-task/SKILL.md` 启动必读明确只更新 task 文件本身时不递归创建 Task List。

**挂载点反向核对**：

- [x] skill 注册：`cs-task/SKILL.md` 和 `cs-task/reference.md` 已存在。
- [x] 根入口路由：`cs/SKILL.md` 已加入 task 相关诉求路由。
- [x] 共享目录约定：`shared-conventions.md` 已加入 tasks 目录和边界。
- [x] 反向核查：本次新增 task 入口只落在上述三类挂载点，未额外扩散到其他 skill。

## 3. 验收场景核对

- [x] 触发 `cs task` 类诉求 → `cs/SKILL.md` 明确路由到 `cs-task`。
- [x] 读取 `cs-task/SKILL.md` → 能知道 active / completed / archived task 的发现和处理流程。
- [x] 读取 `cs-task/reference.md` → 能知道 Task List schema、正文结构、状态机、归档命名和 user_question_answer 规则。
- [x] 检查 shared conventions → `.codestable/tasks/active` 与 `.codestable/tasks/archived` 是正式目录。
- [x] 反向核对：本 feature 没有接入所有 skill 的 auto / ask 分级。

## 4. 术语一致性

- [x] Task List：`cs-task/SKILL.md` 和 `cs-task/reference.md` 使用一致。
- [x] Active Task / Archived Task：目录语义与状态机一致。
- [x] cs-task Runtime：作为 internal runtime 的定位一致。
- [x] Agent Native Tasks：始终被描述为运行时镜像，不是 source of truth。

## 5. 架构归并

- [x] 本 feature 改动的是 CodeStable 技能包协议和 shared conventions，当前仓库没有正式 architecture doc；按 design 第 4 节，本次不做 architecture 归并。
- [x] 稳定的系统级约定已写入 `cs-onboard/reference/shared-conventions.md`，作为后续项目 onboard 模板来源。

## 6. requirement 回写

- [x] design frontmatter `requirement: null`，且本 feature 是 CodeStable 技能包协议能力的 roadmap 子项；当前不回写 requirement。

## 7. roadmap 回写

- [x] design frontmatter 包含 `roadmap: codestable-task-system` 和 `roadmap_item: task-core-storage-runtime`。
- [x] `.codestable/roadmap/codestable-task-system/codestable-task-system-items.yaml` 已将该条目从 `in-progress` 回写为 `done`，并保留 `feature: 2026-05-30-task-core-storage-runtime`。
- [x] roadmap 主文档第 5 节中该条目状态同步为 `done`，对应 feature 指向 `2026-05-30-task-core-storage-runtime`。

## 8. attention.md 候选盘点

- [x] 候选：当前仓库用于 bootstrap Task System 时允许缺少 `.codestable/attention.md` 继续读取 `.codestable/tasks/` 和 roadmap 上下文。此规则已写入 `cs-task/SKILL.md`，无需另写 attention。

## 9. 遗留

- 后续子 feature：`task-integration-policy` 负责所有 CS skill 的 auto / ask / route-only / internal 分级。
- 后续子 feature：`task-agent-sync-protocol` 负责更细的 Agent Native Tasks 同步协议。
- 后续一致性：`task-onboard-docs-consistency` 需要处理 README 与 brainstorm/brainstorms 路径漂移。
