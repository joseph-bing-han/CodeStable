---
doc_type: issue-report
issue: historical-review-evidence-remediation
status: confirmed
issue_path: standard
severity: P1
summary: CodeStable doctor 被历史 review 证据不符合当前契约的 P1 finding 阻塞
tags:
  - codestable
  - workflow-governance
  - review-evidence
---

# 历史 CodeStable review 证据合规遗留 Issue Report

## 1. 问题现象

在仓库根目录运行当前 `codestable-doctor.py --root . --json` 时，健康检查返回 `status: blocked`。
检查识别出 25 个 P1 finding，分别是 9 个已完成单元缺少 canonical `{slug}-review.md`，以及 16 个
历史 review 的 `reviewer` 字段不符合当前要求的 `subagent`。

## 2. 复现步骤

1. 在仓库根目录执行：
   `python3 "/Users/joseph/.cursor/plugins/local/codestable/skills/cs-onboard/tools/codestable-doctor.py" --root . --json`
2. 观察输出的 `status`。
3. 观察到：命令以非零状态退出，`status` 为 `blocked`，并列出 25 个 P1 finding。

复现频率：稳定。

## 3. 期望 vs 实际

**期望行为**：已归档或已完成的历史 CodeStable 单元应具备可接受的历史兼容证据，仓库在没有当前实现改动或活动 Task 时通过健康检查。

**实际行为**：历史 review 文件名和 reviewer 元数据被按当前严格门禁直接判为 P1，导致健康检查持续阻塞。

## 4. 环境信息

- 涉及模块 / 功能：CodeStable workflow health、`codestable-doctor.py`、历史 Feature / Issue / Refactor review 证据。
- 相关文件 / 函数：`.codestable/features/`、`.codestable/issues/`、`.codestable/refactors/` 下的历史 review 文件；`plugins/codestable/skills/cs-onboard/tools/codestable-doctor.py`。
- 运行环境：本地 macOS 仓库根目录。
- 其他上下文：工作区干净；runtime manifest 与 runtime sync 检查均通过；不存在此前活动 Task。

## 5. 严重程度

**P1** — 健康检查是 CodeStable workflow 的必经门禁；25 个历史证据 finding 会阻塞后续工作流报告成功状态。

## 备注

本 Issue 的目标是处置历史证据兼容与门禁规则，不重新实现已完成的业务或 CodeStable 功能。
