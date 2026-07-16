---
doc_type: feature-implementation
feature: 2026-07-16-cursor-plugin-v104-hardening
status: accepted
updated: 2026-07-17
---

# cursor-plugin-v104-hardening 实现记录

## 结果

功能实现与 implementation 验证已完成。Checklist 全部 6 个 implementation steps 均达到退出
信号。原 Step 7 属于 code review 之后的 acceptance 回写；owner 已批准把它从 implementation
steps 移除，其合同继续由 C13、DoD 和 requirement delta 应用条件约束，不提前伪造验收完成。

## 基线

- clean detached `HEAD`：package checker 通过，正式 tests 为 `606 passed / 1 skipped`，runtime
  `status=ok`。
- 当前工作区：runtime 唯一 drift 为
  `.codestable/reference/workflow-conventions.md`；根 `cs-onboard/` 和 plugin cache 会阻断直接
  package check，按 approved design 使用 Git-aware isolated candidate 取证。
- Cursor identity 变异基线：marketplace entry name 与 plugin manifest name 的破坏均未产生
  finding。
- dirty scope：本 feature 实现文件与 feature artifacts；其他 `.codestable/` untracked
  audits/features/issues/tasks/tools 是既有 baseline，不属于本轮改动。

## Step 1：Cursor 分发合同

- 退出信号：合法 manifests 通过；identity、source 和 manifest 破坏返回精确 `Finding`。
- RED：design 前置 mutation audit 已证明 marketplace entry name 和 plugin manifest name 破坏
  均返回空 findings。
- GREEN：新增 `check_cursor_distribution_contract`，验证 marketplace name/entry/owner、source
  常量与仓库内解析、plugin manifest presence、双向 identity、skills path；继续由统一
  `Finding` 输出。
- VERIFY：package/release 定向测试 `37 passed`；isolated candidate findings 为 `[]`。
- 影响面：`tools/check-plugin-package.py`。
- 清洁度：离线确定性运行；未引入 schema 下载、第二套 validator、调试输出或临时 TODO。

## Step 2：负向回归与版本合同

- 退出信号：Cursor 审计变异场景 fail-closed，原 Codex/Claude/skills-only 合同继续通过。
- TDD evidence：新增 entry identity、plugin identity、identity mismatch、source missing、manifest
  missing、Cursor version、README Cursor 入口及 agents/hooks 反向用例；baseline mutation 结果作为
  RED 证据，最小 checker 实现后全部 GREEN。
- VERIFY：`tests/test_plugin_package.py` 与 `tests/test_cs_skill_release.py` 共 `37 passed`；版本 bump
  fixture 继续断言 Cursor plugin version 更新为 `1.1.0`。
- 影响面：`tests/test_plugin_package.py`；既有 release fixture 无需修改。
- 清洁度：无低价值 schema 镜像测试；每个失败场景均观察公开 finding/error contract。

## Step 3：Cursor 安装与升级入口

- 退出信号：中英文 README 均含当前官方 Cursor 安装/升级入口，文档守卫可检测回退。
- TDD exception：外部 Cursor Dashboard/Customize UI 无本地自动化环境；使用官方 Markdown 事实核验
  加静态 package guard。
- 官方证据（2026-07-16）：`https://cursor.com/docs/plugins.md` 明确列出
  `Dashboard -> Plugins`、`Import from Repo`、`Customize`、`Enable Auto Refresh` 与手动
  `Refresh`；Auto Refresh 依赖 Cursor GitHub App，重新索引最多每 10 分钟一次。
- GREEN：README 双语新增 Team Marketplace 导入、开发者安装、自动/手动刷新说明，并明确不代表
  已发布到公开 marketplace。
- VERIFY：package checker 要求官方文档 URL 与关键 UI token；缺失入口的双语负向测试通过。
- 影响面：`README.md`、`README.en.md`、README guard。
- 清洁度：两种语言同步，无不存在的 Cursor CLI 命令或 agents/MCP 宣称。

