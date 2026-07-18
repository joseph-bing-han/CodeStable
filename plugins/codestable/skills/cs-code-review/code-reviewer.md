# CodeStable Code Review Agent Task Template

Use this template when dispatching the CodeStable reviewer subagent.

Dispatch order (full runtime mapping in `.codestable/reference/tools.md` → Subagent Runtime Mapping):

1. Preferred Cursor subagent: use `codestable-code-reviewer` and fill this template.
2. Native runtime bridge: if the runtime cannot explicitly invoke that custom subagent but does expose a generic `Subagent` tool, read `plugins/codestable/agents/code-reviewer.md`, fill this template, and launch a `readonly: true` `generalPurpose` subagent with the combined message only when the runtime can request the current conversation model at its highest thinking level, or it explicitly guarantees that an unpinned subagent inherits the current parent model.
3. If neither model-safe bridge condition is true, perform review with the current main model at its highest thinking level and record `reviewer: self`.

The reviewer must run at the highest thinking level of the current conversation model (Opus 4.8 → `max`, `gpt-5.6-sol` → `xhigh`). Never use `Explore`, `explorer`, a Fast model preset, `model: fast`, or an unknown-model bridge for this review gate; those downgrade the review to a low-budget heterogeneous model and are a fail-closed violation.

**Dispatch code-reviewer subagent:**
Use the `codestable-code-reviewer` subagent with the filled template. If unavailable, use the native bridge described below.

The reviewer must receive work-product context only. Do not paste the current conversation history.

Do not call a literal `codestable:code-reviewer` Task tool in Cursor. Cursor registers this plugin reviewer as the hyphenated custom subagent `codestable-code-reviewer`; the colon form is only a legacy logical contract name and is not the default executable name.

For the native runtime bridge, wrap the filled task body below together with the full contents of `plugins/codestable/agents/code-reviewer.md`, for example:

```text
Your task is to perform a CodeStable code review. Follow the instructions below exactly.

<agent-instructions>
[paste plugins/codestable/agents/code-reviewer.md body]
</agent-instructions>

<review-task>
[paste the filled template below]
</review-task>

Execute this now. Output ONLY the structured response requested by the review task.
```

```text
Your task is to perform a CodeStable code review. Follow the instructions below exactly.

<review-instructions>
You are reviewing completed work for production readiness before the main agent writes the final CodeStable review report.

You are read-only:
- Do not modify files.
- Do not update CodeStable checklist, design, task, QA, or acceptance files.
- Do not write the final `{slug}-review.md`; return findings to the main agent.

## What Was Implemented

{DESCRIPTION}

## Requirements / Plan

{PLAN_OR_REQUIREMENTS}

## CodeStable Context

- Workflow source: {WORKFLOW_SOURCE}
- Preferred Cursor subagent: `codestable-code-reviewer`
- Expected reviewer thinking budget: the current conversation model at its highest thinking level (Opus 4.8 → `max`, `gpt-5.6-sol` → `xhigh`), as described by `plugins/codestable/agents/code-reviewer.md`
- Native bridge executor: readonly `generalPurpose` subagent with `plugins/codestable/agents/code-reviewer.md`
- Model fallback rule: request the current main model at its highest thinking level when selectable; otherwise use a bridge only when parent-model inheritance is guaranteed; otherwise perform self review with the current main model at its highest thinking level. Never fall back to Explore, Fast, or unknown-model presets.
- Review report target: {REVIEW_REPORT_PATH}
- Task spine: {TASK_SPINE_PATH}
- Relevant spec files: {SPEC_PATHS}

## Git Material To Review

{GIT_MATERIAL}

If a git range is supplied, review that range. Otherwise, review the current working tree diff and staged diff from the material above.

## Changed / Untracked Files To Inspect

{CHANGED_FILE_CONTENTS}

If `git status --short` lists untracked files that are part of this work, inspect their content explicitly. Do not assume `git diff` includes untracked files. State which untracked files you reviewed.

## What To Check

### Plan alignment
- Does the implementation match the plan / requirements?
- Are deviations justified improvements, or problematic departures?
- Is all planned functionality present?
- Did the implementation quietly expand scope?

### Code quality
- Clean separation of concerns?
- Proper error handling?
- Type safety where applicable?
- DRY without premature abstraction?
- Edge cases handled?

### Architecture
- Sound design decisions?
- Reasonable scalability and performance?
- Security concerns?
- Integrates cleanly with surrounding code?
- Avoids new reverse dependencies or layer violations?

### Testing
- Tests verify real behavior, not implementation details only?
- Edge cases covered?
- Integration tests where they matter?
- Existing tests still meaningful?

### Production readiness
- Migration strategy if schema changed?
- Backward compatibility considered where relevant?
- Documentation / CodeStable follow-up complete?
- No obvious bugs, data loss, permission leaks, or operational risks?

## Severity Calibration

Use this severity scale in your raw output:

- Critical: must fix before QA / merge. Bugs, security issues, data loss risks, broken requirements, unreliable acceptance path.
- Important: should fix before proceeding. Architecture problems, missing requirement pieces, poor error handling, meaningful test gaps.
- Minor: nice to have. Style, clarity, small optimizations, documentation polish.

Categorize by actual severity. Not everything is Critical.

## Output Format

### Strengths
[What's well done? Be specific.]

### Issues

#### Critical (Must Fix)
[Bugs, security issues, data loss risks, broken functionality]

#### Important (Should Fix)
[Architecture problems, missing features, poor error handling, test gaps]

#### Minor (Nice to Have)
[Code style, optimization opportunities, documentation polish]

For each issue:
- File:line reference, or the most precise repository evidence available
- What's wrong
- Why it matters
- How to fix, if not obvious

### Recommendations
[Improvements for code quality, architecture, or process]

### Test And QA Focus
[Scenarios QA must verify, tests to add or strengthen, and points review cannot fully confirm]

### Assessment

**Ready to proceed?** [Yes | No | With fixes]

**Reasoning:** [1-2 sentence technical assessment]

## Critical Rules

DO:
- Categorize by actual severity.
- Be specific and evidence-based.
- Explain why each issue matters.
- Acknowledge strengths.
- Give a clear verdict.

DON'T:
- Say "looks good" without checking.
- Mark nitpicks as Critical.
- Give feedback on code you did not actually read.
- Be vague, such as "improve error handling" with no path or failure mode.
- Avoid giving a clear verdict.
</review-instructions>

Execute this now. Output ONLY the structured response following the format specified above.
```

## Placeholder Meanings

- `{DESCRIPTION}`: brief summary of what was built.
- `{PLAN_OR_REQUIREMENTS}`: spec paths, task text, or requirements.
- `{WORKFLOW_SOURCE}`: feature, feature-ff, issue, refactor, refactor-ff, ad-hoc, or pre-merge.
- `{REVIEW_REPORT_PATH}`: final CodeStable review report path that the main agent will write.
- `{TASK_SPINE_PATH}`: active Task path, or `none` for ad-hoc / pre-merge.
- `{SPEC_PATHS}`: relevant CodeStable design/report/fix-note/checklist paths.
- `{GIT_MATERIAL}`: status, diff, staged diff, or explicit base/head range.
- `{CHANGED_FILE_CONTENTS}`: contents or path list for changed files not fully represented in `git diff`, especially untracked files.
