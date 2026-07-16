---
doc_type: issue-fix
issue: 2026-06-21-entry-subskills-full-workflow-spine
path: standard
fix_date: 2026-06-21
related:
  - entry-subskills-full-workflow-spine-analysis.md
tags: [workflow, entry-skill, orchestration]
---

# 子入口缺少完整工作流闭环修复记录

## 1. 实际采用方案

采用分析阶段推荐的方案 B：

1. 在 shared conventions 中补上“所有用户可直达入口都是完整入口”的统一守卫。
2. 在 system overview 中补上“入口等价原则”，让项目运行时副本和 onboard 模板都明确 direct-entry 不会降级成局部入口。
3. 同步当前仓库里的技能源码与模板：`cs/`、`cs-feat/`、`cs-issue/`、`cs-brainstorm/`、`cs-refactor/`、`cs-roadmap/`、`cs-audit/`、`cs-onboard/reference/`、`README*`。
4. 外部 `/Users/joseph/.agents/skills/cs` 运行目录不保留本地改动，由用户后续自行 `git pull` 同步。

## 2. 改动文件清单

- `.codestable/reference/shared-conventions.md`
- `.codestable/reference/system-overview.md`
- `cs/SKILL.md`
- `cs-feat/SKILL.md`
- `cs-issue/SKILL.md`
- `cs-brainstorm/SKILL.md`
- `cs-refactor/SKILL.md`
- `cs-roadmap/SKILL.md`
- `cs-audit/SKILL.md`
- `cs-onboard/reference/shared-conventions.md`
- `cs-onboard/reference/system-overview.md`
- `README.md`
- `README.en.md`
- `.codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-report.md`
- `.codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-analysis.md`
- `.codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-fix-note.md`
- `.codestable/issues/2026-06-21-entry-subskills-full-workflow-spine/entry-subskills-full-workflow-spine-code-review.md`
- `.codestable/tasks/archived/2026-06-21-entry-subskills-full-workflow-spine.md`

## 3. 验证结果

- 行数验证：所有本次修改的 Markdown 文件都复查到不超过 300 行；当前项目的 `shared-conventions.md` 保持在 300 行上限以内。
- 口径验证：`rg` 已命中当前项目的 shared conventions、system overview 和本次 issue 产物中的“完整入口 / 入口等价 / 同一条主线”语义，说明当前仓库运行时副本已同步。
- 源码验证：`git status --short` 已命中当前仓库内 11 个可发布源码文件，说明本次修复已真正落到能推送 GitHub 的项目文件，而不是只停在本地运行目录。
- 外部目录验证：`git -C /Users/joseph/.agents/skills/cs status --short` 已恢复为空，本次未保留任何外部技能源码改动。

## 4. 遗留事项

- 本次修复已经覆盖当前项目源码与运行时副本；`/Users/joseph/.agents/skills/cs` 下的运行目录需要用户后续自行 `git pull` 同步。
- doc-only 入口本身已经有各自的 Task / archive 收口规则，因此本次没有扩改其它文档型入口。
