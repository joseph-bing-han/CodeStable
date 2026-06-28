---
doc_type: issue-fix
issue: 2026-06-30-task-archive-stale-active-rewrite
status: completed
fixed: 2026-06-30
tags:
  - cs-task
  - archive
  - workflow-spine
---

# task-archive-stale-active-rewrite Fix Note

## 1. 根因

`cs-task archive` 已经要求用 `mv` 移动 active 原文件，但协议仍没有显式约束移动后的旧 active 路径写入上下文。实际执行中，active 源文件被移动后仍可能被旧 editor buffer、旧工具上下文或后续误用的 active 路径重新写回；如果最终只信一次 shell `test ! -e active && test -e archived` 的历史结果，就会误报归档成功。

## 2. 修复内容

- `cs-task/SKILL.md`：归档动作新增“active 源路径视为失效路径”，禁止对移动后的 active 路径继续 ApplyPatch / Edit / Write / 保存旧 buffer。
- `cs-task/SKILL.md`：归档动作新增最终回复前的当前文件系统验证，要求确认 archived 目标存在且 `status: archived`，同时 active 源路径不可读 / 不存在。
- `cs-task/reference.md`：同步上述归档规则，作为项目共享参考协议。
- `tests/test_workflow_contracts.py`：新增契约断言，覆盖 stale active rewrite、最终回复前验证、不能只依赖历史 shell test exit code。
- `/Users/joseph/.agents/skills/cs/cs-task/`：同步已安装 skill 副本，确保后续会话加载到新规则。

## 3. 验证

- `uvx pytest -q`：通过，21 tests passed。
- 文件级验证：source 与 installed skill 均包含相同 archive 规则，包括 active 源路径失效、禁止旧 buffer 写回、最终回复前当前文件系统验证、不能只依赖历史 shell test exit code。

## 4. 影响范围

- 只修改 CodeStable `cs-task` 归档协议与 workflow contract test。
- 不引入可执行归档器实现；后续若新增 runtime tool，应把本协议落实为代码级原子 move + final filesystem verification。

## 5. 后续 gate

修复记录落盘后进入 `cs-code-review`。review passed 后再将 Task 标记 completed 并执行 `cs-task archive`。
