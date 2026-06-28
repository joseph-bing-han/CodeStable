---
doc_type: reference
status: current
topic: local-override-workflow
updated: 2026-07-17
---

# CodeStable 本地 Override 工作流契约

本文件是 CodeStable 本地适配的 canonical 约束。上游同步、插件升级、runtime 同步和 skill 重构都不得静默移除或弱化这里定义的能力。

## 1. Override 目标

本地 Override 以当前上游 CodeStable 为主体，只补充本机工作流和工具集需要的稳定增量。长期维护模型是：

```text
upstream CodeStable
  + local Task spine
  + local independent review gate
  + local automatic orchestration constraints
```

本地增量必须保持可识别、可验证、可重放；不得通过复制旧版完整 skill 树回退上游架构。

## 2. 不可变约束

1. CodeStable 不创建、不要求、不默认使用隔离检出目录。branch 与隔离工作区策略由宿主、owner 或独立 skill 决定。
2. CodeStable 核心 workflow 不依赖 OCR、桌面应用或其它第三方 APP。review 只依赖宿主提供的独立 Task agent；没有该能力时必须 fail closed，不得静默降级。
3. `cs-code-review` 是统一的 design/code review 横切 gate。它只读审查并落盘 review 报告，不直接实现修复。
4. `cs-task` 是所有写入型 workflow 的强制运行账本。Task 文件是 source of truth，Agent 原生 Todo/Tasks 只是运行时镜像。
5. `cs`、`cs-feat`、`cs-issue`、`cs-refactor`、`cs-epic` 等用户可直达入口都是完整入口。下一阶段确定时必须在当前 run 自动继续，不要求用户再次输入 `/cs-*` 命令。
6. Task gate 与 review gate 不可选、不可缺失。流程开始首次落盘前必须创建或恢复 Task；实现批次完成后必须进入 `cs-code-review`；通过后才能完成并归档 Task。
7. Review 以一个可验收的实现批次为粒度。先完成当前 design/checklist/fix 范围，再统一 review；不得修一个 finding、其余实现尚未完成时就频繁重启 review。
8. 上游同步和安装升级必须执行 local override 回归检查。缺少 `cs-task`、Task runtime、独立 review gate或自动编排契约时，更新不得报告成功。

## 3. 标准 Workflow Spine

所有会修改项目文档或代码的 workflow 统一遵守：

```text
入口 skill
  -> preflight 与仓库事实恢复
  -> 分析
  -> 设计方案
  -> 方案文档落地
  -> 创建或恢复 Task
  -> 实施当前批次
  -> 更新 Task 进度
  -> 继续实施和更新 Task
  -> 完成整个实施批次
  -> cs-code-review 首轮独立审查
  -> 集中修复本轮全部 blocking / important findings
  -> focused closure 或完整独立复审
  -> 重复直到 review passed
  -> 需要时执行 QA / acceptance
  -> Task 标记 completed
  -> 原子归档 Task
  -> 确认 active 同名文件不存在
```

`completed` 不是最终状态；只有 archived 正本有效、active 无同名残留时，workflow 才真正闭环。

## 4. Task Gate

- 写入型 workflow 在首次修改项目文件前必须存在 active Task。
- Task frontmatter 必须记录 `workflow`、`owner_skill`、`related_docs` 和当前状态。
- 每个可观察实施批次结束后，先更新 Task 文件，再同步 Agent Tasks。
- review、QA、acceptance 等证据缺失时，Task 不得进入 `completed`。
- archive 必须通过 `<cs-onboard skill>/tools/codestable-task-runtime.py`；不得把 `.codestable/tools/` 作为新版入口。
- archive 必须使用 tombstone 防止旧 buffer 或并发写入重新生成 active 文件。

## 5. Review Gate 与批次策略

- 首次 review 和实质修改后的完整复审必须使用独立 Task agent。
- reviewer 不可用、失败或配置不匹配时写 `blocked` 并停止；不得改用 OCR、self review 或第三方 APP。
- 同一实现批次中的 findings 先统一收集，再由实现 workflow 集中修复。
- 仅测试、文档、类型、metadata 或窄小无行为变化的 closure diff 可复用首次独立 reviewer，执行 focused closure。
- 生产行为、公开契约、安全、数据、并发、架构变化或无法确定的变化必须完整独立复审。
- Review 报告的 `reviewer` canonical 值是 `subagent`；历史 `subagent+ocr` 可读但不得由新流程产生。

## 6. 自动编排边界

- 机械 handoff、Task create/update、确定性的下一阶段和 review/归档门禁属于自动继续。
- 只有真实路线歧义、设计/需求确认、高风险操作、外部授权和不可恢复冲突才允许 HumanCheckpoint。
- 自动继续不授权跳过目标 skill 的协议，也不授权执行 commit、push、生产修改或关键数据变更。
- 最终回答前必须确认 `workflow-next` 不再要求继续，并且 Task 已按本流程要求归档。

## 7. 上游同步保护清单

每次 upstream rebase、插件升级或技能刷新后至少验证：

- `plugins/codestable/skills/cs-task/` 存在且可发现；
- `codestable-task-runtime.py` 属于 `cs-onboard/tools/` capability；
- `codestable_common.KNOWN_SKILL_DIRS` 包含 `cs-task`；
- `cs-code-review` 及其 references 不含 OCR 执行 lane；
- `codestable-doctor.py` 不检测 OCR；
- review gate 只接受独立 Task agent 证据；
- 写入型入口包含 Task spine，并能在当前 run 自动推进；
- runtime sync manifest 与 health 输出一致；
- 相关 pytest、`git diff --check` 和 runtime sync check 通过。

## 8. 历史兼容边界

- `.codestable/tools/`、旧隔离检出/branch 工具和旧安装缓存只用于恢复历史事实，不是新版运行入口。
- 历史 review 报告中的 `subagent+ocr` 可以作为旧证据读取；新报告不得继续写该值。
- 不恢复旧版入口 skill 的手工阶段跳转；当前 `continuing-current-run` 和 `workflow-next` 是自动编排主体。
