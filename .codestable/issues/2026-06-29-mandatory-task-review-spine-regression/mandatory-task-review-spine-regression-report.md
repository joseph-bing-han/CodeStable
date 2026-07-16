---
doc_type: issue-report
issue: 2026-06-29-mandatory-task-review-spine-regression
status: confirmed
severity: P1
summary: 完整入口流程仍可能缺失 cs-task 与 cs-code-review 强制主线
tags: [workflow, task, code-review, handoff]
---

# 完整入口缺失 Task 与 Code Review 主线 Issue Report

## 1. 问题现象

Cursor 对话记录显示，用户通过 `/cs-issue` 处理 MQTT 离线消息补发失败时，流程没有自动完整推进：report 没有先落盘并创建 Task，analyze / fix 需要用户手动触发，fix 阶段完成后只提示下一步应进入 `cs-code-review`，没有自动执行最终质量门禁；用户随后还要手动调用 `/cs-task` 补建缺失任务。

## 2. 复现步骤

1. 用户针对日志问题直接输入 `/cs-issue 先解决异常 A`。
2. Agent 在 chat 中整理 issue 信息和初步根因，但没有先创建 Task List，也没有自动落盘 report 后进入 analyze。
3. 用户手动输入 `/cs-issue-analyze`、`/cs-issue-fix 方案A` 后，Agent 完成代码修复和 fix-note。
4. Agent 只提示“下一步应进入 `cs-code-review`”，没有自动执行 review；用户再输入 `/cs-task 缺少对应的task` 才补建 Task。

复现频率：对话记录中稳定出现一次完整链路断裂。

## 3. 期望 vs 实际

**期望行为**：任何完整入口进入代码型 workflow 后，首次落盘前必须自动创建 / 恢复 Task；每阶段结束必须更新 Task 的 `owner_skill` 与文档索引；fix / impl 完成后必须自动进入 `cs-code-review`；review 通过后才能 complete 并立即归档 Task。

**实际行为**：入口和阶段技能虽然有“自动进入”与“Task 接入”描述，但缺少不可绕过的动作级 spine gate，导致 Agent 能在 chat 中完成分析或修复，却跳过 Task 创建、Task 更新、code review 和归档。

## 4. 环境信息

- 涉及模块 / 功能：CodeStable skill workflow contract。
- 相关文件 / 函数：`cs-issue-report/SKILL.md`、`cs-issue-analyze/SKILL.md`、`cs-issue-fix/SKILL.md`、`cs-task/SKILL.md`、`cs-code-review/SKILL.md`、`cs-feat-impl/SKILL.md`、`cs-feat-accept/SKILL.md`、`cs-feat-ff/SKILL.md`、`cs-refactor/SKILL.md`、`cs-refactor-ff/SKILL.md`、`.codestable/reference/shared-conventions.md`、`cs-onboard/reference/shared-conventions.md`
- 运行环境：CodeStable Markdown skill runtime。
- 其他上下文：证据文件为 `/Users/joseph/Downloads/cursor_mqtt_log_warning_analysis.md`。

## 5. 严重程度

**P1** — 这会破坏 CodeStable 的核心承诺：入口不同或阶段推进方式不同，都不应导致 Task、Code Review 和归档缺失。

## 备注

本问题不是单纯“没有自动进入下一个 skill”，而是完整工程主线缺少硬门禁：Task、code review、archive 都必须成为不可跳过的 workflow spine。
