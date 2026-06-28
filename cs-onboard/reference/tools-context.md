# CodeStable Context And Commit Tools

This file is copied by `cs-onboard` to
`.codestable/reference/tools-context.md`. It extends `tools.md` with the context,
commit planning, and backlog tools.

## 1. build-context-packet.py

Generates a durable context packet for a next-stage agent, reviewer, human
reviewer, owner, or learner without copying the full chat history.

```bash
python3 .codestable/tools/build-context-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --audience handoff --output /tmp/codestable-handoff.md \
  --decided "Use staged review packets" \
  --rejected "Do not adopt full Team pipeline" \
  --risk "Verification can be skipped if no gate enforces evidence" \
  --remaining "Run maintainer verifier after push" \
  --evidence "uvx --with pytest pytest -> passed"
```

Audiences:

- `handoff`: next-stage agent / reviewer context, fixed six-section shape.
- `human-reviewer`: full context report for human review.
- `owner-decision` / `owner-judgment`: auxiliary context for decisions, never a
  replacement for `approval-report.md`.
- `learner`: learning report context.
- `interviewee`: real interview / retrospective outline.

For owner approval checkpoints, first write the unit's `approval-report.md` per
`approval-conventions.md`. If a context packet is useful, attach or reference it
as evidence instead of creating `*-owner-context.md` as the approval surface.

Handoff output sections:

- `Decided`
- `Rejected`
- `Risks`
- `Files`
- `Remaining`
- `Evidence`

Non-handoff audiences output `Decision Brief`, `Working Context`, and
`Evidence Appendix`. Map `.codestable/attention.md` to a supported `--language`
value (`en` or `zh`). When the project's report language policy is not
supported by the tool, adapt the generated packet into the project language
before sharing it. Secret-like paths and tokens are redacted.

## 2. check-context-sufficiency.py

Checks generated handoff / audience reports for recognizable structure,
secret-like text, concrete files, and evidence.

```bash
python3 .codestable/tools/check-context-sufficiency.py --file /tmp/codestable-human-review.md --strict --json
```

Use before dispatching a human reviewer / subagent reviewer, or before sharing a
context packet as evidence in an approval report.

## 3. plan-commits.py

Read-only commit planner. It groups dirty paths by logical bucket and flags
migration doc-sync, runbook doc-sync, tracked ignored files, large files, and
live writers. It does not stage or commit.

```bash
python3 .codestable/tools/plan-commits.py --root . --json
```

Common buckets: `code`, `tests`, `docs`, `migrations`, `database_docs`, `data`,
`logs`, `codestable`, `installed_skill`, `unknown`.

## 4. codestable-backlog.py

Scans `.codestable/` for human-review and follow-up backlog before final
reporting.

```bash
python3 .codestable/tools/codestable-backlog.py --root . --json
```

It reports `needs-human-review`, `Human review required`, explicit `Follow-up:`
lines, `## Follow-Ups` bullets, accepted / deferred P2, and `attention.md`
candidates. It skips `.codestable/reference/` and `*-review-packet.md`, ignores
resolved follow-up records, and treats canceled lifecycle files as history.
