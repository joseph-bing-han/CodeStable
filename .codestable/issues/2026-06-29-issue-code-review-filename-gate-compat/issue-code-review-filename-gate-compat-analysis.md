---
doc_type: issue-analysis
issue: 2026-06-29-issue-code-review-filename-gate-compat
status: confirmed
root_cause_type: logic
related: [issue-code-review-filename-gate-compat-report.md]
tags: [codestable, worktree-gate, code-review]
---

# issue code review 文件名导致 gate 误判根因分析

## 1. 问题定位

| 位置 | 说明 |
|---|---|
| `cs-issue/SKILL.md` | issue 工作流文件树约定最终审查产物为 `{slug}-code-review.md` |
| `cs-onboard/tools/codestable_common.py` | `review_file_for` 固定返回 `{slug}-review.md` |
| `cs-onboard/tools/validate-implementation-review.py` | 内置重复的 `review_file_for` 同样固定返回 `{slug}-review.md` |

## 2. 失败路径还原

issue fix-note 存在后，gate 判断该 unit 需要 review；随后固定查找 `{slug}-review.md`。如果实际按 issue 约定写的是 `{slug}-code-review.md`，gate 就误报缺 review。

## 3. 根因

工具层把 feature/refactor 的 `{slug}-review.md` 命名泛化到了 issue，但 issue 工作流历史约定是 `{slug}-code-review.md`。两处 gate 实现没有做兼容候选列表。

## 4. 影响面

- issue commit gate
- implementation review validation gate
- 依赖 `missing_review_findings` 的 doctor / finish gate

## 5. 修复方案

采用兼容修复：

1. 为 review 文件增加候选列表。
2. issue 优先识别 `{slug}-code-review.md`，同时兼容 `{slug}-review.md`。
3. feature / refactor 继续使用 `{slug}-review.md`。
4. 补充测试覆盖 issue code-review 文件可放行、issue review 文件仍兼容。
