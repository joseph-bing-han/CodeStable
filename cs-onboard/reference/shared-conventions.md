# CodeStable 共享口径

由 `cs-onboard` 复制到项目的 `.codestable/reference/shared-conventions.md`。所有 CodeStable 子技能用项目相对路径 `.codestable/reference/shared-conventions.md` 引用本文件——跨子技能共享但不适合堆在单个技能里的规范的唯一权威版本。

skill 本身不共享文件系统（每个 skill 是独立安装单元），共享口径不能放在某个 skill 内部被别的 skill 引用。放在"工作项目"里对所有 skill 都可达。

---

## 0. 目录结构与路径命名

onboard 完成后骨架（`cs-onboard` 负责搭建）：

```
.codestable/
├── attention.md           CodeStable 技能启动必读的项目注意事项
├── requirements/          能力愿景 + 领域模型 + 决策记录
│   ├── VISION.md           能力中心索引（cs-req 维护）
│   ├── {slug}.md           一个能力一份，扁平（cs-req 产出）
│   ├── CONTEXT.md          领域术语表（cs-domain lazy 创建；多 context 时被 CONTEXT-MAP.md 替代）
│   ├── CONTEXT-MAP.md      多 context 拓扑入口（cs-domain，仅多 context 时存在）
│   ├── adrs/               架构决策记录（cs-domain，lazy 创建）
│   │   └── NNN-{slug}.md   Nygard 四节 + 状态机 frontmatter
│   └── {ctx}/              子 context 子目录（仅多 context 时存在）
│       ├── CONTEXT.md      子 context 术语
│       ├── adrs/           子 context 特定 ADR
│       └── {capability}.md 归属本 context 的能力
├── roadmap/               规划层（"接下来怎么做这块大需求 + 模块怎么切 + 接口怎么定"）
│   └── {slug}/            一个大需求一个子目录（cs-roadmap 产出）
│       ├── {slug}-roadmap.md   主文档：背景 / 范围 / 模块拆分 / 接口契约 / 子 feature 清单 / 排期
│       ├── {slug}-items.yaml   机器可读子 feature 清单，acceptance 回写状态
│       ├── {slug}-roadmap-review.md 人工确认前的规划审查报告
│       └── drafts/             可选
├── goals/                 目标聚合根（起点报告 / 自主迭代 / 功能验收）
│   └── {slug}/           一个 bounded goal 一个子目录（cs-goal 产出）
│       ├── {slug}-start-report.md 起点报告
│       ├── {slug}-state.yaml     机器可读状态
│       ├── {slug}-iteration-*.md 迭代报告
│       └── {slug}-functional-acceptance.md 子 agent 功能验收
├── features/              feature spec 聚合根
│   └── YYYY-MM-DD-{slug}/  每个 feature 一个目录
│       ├── {slug}-brainstorm.md  （可选，case 2 时产出）
│       ├── {slug}-design.md      （标准流程）
│       ├── {slug}-checklist.yaml （标准流程）
│       ├── {slug}-design-review.md（人审前方案审查）
│       ├── {slug}-review.md      （实现后代码审查）
│       ├── {slug}-qa.md          （代码审查后 QA gate）
│       ├── {slug}-acceptance.md  （标准流程）
│       └── {slug}-ff-note.md     （fastforward 通道唯一产物，与标准流程产物互斥）
├── issues/                issue spec 聚合根
│   └── YYYY-MM-DD-{slug}/
│       ├── {slug}-report.md
│       ├── {slug}-analysis.md   （根因不显然才有）
│       ├── {slug}-fix-note.md
│       └── {slug}-code-review.md
├── refactors/             refactor spec 聚合根
│   └── YYYY-MM-DD-{slug}/
│       ├── {slug}-scan.md
│       ├── {slug}-refactor-design.md
│       ├── {slug}-checklist.yaml
│       └── {slug}-apply-notes.md
├── tasks/                 任务运行账本（cs-task 维护）
│   ├── active/
│   │   └── {task}.md
│   └── archived/
│       └── YYYY-MM-DD-{task}.md
├── compound/              沉淀类文档统一目录（cs-keep 产出）
│   └── YYYY-MM-DD-{slug}.md
│                          纯 markdown，无 frontmatter，grep 检索
├── brainstorm/            brainstorm 阶段 spike 实验代码区（cs-brainstorm 临时产出）
│   └── {slug}/            一次 spike 一个子目录，文件名随意
│                          验完不强制清理，结论回写到对应 brainstorm note
├── tools/                 跨工作流共享脚本（onboard 从技能包释放）
└── reference/             共享参考文档（onboard 从技能包释放）
```

