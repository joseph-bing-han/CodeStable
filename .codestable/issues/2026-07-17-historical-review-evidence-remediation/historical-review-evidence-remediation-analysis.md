---
doc_type: issue-analysis
issue: historical-review-evidence-remediation
status: confirmed
root_cause_type: logic
related:
  - historical-review-evidence-remediation-report.md
tags:
  - codestable
  - review-evidence
  - historical-compatibility
---

# 历史 CodeStable review 证据合规遗留根因分析

## 1. 问题定位

| 关键位置 | 说明 |
|---|---|
| `plugins/codestable/skills/cs-onboard/tools/codestable-doctor.py:29-32,50-52` | `diagnose()` 枚举 Feature、Issue、Refactor 单元，并将 `missing_review_findings()` 的 P1 结果汇入 health report。 |
| `plugins/codestable/skills/cs-onboard/tools/codestable_common.py:301-306` | `review_file_for()` 仅构造 `{slug}-review.md`，不能发现历史 Issue 的 `{slug}-code-review.md`。 |
| `plugins/codestable/skills/cs-onboard/tools/codestable_common.py:420-453,658-680` | 当前 canonical evidence 强制要求当前文件名、`reviewer: subagent` 及完整 metadata；不满足即列为 P1。 |
| `plugins/codestable/skills/cs-onboard/tools/codestable_common.py:562-576,621-675` | 已存在 pre-2026-07-17、已归档 Task、`subagent+ocr` 的受限 legacy 兼容逻辑，但尚未覆盖历史异名 review 或其它可验证独立审查证据。 |

## 2. 失败路径还原

**正常路径**：完成中的当前单元产生 `{slug}-review.md`，由独立 Task agent 以 `reviewer: subagent` 写入完整当前 metadata；doctor 将其认定为 canonical evidence 并通过。

**失败路径**：历史已完成单元进入 doctor 枚举后，`review_file_for()` 只查找当前文件名；异名的 `{slug}-code-review.md` 因此直接被认定为缺失。即使文件名符合当前规则，历史 `self`、`subagent+ocr` 或缺失的 reviewer metadata 也无法通过当前 canonical 判定，最终被统一提升为 P1。

**分叉点**：`plugins/codestable/skills/cs-onboard/tools/codestable_common.py:301-306` 与 `:658-680` — 当前契约被无差别应用于历史归档产物，且没有基于原始独立审查事实的完整历史分类。

## 3. 根因

**根因类型**：逻辑错误。

**根因描述**：doctor 将“当前 canonical evidence 是否完整”错误等同于“历史单元是否经过可验证独立审查”。现有例外仅处理 pre-cutoff 归档的 `subagent+ocr`，未处理早期 Issue 的异名 review 文件，也不能在不篡改 `reviewer` 原始值的情况下区分“历史上真实执行过独立审查”与“只做了 self review 或 review 根本不存在”。

**是否有多个根因**：是。

1. 历史 Issue 的 review 文件命名与当前 canonical 文件名不兼容。
2. 历史 review metadata 不具备当前 schema，但其中一部分正文保留了可验证的独立审查事实。
3. 另有 11 个单元确实没有可验证的独立审查，不能靠兼容判定消解。
4. **修订发现**：25 个 P1 中仅 10 个单元拥有有效 archived Task，另外 15 个单元在引入严格 Task spine 前未形成 archived Task；原方案将 archived Task 作为全部历史兼容证据的前提，无法覆盖这些真实历史记录。

## 4. 影响面

- **影响范围**：当前 25 个历史 Feature、Issue 与 Refactor 单元；任意后续运行 `codestable-doctor.py` 的工作流都会被 P1 阻塞。
- **潜在受害模块**：`cs-feat`、`cs-issue`、`cs-refactor`、`cs-task` 的完成/归档前健康检查，以及 release 前 runtime 验证。
- **数据完整性风险**：无业务数据风险；但若直接改写历史 `reviewer` 或复制 review 文件，会损坏审查溯源与治理可信度。
- **严重程度复核**：维持 **P1**。问题不影响运行时业务功能，但会系统性阻塞 CodeStable 的可信 workflow completion。

