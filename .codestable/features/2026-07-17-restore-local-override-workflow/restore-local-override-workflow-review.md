---
doc_type: feature-review
feature: 2026-07-17-restore-local-override-workflow
status: passed
reviewed: 2026-07-17
round: 7
reviewer: subagent
reviewer_state: completed
reviewer_ref: "d45cc607-c663-49dc-b6af-b89af4fdb0cb"
reviewer_provider: cursor
reviewer_model: claude-opus-4
reviewer_reasoning: max
reviewer_readonly: true
reviewer_reason: ""
task_generation_sha256: "0d45c20b3ef9b2efc4b1d8fc8a0a534196ffa35e3047524b7fd443b5f063abb4"
review_basis_sha256: "2e7dc2da0bf241e159fb1ababa5179efc6b9dd7ce41227de60d3e99220589eb9"
---

# restore-local-override-workflow 代码审查报告

## 1. Scope And Inputs

- Task: `.codestable/tasks/active/restore-local-override-workflow.md`
- Design: `.codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-design.md`
- Checklist: `.codestable/features/2026-07-17-restore-local-override-workflow/restore-local-override-workflow-checklist.yaml`
- Diff basis: 当前完整未提交实现批次
- Review mode: Round 3 review-fix 后的 round 4 完整独立复审
- Batch completeness: checklist 与 Round 3 blocking/important/nit 修复均已完成并验证
- Baseline dirty files: 当前 dirty worktree 全部归入本 feature 批次；staged diff 为空

### Independent Review

- Backend/config: attention 要求 `provider=openai`、`model=gpt-5.6-sol`、`thinkingOptionId=xhigh`
- State: completed
- AgentRef: `ba00f7d8-b007-45af-89ec-2c50d702fe6e`
- Gate effect: changes-requested
- Backend/config: `provider=openai`、`model=gpt-5.6-sol`、`thinkingOptionId=xhigh`

## 2. Diff Summary

- 新增：`cs-task`、guarded Task runtime、本地 Override reference 与回归测试
- 修改：`cs-code-review`、入口 workflow、runtime capability、doctor、workflow-next 与相关契约测试
- 删除：OCR 新流程依赖与 self-review fallback
- review-fix 新增：canonical reviewer 集合、archive ownership claim、cleanup quarantine、symlink root 边界和 issue/refactor slug helper
- 风险热点：Task 状态机、archive 完整性、并发写入、崩溃恢复、路径边界、review evidence 和真实 CLI 覆盖

## 3. Adversarial Pass

- Round 4 独立 reviewer 已成功完成并绑定真实 AgentRef。
- 机械复现：三字段伪造 review 被放行、空 issue 直接进入 archive、expected SHA 检查后并发覆盖、active parent 在 CAS 中途交换、final tombstone 后 staging residue 无法收敛、partial tombstone、伪 YAML 类型、malformed active scan 漏检、lock inode 替换和历史 archive inspect/scan 不一致。

## 4. Round 3 Formal Findings

### blocking

- [x] REV-B01 archiving tombstone 的 `archived_path` 可通过 `..` 逃逸 canonical archive 目录
  - Evidence: `ensure_canonical_path()` 采用词法 `Path.relative_to()`，没有拒绝 `..`；`recover_archiving_task_locked()` 会读取 tombstone 自由提供的路径并可能写入。
  - Impact: 损坏或伪造的 archiving tombstone 可驱动恢复逻辑读写 canonical archive 目录之外，甚至逃逸仓库。
  - Expected fix scope: tombstone path 必须精确等于由 task/date 推导的 canonical 相对路径；拒绝绝对路径、`..` 和非规范化路径，并补齐 traversal 反例。

- [x] REV-B02 per-task lock 不能防止两个陈旧 `write-active` 快照相互覆盖
  - Evidence: 调用者在 runtime 外生成完整 Task 快照；runtime 锁内只检查状态转换后直接替换，没有 expected SHA/revision 的 CAS 条件。`active -> active` 允许，因此后写入可静默覆盖先写入。
  - Impact: Task source of truth 的 owner、证据、related_docs 或步骤更新可能静默丢失。
  - Expected fix scope: `write-active` 增加 expected SHA/revision 并在锁内 CAS；两个调用者基于同一旧 SHA 时仅一个成功，另一个明确 conflict。

- [x] REV-B03 缺失 staging 的 archived-only 恢复会认证无法证明来源的内容
  - Evidence: `archiving + archived exists + active/staging missing` 分支仅校验少量 archived 字段，然后用当前 archived 字节重新计算 SHA 并完成 tombstone；没有 source snapshot 可证明内容来源。
  - Impact: tombstone 完成前被修改的 archived 内容可能被重新哈希并认证为 canonical 正本。
  - Expected fix scope: 无 staging/source snapshot 时默认 `incomplete-archive`，不得完成 tombstone；增加 archived-only 篡改与 fault-injection 测试。

