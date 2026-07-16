---
doc_type: feature-acceptance
feature: 2026-06-28-sync-upstream-code-review
status: passed
accepted_at: 2026-06-28
summary: upstream-first rebase 已完成，cs-code-review 保持 upstream 原生，本地扩展收敛为 overlay patch
tags: [codestable, code-review, upstream-sync]
---

# sync-upstream-code-review 验收报告

## 1. 接口契约核对

- `cs-code-review/`：`git diff --quiet upstream/main -- "cs-code-review"` 通过，输出 `cs-code-review matches upstream`。
- `browser-bridge/`：`HEAD` 与 `upstream/main` 文件数均为 15，确认本地旧删除未进入最终主体。
- `cs-task`：作为本地 overlay 能力保留，协议集中在 `cs-task/SKILL.md`、`cs-task/reference.md` 与各入口/收尾 skill 的 Task 接入段。

## 2. 行为与决策核对

- upstream-first：当前 `HEAD` 等于 `upstream/main`，本地扩展以工作区 overlay diff 存在，提交栈不再夹带跑偏删除。
- 冲突处理：旧技能删除冲突按 upstream 处理；旧 `cs-code-review/reference.md` 未保留为最终主体。
- overlay patch：已生成 `/tmp/codestable-local-overlay.patch`，共 1094 行，可作为本地扩展重放证据。
- 长期策略：以后同步按 `upstream/main + overlay patch stack` 维护，不维护平行大 fork。

## 3. 验收场景核对

- S1：`cs-code-review/` 目录与 upstream 一致，通过。
- S2：rebase 后跑偏项已识别并清理；当前提交栈无 browser-bridge 删除与旧 review reference，工作区 overlay 不触碰 `cs-code-review/`。
- S3：feature acceptance / fastforward / issue / refactor 的流程文档包含进入 `cs-code-review` 与 Task 回填/归档语义。
- S4：自定义自动化流程已落在 `cs-task` 与入口/收尾 skill 的 Task 接入段。
- S5：`cs-onboard/reference/shared-conventions.md` 与 `cs-onboard/reference/system-overview.md` 已同步新项目模板。
- S6：`git diff --check upstream/main -- .` 通过，无 whitespace 错误。
- S7：`python3 .codestable/tools/validate-yaml.py --file ... --yaml-only` 通过。

## 4. 术语一致性

- `cs-code-review`：作为 upstream 原生最终质量门禁使用。
- `cs-task` / `Task List`：作为本地 overlay 的任务运行账本使用。
- `overlay patch stack`：定义为本地扩展重放机制，不替代 upstream 主体。

## 5. 架构归并

- 本次变更确认 CodeStable 维护策略：upstream 为主体，本地能力以 overlay 维护。
- 需要后续在 architecture 中归并的稳定约束：`cs-code-review` 为 upstream 原生质量门禁，`cs-task` 为本地 overlay 任务账本。
- 当前 feature 不直接更新架构中心文档；后续可通过 `cs-arch` 或 `cs-docs-neat` 做体系文档整理。

## 6. requirement 回写

- 本次为维护性迁移，不新增独立用户能力，`requirement: null`，无需 requirement 回写。

## 7. roadmap 回写

- 本 feature 非 roadmap 起头，`roadmap: null` / `roadmap_item: null`，无需 roadmap 回写。

## 8. attention.md 候选盘点

- 候选：同步 upstream 时采用 `upstream/main + overlay patch stack`；冲突默认保留 upstream，再重放 `cs-task` 与自动化流程 overlay。
- 是否写入 attention.md：本报告仅登记，是否追加为常驻提示交由后续 `cs-note` 决定。

## 9. 遗留

- overlay 目前仍是工作区 diff，尚未作为最终 scoped commit 固化；需先进入 `cs-code-review` 做最终质量门禁。
- README / `cs-feat-impl/SKILL.md` 超过 300 行是 upstream 主体既有状态，本次不拆 upstream 主体。
