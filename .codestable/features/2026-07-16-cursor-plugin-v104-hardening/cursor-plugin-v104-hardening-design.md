---
doc_type: feature-design
feature: 2026-07-16-cursor-plugin-v104-hardening
requirement: plugin-market-distribution
roadmap: null
roadmap_item: null
execution_lane: standard
status: approved
summary: 加固 Cursor 插件分发合同并清理 v1.0.4 stale runtime reference
tags: [cursor, plugin, distribution, runtime, validation]
---

# cursor-plugin-v104-hardening design

## 0. 术语约定

- **Cursor marketplace manifest**：仓库根 `.cursor-plugin/marketplace.json`，负责把 `codestable` 名称映射到 `plugins/codestable` 插件实体。
- **Cursor plugin manifest**：`plugins/codestable/.cursor-plugin/plugin.json`，声明插件身份、版本和 `skills` 组件路径。
- **身份一致性**：marketplace entry `name` 与 plugin manifest `name` 必须同为 `codestable`；只验证任一侧不算通过。
- **仓库分发校验器**：`tools/check-plugin-package.py`。它是 CodeStable 跨 Codex、Claude、Cursor、skills CLI 的发布门禁，不是通用 Cursor schema validator。
- **managed runtime asset**：由 `cs-onboard` 模板同步到项目 `.codestable/gates/`、`.codestable/reference/`、`.codestable/.gitignore` 和 runtime manifest 的受管资产。
- **legacy compatibility asset**：`.codestable/tools/` 和旧 worktree/branch artifacts。它们不是 v1.0.4 新版入口，本 feature 不默认删除或覆盖。
- **stale target-only reference**：项目 runtime 中存在、但当前 `cs-onboard/references/` 模板已不存在的受管 reference；本次实例是 `.codestable/reference/workflow-conventions.md`。

## 1. 决策与约束

### 需求摘要

- 做什么：补齐 Cursor 分发合同的身份和路径校验、负向测试、安装文档，并把当前项目 runtime 同步到 v1.0.4 健康状态。
- 为谁做：维护 CodeStable 发布资产的开发者，以及通过 Cursor marketplace 安装 CodeStable 的用户。
- 成功标准：官方 Cursor validator 会拒绝的 name/source 破坏在本地 checker 中同样失败；中英文 README 有可执行的 Cursor 安装/升级入口；叠加 scoped diff 的 Git-aware 隔离候选通过 package checker/runtime health，当前工作区通过正式 tests/runtime health/`git diff --check`。主工作区既有根 skill/cache 污染不属于本 feature。
- 明确不做：不恢复 `cs-task`、固定模型 reviewer、旧自动编排或第二套 runtime 状态机；不实现通用 Cursor 插件 schema 引擎；不引入在线 schema 下载作为发布门禁；不自动删除 `.codestable/tools/`、历史 tasks/issues/features/audits；不在本 feature 中 bump 版本、commit 或发布 marketplace。

### 复杂度档位

- Compatibility = cross-host：同一插件实体继续服务 Codex、Claude、Cursor 和 skills CLI。
- Public surface = stable：manifest identity、README 安装命令和 package checker 都属于发布接口。
- Validation = tested：必须有正向、负向和真实 runtime health 证据。
- 其余走工具链维护默认档位，无数据库、外部业务 API、权限和并发语义。

### 关键决策

1. **扩展现有 requirement，不新建平行分发能力**：本 feature 继续归属 `plugin-market-distribution`；先形成 owner-approved requirement delta，把跨宿主故事从 Codex/Claude 扩展到 Cursor，再在验收时追加实现记录。
2. **仓库校验器保持跨宿主总入口**：不删除 `check-plugin-package.py`，只补 CodeStable 当前 Cursor manifest 的关键不变量。
3. **离线、确定性校验**：checker 不在运行时下载 Cursor schema；校验当前仓库需要的 name、source、路径可达、版本和 skills-only 合同。
4. **身份必须双向一致**：同时验证 marketplace entry name、plugin name 及两者相等，不能靠两个独立常量检查代替一致性检查。
5. **安装文档是功能挂载点**：manifest 存在但 README 无 Cursor 入口视为交付不完整；中英文必须同步。
6. **runtime 清理由官方同步器执行**：保留 clean tracked target-only stale asset 的既有安全清理能力，并修正同步器对 untracked target-only stale asset 的分类，使这两类 package-owned stale asset 均可无 `--force` 删除；staged/modified target-only、source-backed dirty asset 和其他 managed dirty 继续阻断。
7. **legacy 与 stale managed asset 分开处理**：只移除 runtime-sync 报告的 stale managed reference；`.codestable/tools/` 和历史产物保持原状。
8. **clean candidate 用 Git-aware 隔离快照验证**：从 `HEAD` 构造临时副本并叠加本 feature scoped diff，排除主工作区既有 untracked 根 skill/cache；快照内初始化最小 Git repository，使 checker 的 `git check-ignore --no-index` 合同真实生效；不得用未包含候选 diff 的 detached `HEAD` 冒充实现验证。

