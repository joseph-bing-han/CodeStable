---
doc_type: feature-design-review
feature: 2026-07-16-cursor-plugin-v104-hardening
status: passed
review_state: passed
review_reason: ""
reviewer_id: "local-main-model"
reviewed: 2026-07-16
round: 3
---

# cursor-plugin-v104-hardening feature design 审查报告

## 1. Scope And Inputs

- Design: `.codestable/features/2026-07-16-cursor-plugin-v104-hardening/cursor-plugin-v104-hardening-design.md`
- Checklist: `.codestable/features/2026-07-16-cursor-plugin-v104-hardening/cursor-plugin-v104-hardening-checklist.yaml`
- Intent / brainstorm: none
- Roadmap: none
- Related docs: `.codestable/requirements/plugin-market-distribution.md`、同目录 requirement delta、`approval-report.md`、既有 plugin distribution feature/acceptance、v1.0.4 release contract 记录
- Code facts checked: `.cursor-plugin/marketplace.json`、`plugins/codestable/.cursor-plugin/plugin.json`、`tools/check-plugin-package.py`、`tests/test_plugin_package.py`、`tests/test_cs_skill_release.py`、README 双语安装段、`plugins/codestable/skills/cs-onboard/tools/codestable_runtime.py`、runtime 相关测试入口

### Independent Review

- Status: local-only
- Detection: local-only
- Provider / agent: 当前主模型；原配置为 Paseo `provider=claude`、`model=claude-fable-5`、`thinkingOptionId=high`
- Raw output: 本报告；round 3 授权见同目录 `approval-report.md` 的 `design-review-local-only-round-3: approved`
- Merge policy: owner 仅授权 round 3 design review 降级；本地审查按完整 invariants fail-closed，不自动批准 design/requirement delta，也不把授权传递给后续 gate
- Gate effect: user-approved downgrade；允许形成 round 3 design-review verdict

## 2. Design Summary

- Goal: 补齐 Cursor 分发合同、防回归测试和双语安装入口，并清理当前项目的 v1.0.4 stale managed reference。
- Key contracts: Cursor marketplace/plugin identity 一致性、source 可达性、skills-only、离线 checker、无 `--force` runtime sync、legacy/history 保留。
- Steps: checklist 共 7 个；风险热点是 checker 假阳性、runtime target-only 清理边界、隔离候选构造和 Cursor 安装文档事实。
- Checks: checklist 共 13 个；均能回到名词契约、挂载点、流程级约束、范围守护或验收场景。
- Baseline / validation: clean detached `HEAD` 已通过 package、正式 tests 和 runtime health；当前工作区除单一 stale reference drift 外，还有会阻断直接 package check 的既有根 skill/cache 污染。

## 3. Findings

### blocking

none

### important

none

### nit

none

### suggestion

- [ ] FDR-003 实现证据中记录 Cursor 官方安装/升级入口的核验日期、官方来源和实际可观察结果，避免 README 只通过字符串守卫却在宿主 UI 变化后失真。

### learning

- managed runtime stale reference 与 `.codestable/tools/` legacy compatibility 必须分开处置；前者由 sync 清理，后者不默认删除。
- 依赖 Git 行为的发布校验器不能在无 `.git` 快照中把命令退出成功直接当成完整合同证据。

### praise

- 方案明确拒绝恢复旧 Task/reviewer/runtime 双轨，并把 clean HEAD 与当前工作区分开验收。
- runtime 设计保留 clean tracked target-only 的既有迁移能力，只为 untracked target-only 增加精确例外，并继续阻断 staged/modified/source-backed dirty asset。

## 4. User Review Focus

- 用户需要重点拍板：是否同时批准 feature design 与 requirement delta；三轮 local-only reviewer 授权均只影响审查主体，不等于批准这两个产品/范围决策。
- implement 需要重点遵守：checker 离线确定性、identity 关系校验、runtime sync 禁止 `--force`、legacy/history 不删除，以及只在具备有效 Git ignore 语义的候选环境产出 package 证据。
- code review / QA / acceptance 需要重点复核：Cursor 安装步骤真实性、负向变异闭环、同步前后路径保护、隔离候选 package 与主工作区 runtime/test 两类证据不混写。

## 5. Evidence Confidence Ledger

| Check | Verdict | Evidence Class | Basis | Follow-up |
|---|---|---|---|---|
| Acceptance Coverage Matrix | pass | E | 顶层成功标准、C12、推进策略和 checklist 均统一为隔离候选 package/runtime 与主工作区 tests/runtime/diff | none |
| DoD Contract | pass | E+C | CMD-001 保持 Git-aware，design 与 checklist 命令一致 | none |
| Steps and checks traceability | pass | E+C | runtime step/checks 已区分 clean tracked、untracked target-only 与 staged/modified/source-backed dirty，且与现有测试合同一致 | none |
| Roadmap contract compliance | pass | E | roadmap/roadmap_item 均为空 | none |
| Module interface design | pass | C | checker Finding seam 与 runtime dirty/stale seam 均给出 caller invariant、error mode、ordering 和测试观察点 | 实现时保持状态分类精确 |
| Validation and artifacts | pass | E+C | 成功标准、runtime 场景、Git-aware 候选命令和必需产物已对齐；checklist YAML 与 artifact diff check 通过 | none |

Summary: E=4, C=2, H=0, H-only core checks=none。

## 6. Residual Risk

- Cursor 实际安装/升级步骤需实现阶段按当前官方 UI/文档核验，不能只凭 repository schema 推断。
- 当前工作区有大量 untracked 历史产物；runtime sync 前后保护检查必须限定路径，避免把历史存在误判成本次变更。
- local-only 审查缺少独立上下文；后续 code review、QA 和 acceptance 必须重新执行各自 reviewer gate，本次授权不得复用。

## 7. Verdict

- Status: passed
- Next: 交给用户同时进行 feature design 与 requirement delta 的整体人工 review；用户明确批准前不进入实现。

## 8. Focused Closure

none；本轮为完整 round 3 review。FDR-005 closure 由统一后的顶层成功标准/C12/checklist 证明，FDR-006 closure 由细分后的 runtime dirty/stale 合同与既有 clean tracked 测试事实证明。