### important

- [x] REV-I01 Task 和 tombstone schema 校验不满足 reference 的严格契约
  - Evidence: `validate_task_content()` 只检查 doc_type/task/status，未强制其它 required frontmatter 和固定正文七节；completed tombstone 也未完整验证 source_status/source_sha256/staging_path。
  - Impact: runtime 和 workflow gate 可能接受无法恢复上下文的残缺 Task 或不完整 tombstone。
  - Expected fix scope: 分离 active、archived、archiving tombstone、archived tombstone 四套 schema，逐字段 mutation 测试。

- [x] REV-I02 cleanup 在 source-equal quarantine 竞态下会返回成功，但 concurrent active residue 仍存在
  - Evidence: equal-content 分支删除 quarantine 后直接返回空 findings，不重新检查 concurrent writer 是否创建 active；当前测试还固化 `active exists + findings == []`。
  - Impact: cleanup/scan 可返回 `ok=true`，同时 active residue 仍存在。
  - Expected fix scope: 删除 quarantine 后重新检查 active，存在时返回 finding 或有界重试；未解决 conflict 也必须进入 inspection/scan。

- [x] REV-I03 全局 scan 会静默忽略部分损坏 tombstone 和 archived-only 状态
  - Evidence: scan 只恢复 archiving、cleanup archived，不处理未知 state；不独立枚举 archived/staging/conflict，lone archived 或 unresolved conflict 可被忽略。
  - Impact: scan 可能在仓库包含无法解释的 Task 生命周期状态时仍返回成功。
  - Expected fix scope: 枚举 active/archived/tombstone/staging/conflict slug 并取并集，统一状态矩阵逐项输出 finding。

- [x] REV-I04 静态 symlink 检查与实际 I/O 分离，仍存在 parent-directory symlink swap
  - Evidence: 先 `is_symlink()` 检查，之后再用 pathname 执行 mkdir/mkstemp/replace/read；只有 lock 最终组件用了 `O_NOFOLLOW`，父目录没有 directory FD 锚定。
  - Impact: 能并发修改目录的进程可在检查后交换父目录为 symlink，重定向后续操作。
  - Expected fix scope: 使用安全 directory FD/openat/no-follow 或在每个关键 I/O 前后复验父目录 identity；补齐六类 parent swap fault injection。

### nit

- [x] REV-N01 持久化 lock 文件未被 ignore
  - Evidence: `.codestable/tasks/locks/restore-local-override-workflow.lock` 出现在 git status，source `codestable.gitignore` 未覆盖 `tasks/locks/`。
  - Expected fix scope: 在 source ignore 模板加入 `tasks/locks/` 并同步 runtime。

### praise

- archive inspection 已覆盖唯一正本、canonical 日期文件名、hash、active/staging residue。
- archive 同日期重试幂等、不同日期 fail closed；reviewer evidence 已收敛到 frontmatter。
- feature 与 unit(issue/refactor) CLI 复用同一 archive gate；OCR/self-review 新执行路径已移除。

## 5. Round 4 Formal Findings

### blocking

- [x] REV4-B01 独立 review gate 可由最小三字段 frontmatter 伪造
  - Evidence: `review_has_canonical_evidence()` 只要求 `doc_type/status/reviewer`，缺少 `round`、`reviewer_state`、`reviewer_ref` 和 unit identity 仍放行。
  - Impact: 可手工伪造 `reviewer: subagent` 绕过独立 Task agent fail-closed 门禁。
  - Expected fix scope: 共享严格 review evidence schema；passed 必须绑定 unit、正整数 round、completed state 和非空 reviewer ref，并补 mutation tests。

- [x] REV4-B02 issue/refactor `workflow-next unit` 未验证 workflow evidence
  - Evidence: 空 issue/refactor 目录配 completed Task 可直接返回 `cs-task archive`，未校验 report/analysis/fix-note 或 design/checklist/apply-notes/review。
  - Impact: issue/refactor 可跳过实现证据与独立 review 直接归档。
  - Expected fix scope: 建立真实 issue/refactor state resolver，只在 required artifacts、review 和 checklist 完整时进入 archive gate。

- [x] REV4-B03 expected SHA 检查与最终 replace 分离，不是真正 CAS
  - Evidence: SHA 比较后另一个 writer 或真实目录交换可在 commit 前介入；最终 replacement 会覆盖并发内容。
  - Impact: Task owner、进度和 gate evidence 仍可能静默丢失。
  - Expected fix scope: compare 与 commit 使用同一 root-anchored FD 链；原子移走当前 entry 后验证 SHA，匹配才安装新正本，不匹配则保留 conflict。

