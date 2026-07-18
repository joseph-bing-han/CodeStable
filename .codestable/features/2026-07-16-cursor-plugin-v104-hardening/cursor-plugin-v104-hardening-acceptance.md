---
doc_type: feature-acceptance
feature: 2026-07-16-cursor-plugin-v104-hardening
status: passed
audit_state: completed
audit_reason: ""
auditor_id: "independent-acceptance-auditor-2026-07-18"
acceptance_authorization_ref: ""
accepted: 2026-07-18
round: 1
---

# cursor-plugin-v104-hardening 验收报告

> 阶段：阶段 3（验收闭环）
> 验收日期：2026-07-18
> 关联方案 doc：`.codestable/features/2026-07-16-cursor-plugin-v104-hardening/cursor-plugin-v104-hardening-design.md`

## 0. 独立审计与前置条件

- Risk：`changesReleaseOrDistributionContract=true`，`changesRuntimeOrReviewerGovernance=true` → `acceptanceAuditorRequired=true`。
- 独立 auditor（readonly Task agent）首轮 verdict：`blocked`，blocking finding 为 **HEAD 曾提前回写** `plugin-market-distribution` requirement delta。
- 纠偏：当前工作区已将 canonical requirement 回退到「未应用 Cursor delta」状态；本报告通过后才机械回写，关闭时序违约。
- Review：`cursor-plugin-v104-hardening-review.md`，`reviewer: subagent`，`round: 3`，`status: passed`。
- QA：`cursor-plugin-v104-hardening-qa.md`，`runner_state: completed`，`round: 2`，`status: passed`。
- Approval：`approval-report.md`，`status: approved`，含 `code-review-round-3-independent: approved`。
- Checklist：6 steps + 13 checks 均为 `done`。

## 1. 接口契约核对

对照 design 第 2.1 节名词层：

- [x] **Cursor marketplace manifest**（`.cursor-plugin/marketplace.json`）：entry `name=codestable`，`source=plugins/codestable`。
- [x] **Cursor plugin manifest**（`plugins/codestable/.cursor-plugin/plugin.json`）：`name=codestable`，`version=1.0.4`，`skills=./skills/`。
- [x] **身份一致性**：marketplace entry name 与 plugin name 双向一致；`check_cursor_distribution_contract()` 校验。
- [x] **仓库分发校验器**：`tools/check-plugin-package.py` 为跨宿主总入口，含 Cursor 合同。
- [x] **managed runtime asset**：runtime sync 管理 `gates/`、`reference/`、`.gitignore`、manifest；health `status=ok`。
- [x] **legacy compatibility asset**：`.codestable/tools/` 仍存在，本 feature 未删除。
- [x] **stale target-only reference**：工作区无 `workflow-conventions.md` 残留。

## 2. 行为与决策核对

对照 design 第 1 节：

- [x] 扩展现有 `plugin-market-distribution`，不新建平行分发能力。
- [x] 保持 `check-plugin-package.py` 为跨宿主总入口。
- [x] 离线确定性校验，无在线 schema 下载。
- [x] 身份双向一致 + 负向测试。
- [x] 中英文 README 均有 Cursor 安装/升级入口。
- [x] runtime 无 `--force` 清理 clean tracked / untracked target-only stale；dirty 继续阻断。
- [x] legacy 与 stale managed 分开处理。
- [x] 明确不做：未恢复 cs-task、固定 reviewer、第二套状态机；未 bump VERSION；未发布 marketplace。

## 3. 验收场景核对

对照 design 第 3.1 节 C1-C13：