### 命名规则

- 需求文档：`requirements/{slug}.md`（能力愿景，不带日期前缀，扁平不分组）；中心索引 `requirements/VISION.md`
- roadmap：`roadmap/{slug}/`（不带日期前缀，平铺不嵌套）
- task list：`tasks/active/{task}.md` 当前任务不带日期；`tasks/archived/YYYY-MM-DD-{task}.md` 历史任务带归档日期
- feature / issue / refactor 目录：带日期前缀 `YYYY-MM-DD-{slug}`
- 沉淀类：`compound/YYYY-MM-DD-{slug}.md`，日期用**归档当天**，纯 markdown 无 frontmatter（cs-keep 产出）
- 领域术语：`requirements/CONTEXT.md`（单 context）或 `requirements/{ctx}/CONTEXT.md`（多 context）；cs-domain lazy 创建
- 架构决策：`requirements/adrs/NNN-{slug}.md`（系统级）或 `requirements/{ctx}/adrs/NNN-{slug}.md`（子 context）；3 位编号，cs-domain 产出
- 项目注意事项入口固定为 `.codestable/attention.md`，所有 CodeStable 子技能启动前必须读取；不再兼容 `AGENTS.md` / `CLAUDE.md` 等外部入口

### 单 context ↔ 多 context 拓扑

- `requirements/CONTEXT-MAP.md` 存在 → 多 context 模式：术语和 ADR 按子 context 分目录
- 只有 `requirements/CONTEXT.md` → 单 context：术语和 ADR 平铺在 `requirements/` 下
- 升级路径见 `cs-domain` 的"单 → 多 context 升级"节

### 改目录结构

改 `cs-onboard/reference/shared-conventions.md` 模板，新项目 onboard 时带上新版本；已有项目手动同步 `.codestable/reference/shared-conventions.md`。

### task list 共享边界

`.codestable/tasks/` 是所有会落盘 workflow 的强制运行主线，不是可选配件。任何会修改项目内文档或代码的 CodeStable skill，一旦结束分析准备首次落盘，必须先通过 `cs-task create/recovery` 创建或复用 Task List；之后按 `modify -> update -> accept/review -> complete -> archive` 推进，直到 active 中无同名残留才算闭环。Task List 是 source of truth，Agent 原生 Tasks/Todo 只是运行时镜像。它不替代 feature/refactor checklist，也不替代 roadmap items；详细 schema 和状态机看 `cs-task/reference.md`。

---

## 1. 共享元数据口径

**feature spec**：brainstorm / design / design-review / review / QA / acceptance 共用 `doc_type` / `feature` / `status` / `summary` / `tags`。子技能只补特有字段。`status`：brainstorm = `confirmed`（落盘即确认无 draft）；design = `draft` / `approved`；design-review / review / QA / acceptance 见对应技能。

新增 feature gate 的 `doc_type`：`feature-design-review`（status: `passed` / `changes-requested` / `blocked`）、`feature-review`（status: `passed` / `changes-requested` / `blocked`）、`feature-qa`（status: `passed` / `failed` / `blocked`）、`feature-acceptance`（status: `passed` / `blocked`）。review / QA 报告是后续 gate 的输入，不替用户批准 design，也不替 acceptance 做最终验收。

**issue spec**：report / analysis / fix-note 共用 `doc_type` / `issue` / `status` / `tags`。`severity` / `root_cause_type` / `path` 由对应阶段按需补。

**归档类（compound）**：由 `cs-keep` 统一产出，写到 `.codestable/compound/YYYY-MM-DD-{slug}.md`。纯 markdown，**无 frontmatter**。三段足够：背景 / 结论 / 证据。检索靠 grep。

**外部读者文档**（cs-doc-tutorial / cs-doc-api）：frontmatter 由各自子技能定义。无特殊说明：`draft` = 待 review，`current` = 当前有效，`outdated` = 代码已变更待同步。

**写作约束**：子技能提字段时优先写"额外字段"或"阶段状态变化"，不重复展开整套通用字段。

---

## 2. {slug}-checklist.yaml 生命周期

- 是 feature 工作流的唯一执行清单
- 由 `cs-feat-design` 在 draft design 成型后先生成 `steps` + `checks`，供 `cs-feat-design-review` 和用户 review；用户确认后随 design 一起进入实现
- `cs-feat-ff` **不生成** checklist（也不写 design / acceptance），是跳过 spec 流程直接写代码的超轻量通道；唯一留下的痕迹是动手后回写的 `{slug}-ff-note.md`（轻量回顾，参与 scoped-commit、可被 cs-req / cs-domain backfill 检索到）