### 基线风险

- `tools/check-plugin-package.py` 当前对 marketplace entry name 和 plugin name 的变异均返回空 findings，存在假阳性。
- clean detached `HEAD` 已通过 package checker、`606 passed / 1 skipped` 和 v1.0.4 runtime health。
- 当前主工作区因 `.codestable/reference/workflow-conventions.md` 返回 `runtime-drift`。
- 该 stale reference 本身是 untracked managed path，现有 `git_dirty_managed_paths` 会先触发 `managed-paths-dirty`，因此当前同步器无法按原计划无 `--force` 自愈。
- 主工作区已有根 `cs-onboard/` 和 plugin `__pycache__`，直接 package check 会被既有本地污染阻断；候选 package 证据必须来自隔离快照。
- 当前 README 只列 Codex、Claude 和 skills CLI，没有 Cursor 安装/升级入口。

### Top 3 风险与缓解

1. **校验器只补常量、不补关系**：增加 name mismatch 变异测试，要求 entry/plugin 各自正确且相等。
2. **放宽 dirty guard 后覆盖用户修改**：仅新增 untracked target-only 例外，并保留 clean tracked target-only 的既有清理合同；staged/modified target-only、source-backed dirty asset 和其他 managed dirty 继续 `managed-paths-dirty`。
3. **隔离验证漏掉候选 diff、Git ignore 语义或文档写出未经验证的 Cursor 操作**：快照必须叠加 scoped diff 并初始化最小 Git repository；安装说明必须对照当前官方文档并记录真实可观察证据。

### 非显然依赖与关键假设

- 假设 Cursor marketplace 继续以仓库根为 source 相对路径基准；官方 validator 已验证这一点。
- 假设 `displayName`、`skills` 和当前 metadata 字段继续符合 Cursor 官方 schema；实现前用当前 schema 再核一次。
- runtime sync 依赖 dirty 分类可证明安全；clean tracked target-only 不属于 dirty，继续按既有合同删除；managed dirty 中只有精确的 untracked target-only stale asset 可作为新增例外，其余 staged/modified target-only、source-backed dirty asset 和其他 managed dirty 必须阻塞。
- 当前 attention 中的 Paseo reviewer 配置属于项目 gate，若不可用则 design-review 阶段停下，不静默自审放行。

## 2. 名词与编排

### 2.1 名词层

#### 现状

- `check_catalog_contracts` 逐字段比较部分 Codex、Claude、Cursor 值，但未验证 Cursor 两个 name 字段及其关系。
- `check_manifest_versions` 已把 Cursor plugin version 纳入根 `VERSION` 对齐。
- Cursor manifests 当前结构和字段符合官方 schema，实际 name/source/version 也正确。
- runtime health 已能识别 target-only reference，并由 `sync_runtime` 的 `remove_target_only_runtime_assets` 清理。
- 但 `sync_runtime` 当前先执行 broad managed dirty guard，导致 untracked target-only stale asset 也无法进入安全清理分支。

#### 变化

- 新增 **CursorDistributionContract** 逻辑边界：marketplace identity、entry identity、plugin identity、source resolution、manifest presence、skills path 和 version alignment。
- `Finding` 继续作为统一失败输出；Cursor 合同失败必须指向具体 manifest 和字段路径。
- 测试 fixture 扩展为能独立变异 marketplace/plugin identity、source 和未知/缺失字段。
- runtime dirty 分类增加“clean tracked/untracked target-only 安全 stale cleanup”与“staged/modified target-only 或 source-backed managed modification”边界，并补对应测试。
- 新增 owner-approved requirement delta，把 Cursor 纳入用户故事和分发宿主范围；第一版历史不重写。