### 方案修订说明

先前确认的方案 A 假定 14 个已有独立审查事实的单元均具有有效 archived Task。源码和仓库事实核验后，该前提不成立：仅 10 个 P1 单元满足 archived Task 条件，15 个历史单元没有 archived Task。因此，必须在开始实现前重新确认历史兼容锚点；不能静默扩大原定例外。

## 5. 修复方案

### 方案 A（修订版）：pre-cutoff 历史证据分类 + 12 个单元补做 focused review（推荐）

- **做什么**：
  1. 将 legacy 资格固定为：unit 日期早于 2026-07-17、没有同 slug active Task、review frontmatter 的 `status: passed`、正确的 unit identity、且 `reviewer` 明确为 `subagent` 或 `subagent+ocr`。
  2. 对 legacy Issue 增加只读候选 `{slug}-code-review.md`；不重命名、复制或修改原文件。
  3. 保留原始 `reviewer` 值。该规则能安全识别 13 个已有明确 agent reviewer 声明的历史单元；没有 reviewer 字段的 1 个单元与原本 self / blocked / 无 review 的 11 个单元，合计 12 个，逐个执行真正的独立 focused review。
  4. 为候选解析、cutoff、无 active Task、frontmatter identity、拒绝 self review 及 post-cutoff 失败路径增加自动化回归测试。
- **优点**：不补造 archived Task 或篡改历史 metadata，且 legacy 例外只接受明确的 agent reviewer 声明。
- **缺点 / 风险**：相比原方案增加 1 个 focused review；历史单元日期成为兼容边界的一部分，必须在测试中锁死 cutoff。
- **影响面**：`codestable_common.py`、相关 pytest、12 个历史单元的新 canonical review 文件、当前 Issue 产物与 Task。

### 方案 B：回填 15 个历史 archived Task，再沿用原 archived-only 例外

 - **做什么**：为缺少 archived Task 的 15 个历史单元追补 Task 生命周期记录，再保留以 archived Task 为唯一 legacy 锚点的当前实现。
 - **优点**：历史兼容规则形式更统一。
 - **缺点 / 风险**：会在没有当时 tombstone 与原始 active Task 的前提下补造生命周期证据；即使不改 reviewer，也会降低 Task 归档记录的历史可信度。不推荐。
 - **影响面**：15 个 Task archive/tombstone 记录，且需要处理新 runtime 对归档状态机的严格要求。

### 方案 C：无条件跳过 pre-cutoff 单元

- **做什么**：doctor 对所有早于 cutoff 的 archived unit 不再校验 review。
- **优点**：改动极小，立即消除全部 25 个 P1。
- **缺点 / 风险**：会将无 review、self review、blocked review 一并静默放行，彻底削弱 health gate；不应采用。
- **影响面**：所有历史 CodeStable 单元，诊断能力显著降低。

### 推荐方案

**推荐修订版方案 A**。它以严格的日期、无 active Task、frontmatter identity 与明确 agent reviewer 声明共同构成历史兼容边界，安全处理 13 个已有独立审查事实的单元；另外 12 个单元通过真正的独立 focused review 形成当前 canonical evidence。该方案不补造 archived Task，也不重写历史事实，并让未来新单元继续执行严格 fail-closed gate。

### Owner 已选方案

Owner 于 2026-07-17 选择**方案 B**：为 15 个缺少 archived Task 的历史单元回填 Task 生命周期记录，再继续使用 archived-only 兼容边界。实施时必须通过 Task runtime 创建 `completed` 正本后原子归档；回填记录须明确标注为历史恢复，不能声称重建了当时不存在的 tombstone 或 reviewer 事实。
