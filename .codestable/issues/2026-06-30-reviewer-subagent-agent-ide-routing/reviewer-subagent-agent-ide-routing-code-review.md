---
doc_type: issue-review
issue: 2026-06-30-reviewer-subagent-agent-ide-routing
status: blocked
reviewed: 2026-06-30
round: 3
---

# reviewer-subagent-agent-ide-routing 代码审查报告

## 1. Scope And Inputs

- Report: `.codestable/issues/2026-06-30-reviewer-subagent-agent-ide-routing/reviewer-subagent-agent-ide-routing-report.md`
- Analysis: `.codestable/issues/2026-06-30-reviewer-subagent-agent-ide-routing/reviewer-subagent-agent-ide-routing-analysis.md`
- Fix note: `.codestable/issues/2026-06-30-reviewer-subagent-agent-ide-routing/reviewer-subagent-agent-ide-routing-fix-note.md`
- Implementation evidence: `.codestable/tasks/active/reviewer-subagent-agent-ide-routing.md`、`.cursor/agents/cs-code-reviewer.md`、当前 git diff、独立测试与 contract test
- Diff basis: `git status --short` 显示 `cs-code-review/`、`cs-onboard/`、`tests/`、`.cursor/`、当前 issue 产物和 active task 的本轮修改；`git diff --cached` 为空
- Baseline dirty files: none

### Independent Review

- Status: pending
- Detection: codestable-managed-subagent
- Agent IDE: cursor
- Managed agent: `.cursor/agents/cs-code-reviewer.md`
- Configured reviewer: `.codestable/config/code-review-subagent.yaml` model={configured} thinking_budget={configured}
- Actual reviewer: model={configured-file-created} thinking_budget={unsupported-by-host-frontmatter} model_apply_status={applied-to-managed-file} thinking_budget_apply_status={unsupported-by-host-frontmatter}
- Provider / agent: none
- Raw output: `.cursor/agents/cs-code-reviewer.md` created; actual review response still pending
- Merge policy: pending 时不得定稿
- Gate effect: blocks final verdict until completed

## 2. Diff Summary

- 新增：`cs-code-review/scripts/configure-review-subagent.py`、`cs-code-review/references/subagent-config.md`、`tests/test_configure_review_subagent.py`、`.cursor/agents/cs-code-reviewer.md`、当前 issue 的 report / analysis / fix-note / code-review
- 修改：`cs-code-review/SKILL.md`、`cs-code-review/references/report-template.md`、`cs-onboard/SKILL.md`、`tests/test_workflow_contracts.py`、active task
- 删除：none
- 未跟踪 / staged：新增文件未 staged，`git diff --cached` 为空
- 风险热点：workflow gate、custom subagent 配置、runtime 识别、测试契约

## 3. Findings

### resolved from round 1

- [x] REV-001 `workflow-gate` 当前 issue 缺少完整的 issue spec 产物链路
  - Resolution: 已补齐当前 issue 的 report / analysis / fix-note，并将这些产物纳入本轮 review 输入。

### resolved from round 2

- [x] REV-002 `independent-review-gate` 当前 runtime 没有产出可核验的独立 reviewer 结果
  - Resolution: 已查明上一轮并非 reviewer 模型执行失败，而是 `cs-code-review` 没有先执行配置脚本，导致 `.cursor/agents/cs-code-reviewer.md` 根本不存在。已实际运行配置脚本创建该 managed agent，并把“先配置、再调用或 fallback”的硬性顺序写入仓库 skill 与已安装 skill。

### blocking

- [ ] REV-003 `custom-subagent-invocation` 当前工具层仍未暴露“按项目 custom subagent 名称启动”的可调用入口
  - Evidence: `.cursor/agents/cs-code-reviewer.md` 已生成且 marker/model 正确；但当前可用工具只暴露通用 Subagent 类型，不能指定项目 custom agent `cs-code-reviewer` 执行一次真实审查回执。
  - Impact: 配置与生成链路已修复，但最终 review evidence gate 仍缺少独立 reviewer 的审查响应；不能把“文件已生成”伪装成“独立审查已完成”。
  - Expected fix scope: 等 Cursor runtime 暴露项目 custom agent 后显式调用 `cs-code-reviewer`，或在 skill 里增加可验证的 custom agent 调用入口说明；若当前产品能力不支持，只能保持 blocked 或由 owner 明确接受 fallback。

### important

- none

### nit

- none

### suggestion

- 建议后续为 `cs-code-review` 增加对旧 managed reviewer 文件的迁移/清理提示，避免项目中同时残留旧名与新名 agent 文件造成理解成本。

### learning

- 把 IDE 识别与 reviewer 文件生成抽成独立脚本后，才能真正用测试锁住“识别 host + 写入官方配置路径 + 拒绝覆盖非 managed agent”这一条链路。

### praise

- `configure-review-subagent.py` + `tests/test_configure_review_subagent.py` 把三类 IDE 输出、路径、marker 和覆盖保护都落成了可执行验证，已经从文档约束升级为行为约束。

## 4. Test And QA Focus

- QA 必须重点复核：
  - 在真实 Cursor review 流程里，`SKILL_DIR/scripts/detect-review-agent.py` 与 `SKILL_DIR/scripts/configure-review-subagent.py` 都按 skill 包路径执行
  - `--agent-ide auto` 在真实运行时生成 `.cursor/agents/cs-code-reviewer.md`，且不得先询问 fallback
  - review 现场能拿到 `actual reviewer` 并写入报告，而不是只停留在 dry-run / 测试层
- 建议新增或加强的测试：none
- 不能靠 review 完全确认的点：当前工具环境里无法直接证明 custom subagent 被真实调用并返回审查结果

## 5. Residual Risk

- 目前已经证明“脚本能生成配置”“skill 会要求先配置再 fallback”“测试能覆盖三类 IDE 输出”，但还没有形成一次真实 `cs-code-reviewer` 审查回执；如果直接放行，独立 reviewer gate 会退化成仅验证配置文件生成。

## 6. Verdict

- Status: blocked
- Next: 等 Cursor runtime 暴露项目 custom subagent 调用入口后，完成一次 `cs-code-reviewer` 独立审查并重跑本审查；若 owner 明确接受 local-only fallback，也可按降级路径重跑
