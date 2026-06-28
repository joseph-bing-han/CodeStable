# Independent Review Protocol

Code review 只使用一个独立 Task agent reviewer。它是 gate 必需环节，不依赖 OCR、桌面应用或其它第三方 review APP。

## 1. Reviewer 状态机

reviewer 选择和只读控制复用共享协议，不在本 skill 复制 backend 选择链：

```haskell
reviewDecision :: AgentEnv -> AgentRun -> Maybe OwnerApproval -> AgentDecision
reviewDecision env run approval = reviewGate (selectTaskAgent Review env) run approval
```

`selectTaskAgent Review` 必须先按 attention 的显式配置匹配 `hostAgentCapabilities`，再按共享 `reviewGate` 处理 launch/await/completed/failed。显式 pin 的配置不可用时 `SelectionBlocked ExplicitConfigUnavailable`，owner 需先改配置；继承配置下独立 reviewer 不可用时返回 `NeedOwnerApproval`，默认 blocked，只有 owner 按 `approval-conventions.md` 显式授权 `ApproveLocalOnly` 才降级为 owner-approved local review。批量、赶时间、已自查、自评低风险或 owner 口头同意都不构成 `ApproveLocalOnly`。

### Reviewer 派发合约（模型档位）

启动 reviewer 前必须按 `.codestable/reference/tools.md` 的 Subagent Runtime Mapping 与本 skill 的 `code-reviewer.md` 派发模板执行，核心约束：

- reviewer 运行在**当前对话主模型的最高思考等级**（Opus 4.8 → `max`，`gpt-5.6-sol` → `xhigh`）；`.codestable/attention.md` 显式 pin 了 provider/model 时以 attention 为准。
- 派发顺序：优先 Cursor 自定义 subagent `codestable-code-reviewer`；不可用时，仅在 runtime 能请求当前主模型最高档、或明确保证未指定模型的通用 subagent 继承当前主模型时，才用 `readonly generalPurpose` bridge（合并 `plugins/codestable/agents/code-reviewer.md` role prompt 与填好的 task body）；两个 model-safe 条件都不满足时，用当前主模型 self review。
- **禁止**用 `Explore` / `explorer`、Fast 模型预设、`model: fast` 或 unknown-model bridge 冒充 reviewer；这类预设会把 review 降级到低思考档异构模型，属于 fail-closed 违规。

```haskell
data ReviewerState
  = ReadyToLaunch
  | Active AgentRef
  | Completed Findings
  | Failed Reason
  | Unavailable Reason

data ReviewDecision
  = Launch AgentCapability AgentConfig
  | Await AgentRef
  | Merge Findings
  | Block Reason
```

- `ReadyToLaunch`：按 `.codestable/reference/agent-conventions.md` 选择 code-review Task agent。
- `Active`：宿主启动成功后立即把真实 `AgentRef` 持久化到 review 报告。
- `Completed`：主 agent 对 findings 做仓库事实核验、去重和严重度归一。
- `Failed` / `Unavailable`：写 `status: blocked`；不 fallback 到 self review 或外部 APP。
- 恢复时 round/ref 必须精确匹配；缺失或不匹配时 fail closed，禁止重复启动。

## 2. Reviewer 输入隔离

独立 reviewer 只接收原始材料：

```text
你是 CodeStable 本次完整实现批次的独立代码审查 agent。只读，不修改文件、不更新 Task/checklist/design。

请读取：
- .codestable/attention.md
- .codestable/reference/local-override-workflow.md（存在时）
- 当前 active Task
- 来源 design/report/analysis/fix-note/refactor spec/checklist
- evidence pack、gate results、DoD results（存在时）
- 当前 git status、git diff、staged diff 或指定 git range
- diff 涉及的人写代码和相邻关键调用点

按 blocking / important / nit / suggestion / learning / praise / residual-risk 输出。
每条 finding 必须给出 file:line 或可机械核验的仓库事实、影响和预期修复边界。
执行对抗式审查：假设本批次至少藏着一个生产 bug，优先攻击 spec 不一致、边界值、错误路径、状态转换、并发时序、权限与数据隔离、持久化与回滚、测试假阳性。
额外输出 Test And QA Focus。
不要写 {slug}-review.md，只回传审查结果。
```

不得把主 agent 已形成的 findings 或 verdict 告诉独立 reviewer，避免确认偏误。

## 3. 批次门禁

启动 reviewer 前必须满足：

- 当前 Task 对应实现步骤全部完成；
- 来源 spec 已定稿；
- 当前 diff/range 能完整归因到本批次；
- 不存在仍计划在本批次实现但尚未完成的项；
- required evidence 已落盘。

如果实现仍有 pending 项，返回来源实现 skill 继续批量完成，不提前 review。

## 4. 结果合并

主 agent 收到 reviewer 结果后：

1. 逐条用当前仓库事实核验；
2. 合并重复 finding；
3. 不可证实的外部结论降为 residual-risk 或丢弃；
4. 生成 `{slug}-review.md`；
5. 新报告固定写 `reviewer: subagent`；
6. 结果已消费且没有 pending permission 后，按 `.codestable/reference/agent-conventions.md` 的 Task agent 生命周期关闭该 reviewer。

遇到 agent capacity/thread limit 时，不预先清理运行中的 agent；只在失败后按最老已完成 agent 清理并重试一次，仍失败则 blocked。

历史报告中的 `subagent+ocr` 表示其中曾包含独立 Task agent，可作为只读旧证据；不得由新流程生成。

## 5. Review-fix 与复审

- 首轮 findings 先完整收集；来源实现 workflow 集中修复全部 blocking/important。
- 仅 test/docs/type/metadata/nit-only 且无行为、契约、安全、数据、并发、架构变化时允许 focused closure。
- Material 或 Unknown 变化必须增加 round 并启动新的独立 reviewer。
- 不得每修一个 finding 就重启 reviewer；以完整修复批次为复审单位。

## 6. Gate 结论

- `reviewer: subagent` + `status: passed`：默认放行。
- reviewer pending/failed/unavailable：默认 blocked。
- 继承配置下独立 reviewer 不可用，且 owner 按 `approval-conventions.md` 显式授权 `ApproveLocalOnly` 时，降级为 owner-approved local review（主 agent 本地审查），记录 owner approval 证据；显式 pin 的配置不可用不适用此降级，owner 需先改配置。
- `reviewer: self` 或无 reviewer 且无 owner approval：不放行。
- 不提供环境变量绕过独立 reviewer 的默认路径。