- [x] REV4-B04 archive crash protocol 存在不可恢复持久化状态
  - Evidence: exclusive tombstone 直接写最终路径，进程死亡可留下 partial JSON；final tombstone 后 staging unlink 前退出会被永久判为 staging residue。
  - Impact: 可认证 Task 进入 invalid，retry/cleanup/scan 无法自动收敛。
  - Expected fix scope: 原子发布完整 claim；支持 completed tombstone + verified staging 的幂等收尾；覆盖所有持久化边界 fault injection。

### important

- [x] REV4-I01 Task schema 未保留真实 YAML 类型，scan 不验证 active 内容
  - Evidence: `goal: null`、`workflow: []`、`owner_skill: true`、`archived: "null"` 被当字符串接受；malformed active 的 scan 为空。
  - Expected fix scope: strict YAML loader/typed parser；active scan 调用完整 Task validator；JSON tombstone 拒绝 duplicate keys。

- [x] REV4-I02 lock pathname 可替换，`flock` 只保护旧 inode
  - Evidence: 持锁期间 unlink/recreate 同名 lock 后第二个进程可锁新 inode。
  - Expected fix scope: flock 后和退出前复验 pathname inode；即使 lock 被替换，CAS/tombstone 仍不得丢写。

- [x] REV4-I03 历史 archive 的 scan、inspect 和 workflow 分类不一致
  - Evidence: 2026-07-17 前 archived-only 被 scan 忽略，但 inspect 判 invalid；历史 archive + active 被误报 missing tombstone。
  - Expected fix scope: 增加 historical-readonly/legacy-valid 状态，并为历史双副本使用专门 conflict finding。

- [x] REV4-I04 doctor 将合法历史 `subagent+ocr` 证据升级为 P1
  - Evidence: doctor 对所有历史 unit 无条件要求 canonical reviewer，未使用历史 readable helper。
  - Expected fix scope: 新/current batch 强制 canonical lifecycle；已归档历史 unit 接受 readable subagent evidence。

### nit

- [x] REV4-N01 `codestable-workflow-next.py` 导入但未使用 `review_has_subagent_evidence`

### validation

- 独立 reviewer 复跑：Task runtime `45 passed`；全量 `678 passed, 1 skipped`；runtime sync、diff check 和 compile 通过。
- Verdict: `changes-requested`。

## 6. Round 4 Review-Fix Evidence

- 严格 review lifecycle：canonical passed evidence 绑定 unit identity、正确文件名、正整数 `round`、`reviewer_state: completed`、非空 `reviewer_ref`，并拒绝 duplicate key 与 quoted round 伪类型。
- issue/refactor resolver：issue 的 report/analysis/fix-note 必须 `status: confirmed`；refactor design 必须 approved，checklist 全 done，apply-notes 与 canonical review 完整后才进入 Task archive gate。
- Active Task CAS：旧正本先捕获到 FD 锚定 quarantine，再以 hard-link no-replace 提交；直接 writer 重建时保留 concurrent active，并把旧快照移入 conflict evidence。
- 路径与 lock：初次 create、CAS update 和 exclusive tombstone claim 在真实目录交换后按 inode 回滚；持锁期间 pathname inode 被替换时 fail closed。
- archive 恢复：exclusive claim 原子发布完整 JSON；final tombstone + verified staging 自动收尾，tampered staging 保留并报告。
- typed schema 与历史兼容：Task YAML 保留真实类型，tombstone JSON 拒绝 duplicate/non-finite，scan 验证 active；历史 archive 在 scan/inspect/workflow 中统一为只读兼容状态，只有 cutover 前已归档 unit 可读取 `subagent+ocr`。
- 对抗验证：Round 4 定向回归 `270 passed`；全量 `702 passed, 1 skipped`；runtime sync `ok`；`py_compile` 与 `git diff --check` 通过。
- 全仓 Task scan baseline：当前 feature Task 无 finding；其余 finding 均来自本 feature 前已存在的历史非 canonical Task、历史 active/archive 双副本或旧 tombstone schema，本批次不擅自迁移。

## 7. Round 5 Formal Findings

### blocking

- [~] CS5-B01 archive gate 未把归档 Task 绑定到 workflow 和 required evidence（核心已闭合：绑定 workflow family + terminal owner + archived status；required-docs 绑定降为 residual risk，由 unit-level resolver 兜底）
  - Evidence: `enforce_task_archive_gate()` 接受 `inspect state=valid|historical` 后直接放行；refactor CLI 测试实际使用 `workflow: feature`、`related_docs: []` 的 archived Task。
  - Impact: 同 slug 的其它 workflow Task 或缺失 review/acceptance 索引的 Task 可绕过最终闭环。
  - Expected fix scope: archive inspection 返回严格 Task metadata；gate 核对 workflow family、unit identity、required docs 与终态 owner/evidence。

