---
doc_type: approval-report
unit: historical-review-evidence-remediation
status: approved
reason: risk
approvals:
  confirm-report: approved
  confirm-fix-plan: superseded
  confirm-revised-fix-plan: approved
approval_groups: {}
created_at: 2026-07-17
---

# 历史 CodeStable review 证据合规遗留审批

## Decision History

- 2026-07-17：owner 批准按标准 Issue 路径继续，先审计历史 review 证据，再实施最小合规修复。
- 2026-07-17：owner 批准方案 A：实现严格历史 evidence 分类，并为 11 个缺少独立审查的单元补做 focused review。
- 2026-07-17：实施前核验发现 15 个历史单元没有 archived Task，原方案的 archived-only 前提不成立；原 fix plan 已 superseded，等待修订方案确认。
- 2026-07-17：owner 选择回填 15 个历史 archived Task，并继续采用 archived-only 兼容边界。

## Decision Needed

已确认回填 15 个历史 archived Task，并继续采用 archived-only 兼容边界；没有独立审查证据的单元仍须补做 focused review。

## Why Now

证据审计与源码追踪已完成，但实施前发现原方案的 archived Task 前提只覆盖 10 个 P1 单元；15 个早期单元没有 archived Task。继续原方案会静默扩大例外范围，因此需要重新确认修订后的兼容边界。

## Context

- 根因分析：`historical-review-evidence-remediation-analysis.md`（修订为 draft）。
- 10 个 P1 单元具有有效 archived Task，15 个没有 archived Task。
- 严格前端声明条件可识别 13 个已有明确 agent reviewer 的历史单元。
- 12 个单元无 reviewer 字段、仅 self review、review blocked 或无 review；必须真实补审。
- 目标是恢复可靠的健康检查，而不是伪造、删除或重写历史证据。

## Options

1. 执行修订版方案 A：以日期、无 active Task、identity、明确 agent reviewer 为联合 legacy 条件；补审 12 个单元。
2. **回填 15 个 historical archived Task 后保持 archived-only 条件（已选）**：新增带历史恢复说明的 Task archive 记录。
3. 暂停处理：保留当前 Issue、Task 和 `blocked` 状态，不修改 gate 或历史 evidence。

## Recommendation

Owner 选择选项 2。回填仅补足缺失的 Task lifecycle record，不修改旧 review 文件；review 证据本身仍由现有 gate 和后续 focused review 约束。

## Risks And Tradeoffs

- 方案 1 需要 12 次独立 focused review，执行时间和 review 产物数量较高。
- 日期目录是历史兼容锚点的一部分，必须以可测试 cutoff 锁死；任何 post-cutoff 单元仍 fail-closed。
- 不修改旧 `reviewer` 字段；历史 `subagent+ocr` 只能在联合 legacy 条件内读取，不能作为新单元通行证。

## Non-Automatic Actions

本次确认不执行 commit、push、merge、发布或删除历史产物；任何需要接受无法补审的残余风险会单独请求确认。

## After You Answer

当前进入历史 Task 回填；完成后重新运行 doctor，按仍存在的 P1 精确确定 focused review 范围。
