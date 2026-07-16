---
doc_type: onboarding-audit
task: refresh-codestable-onboard
status: completed
created: 2026-07-03
updated: 2026-07-03
owner_skill: cs-onboard
---

# CodeStable 版本刷新审计

## 1. 扫描结论

当前仓库已经存在 `.codestable/`，属于 CodeStable 迁移刷新路径，不是空仓库初始化路径。

未检测到 `.ccodestable/` 目录。本次按当前项目实际存在的 `.codestable/` 执行适配。

## 2. 已执行刷新

| 项目 | 来源 | 目标 | 结果 |
|---|---|---|---|
| shared tools | `plugins/codestable/skills/cs-onboard/tools/` | `.codestable/tools/` | 已覆盖同步 |
| shared reference | `plugins/codestable/skills/cs-onboard/reference/` | `.codestable/reference/` | 已覆盖同步 |
| gate config | `plugins/codestable/skills/cs-onboard/gates/` | `.codestable/gates/` | 已同步 |

## 3. 本次适配到的新版资产

### tools

- 新增或刷新 `codestable_gate_common.py`
- 新增或刷新 `codestable-dod-contract-gate.py`
- 新增或刷新 `codestable-dod-runner.py`
- 新增或刷新 `codestable-evidence-pack.py`
- 新增或刷新 `codestable-goal-consistency-gate.py`
- 新增或刷新 `codestable-scope-gate.py`
- 刷新 `codestable-main-publish.py`
- 刷新 `validate-implementation-review.py`
- 刷新其他共享工具脚本

### reference

- 新增或刷新 `workflow-conventions.md`
- 刷新 `shared-conventions.md`
- 刷新 `system-overview.md`
- 刷新 `approval-conventions.md`
- 刷新 `execution-conventions.md`
- 刷新其他共享参考文档

### gates

- 新增 `.codestable/gates/roadmap-goal-gates.yaml`

## 4. 骨架检查

以下标准聚合根目录已存在：

- `.codestable/requirements/`
- `.codestable/roadmap/`
- `.codestable/goals/`
- `.codestable/features/`
- `.codestable/issues/`
- `.codestable/refactors/`
- `.codestable/audits/`
- `.codestable/brainstorms/`
- `.codestable/brainstorm/`
- `.codestable/compound/`

`.codestable/attention.md` 已存在，保留原内容。

## 5. 保留原位项

以下目录属于既有项目内容或历史结构，本次未移动、未删除：

- `.codestable/architecture/`
- `.codestable/config/`
- `.codestable/tasks/`
- `.codestable/reference/branch-guard-hooks.md`
- 已存在的 feature / issue / roadmap / requirement 文档

## 6. 验证结果

已验证：

- `.codestable/tools/` 已包含新版共享工具
- `.codestable/reference/` 已包含新版参考文档
- `.codestable/gates/roadmap-goal-gates.yaml` 已存在
- 标准骨架聚合根目录已存在

结论：当前项目 `.codestable/` 已适配本次 CodeStable 版本更新。
