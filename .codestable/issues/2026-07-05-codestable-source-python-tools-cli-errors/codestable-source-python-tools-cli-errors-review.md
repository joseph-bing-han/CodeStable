---
doc_type: issue-review
issue: 2026-07-05-codestable-source-python-tools-cli-errors
status: passed
reviewer: subagent
reviewed: 2026-07-18
round: 2
review_basis: independent-readonly-historical-remediation
---

# codestable-source-python-tools-cli-errors 独立审查（Round 2）

## Verdict

**passed**

## Findings

### blocking
无。

### important
无。

### nit
历史 fix-note 仍提及 `codestable-main-publish.py`；该工具已按 local-override design 正式退役，不恢复到 plugin source。

## 核验摘要

- canonical `validate-yaml.py` 提供 `--root`；相对 `--file`/`--dir` 相对 repository root；非仓库 cwd 无 root 时退出 2。
- `codestable-main-publish.py` 不在 plugin package；legacy `.codestable/tools/` 保留兼容、非新版入口。
- package checker / tests 覆盖相关边界。

## Residual Risk

- legacy `.codestable/tools/validate-yaml.py` 与 canonical 漂移；新版只调用 skill 目录 tools。