#### 接口示例

```text
输入：marketplace plugins[0].name = "wrong-plugin"，plugin.json name = "codestable"
输出：check_repo 返回非空 Finding，明确报告 marketplace/plugin identity mismatch
```

```text
输入：plugins[0].source 指向不存在目录或目录内缺 .cursor-plugin/plugin.json
输出：check_repo 返回非空 Finding，指出 source 或 manifest 不可达
```

```text
输入：当前合法 Cursor manifests + VERSION=1.0.4
输出：Cursor contract 无 findings，整体 package check 可继续通过
```

### 2.2 编排层

本 feature 是线性加固流程，无复杂并行状态机：先固定 contract，再补负向证据，再接文档，最后同步 runtime 并做双环境验收。

#### 现状

1. package checker 读取各宿主 manifests。
2. tests 证明部分字段和版本合同。
3. README 暴露 Codex/Claude/skills CLI 入口。
4. runtime-sync 在 clean clone 正常，在当前工作区报告 stale reference。

#### 变化

1. checker 先解析 Cursor marketplace 与 plugin manifests，验证当前仓库合同和两者关系。
2. 负向测试逐个破坏 name/source/manifest/version，证明 checker fail-closed。
3. README/README.en 增加 Cursor 安装与升级说明，并由 checker 或测试检查关键入口不丢失。
4. 加固 runtime dirty 分类，再对当前项目执行 check → sync（无 force）→ check，记录 removed paths 和最终 health。
5. 从 `HEAD` 创建 Git-aware 隔离副本并叠加 scoped candidate diff：隔离候选运行 package checker 和 runtime health；当前工作区运行正式 tests、runtime health 和 diff cleanliness。主工作区既有根 skill/cache 污染不纳入本 feature，也不要求其直接 package check 通过。

#### 流程级约束

- 错误语义：manifest 解析失败、source 不可达、identity mismatch、version mismatch 都返回非零，不抛裸 traceback。
- 幂等性：合法 package 重复检查结果一致；runtime 已同步后再次 check 为 `status: ok` 且无额外删除。
- 顺序约束：先完成 checker/test，再改 README，最后执行当前项目 runtime sync。
- 可观测点：findings JSON、pytest 输出、README diff、runtime `removed_paths`、两次 health JSON、`git diff --check`。

### 2.3 挂载点清单

- Cursor marketplace：`.cursor-plugin/marketplace.json` — 合同被 checker 完整验证，不改变当前合法值。
- Cursor plugin manifest：`plugins/codestable/.cursor-plugin/plugin.json` — 身份、版本和 skills path 被 checker 完整验证。
- 发布门禁：`tools/check-plugin-package.py` — 增加 Cursor identity/source 关系检查。
- 安装入口：`README.md` / `README.en.md` — 增加 Cursor 安装与升级说明。
- Runtime 同步器：`plugins/codestable/skills/cs-onboard/tools/codestable_runtime.py` — 保留 clean tracked target-only 的既有清理能力，并区分新增可安全删除的 untracked target-only asset 与必须阻塞的 managed modification。
- 项目 runtime：`.codestable/reference/` + `.codestable/runtime-manifest.json` — 通过 v1.0.4 runtime sync 清除 stale managed reference。
- 能力愿景：requirement delta + `.codestable/requirements/plugin-market-distribution.md` — owner 批准后扩展 Cursor 宿主范围，验收时追加实现记录。

### 2.4 推进策略

1. 分发合同骨架：定义 Cursor identity/source/path 不变量并接入统一 findings。
   退出信号：合法 manifests 通过，任一 identity/source 破坏返回精确 Finding。
2. 防回归证据：补齐 Cursor 负向测试和版本发布测试。
   退出信号：目标变异场景全部 fail-closed，原 package 测试继续通过。
3. 用户入口：补齐中英文 Cursor 安装/升级说明及文档守卫。
   退出信号：两份 README 均包含经官方事实核验的 Cursor 入口，checker/test 能发现文档回退。