`steps` 的粒度是 **编排-计算分离维度的切片策略**——按"先编排骨架、后计算节点、最后持久化与测试"写（最简 Workflow 先行 → 逐个节点填充），**不下沉到 file:line / 函数级**。具体改哪个文件由 implement 阶段决定。

**design 的职责**：

- 提取 `steps`（4-8 步，每步独立可验证退出信号）：后端节奏 = 编排骨架 → 计算节点逐个填 → 接通持久化 → 测试覆盖；前端 = 静态结构 → 交互逻辑 → 状态接入 → 联调收尾
- 提取 `checks`：第 1 节"明确不做"→ 范围守护；第 2.1 接口 → 名词契约；第 2.2 主流程 + 流程级约束 → 编排骨架；第 2.3 挂载点 → 挂载点；第 3 节场景清单 → 验收场景

**implement 的职责**：

- 按 `steps` 顺序执行，每步完成把 status `pending` → `done`
- 实现到具体文件级时需要拆分某步、或发现微重构是其前置（参考第 7 节反射检查）→ 跟用户对齐后追加 / 拆分 steps，**不偷偷做**
- 不改写 `checks`

**acceptance 的职责**：只更新 `checks[].status`（`pending` → `passed` / `failed`），不重写 `steps`。

**写作约束**：子技能描述 checklist 时只补本阶段读 / 写哪一部分，不重新定义生命周期。

---

## 2.5 roadmap ↔ feature 衔接协议

`.codestable/roadmap/{slug}/{slug}-items.yaml` 是规划层和 feature 执行层的唯一接口。三个技能共同读写它——是 skill 都读写项目共享产物，不算耦合。

**items.yaml 状态机**：

```
planned  → in-progress  （cs-feat-design 启动 feature 时改）
in-progress → done      （cs-feat-accept 验收完成时改）
planned  → dropped      （cs-roadmap update 模式，用户决定不做时改）
```

`done` / `dropped` 是终态。需要回退重做的新加一条 slug 略改的条目，不改终态。

**cs-roadmap 的职责**：生成和维护 roadmap 主文档 + items.yaml；把 `planned` 改 `dropped`（用户放弃时）；不改 `in-progress` / `done`（feature 技能负责）。

**cs-roadmap-review 的职责**：在人审前只读审查 roadmap 主文档 + items.yaml + 相关事实，写 `{slug}-roadmap-review.md`；不修改 roadmap，不替用户批准。

**cs-feat-design 的职责**（从 roadmap 起头时）：

1. design.md frontmatter 加 `roadmap: {roadmap-slug}` + `roadmap_item: {子 feature slug}`
2. items.yaml 对应条目 `status: in-progress` + `feature: YYYY-MM-DD-{slug}`
3. 校验 yaml

**cs-feat-design-review 的职责**：在人审前只读审查 design + checklist + 相关事实，写 `{slug}-design-review.md`；不修改 design/checklist，不替用户批准。

直接起 feature（非 roadmap 来）两字段留空，不触发 roadmap 写。

**cs-feat-accept 的职责**：

1. 读 design frontmatter `roadmap` / `roadmap_item`
2. 空 → 跳过
3. 有值 → items.yaml 对应条目 `status: done`；同步主文档子 feature 清单显示状态；校验 yaml

回写是**实际写文件的动作**，验收报告要明确记录回写结果。

**最小闭环标记**：items.yaml 每份只有一条 `minimal_loop: true`，标记"做完后系统能端到端跑通最窄路径"。design 启动 `minimal_loop` 条目时优先级最高。

## 2.6 自动编排与结构化询问协议

CodeStable 入口和阶段技能默认自动编排：下一步可确定时直接继续，不要求用户复制粘贴 `cs-*` 名称；只有真实歧义、review 或风险操作才询问。所有用户可直达的入口 skill 都视为完整入口：从 `cs` 根入口路由过来和用户直接点名该入口等价，不能停在“下一步建议 / 推荐使用某个 skill / 请运行某个 skill”；代码型入口继续到 `cs-code-review` → `cs-task archive`，文档 / 规划型入口完成本 lane 落盘与归档，分诊 / 审计型入口把 handoff 交给下游后仍算同一条主线。

