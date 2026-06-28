# CodeStable 架构骨架迁移说明

## 背景

本文由历史遗留文件 `.codestable/architecture/ARCHITECTURE.md` 迁移而来。

原目录 `architecture/` 不属于当前 CodeStable 标准骨架，因此本次将其内容迁移到 `compound/` 统一沉淀，并删除旧遗留目录。本文保留原骨架中的有效信息，同时明确哪些部分仍待通过当前正式流程补齐。

## 现有内容

### 项目简介

CodeStable 是一组面向软件开发生命周期的 Cursor Agent Skills。它把新功能、问题修复、重构、架构文档、知识沉淀和任务恢复等活动拆成可复用的技能流程，并把长期产物统一放入 `.codestable/`。

### 核心概念 / 术语表

- **Skill**：一个独立的 Agent 工作流入口，通常由 `SKILL.md` 和可选 `reference.md` 组成。
- **CodeStable 产物**：由各技能维护的需求、架构、roadmap、feature、issue、compound 等文档。
- **共享口径**：放在 `.codestable/reference/shared-conventions.md` 的跨技能规范。

### 子系统 / 模块索引

当前迁移自旧骨架，原文为待补齐状态。

如果后续需要正式维护 CodeStable 的模块边界、职责分层、流程拓扑或技能编排关系，建议通过当前主线流程重新产出，而不是恢复旧 `architecture/` 目录。

### 关键架构决定

当前迁移自旧骨架，原文为待补齐状态。

后续若形成稳定决策，建议优先落到：

- `.codestable/requirements/adrs/`：适合明确、可编号的架构决策
- `.codestable/compound/`：适合阶段性总结、迁移说明、流程收尾记录

### 已知约束 / 硬边界

- 单个 Markdown 文档不得超过 300 行，超过必须拆分。

## 迁移结论

- 历史遗留文件 `.codestable/architecture/ARCHITECTURE.md` 已迁移到当前标准目录
- 旧 `architecture/` 目录可以安全删除
- 后续不再建议重新引入 `.codestable/architecture/` 作为长期主线目录