4. runtime 安全清理：加固 dirty 分类并无 `--force` 同步当前项目 managed runtime。
   退出信号：clean tracked 与 untracked target-only stale asset 均可删除；staged/modified target-only、source-backed dirty asset 和其他 managed dirty 仍阻塞；legacy/history 未变化，二次 check 为 `ok`。
5. Requirement delta：持久化 Cursor 宿主范围扩展并取得 owner approval。
   退出信号：delta 只扩展 Cursor 用户故事/解决方案，不重写既有实现历史和边界。
6. 集成验收：分别验证叠加 scoped diff 的 Git-aware 隔离候选和当前工作区。
   退出信号：隔离候选的 package checker/runtime health 通过；当前工作区的正式 tests、runtime health 和 diff check 通过。

### 2.5 结构健康度与微重构

##### 评估

- 文件级 — `tools/check-plugin-package.py`：约 300 行，职责是仓库级跨宿主发布校验；新增 Cursor 关系检查仍属于同一职责，但应抽出小函数避免 `check_catalog_contracts` 继续膨胀。
- 文件级 — `tests/test_plugin_package.py`：fixture 与多宿主负向测试集中，职责一致；本次按 Cursor 场景分组，不拆测试模块。
- 文件级 — `codestable_runtime.py`：runtime health/sync 集中在同一模块；本次只收紧 dirty 分类和 stale cleanup 顺序，不拆模块。
- 文件级 — `README.md` / `README.en.md`：只改安装/升级段，不做全文重组。
- 目录级 — `tools/` 和 `tests/`：本次不新增多个同类文件，不触发目录重组。
- Compound — 命中的旧 reviewer/runtime mapping 已过时，不作为新 contract；canonical skill 路径约定继续遵守。

##### 结论：不做结构微重构

保持现有总 checker；仅在文件内抽取 Cursor 专用校验函数。它是职责内整理，不改变对外行为，不单独设迁移步骤。

##### 超出范围的观察

- 如未来要完整镜像 Cursor 官方 JSON schema，应单独设计 schema vendoring/更新策略；本 feature 不引入远程依赖或第二套通用 validator。
- `.codestable/tools/` legacy 文件是否最终删除需独立 owner 决策，本 feature 不处理。

## 3. 验收契约

### 3.1 关键场景清单

- C1 正常：当前 Cursor marketplace/plugin manifests → package checker 通过且名称一致。
- C2 错误：marketplace entry name 错误 → checker 非零并报告具体字段。
- C3 错误：plugin manifest name 错误 → checker 非零并报告具体字段。
- C4 错误：两侧 name 均合法但不相等 → checker 非零并报告 identity mismatch。
- C5 错误：source 不存在或缺 plugin manifest → checker 非零并报告不可达路径。
- C6 错误：Cursor plugin version 偏离 `VERSION` → checker 非零。
- C7 正常：版本 bump fixture → Cursor plugin version 与其他宿主一起更新。
- C8 文档：中文和英文 README 均能找到 Cursor 安装与升级入口，且不宣称注册 agents/MCP。
- C9 runtime：仅存在 clean tracked 或 untracked target-only stale reference 时，无 `--force` sync 精确删除它，二次 check 为 `ok`。
- C10 guard：任一 staged/modified target-only、source-backed dirty asset 或其他 managed dirty 仍返回 `managed-paths-dirty`，内容不被覆盖。
- C11 兼容：`.codestable/tools/`、tasks、issues、features、audits 在 runtime sync 前后保持不变。
- C12 集成：叠加本 feature scoped diff 的 Git-aware 隔离候选通过 package checker 与 runtime check；主工作区通过正式 tests、runtime check 和 `git diff --check`。主工作区既有根 skill/cache 污染不作为本 feature package 失败，也不在本 feature 中清理。
- C13 requirement：owner-approved delta 将 Cursor 纳入分发用户故事，既有边界和第一版实现记录保持不变。

### 3.2 明确不做的反向核对项

- plugin manifest 不应新增 `agents`、`mcpServers`、hooks 或固定 reviewer model。
- skills/workflow 文档不应重新出现 `cs-task` 强制主线或旧 `workflow-conventions.md` 引用。
- runtime 同步命令不应包含 `--force`。
- diff 不应删除 `.codestable/tools/`、历史 tasks/issues/features/audits。
- 发布流程不应依赖在线下载 Cursor schema。
- 本 feature 不应修改 `VERSION` 或新增发布 commit。

