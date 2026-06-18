---
name: cs-feat-qa
description: feature 流程阶段 2.6——代码审查通过后的本地 QA 验证 gate。对照 design / checklist / review 报告和最终 diff，运行必跑命令、测试、浏览器或手工验证，产出 {slug}-qa.md；QA 失败时回到 cs-feat-impl 的 qa-fix，不能直接进入验收。触发：用户说"做 QA"、"跑测试验收前验证"、"review 过了跑 QA"、"跑 cs-feat-qa"。
---

# cs-feat-qa

## 启动必读

开始任何判断或动作前，先读取 `.codestable/attention.md`；缺失则视为骨架不完整，提示先补齐或运行 `cs-onboard`，不要回退到外部 AI 入口文件。

本阶段是 review 通过后、acceptance 前的本地 QA gate。它只读代码和产物、运行验证命令 / 浏览器 / API / 手工检查，并写 `{slug}-qa.md`。默认不改代码、不改 checklist、不改 design；发现失败后回到 `cs-feat-impl` 的 qa-fix。

QA 的目标不是再做一遍 code review，也不是最终归档验收报告。它回答一个问题：在当前工作区里，design 承诺的关键行为是否有足够的运行证据，review 指出的测试焦点和 residual risk 是否被实际覆盖。

> 共享路径与命名约定看 `.codestable/reference/shared-conventions.md` 第 0 节。

---

## 输入

进入 QA 前必须读取：

- `.codestable/attention.md`
- `{slug}-design.md`
- `{slug}-checklist.yaml`
- `{slug}-review.md`
- 实现完成汇报 / review-fix 汇报（如有）
- `git status --short`
- `git diff`（有 staged diff 时也读 `git diff --cached`）
- design 里的必跑验证命令 / 基线风险 / 验收场景 / 证据类型 / 清洁度规则
- review 报告第 4 节 Test And QA Focus 和第 5 节 Residual Risk
- 项目测试入口：README、package scripts、Makefile、CI 配置、历史 acceptance / qa 报告里与本 feature 相关的命令

如果工作区有 feature 外的既有 dirty 文件，记录 baseline/无关变更；QA 结论只覆盖本 feature 可归因的改动。无法区分归因时写 `blocked` 或 `residual-risk`，不要假装通过。

---

## 启动检查

1. `{slug}-design.md` 存在且 `status=approved`。
2. `{slug}-checklist.yaml` 存在，`steps` 全 `done`，`checks` 仍未由 acceptance 全部通过。
3. `{slug}-review.md` 存在，frontmatter `doc_type=feature-review`、`status=passed`，无 unresolved `blocking` findings。
4. 如果 review 报告不是基于当前 diff：先回 `cs-feat-review` 复审。qa-fix 或其他代码改动会让旧 review 过期。
5. 如果已有 `{slug}-qa.md`：
   - `status=passed` 且 diff 未变化：提示可进入 `cs-feat-accept`。
   - `status=failed` / `blocked`：读取旧失败项，确认是否处于 qa-fix 后的复测。
   - diff 已变化：重新 QA，并在报告里记录轮次。

---

## QA 流程

### 1. 建验证矩阵

从 design 第 3 节关键场景、design 必跑命令、review Test And QA Focus、review residual risk 汇总 QA 矩阵：

- 场景：输入 / 触发 → 期望可观察结果。
- 证据类型：unit / function / integration / e2e / browser / API / manual / typecheck / diff。
- 命令或动作：具体命令、页面路径、API 请求、手工步骤。
- 失败判据：什么结果算 fail，不写"看起来正常"。
- 归因：本 feature / 既有基线 / 环境不可用 / 无法判断。

优先使用项目已有测试入口和既有工具，不为了 QA 临时引入新测试框架。需要新增测试代码时，QA 不直接写；把它记为 failed item，回 `cs-feat-impl` qa-fix。

### 2. 运行验证

按从便宜到昂贵、从自动到手工的顺序运行：

1. 基线相关命令：typecheck / lint / build / targeted unit 或项目等价命令。
2. 与 feature 直接相关的 unit / function / integration / e2e 测试。
3. review 指出的重点验证和 residual risk。
4. 前端 / 用户可见改动：浏览器验证、截图或明确手工路径；只跑 typecheck 不算 QA 通过。
5. API / 后端能力：真实请求、集成测试或可复现的命令行调用。
6. 清洁度复核：debug 输出、临时 TODO/FIXME、注释掉代码、无用 import、方案外文件。

每条证据必须记录命令、退出码或观察结果。命令不可运行时写具体原因：缺依赖、服务不可启动、外部凭证缺失、环境限制、成本过高。不可运行不是自动通过。

