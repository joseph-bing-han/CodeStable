---
doc_type: feature-design-review
feature: 2026-06-30-remove-worktree-flow
status: passed
reviewed: 2026-06-30
round: 2
---

# remove-worktree-flow feature design 审查报告

## 1. Scope And Inputs

- Design: `.codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-design.md`
- Checklist: `.codestable/features/2026-06-30-remove-worktree-flow/remove-worktree-flow-checklist.yaml`
- Intent / brainstorm: none
- Roadmap: none
- Related docs: `.codestable/attention.md`
- Code facts checked: worktree keyword inventory across tools, tests, skills, README/reference docs, and `.codestable` published copies

### Independent Review

- Status: completed
- Detection: local-review with readonly subagent assistance
- Provider / agent: readonly codebase exploration subagent
- Raw output: reported `changes-requested` for incomplete inventory and weak residual-scan coverage
- Merge policy: findings were fact-checked against current repository references, then merged into design revisions
- Gate effect: original blocking findings resolved by revising design and checklist; final local review passed

## 2. Design Summary

- Goal: remove all worktree-specific tools, calls, hooks, tests, and workflow documentation from CodeStable.
- Key contracts: delete worktree-only assets; decouple shared tools; preserve review evidence, Task spine, YAML validation, and review-packet abilities.
- Steps: 6 steps, now split across inventory, asset deletion, shared-tool decoupling, tests, documentation, and residual verification.
- Checks: expanded to cover `.codestable` published copies, root docs, semantic residual scans, and non-worktree quality gates.
- Baseline / validation: YAML validation, full pytest run, script-name residual scan, semantic residual scan, and published-copy scan.

## 3. Findings

### blocking

none

### important

none

### nit

none

### suggestion

- FDR-001 During implementation, keep a short inventory note in the step evidence so code review can distinguish expected feature-process residuals from accidental product residuals.

### learning

- Capability removal that spans skills, tools, docs, tests, and published `.codestable` copies needs two residual scans: script-name scans catch direct references, while semantic scans catch old workflow guidance after filenames are gone.

### praise

- The revised design keeps non-worktree quality gates explicit, reducing the risk of deleting review/task discipline together with the worktree mechanism.

## 4. User Review Focus

- 用户需要重点拍板：是否接受“不实现新的 branch guard hook 替代品”。
- implement 需要重点遵守：同步清理源码侧与 `.codestable` 发布副本；残留只允许存在于本 feature 流程产物中。
- code review / QA / acceptance 需要重点复核：root docs、workflow/catalog、reference 与 contract tests 是否已同步去除旧语义。

## 5. Residual Risk

- `rg` 语义扫描可能命中历史 feature 文档或本次流程产物；实现阶段必须分类说明每个保留残留的理由。
- 如果 `.codestable` 发布副本与技能包源码存在历史漂移，实现阶段需要以“最终无旧流程残留”为准，而不是假设两侧文件一一对应。

## 6. Verdict

- Status: passed
- Next: 交给用户整体 review；用户批准后进入 `cs-feat-impl` 实现。