### 3.3 Acceptance Coverage Matrix

| Scenario | Covered By Step | Evidence Type | Command / Action | Core? |
|---|---|---|---|---|
| C1-C6 Cursor contract | S1-S2 | pytest + findings JSON | `pytest tests/test_plugin_package.py` | yes |
| C7 version bump | S2 | pytest | `pytest tests/test_cs_skill_release.py` | yes |
| C8 install docs | S3 | diff + test | README 双语检查 | yes |
| C9-C10 runtime safety | S4 | pytest + command JSON | runtime tests + check/sync/check | yes |
| C11 legacy preservation | S4 | filesystem/status diff | 同步前后路径清单核对 | yes |
| C12 integrated result | S6 | command output | Git-aware isolated candidate package/runtime + workspace tests/runtime/diff | yes |
| C13 requirement delta | S5 | owner approval + diff | req delta review | yes |

### 3.4 DoD Contract

| ID | 要求 | 证据 | 阻塞级别 |
|---|---|---|---|
| DOD-DESIGN-001 | design/checklist 完整且通过独立或 owner-approved local design review | design-review report + approval ref | blocking |
| DOD-IMPL-001 | checklist steps 全部完成并有逐步证据 | checklist + implementation report | blocking |
| DOD-REVIEW-001 | code review passed，无 unresolved blocking | review report | blocking |
| DOD-QA-001 | 隔离候选 package/runtime 与主工作区完整回归通过 | QA report + command output | blocking |
| DOD-ACCEPT-001 | runtime health 为 ok，requirement 实现记录已回写 | acceptance report | blocking |

Validation Commands：

| ID | 命令 | 目的 | 核心性 | 失败处理 |
|---|---|---|---|---|
| CMD-001 | `tmp=$(mktemp -d) && git archive HEAD \| tar -x -C "$tmp" && git -C "$tmp" init -q && git diff --binary HEAD -- tools/check-plugin-package.py tests/test_plugin_package.py tests/test_cs_skill_release.py README.md README.en.md plugins/codestable/skills/cs-onboard/tools/codestable_runtime.py tests/test_codestable_doctor.py tests/test_skill_entry_simplification.py \| (cd "$tmp" && git apply -) && python3 "$tmp/tools/check-plugin-package.py" --root "$tmp" && python3 "$tmp/plugins/codestable/skills/cs-onboard/tools/codestable-runtime-sync.py" --root "$tmp" --source-skill-dir "$tmp/plugins/codestable/skills/cs-onboard" --plugin-version 1.0.4 --check --json` | Git-aware 隔离候选 package/runtime 合同 | core | fix-or-block |
| CMD-002 | `uv run --with pytest --with pyyaml pytest tests/test_plugin_package.py tests/test_cs_skill_release.py` | 定向合同回归 | core | fix-or-block |
| CMD-003 | `uv run --with pytest --with pyyaml pytest tests` | 正式全量测试 | core | fix-or-block |
| CMD-004 | `python3 plugins/codestable/skills/cs-onboard/tools/codestable-runtime-sync.py --root . --source-skill-dir plugins/codestable/skills/cs-onboard --plugin-version 1.0.4 --check --json` | runtime health | core | fix-or-block |
| CMD-005 | `uv run --with pytest --with pyyaml pytest tests/test_codestable_doctor.py tests/test_skill_entry_simplification.py` | runtime dirty/stale 回归 | core | fix-or-block |
| CMD-006 | `git diff --check` | diff 清洁度 | core | fix-or-block |

Required Artifacts：design-review、implementation evidence、code review、QA、acceptance、runtime check/sync/check JSON 摘要。

## 4. 与项目级架构文档的关系

- 名词：通过 owner-approved requirement delta，让 `plugin-market-distribution` 增加 Cursor marketplace 作为第四个分发宿主。
- 流程：不改变 CodeStable workflow 架构，只加固发布前校验和 runtime 迁移证据。
- 稳定约束：宿主 manifests 共享版本但各自遵守宿主 schema；统一 checker 验证仓库当前分发合同，不冒充通用宿主 validator。
- ADR：当前不需要新 ADR；没有引入难以回退的跨模块架构选择。