**checkpoint 分级**：`L0` 机械路由自动继续，Task 创建 / 恢复属于 L0；`L1` 信息不足用结构化问题；`L2` 阶段 review 提供“通过继续 / 修改 / 暂停 / 自由输入”；`L3` 删除、覆盖、提交、迁移、生产操作、关键数据改动必须显式确认。

**Workflow spine gate**：代码型 workflow 不允许缺 `Task → spec 产物 → code review → archive` 任一环。首次创建项目文档或改代码前必须已有 active Task，且 `owner_skill` / `related_docs` 已登记；阶段产物只在 chat 里不算完成；fix / impl / apply / ff-note 完成后必须立即执行 `cs-code-review`，不是只提示下一步；review 通过前 Task 不能 `completed`，review 通过后必须进入 `cs-task archive`；若发现已落产物或代码改动但 Task 缺失，当前动作是先执行 `cs-task backfill` 并续跑缺失 review / QA / acceptance 证据，不是报告“缺 task”后结束。

**handoff / 结构化问题**：进入目标 skill 前保留 `from_skill` / `to_skill` / `user_goal` / `detected_workflow` / `current_stage` / `target_stage` / `evidence` / `decisions` / `open_questions` / `next_action`。`open_questions` 为空必须继续，非空转成编号 `1..4` 结构化问题，推荐路径放 `1`，最后保留“自由输入补充信息”。`to_skill` 已确定且 `open_questions` 为空时，当前 agent 的下一步动作是读取并执行目标 `SKILL.md`，不是只输出目标名；用户在 L2 checkpoint 选择“通过继续”后立刻续跑下游 skill。当前 skill 可以决定、交接并继续执行目标 skill，但不能绕过目标 skill 规则、替目标 skill 产出文件或跳过 L2/L3。

---

## 3. 阶段收尾推荐

**feature-acceptance** 收尾按顺序判断：

1. `cs-keep`：沉淀坑点 / 技巧 / 长期约束 / 选型
2. `cs-doc-tutorial`：开发者 / 用户指南
3. `cs-doc-api`：公开 API 参考
4. `cs-docs-neat`：阶段 / 里程碑收尾时同步 `.codestable/`、README/docs、`CLAUDE.md` / `AGENTS.md` 和 agent 记忆
5. `scoped-commit`

**issue-fix** 收尾按顺序判断：

1. `cs-keep`：沉淀坑点或暴露的长期约束
2. `cs-docs-neat`：修复暴露了文档、agent 入口或记忆不一致时做全局整理
3. `scoped-commit`

**feature-ff** 收尾按顺序判断（比标准 acceptance 短，没有 req 回写动作）：

1. `cs-keep`：动手过程暴露的坑或拍板的长期约束
2. `cs-docs-neat`：快速改动影响 README/docs 或 agent 入口时同步
3. `scoped-commit`

**roadmap** 收尾按顺序判断：

1. `cs-docs-neat`：roadmap 确认落盘或整个 roadmap goal 完成后，同步 `.codestable/`、README/docs、`CLAUDE.md` / `AGENTS.md` 和 agent 记忆
2. 后续若要自动推进整份 roadmap，再走 `cs-roadmap-impl-goal`

**统一规则**：一律一句话提示；用户说"不用"立即跳过；不强制；上游主动提示，下游承接执行。Task 真正闭环以 `cs-task archive` 完成并清空 active 残留为准。

---

## 4. 收尾提交（scoped-commit）

feature-ff / acceptance / issue-fix / refactor-ff / refactor apply 走完且 `cs-code-review` 通过后，把本次产物提交为一个 commit：

- **范围**：本次工作改到的代码 + 相关 spec 文档 + 本次实际更新过的 CONTEXT.md / ADR / req doc + 本次实际更新过的 roadmap items.yaml / 主文档
- **不该进**：和本次工作无关的顺手修改；属于"下次另起 feature / issue"的扩大范围
- **提交前确认**：用户没明确同意不要 `git commit`
- **commit message**：一句话说清"做了什么"，不贴 spec 目录路径

补充：
- `feature-ff`：相关 spec 文档 = `{slug}-ff-note.md` + `{slug}-code-review.md`
- `refactor-ff`：相关 spec 文档 = `{slug}-code-review.md` + 可选 `{slug}-refactor-note.md`
- 一旦上游阶段把 `owner_skill` 切到 `cs-code-review`，本地 `scoped-commit` 的最终确认与执行由 `cs-code-review` 统一负责；上游 skill 不再重复发起提交询问。PR / merge 只表示 review 已满足前置条件，不属于 CodeStable 内部自动执行范围。