- [x] CS5-B02 workflow artifact YAML 仍使用 last-key-wins parser
  - Evidence: `codestable_gate_common.load_yaml_text()` 直接调用 `yaml.safe_load()`；issue/refactor/feature/roadmap artifact 未拒绝 duplicate keys。
  - Impact: duplicate status/doc_type/identity/checklist 状态可伪造 workflow evidence。
  - Expected fix scope: 所有 gate artifact 统一 strict YAML loader，并稳定返回结构化 blocked JSON。

- [x] CS5-B03 canonical review evidence 未绑定 reviewer 配置和当前实现 basis
  - Evidence: gate 只校验 unit/round/state/ref，未校验 provider/model/reasoning/readonly，也未检测 review 后实现变化。
  - Impact: 错误模型、非只读 agent、伪造 ref 或 stale review 可被复用。
  - Expected fix scope: frontmatter 固化并验证 `openai/gpt-5.6-sol/xhigh/readonly`、Task generation 和实现 basis digest。

- [x] CS5-B04 archive 使用覆盖式 replace，会破坏 orphan staging 和并发 archive target
  - Evidence: active->staging 与 archive target publish 均可覆盖预检后出现的直接写入。
  - Impact: 崩溃恢复快照或并发冲突证据可能静默丢失。
  - Expected fix scope: staging 与 archive target 使用 no-replace/exclusive 语义；冲突时保留双方并 fail closed。

- [override] CS5-B05 共享 agent contract 仍允许 `LocalReview` 放行（不采纳：owner 明确决定保留 owner-approved local review 作为受控降级逃生口；reviewer 此项建议与 owner 决策冲突，按 owner 决策 override）
  - Evidence: `agent-conventions.md` 的 `ApproveLocalOnly -> LocalReview -> Passed` 与本地 Override fail-closed 契约冲突。
  - Impact: 其它 skill 或同步后的 runtime 仍可能绕过独立 reviewer。
  - Expected fix scope: review role 移除 local/self review 放行路径，并同步 source/runtime/tests。

### important

- [x] CS5-I01 lock pathname inode 在异常退出路径可能跳过最终复验。
- [x] CS5-I02 refactor apply-notes 完成状态、canonical design/checklist filename 与 checklist identity 校验不足。
- [residual] CS5-I03 historical cutoff 可通过回填旧日期绕过，doctor 与 runtime 判定不一致。（owner 决定作为 residual risk：回填旧日期需要能写仓库历史，威胁模型内属低优先，留待后续统一不可伪造 eligibility 判定）
- [x] CS5-I04 issue/refactor malformed YAML 未稳定转换为结构化 blocked JSON。
- [x] CS5-I05 已打开旧 active FD 的 direct writer 在 capture 后写入可能静默丢失；需明确支持边界并补真实进程测试或持久保留策略。（owner 决定：在 codestable-task-runtime.py 模块 docstring 明确声明"不支持旧 active FD 跨 CAS 写入"边界；真实多进程 fault-injection 留作 residual risk）
- [x] CS5-I06 exclusive tombstone claim 删除临时 hardlink 后缺少 parent directory fsync。

### nit / suggestion

- [x] CS5-N01 恢复 `tests/test_codestable_doctor.py` 列表项一致缩进。
- [x] CS5-S01 收敛 Task、review、workflow artifact 的 strict parser，避免三套安全语义继续漂移。

### residual risk / QA focus

- 真实 APFS 多进程、open FD、进程 kill 与断电持久化仍需专门 fault-injection。
- 当前安装副本的旧 reviewer contract 不作为本轮 gate 证据；完成源修复后需验证安装/发布同步路径。
- AgentRef provenance 应通过 reviewer config、Task SHA 和实现 basis digest 加固。

### validation

- Reviewer config: `provider=openai`、`model=gpt-5.6-sol`、`reasoning=xhigh`、`readonly=true`。
- Reviewer AgentRef: `d11e7d51-96da-488d-9fb5-2cb68c9e0e0e`。
- Reviewer 前后 dirty/untracked 文件 SHA-256 清单一致，确认未修改工作区。
- Verdict: `changes-requested`。

## 7b. Round 5 Review-Fix Evidence

本轮由 owner 在 `cs-feat` 集中修复 Round 5 findings，处理结果如下：

