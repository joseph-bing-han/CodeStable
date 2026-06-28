---
doc_type: issue-fix
issue: 2026-07-11-task-archive-runtime-guard-regression
status: completed
fixed: 2026-07-11
path: standard
tags:
  - cs-task
  - archive
  - runtime-guard
  - concurrency
---

# Task 归档后 active 文件重现回归 Fix Note

## 1. 已确认根因

历史修复只在 `cs-task` Markdown 协议中声明 active 源路径失效，并通过字符串契约测试防止规则丢失。真实归档仍由多个独立工具调用拼接，没有 tombstone、active 写入守卫或文件系统行为测试，因此 interrupted 延迟写入或旧 buffer 保存仍能在 `mv` 后重新创建 active 文件。

## 2. 修复内容

- 新增 `plugins/codestable/skills/cs-onboard/tools/codestable-task-runtime.py`，提供 `write-active`、`archive`、`cleanup` 和 `scan` 四个受控入口。
- create / update / complete / backfill 的 active 写入统一通过 `write-active`，校验 Task frontmatter、slug、状态，并在 archived 正本或 `archiving` / `archived` tombstone 存在时拒绝写入。
- archive 先记录归档前 SHA-256 和 `archiving` tombstone，再原子移动 active 文件、更新 archived 正本、完成 tombstone，并执行稳定性窗口复验。
- cleanup 对归档后重现的 active 文件进行内容判定：与归档前快照一致则安全删除；内容分叉返回 `divergent-active-residue` 并阻塞，禁止静默覆盖。
- legacy 项目即使没有 tombstone，只要已有同 slug archived 正本，`write-active` 仍会拒绝重建；scan 会把 active/archived 冲突报告为 `legacy-archive-without-tombstone`。
- 更新 `cs-task` skill、reference、onboard 共享目录结构和工具参考，使相关技能表述统一切换到 runtime 模式。
- 更新插件打包检查，确保 Task runtime 属于必须分发资产；同步当前项目骨架与本地安装副本。

## 3. 测试与验证

- 新增 `tests/test_task_runtime.py`，覆盖：tombstone 写入拒绝、legacy archived 写入拒绝、正常归档、同源 stale rewrite 清理、分叉阻塞、非法状态拒绝和目标冲突拒绝。
- 更新 `tests/test_plugin_package.py`，验证 Task runtime 缺失时打包检查失败。
- 更新 `tests/test_workflow_contracts.py`，从旧 `mv` 字符串约束切换为 runtime、tombstone 和分叉阻塞契约。
- `uvx pytest -q tests/test_task_runtime.py tests/test_plugin_package.py tests/test_workflow_contracts.py`：32 passed。
- `uvx pytest -q`：71 passed。
- Review-fix 故障注入测试：archived 内容写入失败和 completed tombstone 写入失败时，runtime 均恢复原始 active 内容并清除未完成 archived/tombstone；archived 正本哈希异常时保留 active 并阻塞 cleanup。
- IDE lint：无诊断。
- `python3 tools/check-plugin-package.py --root .`：Task runtime 资产检查通过；全量命令仍被既有根目录 `cs-onboard` 残留、历史 `__pycache__` 和 `README.en.md` 命令缺失阻塞，这些问题在本次修复前已记录，不属于本次范围。

## 4. 影响范围与剩余边界

- 影响 CodeStable Task create / update / complete / backfill / archive / cleanup 的执行协议和分发资产。
- runtime 能保护所有经过 CodeStable 入口的写入，并检测通用编辑工具绕过 runtime 后留下的残留。
- 操作系统无法禁止外部编辑器在 runtime 退出后直接写文件，因此最终 cleanup 与当前文件系统复验仍是归档成功硬条件。
- legacy archived Task 没有归档前 SHA-256 时，runtime 不会猜测并删除分叉 active 文件，只会阻塞并要求人工处理。

## 5. 顺手发现

- 插件全量打包检查存在既有失败项：根目录 `cs-onboard` 残留、插件工具目录历史 `__pycache__`、`README.en.md` 安装命令不完整。本次不顺手修改，避免扩大 Issue 范围。

## 6. 后续 gate

修复和自动化验证已完成；下一步进入 `cs-code-review` 独立审查。review 通过后，通过新 Task runtime 完成本 Issue Task 的归档并验证 tombstone 生效。
