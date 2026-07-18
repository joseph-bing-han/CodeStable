---
doc_type: issue-review
issue: 2026-06-29-issue-code-review-filename-gate-compat
status: passed
reviewer: subagent
reviewed: 2026-07-18
round: 2
review_basis: independent-readonly-historical-remediation
---

# issue-code-review-filename-gate-compat 独立审查（Round 2）

## Verdict

**passed**

## Findings

### blocking
无。

### important
无。

### nit
兼容命中失败时统一报缺 canonical review；可区分 legacy schema 不合格（非本轮阻塞）。

## 核验摘要

- `legacy_issue_review_file_for` 仅对 issues 返回 `{slug}-code-review.md`。
- `review_has_subagent_evidence(..., allow_legacy_issue_filename=True)` 仍要求 `status=passed`、`reviewer in {subagent,subagent+ocr}`、`doc_type=issue-review`、identity 等于 unit directory。
- pre-cutoff archived Task 存在时才允许 legacy 路径；active residue / post-cutoff 拒绝。
- 回归：`tests/test_local_override_workflow.py` 正向 + schema/identity 负向覆盖。

## Residual Risk

- 历史 self-review 的 legacy 文件保留为历史产物，不作为本结论依据。