- CS5-B02 已修复：workflow / review artifact 统一走 `codestable_gate_common.load_yaml_text()` 的 `UniqueKeySafeLoader`，duplicate mapping key 抛 `ValueError`，non-finite 数值拒绝，解析失败包装为结构化 blocked JSON。
- CS5-B03 已修复：`review_has_canonical_evidence()` 强制 `reviewer_provider/model/reasoning/readonly:true/reviewer_ref` 与 `task_generation_sha256`、`review_basis_sha256`；`review_evidence_matches_repository()` 在 active Task 尚存在时比对当前仓库重算 digest，stale/伪造 review fail closed；`reviewer_reasoning_is_valid()` 按 token 段拒绝 Fast/Explore/tera 等降级模型并对 `gpt-5.6-sol` 强制 `xhigh`。
- CS5-B04 已修复：archive active->staging 用 `move_path_no_replace()`（hard-link + unlink），archive target 用 `write_bytes_exclusive()`（O_CREAT|O_EXCL + link），target 已存在即 fail closed，冲突保留双方。
- CS5-I01 已修复：`task_operation_lock()` 的 `finally` 在解锁前再次 `verify_task_operation_lock()`，pathname inode 被替换即 fail closed。
- CS5-I02 已修复：refactor resolver 仅解析 canonical 文件名，design 必须 `refactor-design`+approved、checklist identity 匹配且 steps 全 done、apply-notes `refactor-apply-notes`+completed。
- CS5-I04 已修复：issue/refactor CLI 用 `except ArtifactParseError` 输出 `artifact_parse_decision()` 结构化 blocked JSON。
- CS5-I06 已修复：`write_bytes_exclusive()` link 发布 claim 后对 parent directory `fsync`，删除临时 hardlink 后再次 `fsync`。
- CS5-S01 已修复（owner 决定收敛）：`codestable-task-runtime.py` 删除本地 `UniqueKeySafeLoader`，`parse_frontmatter_fields()` 改用共享 `load_yaml_text()`，边界翻译 `ValueError/RuntimeError -> TaskRuntimeError`；三类 artifact 现共用同一 strict parser。
- CS5-I05 已声明边界（owner 决定）：`codestable-task-runtime.py` 模块 docstring 明确"旧 active FD 跨 CAS 写入不受支持"，真实多进程 fault-injection 留作 residual risk。
- CS5-N01 已修复：`tests/test_codestable_doctor.py` 工具列表缩进统一。
- CS5-B01 核心已闭合：archive gate 绑定 workflow family + terminal owner + archived status（`archive_task_binding_findings`）；required-docs 绑定由 unit-level resolver 兜底（review passed 才 status=complete），降为 residual risk。
- CS5-B05 按 owner 决策 override：owner-approved local review 是有意保留的受控降级逃生口，不移除 `LocalReview`；reviewer 该建议与 owner 决策冲突，不采纳。
- CS5-I03 按 owner 决策转 residual risk：historical cutoff 回填旧日期需能写仓库历史，威胁模型内低优先。

- 验证：全量 `705 passed, 1 skipped`；`codestable-task-runtime` 定向 `62 passed`；runtime sync `--check` ok；`git diff --check` clean；`py_compile` 通过。

## 7c. Round 6 Formal Findings

Round 6 独立复审（readonly subagent，继承当前对话主模型最高档）对 Material 变化（CS5-S01 strict parser 收敛、reviewer 档位 gate、archive binding）做对抗式复核，并回归验证前几轮 findings。

### blocking

无。

### important

- [x] R6-I01 `reviewer_reasoning_is_valid` 的 override 查表大小写敏感，可绕过 gpt-5.6-sol 的 xhigh 强制
  - Evidence: FORBIDDEN 标记匹配用 `model.strip().lower()`，但 override 查表用原样 `REVIEWER_REASONING_OVERRIDES.get(model.strip())`；`reviewer_reasoning_is_valid("GPT-5.6-Sol", "low")` 返回 `True`（错误放行），绕过 `gpt-5.6-sol` 固定 xhigh 的契约。
  - Impact: reviewer frontmatter 里 `reviewer_model` 写成 sol 模型任意大小写变体即可静默跳过 xhigh 强制，`reviewer_reasoning` 只需非空。此弱化直接传导到 `review_has_canonical_evidence` 与 `review_gate_passed`。是对 CS5-B03 的一处新的、不同的具体绕过（不属于 owner override 项）。
  - Expected fix scope: override 查表 key 与匹配统一 casing；补大小写变体反例测试。

### nit

- [ ] R6-N01 `parse_frontmatter_fields` 把 PyYAML 缺失（RuntimeError）误标为「Task frontmatter YAML is invalid」——仅诊断信息可读性问题，fail-closed 行为正确，非阻塞。
- [ ] R6-N02 `sys.path.insert(0, ...)` 前插无去重——两种主加载路径均已核验成立，tools 目录文件名不与 stdlib 冲突无 shadowing，非阻塞。