## Step 4：v1.0.4 runtime 安全清理

- 退出信号：clean tracked/untracked target-only 可删除；staged/modified/source-backed dirty
  继续阻塞；legacy/history 保留；二次 check 为 `ok`。
- RED：现有 broad dirty guard 会把 untracked target-only stale reference 判为
  `managed-paths-dirty`；clean tracked target-only 的既有迁移测试必须保持绿色。
- GREEN：`git_dirty_managed_paths` 使用 porcelain status 与 `--untracked-files=all`，只豁免状态
  为 `??` 且被 runtime 模板判定为 target-only 的精确路径；其他状态继续返回 dirty。
- VERIFY：runtime tests `27 passed`；focused runtime/entry tests `60 passed`。新增测试覆盖
  untracked 删除、staged target-only 阻塞、modified tracked target-only 阻塞、source-backed
  dirty 阻塞。
- 真实同步：无 `--force` 执行成功，只移除
  `.codestable/reference/workflow-conventions.md`；同步结果与二次 check 均为 `status=ok`、
  `drifted_paths=[]`。
- 保护证据：`.codestable/tools/`、tasks、issues、features、audits 的 scoped status 在同步前后逐项
  一致；managed runtime 同步后无额外 dirty path。
- 影响面：`codestable_runtime.py`、`tests/test_codestable_doctor.py`、当前项目 stale reference。
- 清洁度：未使用 `--force`，未删除 legacy/history，未改 `.codestable/tools/`。

## Step 5：Requirement delta

- 退出信号：delta 仅扩展 Cursor 用户故事/解决方案，不重写历史。
- 证据：owner 已同时批准 design 与 requirement delta；delta `status=approved`，应用条件仍要求
  implementation、code review、QA/acceptance 全部通过后才机械回写 requirement。
- 影响面：`cursor-plugin-v104-hardening-req-delta.md`。
- 清洁度：尚未提前修改 canonical requirement 的实现记录。

## Step 6：集成验证

- Git-aware isolated candidate：初始化最小 Git repository、叠加 scoped binary diff 后，package
  checker 返回 `ok=true, findings=[]`，runtime check 返回 `status=ok`。
- 定向 package/release：`37 passed`。
- 正式全量：`617 passed, 1 skipped`。
- runtime 聚焦：`60 passed`。
- 当前工作区 runtime：`status=ok`，plugin/runtime version 均为 `1.0.4`，无 drift/missing。
- `git diff --check`：通过。
- `VERSION`：无修改；未 commit、未发布 marketplace。

## 交付物与场景索引

- Cursor contract：`tools/check-plugin-package.py`，覆盖 C1-C6。
- package/runtime regression：`tests/test_plugin_package.py`、
  `tests/test_codestable_doctor.py` 与既有 release fixture，覆盖 C2-C10。
- 双语安装/升级入口：`README.md`、`README.en.md`，覆盖 C8。
- runtime 实例迁移：删除 stale target-only reference，保留 legacy/history，覆盖 C9-C11。
- isolated/workspace 验证输出：覆盖 C12。
- approved requirement delta：覆盖 C13 的实现前授权；canonical requirement 回写仍待 acceptance。

## Final Audit

- 已逐条复核 design C1-C13；除 acceptance-only canonical requirement 回写外均已有实现证据。
- 新增代码无调试输出、临时 TODO/FIXME、注释掉代码或无用 import。
- 未恢复 `cs-task`、旧 workflow 状态机、agents/MCP/hooks 或固定 reviewer model。
- 未修改 `VERSION`、未 commit、未发布 marketplace。
- 生命周期修正：owner 已批准把 acceptance-only 回写从 implementation steps 移除；canonical
  requirement 仍只能在 review/acceptance 通过后机械应用。
- 状态：implementation inputs 已完整，可进入 code review gate。