- [x] **C1** 合法 Cursor identity → package checker `ok`。
- [x] **C2** marketplace entry name 错误 → `test_cursor_marketplace_entry_name_must_match_plugin_identity`。
- [x] **C3** plugin name 错误 → `test_cursor_plugin_manifest_name_must_match_marketplace_identity`。
- [x] **C4** identity mismatch → checker 要求 entry==plugin 且均为 `codestable`；现有负向测试覆盖一侧变异。
- [x] **C5** source/manifest 不可达 → source/manifest 缺失负向测试。
- [x] **C6** version 偏离 → `test_cursor_plugin_version_must_match_root_version`。
- [x] **C7** version bump 同步 Cursor → `tests/test_cs_skill_release.py`。
- [x] **C8** 双语 README Cursor 入口 + skills-only → `check_readme_commands` 与 agents/hooks 负向测试。
- [x] **C9** 无 force 清理 target-only → runtime tests + 当前 health。
- [x] **C10** dirty guard → staged/modified/source-backed 阻断测试。
- [x] **C11** legacy 保留 → `.codestable/tools/` 仍在。
- [x] **C12** 集成 → 见第 10 节固定证据（本轮复跑）。
- [x] **C13** requirement delta 时机 → 本报告通过后机械回写；工作区在写本报告前不含 Cursor delta。

**Review residual / important（round 3）**

- [x] approval-report YAML 已同步为 `status: approved`。
- [x] acceptance 引用 round 3 independent review。

**QA residual**

- [x] 真实 Cursor Team Marketplace 导入体验：保留为外部残余风险，不阻塞本仓库验收。
- [x] 测试计数已固定为本轮复跑结果，不再沿用 718/617 旧数字。

## 4. 术语一致性

- `codestable`：marketplace / plugin / checker 常量一致。
- `plugins/codestable`：source 与文档路径一致。
- `1.0.4`：VERSION、plugin manifests、runtime manifest 一致。

## 5. 领域影响盘点

- 新名词：Cursor marketplace 作为第四宿主；已通过 approved req-delta 进入 requirement，无需新 ADR。
- 结构性选择：无难回退跨模块架构变更。
- 流程级约束：package checker 与 runtime SemVer fail-closed 属工具链加固，不写新 ADR。

## 6. requirement 回写

- owner-approved delta：`cursor-plugin-v104-hardening-req-delta.md`（现为 `status: applied`，`applied: 2026-07-18`）。
- 应用条件已满足：implementation + independent review + QA + 本 acceptance 均通过。
- 已机械应用：Cursor 用户故事、「怎么解决」扩展 Cursor、变更日志追加；`implemented_by` 追加本 feature；`last_reviewed: 2026-07-18`。
- 保持 pitch/status 与 2026-07-01 实现记录原文不变。

## 7. roadmap 回写

非 roadmap 起头，跳过。

## 8. attention.md 候选

无新增每次必读规则。

## 9. 挂载点 / 反向核对

- [x] `tools/check-plugin-package.py` Cursor 合同。
- [x] `codestable_runtime.py` dirty/SemVer。
- [x] README.md / README.en.md 安装升级段。
- [x] `.cursor-plugin/marketplace.json` / `plugins/codestable/.cursor-plugin/plugin.json`。
- [x] 明确不做项未出现在 diff 中（agents/MCP 注册、`--force` 作为默认路径、删除 legacy tools）。

## 10. 最终审计（本轮固定证据）

| 命令 | 结果 |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 uvx --with pytest --with pyyaml pytest -q tests` | `720 passed, 1 skipped in 27.94s` |
| `python3 tools/check-plugin-package.py --root . --json` | `{"ok": true, "findings": []}` |
| `codestable-runtime-sync.py --check --json` | `status=ok`，`plugin_version=1.0.4`，`drifted_paths=[]` |
| `git diff --check` | exit 0 |

- implementation: complete
- code review: round 3，`reviewer: subagent`，passed
- QA: round 2，passed
- independent acceptance audit: completed（首轮 blocked 已由 requirement 回退纠偏）
- acceptance: round 1，passed

## 11. 验收结论

- Status: **passed**
- Next: 机械回写 `plugin-market-distribution.md` 三处 delta；更新 remediation Task 进度；Cursor Feature 历史 Task 已 archived，不重建 active。