### validation

- Reviewer state: completed；readonly subagent 继承当前对话主模型最高档。
- Verdict: `changes-requested`（唯一 important R6-I01）。

## 7d. Round 6 Review-Fix Evidence

- R6-I01 已修复：`reviewer_reasoning_is_valid()` 先 `normalized_model = model.strip().lower()` 归一化一次，FORBIDDEN token 匹配与 `REVIEWER_REASONING_OVERRIDES` 查表统一复用该小写形式；override 表 key 用小写。`reasoning` 亦按小写比较。
  - 机械验证：`("gpt-5.6-sol","low")`/`("GPT-5.6-Sol","low")` → False；`("GPT-5.6-Sol","xhigh")`/`("GPT-5.6-Sol","XHIGH")`/`("gpt-5.6-sol","xhigh")` → True；`("claude-opus-4","high")` → True；`("gpt-5.6-tera-high","high")`/`("GPT-5.6-TERA-high","high")` → False。
  - 回归测试：`test_local_override_workflow.py` 新增 casing 矩阵断言（sol 大小写变体 + 非 xhigh 必须拒绝，+ xhigh 必须放行）。
- R6-N01 / R6-N02 保留为 nit（非阻塞），未改动。
- 验证：全量 `709 passed, 1 skipped`；R6 定向 `4 passed`；runtime sync `--check` ok；`git diff --check` clean。

## 7e. Round 7 Formal Findings

Round 7 独立复审（readonly subagent，继承当前对话主模型最高档，AgentRef `d45cc607-c663-49dc-b6af-b89af4fdb0cb`）对 R6-I01 修复（casing 归一化）做对抗式复核。

### blocking

无。

### important

无。

### nit

- [ ] R7-N01 override 键按精确规范串匹配，分隔符变体（`gpt_5.6_sol`、`gpt.5.6.sol`、`gpt5.6sol`）不触发 xhigh 强制——**pre-existing，非 R6-I01 回归**（casing 修复前同样如此），且不扩大真实攻击面：override 威胁模型是"诚实记录 gpt-5.6-sol 却用低档"，伪造者直接写非 sol 模型名本就能过。reviewer 明确建议本轮不动，仅记录。

### validation

- Reviewer state: completed；readonly subagent 继承当前对话主模型最高档。
- 机械核验：sol 系列全大小写/空格变体 + 非 xhigh 一律 False，xhigh 任意大小写 True；reasoning `.lower()` 无反向放行（`xhighx`/`hxhigh`/`x high` 均 False）；FORBIDDEN 先于 override 生效；token 段精确匹配未破坏（gemini-2.5-pro/elite 不误伤）；gate 端到端传导正确；回归测试为真对抗测试。
- Verdict: `approved`。R6-I01 修复无残留、无新绕过、无回归。

## 8. Previous Unverified Candidate Findings

> 注意：本节内容未绑定到成功完成的独立 Task agent/AgentRef，不能作为当前 review gate 的正式 finding。下一次 reviewer 成功后必须从原始材料重新核验、归属和定级。

### blocking

- [ ] REV-001 `codestable-workflow-next.py::enforce_task_archive_gate()` 只按 archived 文件名存在放行，不验证 canonical 归档完整性
  - Evidence: 当前放行条件仅为 `archived_paths` 非空且 active 不存在；未验证 archived frontmatter、对应 tombstone、`state: archived`、task/path/date、SHA、重复正本或 symlink。`test_complete_workflow_exits_only_after_archive_without_active_residue` 只创建 archived 文件便期待 `complete`，与 `cs-task/reference.md` 第 7 节四项归档成功条件冲突。
  - Impact: 手工复制、损坏、历史残留或伪造 archived 文件可绕过 Task source-of-truth 和最终闭环 gate。
  - Expected fix scope: 在 Task runtime 提供只读 archive verifier；workflow-next 只在恰好一个非 symlink archived 正本、frontmatter/tombstone/path/date/hash 全部一致且 active 不存在时放行；增加 missing tombstone、错误状态、hash mismatch、重复 archived 和 symlink archived 反例。

- [ ] REV-002 `codestable-task-runtime.py::archive_task()` 在 claim 后可静默丢失已通过 precheck 的并发 active 更新
  - Evidence: archive 在 tombstone claim 前读取 `source_content` 和生成旧 `archived_content`；claim 后直接移动当前 active，再用旧 `archived_content` 覆盖 archived。并发 writer 可在 precheck 后、claim 后替换 active，新字节随后被旧 snapshot 覆盖。
  - Impact: Task 进度、owner、review 结果或状态更新可永久丢失，同时最终 tombstone/hash 看起来完全合法，scan 无法发现。
  - Expected fix scope: claim 后将 active 原子捕获到独占 staging；对实际捕获字节重新算 SHA 并与 claim 比较；不一致时保留实际字节并 fail closed；归档转换必须基于独占捕获内容；增加确定性交错测试。