### 3. 判定

- `passed`：所有 blocking QA items 通过；不可运行项有明确非阻塞理由和 acceptance 可复核的 residual risk。
- `failed`：关键场景失败、必跑命令失败且归因本 feature、review 重点未覆盖、测试缺口会影响验收可信度、前端未做浏览器验证。
- `blocked`：输入缺失、review 未通过、环境不可用到无法判断核心行为、dirty diff 归因不清。

QA failed 时不要直接修代码。输出报告后进入 `cs-feat-impl` qa-fix；qa-fix 修完必须先重跑 `cs-feat-review`，再重跑 `cs-feat-qa`。

---

## 报告模板

报告路径：`.codestable/features/{feature}/{slug}-qa.md`。

```markdown
---
doc_type: feature-qa
feature: YYYY-MM-DD-slug
status: passed|failed|blocked
tested: YYYY-MM-DD
round: 1
---

# {slug} QA 报告

## 1. Scope And Inputs

- Design: {path}
- Checklist: {path}
- Review: {path}
- Diff basis: {git status / git diff 摘要}
- Baseline dirty files: {none / 列表 + 归因}

## 2. Verification Matrix

| ID | 来源 | 场景 / 风险 | 证据类型 | 命令或动作 | 期望 | 结果 |
|---|---|---|---|---|---|---|
| QA-001 | design S1 | {描述} | unit/e2e/browser/manual | `{命令}` | {期望} | pass/fail/blocked |

## 3. Command Results

- `{命令}` → exit {code}：{摘要}
- 未运行：{命令} → {具体原因 + 是否阻塞}

## 4. Scenario Results

- [ ] QA-001 {场景}：pass/fail/blocked
  - Evidence: {输出 / 截图 / 请求响应 / 手工路径}
  - Notes: {归因 / 风险}

## 5. Findings

### failed

- [ ] QA-001 {失败项}
  - Evidence: {证据}
  - Impact: {为什么影响验收}
  - Expected fix scope: {只描述失败边界，不替实现写方案}

### blocked

- [ ] QA-00N {阻塞项}

### residual-risk

- {无法完全验证但不阻塞的风险；没有写 none}

## 6. Cleanliness

- Debug output: pass/fail
- Temporary TODO/FIXME/XXX: pass/fail
- Commented-out code: pass/fail
- Unused imports / dead code from this feature: pass/fail
- Out-of-scope files: pass/fail

## 7. Verdict

- Status: passed|failed|blocked
- Next: `cs-feat-accept` | `cs-feat-impl` qa-fix -> `cs-feat-review` -> `cs-feat-qa` | 补齐环境后重跑 `cs-feat-qa`
```

没有某类 finding 时写 `none`，不要删除章节；复测要能对比。

---

## qa-fix 衔接

如果 QA `failed`：

1. 报告 `status: failed`。
2. 告诉用户下一步触发 `cs-feat-impl` 的 qa-fix 模式。
3. qa-fix 只修 QA failed / blocked items，不处理顺手发现，不扩大 feature 范围。
4. qa-fix 修完会改变 diff，必须重跑 `cs-feat-review`；review passed 后再重跑 `cs-feat-qa`。
5. QA passed 后才能进入 `cs-feat-accept`。

如果 QA `blocked`：

- 先补环境 / 输入 / review 状态；不把 blocked 写成通过。

如果 QA `passed`：

- 告诉用户下一步是 `cs-feat-accept`。

---

## 退出条件

- [ ] 已读取 attention、design、checklist、review、实现证据、git status、git diff。
- [ ] 已确认 review passed 且基于当前 diff。
- [ ] 已建立 verification matrix，覆盖 design 关键场景、必跑命令、review Test And QA Focus、review residual risk。
- [ ] 已运行可运行的验证命令 / 浏览器 / API / 手工检查，并记录结果。
- [ ] 未运行项都有具体原因和阻塞判断。
- [ ] 已完成清洁度复核。
- [ ] 已写 `.codestable/features/{feature}/{slug}-qa.md`。
- [ ] failed / blocked 时没有进入 acceptance，而是指向 qa-fix 或补环境。
- [ ] passed 时明确告诉用户下一步 `cs-feat-accept`。

---

## 容易踩的坑

- 把 QA 写成第二次 code review，不运行任何证据。
- 只跑 typecheck 就宣称前端用户路径通过。
- 命令失败但归因不清就写 passed。
- QA 阶段直接修代码，绕过 qa-fix / review 复审。
- qa-fix 后跳过 review，直接重跑 QA 或进入 acceptance。
- 不记录未运行原因，导致 acceptance 无法判断剩余风险。
