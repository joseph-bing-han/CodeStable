---
doc_type: issue-review
issue: 2026-07-14-standalone-runtime-version-unknown
status: passed
reviewer: subagent
reviewed: 2026-07-18
round: 3
review_basis: independent-readonly-historical-remediation
---

# standalone-runtime-version-unknown 独立审查（Round 3）

## Verdict

**passed**

## Findings

### blocking
无。

### important
无。

### nit
无。

## 核验摘要

- `discover_plugin_version()` 仅接受严格 SemVer；非法/空 VERSION 与 manifest version 返回 `None`。
- 最近 standalone `VERSION` 存在但非法时立即 fail closed，不向祖先回退。
- `sync_runtime()` 在 `version-unavailable` 时不改 manifest / 不复制 assets。
- 回归：`tests/test_codestable_doctor.py` 覆盖 unknown/invalid/合法 prerelease+build。
- identity 字段修正为完整 unit directory 名。

## Residual Risk

- 正常发布包路径已覆盖；手工损坏包仍依赖 fail-closed 路径。
