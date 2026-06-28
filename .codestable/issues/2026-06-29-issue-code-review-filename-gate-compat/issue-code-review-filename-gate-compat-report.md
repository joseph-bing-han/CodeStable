---
doc_type: issue-report
issue: 2026-06-29-issue-code-review-filename-gate-compat
status: confirmed
severity: P1
tags: [codestable, worktree-gate, code-review]
---

# issue code review 文件名导致 gate 误判问题报告

## 1. 问题现象

在 XebnIoT 已完成 issue 修复并落盘 `{slug}-code-review.md` 后，执行 commit gate 仍提示缺少 `{slug}-review.md`。

## 2. 复现线索

1. issue 目录存在 `{slug}-fix-note.md`
2. issue 目录存在 `{slug}-code-review.md`
3. 执行 `codestable-worktree-gate.py commit --unit .codestable/issues/YYYY-MM-DD-{slug}`
4. gate 报缺少 `{slug}-review.md`

## 3. 期望行为

issue 工作流应识别 `cs-issue` 约定的 `{slug}-code-review.md`，不能把已存在的 review 误判为缺失。

## 4. 实际影响

已完成 review 的 issue 可能在 commit / finish gate 阶段被误阻塞，导致 task 收口和运行时副本验证产生假失败。

## 5. 初始范围

修复 CodeStable gate 工具对 issue review 文件名的兼容逻辑，并同步相关测试。
