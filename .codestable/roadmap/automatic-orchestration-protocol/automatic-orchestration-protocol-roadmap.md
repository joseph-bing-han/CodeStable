---
doc_type: roadmap
slug: automatic-orchestration-protocol
status: active
created: 2026-05-30
last_reviewed: 2026-05-30
tags: [workflow, orchestration, skills]
related_requirements: []
related_architecture: [ARCHITECTURE]
---

# CodeStable 自动编排协议

## 1. 背景

当前 CodeStable 的 `cs` 总入口和多个路由型技能主要承担“建议用户下一步触发哪个 skill”的职责。这个设计保证了阶段边界清晰，但真实使用时会让用户重复输入 `/cs-feat`、`/cs-feat-design`、`/cs-feat-impl` 等机械命令。

本 roadmap 的目标是把 CodeStable 入口和阶段衔接从“建议式路由”升级为“自动编排”：当下一步是确定性的流程推进时，AI 必须自动继续执行目标 skill；只有遇到真实歧义、方案 review、安全边界或用户决策点时，才用编号选项向用户确认。

## 2. 范围与明确不做

### 本 roadmap 覆盖

- 定义跨 CodeStable 技能共享的自动编排协议。
- 统一结构化用户询问协议，减少开放式追问和无意义二次触发。
- 改造 `cs`、`cs-feat`、`cs-issue`、`cs-task`、`cs-roadmap` 等入口 / 路由型技能。
- 改造 `cs-brainstorm`、feature 阶段技能、issue 阶段技能等阶段型技能的退出语义。
- 增加一致性验收规则，防止技能文档之间出现“一个要求自动继续、另一个要求用户重新触发”的冲突。

### 明确不做

- 不取消 design、roadmap、issue analysis 等需要用户 review 的真实 checkpoint。
- 不让一个 skill 直接替另一个 skill 产出文件；只允许自动读取并执行目标 skill 的职责。
- 不实现新的 Agent runtime 工具；只基于现有 Agent 工具能力描述协议。
- 不重构所有 CodeStable 技能内容结构，只更新与自动编排、提问、退出语义相关的表述。
- 不处理非 CodeStable 技能，例如 browser-bridge、goframe、laravel 等。

## 3. 模块拆分（概设）

```text
CodeStable 自动编排协议
├── 共享协议层：定义自动继续、checkpoint 分级、handoff 和结构化提问规则
├── 入口编排层：把根入口和 workflow 入口从“建议路由”改成“执行路由”
├── 阶段衔接层：把阶段完成后的退出语义改成“确认后自动进入下一阶段”
└── 一致性验收层：扫描并修正所有相关 skill 的旧式提示和冲突表述
```

### 共享协议层 · orchestration-protocol

- **职责**：在共享文档中定义所有 CodeStable 技能共同遵守的自动编排规则。
- **承载的子 feature**：`orchestration-shared-protocol`
- **触碰的现有代码 / 模块**：`cs-onboard/reference/shared-conventions.md`，以及已复制到项目里的 `.codestable/reference/shared-conventions.md`

### 入口编排层 · entry-orchestration

- **职责**：改造所有只做路由的入口技能，让路由结果成为下一步动作，而不是用户需要复制粘贴的建议。
- **承载的子 feature**：`orchestration-entry-skills`
- **触碰的现有代码 / 模块**：`cs/SKILL.md`、`cs-feat/SKILL.md`、`cs-issue/SKILL.md`、`cs-task/SKILL.md`、`cs-roadmap/SKILL.md`

### 阶段衔接层 · stage-handoff

- **职责**：改造阶段型技能的收尾规则，让 review 通过后自动进入下一阶段；保留真实 checkpoint。
- **承载的子 feature**：`orchestration-stage-skills`
- **触碰的现有代码 / 模块**：`cs-brainstorm/SKILL.md`、`cs-feat-design/SKILL.md`、`cs-feat-impl/SKILL.md`、`cs-feat-accept/SKILL.md`、`cs-issue-report/SKILL.md`、`cs-issue-analyze/SKILL.md`、`cs-issue-fix/SKILL.md`

### 一致性验收层 · orchestration-consistency

- **职责**：统一清理所有相关技能中的旧式“建议触发 / 停下来等用户输入 / 本技能只做路由不执行”等冲突表述，并验证文档行数和协议一致性。
- **承载的子 feature**：`orchestration-consistency-pass`
- **触碰的现有代码 / 模块**：所有 `cs-*/SKILL.md` 中涉及路由、阶段退出、用户询问的段落

## 4. 模块间接口契约 / 共享协议（架构层详设）

### 4.1 Skill Handoff 协议

**方向**：入口编排层 / 阶段衔接层 → 目标 skill  
**形式**：运行时上下文约定，不强制落盘

**契约**：

```yaml
handoff:
  from_skill: string
  to_skill: string
  user_goal: string
  detected_workflow: string
  current_stage: string
  target_stage: string
  evidence:
    - string
  decisions:
    - string
  open_questions:
    - string
  next_action: string
```

**约束**：

- `to_skill` 一旦确定，不得要求用户再次输入该 skill 名。
- `evidence` 必须包含做出路由判断的最小依据，例如用户原话、已存在的 spec 文件、roadmap item。
- `open_questions` 为空时必须自动继续。
- `open_questions` 非空时必须转换为结构化用户问题。

