---
name: cs-code-review
description: "Code review gate。实现批次完成后启动独立 Task agent 审查；review-fix 后按变化风险选择 focused closure 或完整独立复审。只读，不实现代码。"
argument-hint: "[--range <git-range>] [scope]"
contracts:
  - grep: "{slug}-review.md"
  - grep: "reviewer: subagent"
  - grep: "只读"
  - grep: "blocking"
  - grep: "references/independent-review/protocol.md"
  - grep: "focused closure"
  - grep: "完整实现批次"
  - not-grep: "OcrLane"
  - not-grep: "git push"
---

# cs-code-review

## 启动必读

动作前先跑 CodeStable preflight：读 `.codestable/attention.md`（缺失先 `cs-onboard`）；不要用 `AGENTS.md`/`CLAUDE.md` 等外部入口代替它；细则见 `.codestable/reference/execution-conventions.md`。项目启用本地 Override 时，同时读取 `.codestable/reference/local-override-workflow.md`。

本次调用参数：$ARGUMENTS。参数非空且不是字面 `$ARGUMENTS` 时解析 `--range <git-range>` 和 scope；无参数默认行为是从 active Task、来源产物与当前 diff 恢复审查范围。

本技能是横切代码审查 gate：任何写入型 workflow 的完整实现批次结束后、commit / QA / acceptance / Task complete 前，必须进行独立只读 review。它只读代码与产物，只写 `{slug}-review.md`；不直接修代码、不更新实现 checklist、不改变 spec。

Review 不依赖 OCR、桌面应用或第三方 review APP。首次审查和实质修改后的完整复审只使用宿主提供的独立 Task agent；能力不可用、启动失败、配置不匹配或结果无法归属时 fail closed，写 `status: blocked` 并停止，不静默降级为 self review。

## Review 批次边界

一次 review 对应一个**完整实现批次**：

- feature：当前 approved design + 全部完成的 checklist；
- issue：report + analysis + 完整 fix-note 和对应 diff；
- refactor：scan/design/checklist + 完整 apply notes 和对应 diff；
- Quick/FF：用户确认范围 + 完整 ff-note 和对应 diff；
- ad-hoc：用户指定的完整 git range 或明确 scope。

来源实现仍有 pending 项时不得提前 review。不得修一个问题、其它计划内实现尚未完成就频繁启动 reviewer。Review findings 由来源实现 workflow 集中修复本轮全部 blocking / important 项，再统一复审。

## Spec

```haskell
data ReviewRequest = ReviewRequest
  { entrySource : Maybe Source
  , gitRange : Maybe Text
  , resumeInput : Maybe ReviewResume
  , repoFacts : RepoFacts
  }
data Source = Feat | FeatFf | Issue | Refactor | RefactorFf | AdHoc
data ReviewState = ReviewState
  { specFinalized : Bool
  , implementationBatchComplete : Bool
  , diffAttributed : Bool
  , reviewerState : ReviewerState
  , priorReview : Maybe Verdict
  , priorIndependentReview : Bool
  , changeClass : ChangeClass
  }
data ReviewerState
  = ReadyToLaunch
  | Pending AgentRef
  | Completed Findings
  | Failed Reason
  | Unavailable Reason
data ReviewResume = ResumeReviewer AgentRef ReviewerResult
data ReviewerResult = ReviewerCompleted Findings | ReviewerFailed Reason
data ChangeClass = Initial | ClosureOnly | Material | Unknown
data Verdict = Passed | ChangesRequested | Blocked
data ReviewOutcome
  = LaunchingIndependentReviewer
  | AwaitingReviewer AgentRef
  | ReviewWritten Verdict
  | FocusedClosure Verdict
  | NeedsHuman ReviewBlocker
data ReviewBlocker
  = AttentionMissing
  | SpecNotFinalized
  | ImplementationBatchIncomplete
  | DiffNotAttributable
  | IndependentReviewerUnavailable
  | InvalidReviewResume
```

```haskell
selectReviewOutcome :: ReviewState -> ReviewOutcome
selectReviewOutcome state
  | not state.specFinalized = NeedsHuman SpecNotFinalized
  | not state.implementationBatchComplete = NeedsHuman ImplementationBatchIncomplete
  | not state.diffAttributed = NeedsHuman DiffNotAttributable
  | state.reviewerState is Failed reason = ReviewWritten Blocked
  | state.reviewerState is Unavailable _ = NeedsHuman IndependentReviewerUnavailable
  | state.reviewerState == ReadyToLaunch = LaunchingIndependentReviewer
  | state.reviewerState is Pending ref = AwaitingReviewer ref
  | focusedClosureEligible state && hasBlocking state = FocusedClosure ChangesRequested
  | focusedClosureEligible state = FocusedClosure Passed
  | hasBlocking state = ReviewWritten ChangesRequested
  | otherwise = ReviewWritten Passed

focusedClosureEligible :: ReviewState -> Bool
focusedClosureEligible state =
  state.priorIndependentReview
  && state.changeClass == ClosureOnly
```

完整复审必须增加 `round` 并重置 reviewer state。启动成功后先把宿主返回的真实 `AgentRef` 写入报告，再返回 awaiting；恢复输入必须匹配同一 round/ref，禁止从聊天记忆猜测或重复启动。

## 进入来源

| 来源 | Review 前置 | 通过后去向 |
|---|---|---|
| `cs-feat` Standard | approved design + checklist 全 done + Task 实现批次完成 | accept-inline |
| `cs-feat` Goal | design/checklist/goal evidence 完整 | QA |
| `cs-feat` Quick/FF | ff-note 与完整实现 diff | Task complete / 收尾 |
| `cs-issue` | report + analysis + fix-note 与完整修复 diff | Task complete / 收尾 |
| `cs-refactor` | refactor spec/checklist/apply notes 与完整 diff | Task complete / 收尾 |
| ad-hoc | 明确 scope 或非空 git range | 返回 verdict |

