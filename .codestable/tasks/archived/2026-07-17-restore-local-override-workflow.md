---
doc_type: task-list
task: restore-local-override-workflow
goal: Restore the complete local CodeStable override workflow on version 1.0.4
status: archived
workflow: feature
owner_skill: cs-feat
created: 2026-07-17
updated: 2026-07-17
archived: 2026-07-17
related_docs:
  - .codestable/reference/local-override-workflow.md
  - .codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-design.md
  - .codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-checklist.yaml
  - .codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-review.md
---

# Restore the complete local CodeStable override workflow on version 1.0.4

## 1. 任务目标

在当前 CodeStable 1.0.4 架构上恢复本地 Override：`cs-task`、受保护的 Task runtime、去 OCR 的独立 `cs-code-review` 门禁、入口自动编排以及 Task -> 实施批次 -> Review -> 归档的完整流程主干。

## 2. 当前状态

archived

Round 5 至 Round 7 独立 review 已全部闭合：Round 5 的 5 blocking / 6 important / 1 nit / 1 suggestion 已按 owner 决策修复或明确 override/residual；Round 6 发现并修复 R6-I01（reviewer 档位 gate casing 绕过）；Round 7 独立复审 verdict = passed。design-review、QA、acceptance 全部 passed，全量 707 passed / 1 skipped。

## 3. Agent 原生 Tasks 同步区

- [x] 恢复本地 Override 契约、Task spine、独立 review gate 与 workflow 编排
- [x] 完成 Round 3 独立 review、集中修复和全量验证
- [x] 完成 Round 4 独立 review、集中修复和全量验证
- [x] 完成 Round 5 独立 code review
- [x] 集中修复 Round 5 的 CS5-B01 至 CS5-B05、CS5-I01 至 CS5-I06，并处理 CS5-N01/CS5-S01
- [x] 完成下一轮独立 code review（Round 6 修复 R6-I01，Round 7 passed）
- [x] 完成 design-review、QA、acceptance、Task complete，准备原子归档

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| reference | `.codestable/reference/local-override-workflow.md` | 本地 Override canonical 契约 |
| design | `.codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-design.md` | 当前 1.0.4 适配设计 |
| design-review | `.codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-design-review.md` | design 独立审查（passed） |
| checklist | `.codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-checklist.yaml` | 原始实施步骤和状态 |
| review | `.codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-review.md` | Round 3 至 Round 7 独立 review 和修复证据 |
| qa | `.codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-qa.md` | QA 验证（passed） |
| acceptance | `.codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-acceptance.md` | 验收（passed） |

## 5. 执行步骤

### 1. 主干恢复与前两轮 hardening

- 状态：done
- 已完成 Task runtime、review gate、workflow spine、archive integrity、CAS、crash recovery、strict schema、路径安全与历史兼容基础实现。

### 2. Round 4 review-fix

- 状态：done
- 已完成 strict review lifecycle、issue/refactor evidence resolver、no-replace active CAS、atomic claim、final staging recovery、typed YAML/JSON、lock inode 和 historical classification。
- 验证：定向 `270 passed`；全量 `702 passed, 1 skipped`；runtime sync、py_compile、`git diff --check` 通过。

### 3. Round 5 独立 review

- 状态：changes-requested
- reviewer：AgentRef `d11e7d51-96da-488d-9fb5-2cb68c9e0e0e`
- 配置：`provider=openai`、`model=gpt-5.6-sol`、`reasoning=xhigh`、`readonly=true`
- 结论：5 blocking、6 important、1 nit、1 suggestion
- 只读证据：reviewer 前后 dirty/untracked 文件 SHA-256 清单一致。

### 4. Round 5 review-fix

- 状态：done
- CS5-B02/B03/B04、CS5-I01/I02/I04/I06、CS5-N01/CS5-S01 已修复；CS5-B01 核心已闭合（workflow family + terminal owner + archived status 绑定）。
- CS5-B05（保留 owner-approved local review 逃生口）、CS5-I03（回填旧日期）、CS5-I05（旧 active FD 跨 CAS 写入，仅 docstring 声明边界）按 owner 决策 override / residual risk。
- 验证：全量 `705 passed, 1 skipped`；runtime sync、diff check 通过。

### 5. Round 6 独立 review 与 review-fix

- 状态：done
- Round 6 verdict：无 blocking，1 important R6-I01（reviewer 档位 gate override 查表 casing 敏感，`GPT-5.6-Sol` 可绕过 xhigh 强制）。
- 修复：`reviewer_reasoning_is_valid` 入口归一化一次，FORBIDDEN 匹配 / override 查表 / reasoning 比较统一复用小写形式；补 casing 变体回归测试。
- 验证：全量 `709 passed, 1 skipped`。

### 6. Round 7 独立复审

- 状态：done
- reviewer：AgentRef `d45cc607-c663-49dc-b6af-b89af4fdb0cb`，继承当前对话主模型（claude-opus-4 / max / readonly）。
- verdict：passed。R6-I01 修复无残留、无反向绕过、无回归；唯一 finding 为 pre-existing nit N-01（override 键分隔符变体，不扩大攻击面）。

### 7. design-review / QA / acceptance / 归档

- 状态：done
- design-review passed、QA passed（707 passed / 1 skipped）、acceptance passed。
- code-review basis digest 在补充过程文档后按 owner 授权 re-stamp（无实现改动）。
- Task 状态转为 completed，进入原子归档。

## 6. 中断恢复提示

全部 gate 已闭环，Task 已 completed。若归档中断，重跑 `codestable-task-runtime.py scan` 收敛 tombstone/staging，再重试 `archive`。

## 7. 完成与归档记录

design → design-review(passed) → 实现 → code-review(Round 3-7，Round 7 passed) → QA(passed) → acceptance(passed) → Task completed。全量 707 passed / 1 skipped，runtime sync 与 `git diff --check` 通过。等待原子归档写入 tombstone。
