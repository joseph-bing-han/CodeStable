# CodeStable 运行时结构

`/cs-onboard` 跑完后，会在项目根生成 `.codestable/` 目录。它是 CodeStable 内部工作流工件的聚合根；对外指南和 API 参考默认仍在 `docs/`。

```text
你的项目/
├── .codestable/
│   ├── requirements/                     # 需求实体
│   │   └── {slug}.md                     # 一个能力一份，扁平不分组
│   │
│   ├── architecture/                     # 架构实体，只记现状
│   │   ├── ARCHITECTURE.md               # 架构总入口 / 索引
│   │   └── {type}-{slug}.md              # 子系统架构 doc
│   │
│   ├── roadmap/                          # 路线图
│   │   └── {slug}/
│   │       ├── {slug}-roadmap.md         # 主文档：背景 / 拆解 / 排期
│   │       ├── {slug}-items.yaml         # 子 feature 清单
│   │       └── drafts/                   # 可选：草稿 / 调研
│   │
│   ├── brainstorms/                      # brainstorm case 4 创意沉淀 / spike
│   │   └── {slug}/
│   │       └── brainstorm.md
│   │
│   ├── features/                         # 特性流程聚合根
│   │   └── YYYY-MM-DD-{slug}/
│   │       ├── {slug}-brainstorm.md      # 可选
│   │       ├── {slug}-design.md          # 方案
│   │       ├── {slug}-checklist.yaml     # 推进清单
│   │       ├── {slug}-acceptance.md      # 验收报告
│   │       ├── {slug}-ff-note.md         # 仅 fastforward，和 design/checklist/acceptance 互斥
│   │       └── {slug}-code-review.md     # 最终代码评审
│   │
│   ├── issues/                           # 问题流程聚合根
│   │   └── YYYY-MM-DD-{slug}/
│   │       ├── {slug}-report.md          # 问题报告
│   │       ├── {slug}-analysis.md        # 根因分析
│   │       ├── {slug}-fix-note.md        # 修复记录
│   │       └── {slug}-code-review.md     # 最终代码评审
│   │
│   ├── refactors/                        # 重构流程聚合根
│   │   └── YYYY-MM-DD-{slug}/
│   │       ├── {slug}-scan.md
│   │       ├── {slug}-refactor-design.md
│   │       ├── {slug}-checklist.yaml
│   │       ├── {slug}-apply-notes.md
│   │       └── {slug}-code-review.md     # refactor-ff 最少也会有这一份；refactor-note 可选
│   │
│   ├── tasks/                            # 任务运行账本（按需由 cs-task 初始化）
│   │   ├── active/
│   │   └── archived/
│   │
│   ├── compound/                         # 知识沉淀统一目录
│   │   └── YYYY-MM-DD-{doc_type}-{slug}.md
│   │
│   ├── tools/                            # 跨工作流共享脚本
│   └── reference/                        # 共享参考文档
│       ├── shared-conventions.md
│       ├── system-overview.md
│       └── ...
│
└── AGENTS.md                             # 项目根入口文件，不在 .codestable/ 内
```

## 要点

- 内部工作流工件聚在 `.codestable/` 下，便于按 feature、issue、refactor 回溯；对外文档默认走 `docs/`。
- `requirements/` 和 `architecture/` 是长效档案，`roadmap/` 是规划层。
- `features/`、`issues/`、`refactors/` 用 `YYYY-MM-DD-{slug}/` 一个目录装齐相关 spec。
- `cs-code-review` 在关联目录写 `{slug}-code-review.md`，作为 commit、PR、merge 前的最终质量门禁。
- `compound/` 是唯一知识沉淀目录，learning、trick、decision、explore 通过 `doc_type` 字段区分。
- `reference/` 由 `cs-onboard` 从技能包复制；共享口径应修改 `cs-onboard/reference/` 模板。
