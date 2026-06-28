---
doc_type: issue-fix
issue: 2026-06-29-issue-code-review-filename-gate-compat
status: fixed
related:
  - issue-code-review-filename-gate-compat-report.md
  - issue-code-review-filename-gate-compat-analysis.md
tags: [codestable, worktree-gate, code-review]
---

# issue code review 文件名导致 gate 误判修复记录

## 1. 根因

CodeStable 工具层固定把实现 review 文件识别为 `{slug}-review.md`，但 issue 工作流的历史约定是 `{slug}-code-review.md`。因此 XebnIoT 这类已按 issue 约定落盘 code review 的任务，会在 commit gate 阶段被误判为缺少 review 证据。

同时，`codestable_common.py` 的 worktree gate 路径没有实现 `CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1`，导致 self review fallback 在 `validate-implementation-review.py` 中可用，但在 commit / finish / doctor 共用的 review finding 路径中不可用。

## 2. 修复范围

- `cs-onboard/tools/codestable_common.py`
- `cs-onboard/tools/validate-implementation-review.py`
- `tests/test_codestable_worktree_gate.py`
- `tests/test_validate_implementation_review.py`
- XebnIoT `.codestable/tools/`、`.codestable/reference/`、`.codestable/hooks/` 运行时副本同步

## 3. 修复内容

1. 增加 review 文件候选列表：
   - issue 优先识别 `{slug}-code-review.md`
   - issue 兼容历史 `{slug}-review.md`
   - feature / refactor 继续使用 `{slug}-review.md`
2. `missing_review_findings` 改为查找实际存在的候选 review 文件，避免误报。
3. `codestable_common.py` 支持 `CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1`，与 `validate-implementation-review.py` 的 fallback 语义一致。
4. 补充 worktree gate 与 implementation review validation 的回归测试。
5. 将最新版 CodeStable runtime tools/reference/hooks 同步到 XebnIoT 的 `.codestable`。

## 4. 回归测试

新增/更新测试覆盖：

- issue `{slug}-code-review.md` 可满足 review evidence
- issue `{slug}-review.md` 仍兼容
- issue 缺 review 时提示 canonical `{slug}-code-review.md`
- worktree commit gate 对 `reviewer: self` 默认阻塞
- 设置 `CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1` 后 worktree commit gate 放行 self review

## 5. 验证命令与结果

```bash
uvx pytest -q
```

结果：

```text
63 passed in 11.93s
```

CodeStable 当前 issue commit gate：

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json commit --unit .codestable/issues/2026-06-29-issue-code-review-filename-gate-compat
```

结果：通过。

XebnIoT 同步后验证：

```bash
CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1 python3 /Users/joseph/code/weigroup/XebnIoT/.codestable/tools/codestable-worktree-gate.py --root /Users/joseph/code/weigroup/XebnIoT --json commit --unit .codestable/issues/2026-06-29-mqtt-offline-message-missing-packet-id
```

结果：通过，且 `required_review` 正确指向 `{slug}-code-review.md`。

## 6. 结果

CodeStable gate 现在能正确识别 issue 工作流的 `{slug}-code-review.md`，并且 worktree gate 与 implementation review validation 对 self review fallback 的语义保持一致。XebnIoT 的 `.codestable` 运行时副本已同步到当前 CodeStable 版本。