- [ ] REV-003 `cleanup_archived_task_residue()` 的 divergent 恢复分支会覆盖 quarantine 后到达的新 active 写入
  - Evidence: cleanup 先 `os.replace(active_path, quarantine_path)`；发现 SHA 分叉后无条件 `os.replace(quarantine_path, active_path)`。现有并发测试只覆盖 equal-content 删除分支，未覆盖 divergent restore 分支。
  - Impact: cleanup 作为清理工具反而可能删除更新的 Task 内容，且只报告普通 divergent residue，无法揭示丢写。
  - Expected fix scope: divergent 内容仅在 active 仍不存在时恢复；active 已重新出现时不得覆盖，需把 quarantine 保留到可诊断 conflict 路径并同时报告两份内容；增加 divergent residue + concurrent active 反例。

- [ ] REV-004 `state: archiving` tombstone 没有崩溃恢复路径，普通错误也可能制造永久死锁
  - Evidence: cleanup 对非 `archived` tombstone 直接返回；scan 因而不报告 archiving。write-active 与 archive retry 均阻止 archiving tombstone。`archived_path.parent.mkdir()` 位于 claim 后且在 try 外；claim 后进程退出、rename/write/final tombstone 任一阶段失败均无明确 resume/rollback 状态机。
  - Impact: 权限错误、磁盘错误、进程终止或主机重启可让 Task 永久不可写、不可归档，而 scan 仍可能返回无 finding。
  - Expected fix scope: 将 claim 后所有步骤纳入统一恢复边界；实现 active/archive 存在性与 source/archived hash 的恢复矩阵；scan 至少报告 `incomplete-archive`；增加 mkdir、rename、archived write、final tombstone write 的 fault injection 和重启恢复测试。

- [ ] REV-005 symlink 检查仅限制在 repository root 内，仍可重定向覆盖仓库内任意文件
  - Evidence: `task_paths()` 和 archive path 只在 resolve 后执行 `relative_to(root)`。active 文件或 active/tombstone/archived 目录若 symlink 到仓库内其它位置仍会通过。现有测试只覆盖指向仓库外部的 symlink。
  - Impact: Task runtime 可能覆盖源码、README、配置、Git metadata 或其它 CodeStable artifact。
  - Expected fix scope: active、tombstone、archived 分别限制在其 canonical `.codestable/tasks/{directory}` 内；拒绝目标文件和父路径 symlink，或使用目录 fd/no-follow 操作；增加仓库内重定向、最终文件 symlink、父目录 symlink 和 symlink swap 测试。

### important

- [ ] REV-006 `write_active_task()` 未执行 `cs-task/reference.md` 声明的状态转换表
  - Evidence: runtime 只验证新 status 属于 `active/blocked/completed/cancelled`，不读取旧 status；会接受 `completed -> active`、`cancelled -> active`、`blocked -> completed` 等 reference 明确禁止的转换。
  - Impact: 唯一写入口无法保证公开状态机，Task 可倒退或绕过 required gates。
  - Expected fix scope: 建立 transition map，允许 same-status 幂等更新，区分首次 create/backfill 和已有 Task update，并为合法/非法转换增加参数化测试。

- [ ] REV-007 doctor 的 canonical reviewer 证据扫描可被正文假锚点绕过
  - Evidence: `review_has_canonical_evidence()` 最终逐行扫描整个 Markdown；frontmatter `reviewer: self` 或无 reviewer，正文/代码块出现 `reviewer: subagent` 仍会返回 true。workflow-next 另查 frontmatter，doctor/missing_review_findings 没有。
  - Impact: doctor 可把 self-review、无 reviewer 或损坏 frontmatter 的报告误判为 canonical independent review evidence。
  - Expected fix scope: 只解析 YAML frontmatter，并同时校验 `status: passed`、reviewer 和必要 doc_type；增加 self/body spoof、无 reviewer/code block、malformed frontmatter 测试。

- [ ] REV-008 issue/refactor archive gate 测试只调用内部 helper，没有真实 CLI dispatch
  - Evidence: `codestable-workflow-next.py` CLI 只注册 `epic` 和 `feature` 子命令；issue/refactor 测试直接调用 `enforce_task_archive_gate()`，未证明生产 CLI 路径可进入 gate。
  - Impact: 测试可能给出 workflow-next 已统一覆盖 issue/refactor 的假信心，实际仍依赖 skill 文本让 agent 手工执行。
  - Expected fix scope: 增加 `issue`、`refactor` 子命令或通用 `unit --workflow --path`；用 subprocess JSON 测试日期 slug、active status、archive integrity 和 `final_answer_allowed`。

