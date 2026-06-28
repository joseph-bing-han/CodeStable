---
doc_type: issue-fix
issue: 2026-06-29-stage-handoff-auto-continue-regression
path: standard
fix_date: 2026-06-29
related:
  - stage-handoff-auto-continue-regression-analysis.md
tags: [workflow, handoff, checkpoint, direct-entry]
---

# 阶段 Handoff 自动续跑回归修复记录

## 1. 实际采用方案

采用分析阶段推荐的方案 B：共享协议动作级加固，并同步关键入口与阶段出口。

核心修复点：

1. 在项目运行时 `.codestable/reference/shared-conventions.md` 与模板 `cs-onboard/reference/shared-conventions.md` 中补上禁止出口：不能停在“下一步建议 / 推荐使用某个 skill / 请运行某个 skill”。
2. 在 system overview 运行时副本与模板中补上动作级要求：目标 skill 已确定且没有开放问题时，当前 agent 必须继续读取并执行目标 skill。
3. 在 `cs`、`cs-issue`、`cs-issue-report`、`cs-issue-analyze`、`cs-brainstorm` 中补强 direct entry、L2 checkpoint 和 handoff 出口。
4. 同步 `cs-feat`、`cs-refactor`、`cs-roadmap`、`cs-audit` 的入口 / 交接措辞，避免其它完整入口继续漂移。

## 2. 改动文件清单

- `.codestable/reference/shared-conventions.md`
- `.codestable/reference/system-overview.md`
- `cs-onboard/reference/shared-conventions.md`
- `cs-onboard/reference/system-overview.md`
- `cs/SKILL.md`
- `cs-issue/SKILL.md`
- `cs-issue-report/SKILL.md`
- `cs-issue-analyze/SKILL.md`
- `cs-brainstorm/SKILL.md`
- `cs-feat/SKILL.md`
- `cs-refactor/SKILL.md`
- `cs-roadmap/SKILL.md`
- `cs-audit/SKILL.md`

## 3. 验证结果

- 行数验证：本次修改的 tracked Markdown 文件均不超过 300 行；`.codestable` 新增 report / analysis / fix-note / review / task 文件也不超过 300 行。
- 口径验证：`rg` 已命中关键短语，包括“不能停在”“当前 agent 必须”“结构化 L2 checkpoint”“不能回复建议使用”。
- 测试验证：`uvx pytest -q` 通过，结果为 `52 passed in 14.14s`。
- 依赖状态：系统 `python3 -m pytest -q` 因未安装 pytest 失败，已用 `uvx pytest -q` 做等价测试运行。

## 4. 遗留事项

- 已同步当前机器安装运行目录 `/Users/joseph/.agents/skills/cs`，本机后续调用会直接读到本次修复。
- `.codestable/` 被 `.gitignore` 忽略，issue / task 运行记录是本项目本地 CodeStable 状态，不会进入普通 git diff。
