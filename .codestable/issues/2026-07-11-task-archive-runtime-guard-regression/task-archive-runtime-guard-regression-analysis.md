---
doc_type: issue-analysis
issue: 2026-07-11-task-archive-runtime-guard-regression
status: confirmed
root_cause_type: concurrency
related:
  - task-archive-runtime-guard-regression-report.md
  - ../2026-06-30-task-archive-stale-active-rewrite/task-archive-stale-active-rewrite-fix-note.md
tags:
  - cs-task
  - archive
  - runtime-guard
  - concurrency
---

# Task 归档后 active 文件重现回归根因分析

## 1. 问题定位

| 关键位置 | 说明 |
|---|---|
| `plugins/codestable/skills/cs-task/SKILL.md:187-205` | 归档逻辑仅以自然语言要求 Agent 执行 `mv`、停止写旧路径并最终复验，没有可执行状态迁移入口。 |
| `plugins/codestable/skills/cs-task/reference.md:173-196` | 参考协议重复相同约束，但无法拦截 IDE buffer 或延迟工具调用对旧路径的底层写入。 |
| `tests/test_workflow_contracts.py:58-91` | 测试只断言协议字符串存在，无法验证真实文件系统上的归档、延迟写回、残留清理和内容分叉。 |
| `plugins/codestable/skills/cs-onboard/tools/` | 已有可分发 Python runtime 工具目录，但不存在 Task 归档执行器或 active 写入守卫。 |
| `tools/check-plugin-package.py:196-220` | 打包检查只验证通用安装资产和 runtime mapping tool，没有验证 Task runtime 工具是否存在并被分发。 |

## 2. 失败路径还原

**正常路径**：Agent 完成 active Task → Shell `mv` 到 archived → 只更新 archived frontmatter 和正文 → 最终确认 archived 正本有效且 active 不存在 → recovery 只看到 archived 历史记录。

**失败路径**：Agent 在归档前对 active 文件发出编辑 → 编辑调用被标记 interrupted、延迟完成或仍存在旧 buffer → Shell `mv` 成功且即时检查确认 active 不存在 → 延迟写入继续使用旧 active 路径并重新创建文件 → active 与 archived 同时存在 → recovery 可能把已闭环任务重新识别为活动任务。

**分叉点**：`plugins/codestable/skills/cs-task/SKILL.md:192-200` — 归档状态迁移由多个独立工具调用拼接，协议无法为 `mv` 之后的旧路径建立代码级 tombstone，也无法把最终验证与清理封装成同一可执行操作。

## 3. 根因

**根因类型**：并发 / 竞态。

**根因描述**：2026-06-30 的历史修复只把“旧 active 路径失效”和“最终回复前复验”写入 Markdown 协议，并用字符串断言防止文字规则丢失。它没有提供可执行归档器，也没有行为测试模拟 `mv` 后旧内容写回。因此底层延迟编辑、旧 buffer 自动保存或后续错误路径引用仍能重新创建 active 文件。即时复验只能发现某一时刻的状态，不能阻止复验之后发生的 stale rewrite。

**是否有多个根因**：是。

1. **主根因**：缺少代码级 Task archive runtime，归档不是单一受控状态迁移。
2. **触发因子**：interrupted 调用未必取消底层执行，或者 IDE 仍持有旧 active buffer。
3. **防护缺口**：现有测试是 Markdown 字符串契约测试，不是文件系统行为测试；插件打包检查也不保证归档 runtime 被分发。

## 4. 影响面

- **影响范围**：所有通过 Agent 拼接 `mv`、编辑 archived 和最终检查完成归档的 CodeStable 项目；连续归档、多次编辑、工具调用 interrupted 或 IDE autosave 场景风险更高。
- **潜在受害模块**：`cs-task archive`、`recovery`、`history`、`backfill`，以及依赖 Task 状态决定后续 gate 的 issue、feature、refactor 和 code review 流程。
- **数据完整性风险**：有。active 与 archived 可能内容一致，也可能发生分叉；静默删除分叉文件会丢失后续修改，静默恢复 active 则会破坏已归档状态。
- **严重程度复核**：维持 P1。它不直接破坏业务数据库，但会破坏 CodeStable workflow spine 的 source-of-truth，并可能触发重复执行或错误恢复。

## 5. 修复方案

### 方案 A：新增专用 Task archive runtime

- **做什么**：在 `plugins/codestable/skills/cs-onboard/tools/` 新增可执行归档工具，统一完成状态校验、目标冲突检查、原子移动、archived 内容更新、稳定性窗口复验，以及 active 残留的同源清理或分叉阻塞；同时更新 `cs-task` 协议、安装骨架、打包检查和行为测试。
- **优点**：直接修复主根因；归档成为可测试的受控操作；改动集中，能沿用现有 runtime 工具分发模式。
- **缺点 / 风险**：无法从操作系统层阻止外部进程在工具退出后永久写回；需要明确稳定性窗口和冲突比较策略。
- **影响面**：新增 runtime 工具、`cs-task` 两份协议、onboard 工具说明、打包检查和测试。

### 方案 B：建立完整 Task 文件 runtime 与全局写入守卫

- **做什么**：把 create、update、complete、archive、recovery 和 backfill 全部收敛到统一 Python runtime；任何写 active 路径前都检查 archived tombstone，已归档 slug 一律拒绝重建。
- **优点**：防护最完整，能够从 CodeStable 自身入口统一阻止 stale active 写入。
- **缺点 / 风险**：范围大，涉及所有 Task 生命周期操作；仍无法拦截 IDE 或通用文件编辑工具绕过 runtime 的直接写入；本次 P1 修复容易扩张成 Task System 重构。
- **影响面**：`cs-task` 全生命周期协议、多个 workflow skill、onboard 工具、安装与迁移机制、大量测试。

### 方案 C：只新增归档后 verifier/cleanup

- **做什么**：保留 Shell `mv`，新增小型验证工具，在稳定性窗口内检查 active 是否重现；同源残留自动删除，分叉残留阻塞。
- **优点**：改动最小，能把当前“最终检查”从文字要求变成行为测试覆盖的代码。
- **缺点 / 风险**：归档仍由多个独立工具调用拼接，不能统一校验状态和目标冲突，也不能减少错误路径引用；属于补救而非根治。
- **影响面**：新增 verifier、少量协议和测试修改。

### 推荐方案

**推荐方案 A**。它把历史修复明确留下的“未来新增 runtime tool”缺口落实为代码，同时把范围限制在 archive 状态迁移，不扩张到整个 Task System。实现中吸收方案 B 的关键守卫：归档工具检测已归档正本和 active 分叉；但不在本次强制重写 create/update 等所有路径。

### 用户确认

用户选择 **方案 B：建立完整 Task 文件 runtime 与全局写入守卫**。本次实现按该方案推进，统一 Task 生命周期的受控入口，并保留对外部工具绕过 runtime 直接写入的检测与清理能力。