### 4.2 Checkpoint 分级协议

**方向**：所有 CodeStable skill → 用户  
**形式**：文档化行为规则

**契约**：

```yaml
checkpoint:
  level: L0 | L1 | L2 | L3
  reason: string
  default_action: auto_continue | ask_structured_question | require_review | require_explicit_confirmation
```

**级别定义**：

- `L0`：机械路由。下一步确定且低风险，必须自动继续。
- `L1`：信息不足。必须用编号选项询问。
- `L2`：用户 review。必须让用户审阅 design、roadmap、analysis 等阶段产物。
- `L3`：高风险操作。涉及删除、覆盖、提交、迁移、生产环境、关键数据时必须显式确认。

**约束**：

- 不得把 L0 包装成用户问题。
- 不得跳过 L2 / L3。
- L2 用户选择“通过并继续”后，下一阶段必须自动执行。

### 4.3 结构化用户问题协议

**方向**：所有 CodeStable skill → 用户  
**形式**：Agent 结构化提问能力

**契约**：

```yaml
question:
  prompt: string
  options:
    - id: "1"
      label: string
    - id: "2"
      label: string
    - id: "3"
      label: string
    - id: "4"
      label: "自由输入补充信息"
```

**约束**：

- 任何选择型问题都必须给 2-4 个编号选项。
- 最后一项必须保留自由输入。
- 推荐路径应放在 `1`。
- 如果用户选择自由输入后仍有歧义，必须重新生成编号选项。
- 不得要求用户复制粘贴 `/cs-*` 命令来完成已判定的下一步。

### 4.4 自动编排边界协议

**方向**：当前 skill → 目标 skill  
**形式**：职责边界规则

**契约**：

```yaml
orchestration_boundary:
  current_skill_may:
    - decide_next_skill
    - pass_handoff_context
    - read_target_skill
    - continue_execution
  current_skill_must_not:
    - produce_target_skill_artifact_without_following_target_skill
    - skip_required_review
    - hide_scope_or_risk_changes
```

**约束**：

- “职责边界”不等于“手动边界”。
- 当前 skill 可以自动进入目标 skill，但不能跳过目标 skill 的流程规则。
- 若目标 skill 发现前置条件不满足，应回到结构化问题，而不是硬冲。

## 5. 子 feature 清单

1. **orchestration-shared-protocol** — 在共享口径中定义自动编排、checkpoint 分级、handoff 和结构化提问协议。
   - 所属模块：共享协议层
   - 依赖：无
   - 状态：done
   - 对应 feature：通过 task-list 实施
   - 备注：最小闭环；完成后后续入口技能有统一协议可引用。

2. **orchestration-entry-skills** — 改造 `cs`、`cs-feat`、`cs-issue`、`cs-task`、`cs-roadmap`，让路由结果自动执行。
   - 所属模块：入口编排层
   - 依赖：`orchestration-shared-protocol`
   - 状态：done
   - 对应 feature：通过 task-list 实施
   - 备注：优先处理最影响用户体验的入口技能。

3. **orchestration-stage-skills** — 改造 brainstorm、feature、issue 阶段技能的退出语义，让 review 通过后自动进入下一阶段。
   - 所属模块：阶段衔接层
   - 依赖：`orchestration-shared-protocol`、`orchestration-entry-skills`
   - 状态：done
   - 对应 feature：通过 task-list 实施
   - 备注：重点保留真实 checkpoint，不把自动编排变成无审核连跑。

4. **orchestration-consistency-pass** — 全仓扫描并修正相关 skill 中旧式路由、提问、退出表述，完成一致性验收。
   - 所属模块：一致性验收层
   - 依赖：`orchestration-entry-skills`、`orchestration-stage-skills`
   - 状态：done
   - 对应 feature：通过 task-list 实施
   - 备注：包括检查单个 Markdown 文档不超过 300 行。

**最小闭环**：第 1 条 `orchestration-shared-protocol` 做完后，CodeStable 已经有统一自动编排协议，后续任一入口技能改造都能引用它，不再各自发明规则。

## 6. 排期思路

先做共享协议层，因为它是所有后续改造的共同约束。随后改入口编排层，最快消除用户最明显的“需要重复输入下一个 skill 名”的体验问题。第三步改阶段衔接层，把 feature / issue / brainstorm 的跨阶段推进改成确认后自动继续。最后做一致性验收层，集中清理所有旧式表述，避免技能之间互相矛盾。

## 7. 观察项

- 当前 `.codestable/architecture/ARCHITECTURE.md` 只是 onboard 骨架，后续可以用 `cs-arch backfill` 为 CodeStable skill 系统补一份现状架构文档。
- `cs-onboard/reference/system-overview.md` 已在一致性验收阶段同步为自动编排表述。
- 本 roadmap 本身推动的是技能文档行为协议，不涉及源代码运行时测试；验收重点应是文档一致性、流程可执行性和关键路径示例。

## 8. 变更日志

- 2026-05-30：创建 roadmap 初稿。
- 2026-05-30：完成共享协议、入口技能、阶段技能与一致性验收改造。
