# CodeStable Runtime Structure

After `/cs-onboard`, a `.codestable/` directory appears at the project root. It is the aggregate root for CodeStable internal workflow artifacts; outward-facing guides and API references still default to `docs/`.

```text
your-project/
├── .codestable/
│   ├── requirements/                     # Requirement entities
│   │   └── {slug}.md                     # One capability per file
│   │
│   ├── architecture/                     # Current architecture
│   │   ├── ARCHITECTURE.md               # Architecture entry point
│   │   └── {type}-{slug}.md              # Subsystem architecture doc
│   │
│   ├── roadmap/                          # Roadmaps
│   │   └── {slug}/
│   │       ├── {slug}-roadmap.md         # Main roadmap
│   │       ├── {slug}-items.yaml         # Sub-feature list
│   │       └── drafts/                   # Optional drafts
│   │
│   ├── brainstorms/                      # Brainstorm case-4 ideation / spikes
│   │   └── {slug}/
│   │       └── brainstorm.md
│   │
│   ├── features/                         # Feature flow aggregate root
│   │   └── YYYY-MM-DD-{slug}/
│   │       ├── {slug}-brainstorm.md      # Optional
│   │       ├── {slug}-design.md          # Design
│   │       ├── {slug}-checklist.yaml     # Progress checklist
│   │       ├── {slug}-acceptance.md      # Acceptance report
│   │       ├── {slug}-ff-note.md         # Fastforward only; mutually exclusive with design/checklist/acceptance
│   │       └── {slug}-code-review.md     # Final code review
│   │
│   ├── issues/                           # Issue flow aggregate root
│   │   └── YYYY-MM-DD-{slug}/
│   │       ├── {slug}-report.md          # Issue report
│   │       ├── {slug}-analysis.md        # Root-cause analysis
│   │       ├── {slug}-fix-note.md        # Fix note
│   │       └── {slug}-code-review.md     # Final code review
│   │
│   ├── refactors/                        # Refactor flow aggregate root
│   │   └── YYYY-MM-DD-{slug}/
│   │       ├── {slug}-scan.md
│   │       ├── {slug}-refactor-design.md
│   │       ├── {slug}-checklist.yaml
│   │       ├── {slug}-apply-notes.md
│   │       └── {slug}-code-review.md     # mandatory even for refactor-ff; refactor-note is optional
│   │
│   ├── tasks/                            # Task ledger (initialized on demand by cs-task)
│   │   ├── active/
│   │   └── archived/
│   │
│   ├── compound/                         # Unified knowledge sink
│   │   └── YYYY-MM-DD-{doc_type}-{slug}.md
│   │
│   ├── tools/                            # Cross-workflow scripts
│   └── reference/                        # Shared reference docs
│       ├── shared-conventions.md
│       ├── system-overview.md
│       └── ...
│
└── AGENTS.md                             # Project root entry file, outside .codestable/
```

## Key Points

- Internal workflow artifacts aggregate under `.codestable/` for fast feature, issue, and refactor lookup; outward-facing docs default to `docs/`.
- `requirements/` and `architecture/` are long-lived archives; `roadmap/` is the planning layer.
- `features/`, `issues/`, and `refactors/` use `YYYY-MM-DD-{slug}/` directories to keep related specs together.
- `cs-code-review` writes `{slug}-code-review.md` in the related directory as the final quality gate before commit, PR, or merge.
- `compound/` is the only knowledge sink; learning, trick, decision, and explore docs are separated by `doc_type`.
- `reference/` is copied by `cs-onboard`; shared conventions should be changed in `cs-onboard/reference/` templates.
