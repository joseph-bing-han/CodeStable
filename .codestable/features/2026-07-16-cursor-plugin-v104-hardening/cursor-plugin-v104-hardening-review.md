---
doc_type: feature-review
feature: 2026-07-16-cursor-plugin-v104-hardening
status: passed
reviewer: self
reviewed: 2026-07-17
round: 1
lane_a_state: unavailable
lane_a_ref: ""
lane_a_reason: explicit-reviewer-config-unavailable
lane_b_state: unavailable
lane_b_ref: ""
lane_b_reason: ocr-cli-not-installed
---

# cursor-plugin-v104-hardening 代码审查报告

## 1. Scope And Inputs

- Design: `.codestable/features/2026-07-16-cursor-plugin-v104-hardening/cursor-plugin-v104-hardening-design.md`
- Checklist: `.codestable/features/2026-07-16-cursor-plugin-v104-hardening/cursor-plugin-v104-hardening-checklist.yaml`
- Evidence pack: none（Standard lane）
- Gate results: none（Standard lane）
- DoD results: checklist commands 与 implementation report
- Implementation evidence: `.codestable/features/2026-07-16-cursor-plugin-v104-hardening/cursor-plugin-v104-hardening-implementation.md`
- Diff basis: 6 个可归因实现文件的 unstaged diff；无 staged diff
- Review mode: initial
- Baseline dirty files: 其他 `.codestable/` untracked audits/features/issues/tasks/tools 为既有 baseline，不属于本轮审查范围

### Independent Review

- Detection: 项目固定 Paseo reviewer 未暴露；`ocr` CLI 未安装
- 环节 A 独立隔离 Task agent: unavailable（Paseo `claude-fable-5/high` adapter unavailable）
- 环节 B OCR CLI: unavailable（`command -v ocr` 非零）
- OCR severity mapping: High→blocking/important，Medium→nit/suggestion，Low→discarded
- Merge policy: owner 已批准本轮 `code-review-local-only`（见同目录 approval-report）；主 agent 按完整 spec-fit、对抗式和行级审查 fail-closed 处理 finding，不自动进入 acceptance
- Gate effect: user-approved downgrade；`reviewer: self`，下游 acceptance 仍需按真实命令证据逐项核验 C1-C13

## 2. Diff Summary

- 新增：本 feature 的 implementation/review 流程产物
- 修改：`README.md`、`README.en.md`、`tools/check-plugin-package.py`、`tests/test_plugin_package.py`、`plugins/codestable/skills/cs-onboard/tools/codestable_runtime.py`、`tests/test_codestable_doctor.py`
- 删除：runtime sync 精确移除 untracked `.codestable/reference/workflow-conventions.md`；该路径删除后未形成 Git diff
- 未跟踪 / staged：feature artifacts 未跟踪；无 staged 文件
- 风险热点：Cursor source/identity 合同的 fail-closed 语义；Git porcelain dirty 分类；untracked target-only 自动删除边界

## 3. Adversarial Pass

- 假设的生产 bug：新增的 untracked target-only 豁免会误删用户 staged/modified 的受管资产，或让 dirty guard 漏放行。
- 主动攻击过的反例：
  - `check_cursor_distribution_contract`：空 `plugins`、非 dict 根、非字符串/空 `source`、绝对路径与 `..` 逃逸、source 目录缺失、plugin manifest 缺失/非法 JSON、单向与双向 identity mismatch、skills 值错误、skills 目录缺失 —— 每条都返回精确 `Finding` 并 fail-closed，`resolve()` + `relative_to(root)` 正确拒绝逃逸。
  - `git_dirty_managed_paths`：staged 新增（`A `）、modified tracked（` M`）、source-backed 修改均不满足 `status == "??"`，全部落入 `dirty` 阻塞；只有 `??` 且属于 `runtime_target_only_paths` 的路径被豁免；`core.quotepath=false` 保证含空格/非 ASCII 路径解析稳定。
  - `sync_runtime`：删除动作在 dirty guard 之后；guard 命中即 `managed-paths-dirty` 早返回，不触发任何 unlink。
- 结果：反例均被现有实现或既有阻塞分支拦下；升级为 findings 的项为 none，残余转入 residual risk / QA focus。

## 4. Findings

### blocking

none

### important

none

### nit

none

### suggestion

- [ ] REV-S1 `check_cursor_distribution_contract` 仅校验 `plugins[0]`，与既有 Codex/Claude 检查同构；未来 marketplace 若允许多 entry，可考虑遍历所有 entry。当前不阻塞，属既有约定延续。

### learning

- code review 的 local-only 授权必须独立于前三轮 design review 授权，且不自动传递到 acceptance。
- 用 `git status --porcelain=v1 --untracked-files=all` 的两字符 status 区分 `??` 与 tracked 变更，是把「安全 stale cleanup」与「用户 managed modification」精确分流的关键。

### praise

- 实现提供 Git-aware isolated candidate、完整 tests（`617 passed / 1 skipped`）和真实无 `--force` runtime sync 证据。
- runtime 豁免同时门控在 `??` 状态与 target-only 成员集合上，保留了 staged/modified/source-backed 的 fail-closed 边界。

## 5. Test And QA Focus

- QA 必须重点复核：Cursor source 逃逸/缺失、identity mismatch、staged/modified target-only 不被删除、README 官方入口真实性。
- Evidence pack residual risks / gate warnings：本轮为 Standard lane，无 evidence pack；reviewer 降级为 local-only 已获授权。
- 建议新增或加强的测试：当前负向覆盖已足；无强制新增。
- 不能靠 review 完全确认的点：Cursor Team Marketplace 的真实组织环境安装/刷新操作。

## 6. Residual Risk

- 本轮为 owner 授权的 local-only review，缺少独立 reviewer 上下文；acceptance 仍须按真实命令证据逐项核验 C1-C13。
- README 的 Cursor 入口依赖官方 UI/文档事实，宿主 UI 变化后需重新核验（见 FDR-003）。

## 7. Verdict

- Status: passed
- Next: 进入 `cs-feat` accept-inline，按 Inline Verification Matrix 逐项核验 C1-C13；requirement delta 与 canonical 回写在 acceptance 阶段机械应用。

## 8. Focused Closure

none