流程来源必须先确认 active Task 存在且 `owner_skill` 已转给 `cs-code-review`。若已有产物/实现但缺 Task，先执行 `cs-task backfill`，同一 run 返回 review。

ad-hoc 参数如果含 `--range`，允许工作区干净并以 `git diff {range}` 获取范围事实。也就是说，ad-hoc range 审查允许工作区干净。非 range 请求仍要求当前工作区存在可归因 diff。

## 输入

Review 前读取：

- `.codestable/attention.md` 和本地 Override 契约；
- 来源 spec、checklist、fix-note、apply-notes、ff-note；
- active Task 的目标、owner、实现步骤和文档索引；
- `git status --short`、unstaged/staged diff 或指定 git range；
- diff 涉及的人写代码和相邻关键调用点；
- goal/gate 模式下的 evidence pack、gate results、DoD results；
- 当前 round 已启动 reviewer 的结果。

范围外 dirty 文件记录为 baseline，不纳入 verdict。无法可靠归因时写 blocked，不把不确定当通过。

## 启动检查

1. attention、Task 和来源 spec 存在；
2. 当前实现批次全部完成，不能留计划内 pending 项；
3. 当前 diff/range 非空且可归因；
4. required gate/evidence 已落盘；
5. 已有 review 时检查 round、reviewer state/ref 和 review 后增量；
6. 仅 test/docs/type/metadata/nit-only 且不改变行为、公开契约、安全、数据、并发或架构的可归因修正可走 focused closure；其它变化或无法确定变化类型时均进入完整独立复审。

## 独立 Reviewer 编排

进入审查前读取 `references/independent-review/protocol.md` 与本 skill 的 `code-reviewer.md` 派发模板。首次 review 和完整复审必须启动一个独立 Task agent，并且只提供原始 spec、Task、diff 与验证证据，不透露主 agent 已形成的结论。

reviewer 的派发顺序、只读 mode 和生命周期由 `.codestable/reference/tools.md` 的 Subagent Runtime Mapping 与 `.codestable/reference/agent-conventions.md` 决定：优先 Cursor 自定义 subagent `codestable-code-reviewer`（该 agent 无 `model:` 字段、依赖继承当前主模型，若 runtime 不能保证继承则退回 bridge 的 model-safe 判定，不直接采信）；不可用时仅在 runtime 能请求当前主模型最高档、或明确保证通用 subagent 继承当前主模型时才用 `readonly generalPurpose` bridge；否则用当前主模型 self review。

reviewer 必须运行在**当前对话主模型的最高思考等级**（Opus 4.8 → `max`，`gpt-5.6-sol` → `xhigh`）；`.codestable/attention.md` 显式 pin 了 provider/model 时严格遵守。**禁止**用 `Explore` / `explorer`、Fast 预设、`model: fast` 或 unknown-model bridge 冒充 reviewer——这会把 review 降级到低思考档异构模型；无法保证模型档位时 blocked，不 fallback。

## 审查方法

独立 reviewer 与主 agent 的事实核验至少覆盖：

- design/spec fit 与范围漂移；
- 状态转换、边界值、错误路径、并发/时序、幂等；
- 权限、安全、敏感信息、跨用户/租户隔离；
- 数据一致性、回滚、迁移与持久化；
- 性能和资源释放；
- 测试是否能在实现损坏时真实失败；
- 复杂度、重复逻辑、错误抽象与维护成本；
- 文档、requirement、architecture 和 acceptance 归并影响。

执行对抗式审查：假设批次中至少有一个生产 bug，构造 3-5 个最可能失败的反例。经仓库事实确认的进入 findings；不能确认的进入 residual risk / QA focus。

## Findings 与 Verdict

- `blocking`：正确性、安全、数据、关键契约或验收可信度阻塞；
- `important`：应在当前批次修复的显著维护性、性能、测试或设计问题；
- `nit` / `suggestion`：不阻塞当前批次；
- `residual-risk`：review 无法独立证明、交给 QA/acceptance 的风险。

`passed` 必须满足：独立 Task agent 已完成、所有 blocking 清零、important 已修复或有明确 owner 接受的后续归属。新报告的 gate 锚点固定写：

```yaml
reviewer: subagent
```

历史报告中的 `subagent+ocr` 可作为含独立 Task agent 的旧证据读取，但新流程不得生成该值。没有完成独立 reviewer 时不得写 `passed`。

## Review-fix 循环

`changes-requested` 后：

1. 来源实现 workflow 读取完整 findings；
2. 集中修复当前 round 的全部 blocking / important；
3. 运行目标验证并更新 Task 进度；
4. 对 closure-only diff 做 focused closure；
5. 对 Material/Unknown diff 启动新 round 完整独立复审；
6. 重复直到 passed。

不得每修一条 finding 就立即重启 review，除非剩余 finding 明确依赖该修复且无法继续批量处理。

## Task Handoff 与退出条件

- `passed`：更新 active Task 的 review 证据和 owner，自动进入来源 workflow 的 QA/acceptance 或 `cs-task complete`；
- `changes-requested`：owner 返回来源实现 skill，集中 review-fix；
- `blocked`：Task 标记 blocked，记录 reviewer ref/reason；
- reviewer pending：等待同一 AgentRef，不启动重复 reviewer；
- 最终 workflow 只有在 review/QA/acceptance 完成且 Task 原子归档后才允许声称闭环。
