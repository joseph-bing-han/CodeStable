---
doc_type: feature-review
feature: 2026-07-16-cursor-plugin-v104-hardening
status: passed
reviewer: subagent
reviewed: 2026-07-18
round: 3
review_basis: independent-readonly-review
---

# cursor-plugin-v104-hardening 独立代码审查报告（Round 3）

## Verdict

**passed** — 无 blocking finding，可进入 acceptance。

## 1. Scope And Inputs

- Design: `cursor-plugin-v104-hardening-design.md`
- Checklist: `cursor-plugin-v104-hardening-checklist.yaml`
- QA: `cursor-plugin-v104-hardening-qa.md`（round 2）
- Approval: `approval-report.md`
- Req delta: `cursor-plugin-v104-hardening-req-delta.md`
- Canonical requirement: `.codestable/requirements/plugin-market-distribution.md`
- Package checker: `tools/check-plugin-package.py`
- Runtime: `plugins/codestable/skills/cs-onboard/tools/codestable_runtime.py`
- Reviewer protocol: `cs-code-review/references/independent-review/protocol.md`
- Agent conventions: `cs-onboard/references/agent-conventions.md`
- Diff basis: 当前 working tree，覆盖 package checker、runtime SemVer、reviewer fail-closed、root compatibility boundary

## 2. 核验结果

### 2.1 Cursor marketplace/plugin identity 一致性

- `.cursor-plugin/marketplace.json` 的 `plugins[0].source` 指向 `plugins/codestable`
- `plugins/codestable/.cursor-plugin/plugin.json` 的 `name` 为 `codestable`、`version` 为 `1.0.4`
- `tools/check-plugin-package.py:157-217` 同时校验 marketplace entry、plugin identity、source 可达性、manifest 存在和 skills 路径
- `tests/test_plugin_package.py` 覆盖 entry name、plugin name、source 和 version 的主要负向场景
- **结论：通过**

### 2.2 Strict SemVer 与 nearest invalid VERSION fail-closed

- `plugins/codestable/skills/cs-onboard/tools/codestable_runtime.py:15-20` 使用严格 SemVer regex，拒绝数值前导零（如 `01.0.0`）和非法 prerelease（如 `1.0.0-01`）
- `discover_plugin_version()` 对最近 standalone `VERSION` 存在但非法时直接返回 `None`，不回退读取父级 manifest：`codestable_runtime.py:74-86`
- `tools/check-plugin-package.py:14-18` 使用相同严格 SemVer 正则
- `tests/test_codestable_doctor.py:158-184` 覆盖 `unknown`、`1.0`、`version-1.0.0`、`1.0.0 trailing`、`1.0.0-01`、nearest ancestor invalid VERSION 不回退等场景
- `tests/test_plugin_package.py:127-135` 覆盖 `01.0.0` 和 `1.0.0-01`
- **结论：通过**

### 2.3 Reviewer gate 降级行为

- `cs-code-review/SKILL.md:150` 定义：subagent 与 model-safe bridge 均不可用时，用当前主模型最高思考档做 review，写 `reviewer: self`
- `cs-code-review/references/independent-review/protocol.md:14` 确认 owner 授权 `ApproveLocalOnly` 后可降级为 owner-approved local review
- `cs-onboard/references/agent-conventions.md` 的 `reviewGate` 保留 `LocalReview` 路径
- `cs-feat`、`cs-epic`、`cs-goal` 的协议和状态机均同步
- 禁止 Explore/Fast/unknown-model 冒充独立 reviewer
- **结论：通过**

### 2.4 Root compatibility boundary

- `tools/check-plugin-package.py:231-265` 对根目录 `cs-*` 路径区分三种情况：git-ignored 跳过、含 `SKILL.md` 的目录报错、仅 `tools/` 目录放行、其它内容报错
- `tests/test_plugin_package.py:185-199` 覆盖 `bin`、`agents`、`.mcp.json` 负向场景与 `tools/` 正向场景
- `tests/test_plugin_package.py:195-206` 覆盖根 `cs-*` 普通文件报错
- **结论：通过**

### 2.5 QA 证据充分性

- QA 报告覆盖：`tests` 720 passed, 1 skipped、package checker `ok`、runtime health `ok`、`git diff --check` 成功
- QA 类型为 non-functional（分发契约、package checker、runtime 版本治理）
- 非功能性 feature 不强制 e2e/browser/API；QA 报告已写明替代证据理由
- **结论：通过**

### 2.6 Requirement delta 回写时机

- `cursor-plugin-v104-hardening-req-delta.md` 要求 acceptance 全部通过后才机械回写
- `.codestable/requirements/plugin-market-distribution.md` 当前仅列 Codex、Claude、`skills` CLI；未包含 Cursor delta
- **结论：通过**

## 3. Important

- **I-1**: `approval-report.md` YAML 中 `code-review-local-only-round-1` 仍为 `pending`。这是历史 artifact，在 acceptance 前应同步更新，否则自动化流程可能假阻塞。
- **I-2**: QA 声明 remediation 后需独立 subagent 复审。本 round 3 已完成独立复审并确认 passed，但需在 acceptance 报告中引用本轮 review evidence。

## 4. Nit

- `check_cursor_distribution_contract()` 仅验证 `plugins[0]`。当前单插件 marketplace 合同下可接受。
- 主工作区存在 `__pycache__` 污染。QA 已声明并归因为 baseline。

## 5. Residual Risk

- 真实 Cursor Team Marketplace 导入、组织权限与 Auto Refresh 仍是外部集成风险，本地测试不能证明。
- `plugins.0` 是 checker 的当前单 entry 合同；若未来支持多 plugin entry，需单独扩展。

## 6. 验证证据

| 项目 | 证据 | 结论 |
|---|---|---|
| 全量 tests | `720 passed, 1 skipped` | 通过 |
| Package checker | `ok: true, findings: []` | 通过 |
| Runtime sync | `status: ok, drifted_paths: []` | 通过 |
| `git diff --check` | exit 0 | 通过 |
| Source doctor | 当前 P1 = 10（均为历史遗留 evidence） | 非本 Feature blocker |