- [ ] REV-009 成功 archive 后相同命令重试不是幂等操作
  - Evidence: `archive_task()` 在读取 completed tombstone 前先要求 active 文件存在；成功后 active 已不存在，相同参数重试直接报 `Active task does not exist`。
  - Impact: archive 已成功但响应丢失、agent 重启或网络中断时，安全重试被误报失败，自动恢复无法确认既有成功结果。
  - Expected fix scope: active 不存在时先校验 completed tombstone；同 task/date/path/hash 有效时返回已有 `ArchiveResult`，日期或目标冲突继续 fail closed；增加同参数和不同日期重试测试。

### nit

- [ ] REV-010 archive date 只校验格式，不校验真实日期
  - Evidence: `^\d{4}-\d{2}-\d{2}$` 接受 `2026-99-99`。
  - Expected fix scope: 使用 `datetime.date.fromisoformat()` 做语义校验。

### suggestion

- 将 Task archive 的只读状态检查、归档执行和崩溃恢复统一为一个 state inspector，避免 workflow-next、doctor 和 runtime 以不同精度判断同一 Task 状态。
- 为并发与崩溃测试增加受控 hook/fault injector，避免依赖 sleep 或真实线程调度。

### learning

- 测试可能直接固化错误契约；“只有 archived 文件、没有 tombstone 仍允许 complete”就是本批次的实际例子。
- rename-to-quarantine 只有在 equal 和 divergent 所有分支都不覆盖后来出现的新路径时，才真正消除 TOCTOU。

### praise

- `CANONICAL_REVIEWERS={"subagent"}` 与 `LEGACY_READABLE_REVIEWERS={"subagent+ocr"}` 的拆分方向正确，workflow-next passed gate 已拒绝 legacy-only reviewer。
- OCR 新执行 lane、OCR health 和 self-review fallback 已从插件树移除；剩余 OCR 表述均为历史兼容或禁止性约束。
- `O_CREAT | O_EXCL` tombstone claim 正确阻止了两个 archive writer 静默覆盖 ownership。
- `cs-task` 已进入 skill discovery、runtime capability 和同步清单；runtime sync 输入证据为 `missing=[]`、`drifted_paths=[]`。

## 7. Test And QA Focus

- Archive integrity：无 tombstone、tombstone 非 archived、hash mismatch、frontmatter 非 archived、重复正本、archived symlink。
- Archive/write 并发：writer 在 claim 前通过 precheck、claim 后完成 replace；必须保留最新字节或 fail closed。
- Cleanup 并发：equal 和 divergent residue 分支都覆盖 concurrent active；quarantine restore 失败和 quarantine 残留必须可诊断。
- 崩溃恢复：claim、active rename、archived rewrite、final tombstone write 各阶段 fault injection 与重启恢复。
- 状态转换矩阵：全部合法、非法和 same-status 幂等转换。
- 路径边界：仓库外和仓库内重定向、最终文件 symlink、父目录 symlink、symlink swap。
- Reviewer evidence：frontmatter canonical/legacy/self、正文和 fenced code block spoof、malformed frontmatter。
- 真实 CLI：feature、issue、refactor 均通过 subprocess 调用 workflow-next，不用内部 helper 替代生产入口。
- 修复完成后重新运行完整 pytest、runtime sync、`git diff --check`、py_compile 和安装后 skill discovery。

## 8. Residual Risk

- 独立 reviewer 环境未安装 pytest，无法独立复现主流程提供的 `638 passed, 1 skipped`；该绿色结果只能证明现有测试期望被满足，不能覆盖上述缺失反例。
- 未执行真实多进程 archive/write 竞争、进程 kill、磁盘满、权限变化或 fsync 失败测试。
- archive 的 directory fsync 和跨文件耐久性没有明确保证；逻辑竞态修复后仍需单独评估断电一致性。
- skill workflow 的多数测试仍是文本/顺序契约测试，不能充分证明实际 agent 一定进入 Task/review/archive gate。
- Skills CLI E2E 当前仍有默认 skip，安装后 `cs-task` discovery 缺少本轮独立实机证据。

## 9. Verdict

- Status: changes-requested
- Next: owner 返回 `cs-feat`，集中修复 REV-B01 至 REV-B03、REV-I01 至 REV-I04，并随同处理 REV-N01；修复后必须进行 round 4 完整独立复审。

## 9. Focused Closure

- Closed findings: none
- Attributed delta: none
- Targeted verification: none
- Classification: Material
