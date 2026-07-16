---
doc_type: issue-code-review
issue: 2026-06-29-issue-code-review-filename-gate-compat
status: passed
reviewer: self
independent_review: local-only
review_round: 1
related:
  - issue-code-review-filename-gate-compat-report.md
  - issue-code-review-filename-gate-compat-analysis.md
  - issue-code-review-filename-gate-compat-fix-note.md
tags: [codestable, worktree-gate, code-review]
---

# issue code review 文件名 gate 兼容修复代码审查

## 1. 审查范围

本次审查覆盖：

- `cs-onboard/tools/codestable_common.py`
- `cs-onboard/tools/validate-implementation-review.py`
- `tests/test_codestable_worktree_gate.py`
- `tests/test_validate_implementation_review.py`
- XebnIoT `.codestable` 运行时副本同步结果

## 2. 独立 reviewer

- 已执行 `cs-code-review/scripts/detect-review-agent.py --pretty`
- Paseo 不可用：`127.0.0.1:6767` 连接失败
- 检测到 `opencode` 直接 CLI，但本 skill 不自动调用直接 agent CLI
- 本轮按 local-only self review 完成，并通过 `CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1` 验证 gate fallback 语义

## 3. Findings

### blocking

none

### important

none

### nit

none

### suggestion

none

### learning

none

### praise

- 修复没有改变 feature / refactor 的既有 `{slug}-review.md` 行为，只对 issue 增加优先 `{slug}-code-review.md` 与兼容候选，改动边界清晰。
- worktree gate 与 implementation review validation 现在共享相同的 issue review 文件名语义，避免同一仓库在不同 gate 中出现相互矛盾的结果。
- 新增测试覆盖了 canonical issue code-review、legacy issue review 和 self review fallback 三个容易回归的边界。

### residual-risk

- 本轮没有启动外部 subagent reviewer；如果后续平台提供 Paseo 或其他 subagent，应优先使用独立 reviewer 重新审关键 gate 改动。
- XebnIoT 既有 review 文件为 `reviewer: self`，默认 gate 仍会阻塞；只有在明确设置 `CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1` 时才放行，这是预期的质量门禁语义。

## 4. 结论

本轮修改满足 issue 工作流命名兼容目标，没有发现 blocking / important 问题。结论：`passed`。

## 5. 已核验的验证证据

```bash
uvx pytest -q
```

```text
63 passed in 11.93s
```

```bash
CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1 python3 /Users/joseph/code/weigroup/XebnIoT/.codestable/tools/codestable-worktree-gate.py --root /Users/joseph/code/weigroup/XebnIoT --json commit --unit .codestable/issues/2026-06-29-mqtt-offline-message-missing-packet-id
```

结果：`ok: true`。