子技能只描述本阶段特有提交范围，通用规则看这里。

---

## 5. 归档检索规则

feature-design / issue-analyze / issue-fix 动手前到 `.codestable/compound/` 搜已有沉淀：

- 总是先搜 `requirements/CONTEXT.md`、`requirements/adrs/`、`compound/`
- `compound/` 直接 `grep -r "关键词" .codestable/compound/`（纯 markdown，无 schema）
- 搜到的结果只作参考输入，不盲目套用——可能已过时或不适合当前上下文
- 搜到和当前方向冲突的决策类沉淀 → **必须**正面回应"为什么仍然这么做"或调整方向

---

## 6. cs-keep 守护规则

`cs-keep` 写 compound 时遵守：

1. **宁缺毋滥**——用户说不出理由的内容直接省略，不要 AI 编造
2. **不替用户写实质内容**——AI 负责起草结构和串联语言，实质结论必须来自用户或可追溯的代码证据
3. **attention.md 检查**——写完若沉淀暴露出"每次启动都该知道"的一两行硬约束，提示用户用 `cs-note` 追加到 `.codestable/attention.md`
4. **起草前先 grep 查重叠**——`grep -r "关键词" .codestable/compound/`。命中相近旧文档就问用户：更新已有 / 新写一份。默认优先更新已有，沿用原文件名，文末加"YYYY-MM-DD 更新"。
5. **识别用户意图是"改已有"还是"记新的"**——用户说"改 / 更新 / 补充 {某条}"或话题高度重合时默认走"更新已有"，不要闷头新建。分不清就问。

---

## 7. 写代码时的反射检查

`cs-feat-impl` 和 `cs-issue-fix` 共用。AI 默认会往"大函数 / 大文件 / god class / 处处特殊分支"漂，这一节把漂移截在发生那一刻。

**不是阈值，是触发器**——硬数字会诱发为拆而拆把自然聚合的代码切碎。每条都是"遇到 X 情况就停下来问自己"。

| 触发场景 | 停下来问自己 |
|---|---|
| 要往一个已经很长的文件追加代码时 | 文件承担几件事？新加的是已有职责延伸还是第 N+1 件事？是第 N+1 就默认新建文件 |
| 要给已经很多方法的类加方法时 | 新方法是核心职责的自然扩展，还是把类推向"什么都能干"？ |
| 写的函数已超过一屏时 | 函数在做几件事？几件事就拆 |
| 要加 `if (特殊情况) { 特殊处理 }` 分支时 | 抽象维度选错了？正确做法可能是把特殊路径和通用路径分成不同函数 / 策略 / 类 |
| 要 copy-paste 一段代码时 | 能抽成共用还是只字面相似？能抽就抽 |
| 要给函数加第 4+ 个参数时 | 函数做的事是不是太多了？参数列表是 API 恶化的早期信号 |
| 要新写"万能工具类 / helper"时 | 真没归属还是只是想不起来放哪儿就先堆 util？ |

**停下来之后**：反射检查只把问题提出来，结论用户定。停下来想清楚的动作（拆 / 新建 / 重命名 / 抽共用）会让改动超出现有 steps 范围 → 跟用户对齐再决定（纳入当前推进 / 记顺手发现留后续）。

不许偷偷拆完继续写，也不许忽略信号硬冲。默认动作是停、问、再继续。

## 8. 报告语言策略

- CodeStable 所有落盘产出的正文**默认用中文**：plan / design、plan review / design-review、code review、QA、验收、issue、refactor、roadmap、goal、compound 等所有人读报告都用中文表达。
- 默认语言以 `.codestable/attention.md` 的「报告语言」节为准（onboard 模板默认中文）；只有 attention 显式改写默认语言时才以 attention 为准。
- 机器状态（YAML / JSON / `state.yaml` / frontmatter 字段）保持机读格式不翻译，不从不同语言的叙述反推状态。
- 默认只写 canonical 报告文件；只有 attention 明确要求多语言副本时，才额外写 `{name}.{lang}.md`。

## 9. 执行约定

实现预检、code review、review evidence、context packet、commit planner 和 subagent 选择拆在 `.codestable/reference/execution-conventions.md`，approval 报告口径在 `approval-conventions.md`。

- **不要让 AI 为了推进当前 workflow 随意切换分支**——需要切换分支、合并、发布或清理长期状态时，先取得 owner 明确确认，并把授权记录到对应 approval report。
