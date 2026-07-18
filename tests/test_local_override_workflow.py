from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins/codestable/skills"
TOOLS = SKILLS / "cs-onboard/tools"
sys.path.insert(0, str(TOOLS))


def load_workflow_next():
    module_path = TOOLS / "codestable-workflow-next.py"
    specification = importlib.util.spec_from_file_location("local_override_workflow_next", module_path)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


workflow_next = load_workflow_next()

import codestable_common


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def stamp_review_shas(root: Path, review_path: Path, task: str) -> None:
    """Backfill a review report's content-binding SHAs with real repository values.

    ``review_gate_passed`` enforces ``review_evidence_matches_repository`` while the
    unit still has an active Task. Test fixtures that keep an active Task must
    therefore carry the SHAs actually computed from the repository, not the
    ``"0" * 64`` placeholder, otherwise the gate correctly rejects them as stale/
    forged evidence.
    """
    task_sha = codestable_common.task_generation_sha256(root, task)
    basis_sha = codestable_common.review_basis_sha256(root, review_path)
    text = review_path.read_text(encoding="utf-8")
    text = text.replace(f'task_generation_sha256: "{"0" * 64}"', f'task_generation_sha256: "{task_sha}"')
    text = text.replace(f'review_basis_sha256: "{"0" * 64}"', f'review_basis_sha256: "{basis_sha}"')
    review_path.write_text(text, encoding="utf-8")


def complete_result() -> dict[str, object]:
    return {
        "ok": True,
        "workflow": "feature",
        "status": "complete",
        "next_action": "CS_FEATURE_QUICK_COMPLETE",
        "reason": "review passed",
        "must_continue": False,
        "final_answer_allowed": True,
        "blocking": [],
        "warnings": [],
        "missing_artifacts": [],
        "evidence": {},
    }


def task_document(task: str, status: str) -> str:
    return (
        "---\n"
        "doc_type: task-list\n"
        f"task: {task}\n"
        f"status: {status}\n"
        "---\n"
    )


def runtime_task_document(
    task: str,
    status: str,
    *,
    workflow: str = "feature",
    owner_skill: str = "cs-feat",
    created: str = "2026-07-17",
    updated: str = "2026-07-17",
) -> str:
    return (
        "---\n"
        "doc_type: task-list\n"
        f"task: {task}\n"
        f"goal: Complete {task}\n"
        f"status: {status}\n"
        f"workflow: {workflow}\n"
        f"owner_skill: {owner_skill}\n"
        f"created: {created}\n"
        f"updated: {updated}\n"
        "archived: null\n"
        "related_docs: []\n"
        "---\n\n"
        f"# Complete {task}\n\n"
        "## 1. 任务目标\n\nComplete the task.\n\n"
        f"## 2. 当前状态\n\n{status}\n\n"
        "## 3. Agent 原生 Tasks 同步区\n\n- [x] Complete implementation\n\n"
        "## 4. CodeStable 文档索引\n\n无。\n\n"
        "## 5. 执行步骤\n\n无。\n\n"
        "## 6. 中断恢复提示\n\n无。\n\n"
        "## 7. 完成与归档记录\n\nReady.\n"
    )


def create_valid_archive(
    root: Path,
    task: str,
    *,
    workflow: str = "feature",
    owner_skill: str = "cs-feat",
) -> None:
    content_path = root / "task-content.md"
    content_path.write_text(
        runtime_task_document(
            task,
            "completed",
            workflow=workflow,
            owner_skill=owner_skill,
        ),
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            str(TOOLS / "codestable-task-runtime.py"),
            "--root",
            str(root),
            "write-active",
            "--task",
            task,
            "--content-file",
            str(content_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(TOOLS / "codestable-task-runtime.py"),
            "--root",
            str(root),
            "archive",
            "--task",
            task,
            "--date",
            "2026-07-17",
            "--stability-checks",
            "1",
            "--stability-delay-ms",
            "0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def write_canonical_review(unit_dir: Path, workflow: str) -> None:
    slug = unit_dir.name.split("-", 3)[-1]
    write(
        unit_dir / f"{slug}-review.md",
        "---\n"
        f"doc_type: {workflow}-review\n"
        f"{workflow}: {unit_dir.name}\n"
        "status: passed\n"
        "round: 1\n"
        "reviewer: subagent\n"
        "reviewer_state: completed\n"
        'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n'
        "reviewer_provider: openai\n"
        "reviewer_model: gpt-5.6-sol\n"
        "reviewer_reasoning: xhigh\n"
        "reviewer_readonly: true\n"
        f'task_generation_sha256: "{"0" * 64}"\n'
        f'review_basis_sha256: "{"0" * 64}"\n'
        "---\n\n"
        "# Review\n",
    )


def write_completed_issue_evidence(issue_dir: Path) -> None:
    slug = issue_dir.name.split("-", 3)[-1]
    for suffix, doc_type in (
        ("report", "issue-report"),
        ("analysis", "issue-analysis"),
        ("fix-note", "issue-fix"),
    ):
        write(
            issue_dir / f"{slug}-{suffix}.md",
            "---\n"
            f"doc_type: {doc_type}\n"
            f"issue: {issue_dir.name}\n"
            "status: confirmed\n"
            "---\n",
        )
    write_canonical_review(issue_dir, "issue")


def write_completed_refactor_evidence(refactor_dir: Path) -> None:
    slug = refactor_dir.name.split("-", 3)[-1]
    write(
        refactor_dir / f"{slug}-refactor-design.md",
        "---\n"
        "doc_type: refactor-design\n"
        f"refactor: {refactor_dir.name}\n"
        "status: approved\n"
        "---\n",
    )
    write(
        refactor_dir / f"{slug}-checklist.yaml",
        f"refactor: {refactor_dir.name}\nsteps:\n  - id: apply\n    status: done\n",
    )
    write(
        refactor_dir / f"{slug}-apply-notes.md",
        "---\n"
        "doc_type: refactor-apply-notes\n"
        f"refactor: {refactor_dir.name}\n"
        "status: completed\n"
        "---\n",
    )
    write_canonical_review(refactor_dir, "refactor")


def test_complete_workflow_backfills_missing_task(tmp_path: Path) -> None:
    feature = tmp_path / ".codestable/features/2026-07-17-safe-change"
    feature.mkdir(parents=True)

    result = workflow_next.enforce_task_archive_gate(complete_result(), feature)

    assert result["status"] == "continue"
    assert result["next_action"] == "cs-task backfill"
    assert result["final_answer_allowed"] is False


def test_complete_workflow_archives_completed_active_task(tmp_path: Path) -> None:
    feature = tmp_path / ".codestable/features/2026-07-17-safe-change"
    feature.mkdir(parents=True)
    write(
        tmp_path / ".codestable/tasks/active/safe-change.md",
        task_document("safe-change", "completed"),
    )

    result = workflow_next.enforce_task_archive_gate(complete_result(), feature)

    assert result["status"] == "continue"
    assert result["next_action"] == "cs-task archive"
    assert result["final_answer_allowed"] is False


def test_complete_workflow_exits_only_after_verified_archive_without_active_residue(tmp_path: Path) -> None:
    feature = tmp_path / ".codestable/features/2026-07-17-safe-change"
    feature.mkdir(parents=True)
    create_valid_archive(tmp_path, "safe-change")

    result = workflow_next.enforce_task_archive_gate(complete_result(), feature)

    assert result["status"] == "complete"
    assert result["final_answer_allowed"] is True


def test_complete_workflow_blocks_archived_file_without_tombstone(tmp_path: Path) -> None:
    feature = tmp_path / ".codestable/features/2026-07-17-safe-change"
    feature.mkdir(parents=True)
    write(
        tmp_path / ".codestable/tasks/archived/2026-07-17-safe-change.md",
        task_document("safe-change", "archived"),
    )

    result = workflow_next.enforce_task_archive_gate(complete_result(), feature)

    assert result["status"] == "blocked"
    assert result["next_action"] == "resolve-task-archive-integrity"


def test_complete_workflow_blocks_archived_hash_mismatch(tmp_path: Path) -> None:
    feature = tmp_path / ".codestable/features/2026-07-17-safe-change"
    feature.mkdir(parents=True)
    create_valid_archive(tmp_path, "safe-change")
    archived_path = tmp_path / ".codestable/tasks/archived/2026-07-17-safe-change.md"
    archived_path.write_text(
        archived_path.read_text(encoding="utf-8").replace("Ready.", "Tampered."),
        encoding="utf-8",
    )

    result = workflow_next.enforce_task_archive_gate(complete_result(), feature)

    assert result["status"] == "blocked"
    assert "archived-target-integrity-failed" in " ".join(result["blocking"])


def test_complete_workflow_strips_date_prefix_for_issue_units(tmp_path: Path) -> None:
    """F-005 regression: archive gate must strip the YYYY-MM-DD prefix for every workflow.

    Previously only the ``feature`` workflow stripped the date prefix. Issue
    and refactor unit directories share the same naming, and using the full
    directory name as the Task slug left active Task residue invisible to the
    archive gate. The gate must look up ``{slug}.md`` (without date) regardless
    of the workflow family.
    """
    issue_result = {**complete_result(), "workflow": "issue"}
    issue_dir = tmp_path / ".codestable/issues/2026-07-17-bug-in-active-unit"
    issue_dir.mkdir(parents=True)
    write(
        tmp_path / ".codestable/tasks/active/bug-in-active-unit.md",
        task_document("bug-in-active-unit", "completed"),
    )

    result = workflow_next.enforce_task_archive_gate(issue_result, issue_dir)

    assert result["status"] == "continue"
    assert result["next_action"] == "cs-task archive"
    assert result["evidence"]["task"] == "bug-in-active-unit"


def test_complete_workflow_strips_date_prefix_for_refactor_units(tmp_path: Path) -> None:
    """F-005 paired regression: refactor workflow also strips the date prefix."""
    refactor_result = {**complete_result(), "workflow": "refactor"}
    refactor_dir = tmp_path / ".codestable/refactors/2026-07-17-skill-entry-cleanup"
    refactor_dir.mkdir(parents=True)
    write(
        tmp_path / ".codestable/tasks/active/skill-entry-cleanup.md",
        task_document("skill-entry-cleanup", "completed"),
    )

    result = workflow_next.enforce_task_archive_gate(refactor_result, refactor_dir)

    assert result["status"] == "continue"
    assert result["evidence"]["task"] == "skill-entry-cleanup"


def test_archive_gate_rejects_cross_workflow_archive_binding(tmp_path: Path) -> None:
    feature_dir = tmp_path / ".codestable/features/2026-07-17-safe-change"
    feature_dir.mkdir(parents=True)

    findings = workflow_next.archive_task_binding_findings(
        complete_result(),
        feature_dir,
        {
            "workflow": "issue",
            "task_status": "archived",
            "owner_skill": "cs-issue",
        },
    )

    assert any("does not match" in finding for finding in findings)
    assert any("not a final owner" in finding for finding in findings)


def test_archive_gate_rejects_non_final_archive_owner(tmp_path: Path) -> None:
    issue_dir = tmp_path / ".codestable/issues/2026-07-17-safe-change"
    issue_dir.mkdir(parents=True)
    issue_result = {**complete_result(), "workflow": "issue"}

    findings = workflow_next.archive_task_binding_findings(
        issue_result,
        issue_dir,
        {
            "workflow": "issue",
            "task_status": "archived",
            "owner_skill": "cs-task",
        },
    )

    assert findings == ["archived Task owner_skill 'cs-task' is not a final owner for issue"]


def test_review_runtime_has_no_third_party_review_commands() -> None:
    reviewed_paths = [
        SKILLS / "cs-code-review/SKILL.md",
        SKILLS / "cs-code-review/references/independent-review/protocol.md",
        SKILLS / "cs-onboard/SKILL.md",
        TOOLS / "codestable-doctor.py",
        TOOLS / "codestable-workflow-next.py",
    ]
    runtime_text = "\n".join(path.read_text(encoding="utf-8") for path in reviewed_paths)

    banned_runtime_markers = (
        "which ocr",
        "ocr review",
        "ocr_health",
        "open-code-review",
        "CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK",
        "REVIEW_FALLBACK_REVIEWERS",
    )
    assert all(marker not in runtime_text for marker in banned_runtime_markers)


def test_canonical_reviewer_set_rejects_legacy_only_values() -> None:
    """F-006 contract: gate must accept only the canonical reviewer value.

    Previous text-only assertions let `SUBAGENT_REVIEWERS = {"subagent",
    "subagent+ocr"}` slip through because they only scanned for banned
    substrings. This test pins the canonical set and asserts the gate rejects
    a fresh report that writes the legacy ``subagent+ocr`` value.
    """
    from codestable_common import CANONICAL_REVIEWERS, LEGACY_READABLE_REVIEWERS

    assert CANONICAL_REVIEWERS == frozenset({"subagent"})
    assert LEGACY_READABLE_REVIEWERS == frozenset({"subagent+ocr"})


def test_review_gate_passed_rejects_new_report_with_legacy_reviewer(tmp_path: Path) -> None:
    """F-006 mutation-style: a new report with reviewer: subagent+ocr must fail the gate.

    Replaces the previous text-contract test that scanned for specific OCR
    command strings. The contract under the local override reference is that
    new reports must carry ``reviewer: subagent``; historical ``subagent+ocr``
    reports stay readable but cannot pass the gate for an active unit.
    """
    legacy_unit = tmp_path / ".codestable/features/2026-07-17-legacy-review"
    legacy_review = legacy_unit / "legacy-review-review.md"
    legacy_review.parent.mkdir(parents=True)
    legacy_review.write_text(
        "---\n"
        "doc_type: feature-review\n"
        "feature: 2026-07-17-legacy-review\n"
        "status: passed\n"
        "round: 1\n"
        "reviewer: subagent+ocr\n"
        "reviewer_state: completed\n"
        'reviewer_ref: "legacy-reviewer-ref"\n'
        "---\n",
        encoding="utf-8",
    )
    canonical_unit = tmp_path / ".codestable/features/2026-07-17-canonical-review"
    canonical_review = canonical_unit / "canonical-review-review.md"
    canonical_review.parent.mkdir(parents=True)
    canonical_review.write_text(
        "---\n"
        "doc_type: feature-review\n"
        "feature: 2026-07-17-canonical-review\n"
        "status: passed\n"
        "round: 1\n"
        "reviewer: subagent\n"
        "reviewer_state: completed\n"
        'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n'
        "reviewer_provider: openai\n"
        "reviewer_model: gpt-5.6-sol\n"
        "reviewer_reasoning: xhigh\n"
        "reviewer_readonly: true\n"
        f'task_generation_sha256: "{"0" * 64}"\n'
        f'review_basis_sha256: "{"0" * 64}"\n'
        "---\n",
        encoding="utf-8",
    )
    legacy_meta = workflow_next.frontmatter(legacy_review)
    canonical_meta = workflow_next.frontmatter(canonical_review)

    assert workflow_next.review_gate_passed(legacy_review, legacy_meta) is False
    assert workflow_next.review_gate_passed(canonical_review, canonical_meta) is True


def test_review_gate_rejects_incomplete_or_typed_spoofed_lifecycle(tmp_path: Path) -> None:
    mutations = {
        "missing-round": "round: 1\n",
        "quoted-round": "round: 1\n",
        "missing-state": "reviewer_state: completed\n",
        "missing-ref": 'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n',
        "wrong-identity": "feature: 2026-07-17-wrong-unit\n",
        "duplicate-reviewer": "reviewer: subagent\n",
        # gate 不再硬编码模型，但已知需要显式档位的 gpt-5.6-sol 必须固定 xhigh。
        "sol-below-top-reasoning": "reviewer_reasoning: xhigh\n",
        # provider / model / reasoning 必须如实记录，留空视为伪填。
        "empty-model": "reviewer_model: gpt-5.6-sol\n",
        "empty-reasoning": "reviewer_reasoning: xhigh\n",
        "empty-provider": "reviewer_provider: openai\n",
        "missing-provider": "reviewer_provider: openai\n",
        "non-readonly": "reviewer_readonly: true\n",
        "non-uuid-ref": 'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n',
    }
    for mutation_name, removed_line in mutations.items():
        unit = tmp_path / ".codestable/features" / f"2026-07-17-{mutation_name}"
        slug = unit.name.split("-", 3)[-1]
        review_path = unit / f"{slug}-review.md"
        content = (
            "---\n"
            "doc_type: feature-review\n"
            f"feature: {unit.name}\n"
            "status: passed\n"
            "round: 1\n"
            "reviewer: subagent\n"
            "reviewer_state: completed\n"
            'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n'
            "reviewer_provider: openai\n"
            "reviewer_model: gpt-5.6-sol\n"
            "reviewer_reasoning: xhigh\n"
            "reviewer_readonly: true\n"
            f'task_generation_sha256: "{"0" * 64}"\n'
            f'review_basis_sha256: "{"0" * 64}"\n'
            "---\n"
        )
        if mutation_name == "quoted-round":
            content = content.replace("round: 1\n", 'round: "1"\n')
        elif mutation_name == "wrong-identity":
            content = content.replace(f"feature: {unit.name}\n", removed_line)
        elif mutation_name == "duplicate-reviewer":
            content = content.replace(
                "reviewer: subagent\n",
                "reviewer: self\nreviewer: subagent\n",
            )
        elif mutation_name == "sol-below-top-reasoning":
            content = content.replace(
                "reviewer_reasoning: xhigh\n",
                "reviewer_reasoning: high\n",
            )
        elif mutation_name == "empty-model":
            content = content.replace(
                "reviewer_model: gpt-5.6-sol\n",
                'reviewer_model: ""\n',
            )
        elif mutation_name == "empty-reasoning":
            content = content.replace(
                "reviewer_reasoning: xhigh\n",
                'reviewer_reasoning: ""\n',
            )
        elif mutation_name == "empty-provider":
            content = content.replace(
                "reviewer_provider: openai\n",
                'reviewer_provider: ""\n',
            )
        elif mutation_name == "non-readonly":
            content = content.replace(
                "reviewer_readonly: true\n",
                "reviewer_readonly: false\n",
            )
        elif mutation_name == "non-uuid-ref":
            content = content.replace(
                'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n',
                'reviewer_ref: "not-a-real-agent-ref"\n',
            )
        else:
            content = content.replace(removed_line, "")
        write(review_path, content)

        try:
            meta = workflow_next.frontmatter(review_path)
        except workflow_next.ArtifactParseError:
            # A strict-parse rejection (e.g. duplicate keys) is itself a
            # fail-closed outcome, which is what the gate must guarantee.
            continue

        assert workflow_next.review_gate_passed(review_path, meta) is False


def test_review_gate_accepts_non_sol_model_with_top_reasoning(tmp_path: Path) -> None:
    """去硬编码后，非 gpt-5.6-sol 模型只要如实记录 provider/model 和该模型最高思考等级即可通过。

    reviewer gate 不再要求固定 openai/gpt-5.6-sol；它接受任何如实记录的 reviewer 身份，
    只对 gpt-5.6-sol 强制 xhigh。这里用另一模型 + 其最高档 reasoning 验证放行。使用 opus 的
    最高档 ``max``（而非 ``high``），避免用非最高档为“降档可通过”背书。
    """
    unit = tmp_path / ".codestable/features/2026-07-17-alt-model-review"
    slug = unit.name.split("-", 3)[-1]
    review_path = unit / f"{slug}-review.md"
    write(
        review_path,
        "---\n"
        "doc_type: feature-review\n"
        f"feature: {unit.name}\n"
        "status: passed\n"
        "round: 1\n"
        "reviewer: subagent\n"
        "reviewer_state: completed\n"
        'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n'
        "reviewer_provider: anthropic\n"
        "reviewer_model: claude-opus-4.8\n"
        "reviewer_reasoning: max\n"
        "reviewer_readonly: true\n"
        f'task_generation_sha256: "{"0" * 64}"\n'
        f'review_basis_sha256: "{"0" * 64}"\n'
        "---\n",
    )

    meta = workflow_next.frontmatter(review_path)

    assert workflow_next.review_gate_passed(review_path, meta) is True


def test_review_gate_accepts_top_tier_models_that_contain_marker_substrings(tmp_path: Path) -> None:
    """降级标记必须按 token 段匹配，不能用裸子串误伤合法顶配模型。

    ``gemini-2.5-pro`` 含子串 ``mini``（ge+mini），``elite-*`` 含子串 ``lite``。若 gate
    用裸子串黑名单，会把整个 Gemini 家族（含顶配 gemini-pro）和其它合法模型误判成降级
    模型、永远 blocked，直接违反“当前对话主模型的可用最高档不得因此失败”的契约。这里
    断言这些合法顶配模型通过 gate。
    """
    passing_models = ("gemini-2.5-pro", "gemini-3-pro", "elite-model")
    for index, model_value in enumerate(passing_models):
        unit = tmp_path / ".codestable/features" / f"2026-07-17-marker-substr-{index}"
        slug = unit.name.split("-", 3)[-1]
        review_path = unit / f"{slug}-review.md"
        write(
            review_path,
            "---\n"
            "doc_type: feature-review\n"
            f"feature: {unit.name}\n"
            "status: passed\n"
            "round: 1\n"
            "reviewer: subagent\n"
            "reviewer_state: completed\n"
            'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n'
            "reviewer_provider: google\n"
            f"reviewer_model: {model_value}\n"
            "reviewer_reasoning: max\n"
            "reviewer_readonly: true\n"
            f'task_generation_sha256: "{"0" * 64}"\n'
            f'review_basis_sha256: "{"0" * 64}"\n'
            "---\n",
        )

        meta = workflow_next.frontmatter(review_path)

        assert workflow_next.review_gate_passed(review_path, meta) is True, model_value


def test_review_gate_rejects_fast_and_explore_reviewer_models(tmp_path: Path) -> None:
    """回归本次根因：Explore/Fast 预设模型（如 gpt-5.6-tera-high）不得充当 reviewer。

    这些预设正是 review 被静默降级到异构弱模型的根因，与思考档位高低无关——它换的是
    模型本身。散文契约声明“禁止 Explore/Fast”，gate 必须机械拒绝：模型名命中降级标记
    时，即便其它 canonical 字段齐全、reasoning 记为高档也不放行。

    注意：gate 不用通用档位名黑名单否决 reasoning。契约是“当前对话主模型的可用最高
    档”，某些模型只有单一档位，那个唯一档就是最高档，不应因档位名（如 low/medium）被
    机械否决。是否最高档由派发纪律与 REVIEWER_REASONING_OVERRIDES 保证。
    """
    forbidden_cases = {
        "explore-tera": ("gpt-5.6-tera-high", "high"),
        "fast-preset": ("some-fast-model", "high"),
        "flash-model": ("gemini-2.5-flash", "high"),
        "haiku-model": ("claude-haiku-4", "high"),
        "mini-model": ("gpt-5-mini", "high"),
        "nano-model": ("gpt-5-nano", "high"),
        "lite-model": ("gemini-2.0-lite", "high"),
    }
    for case_name, (model_value, reasoning_value) in forbidden_cases.items():
        unit = tmp_path / ".codestable/features" / f"2026-07-17-{case_name}"
        slug = unit.name.split("-", 3)[-1]
        review_path = unit / f"{slug}-review.md"
        write(
            review_path,
            "---\n"
            "doc_type: feature-review\n"
            f"feature: {unit.name}\n"
            "status: passed\n"
            "round: 1\n"
            "reviewer: subagent\n"
            "reviewer_state: completed\n"
            'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n'
            "reviewer_provider: openai\n"
            f"reviewer_model: {model_value}\n"
            f"reviewer_reasoning: {reasoning_value}\n"
            "reviewer_readonly: true\n"
            f'task_generation_sha256: "{"0" * 64}"\n'
            f'review_basis_sha256: "{"0" * 64}"\n'
            "---\n",
        )

        meta = workflow_next.frontmatter(review_path)

        assert workflow_next.review_gate_passed(review_path, meta) is False, case_name


def test_reviewer_reasoning_override_is_case_insensitive() -> None:
    """R6-I01 回归：gpt-5.6-sol 的 xhigh 强制不得被模型名大小写变体绕过。

    根因是 FORBIDDEN 标记匹配用小写、override 查表用原样大小写，导致
    "GPT-5.6-Sol" 之类变体跳过 xhigh 强制、只需 reasoning 非空即放行。归一化一次后
    大小写变体必须与规范小写行为一致：非 xhigh 一律拒绝，xhigh 才放行。
    """
    import codestable_common

    for model_variant in ("gpt-5.6-sol", "GPT-5.6-Sol", "gpt-5.6-SOL", "Gpt-5.6-Sol"):
        assert codestable_common.reviewer_reasoning_is_valid(model_variant, "low") is False, model_variant
        assert codestable_common.reviewer_reasoning_is_valid(model_variant, "medium") is False, model_variant
        assert codestable_common.reviewer_reasoning_is_valid(model_variant, "xhigh") is True, model_variant
        assert codestable_common.reviewer_reasoning_is_valid(model_variant, "XHIGH") is True, model_variant


def test_review_gate_rejects_sol_casing_variant_below_top_reasoning(tmp_path: Path) -> None:
    """R6-I01 端到端回归：review gate 必须拒绝 sol 大小写变体 + 非 xhigh 的证据。"""
    unit = tmp_path / ".codestable/features/2026-07-17-sol-casing-bypass"
    slug = unit.name.split("-", 3)[-1]
    review_path = unit / f"{slug}-review.md"
    write(
        review_path,
        "---\n"
        "doc_type: feature-review\n"
        f"feature: {unit.name}\n"
        "status: passed\n"
        "round: 1\n"
        "reviewer: subagent\n"
        "reviewer_state: completed\n"
        'reviewer_ref: "d11e7d51-96da-488d-9fb5-2cb68c9e0e0e"\n'
        "reviewer_provider: openai\n"
        "reviewer_model: GPT-5.6-Sol\n"
        "reviewer_reasoning: low\n"
        "reviewer_readonly: true\n"
        f'task_generation_sha256: "{"0" * 64}"\n'
        f'review_basis_sha256: "{"0" * 64}"\n'
        "---\n",
    )

    meta = workflow_next.frontmatter(review_path)

    assert workflow_next.review_gate_passed(review_path, meta) is False


def test_doctor_flags_active_unit_review_with_legacy_only_reviewer(tmp_path: Path) -> None:
    """F-006 follow-up: doctor must P1 an active unit whose review only carries legacy evidence.

    A fresh implementation batch must use the canonical reviewer. A unit with a
    historical-style ``reviewer: subagent+ocr`` cannot be considered reviewed
    for an active unit and must surface as a P1 finding.
    """
    import codestable_common

    feature_dir = tmp_path / ".codestable/features/2026-07-17-legacy-review-unit"
    feature_dir.mkdir(parents=True)
    (feature_dir / "legacy-review-unit-checklist.yaml").write_text(
        "steps:\n  - id: one\n    status: done\n",
        encoding="utf-8",
    )
    review_path = feature_dir / "legacy-review-unit-review.md"
    review_path.write_text(
        "---\n"
        "doc_type: feature-review\n"
        "status: passed\n"
        "reviewer: subagent+ocr\n"
        "---\n",
        encoding="utf-8",
    )

    findings = codestable_common.missing_review_findings(
        tmp_path,
        [codestable_common.unit_dir_for(".codestable/features/2026-07-17-legacy-review-unit")],
    )

    assert len(findings) == 1
    assert findings[0].severity == "P1"
    assert "canonical" in findings[0].message


def test_doctor_accepts_legacy_reviewer_only_for_historical_archived_unit(
    tmp_path: Path,
) -> None:
    import codestable_common

    feature_dir = tmp_path / ".codestable/features/2026-07-16-historical-review"
    feature_dir.mkdir(parents=True)
    write(
        feature_dir / "historical-review-checklist.yaml",
        "steps:\n  - id: one\n    status: done\n",
    )
    write(
        feature_dir / "historical-review-review.md",
        "---\n"
        "doc_type: feature-review\n"
        "feature: 2026-07-16-historical-review\n"
        "status: passed\n"
        "reviewer: subagent+ocr\n"
        "---\n",
    )
    archived_task = runtime_task_document(
        "historical-review",
        "completed",
        created="2026-07-16",
        updated="2026-07-16",
    )
    archived_task = archived_task.replace("status: completed", "status: archived", 1)
    archived_task = archived_task.replace("archived: null", "archived: 2026-07-16", 1)
    archived_task = archived_task.replace(
        "## 2. 当前状态\n\ncompleted",
        "## 2. 当前状态\n\narchived",
        1,
    )
    write(
        tmp_path / ".codestable/tasks/archived/2026-07-16-historical-review.md",
        archived_task,
    )

    findings = codestable_common.missing_review_findings(
        tmp_path,
        [Path(".codestable/features/2026-07-16-historical-review")],
    )

    assert findings == []


def test_doctor_accepts_legacy_issue_code_review_for_historical_archived_unit(
    tmp_path: Path,
) -> None:
    """Pre-canonical Issue review filenames remain valid historical evidence."""
    import codestable_common

    issue_dir = tmp_path / ".codestable/issues/2026-07-16-historical-issue-review"
    issue_dir.mkdir(parents=True)
    write(issue_dir / "historical-issue-review-fix-note.md", "# Historical fix\n")
    write(
        issue_dir / "historical-issue-review-code-review.md",
        "---\n"
        "doc_type: issue-review\n"
        "issue: 2026-07-16-historical-issue-review\n"
        "status: passed\n"
        "reviewer: subagent\n"
        "---\n",
    )
    archived_task = runtime_task_document(
        "historical-issue-review",
        "completed",
        workflow="issue",
        created="2026-07-16",
        updated="2026-07-16",
    )
    archived_task = archived_task.replace("status: completed", "status: archived", 1)
    archived_task = archived_task.replace("archived: null", "archived: 2026-07-16", 1)
    archived_task = archived_task.replace(
        "## 2. 当前状态\n\ncompleted",
        "## 2. 当前状态\n\narchived",
        1,
    )
    write(
        tmp_path / ".codestable/tasks/archived/2026-07-16-historical-issue-review.md",
        archived_task,
    )

    findings = codestable_common.missing_review_findings(
        tmp_path,
        [Path(".codestable/issues/2026-07-16-historical-issue-review")],
    )

    assert findings == []


def test_doctor_rejects_mismatched_legacy_issue_code_review_metadata(
    tmp_path: Path,
) -> None:
    """Legacy filenames relax only the filename, never schema or identity."""
    import codestable_common

    issue_dir = tmp_path / ".codestable/issues/2026-07-16-historical-issue-review"
    issue_dir.mkdir(parents=True)
    write(issue_dir / "historical-issue-review-fix-note.md", "# Historical fix\n")
    archived_task = runtime_task_document(
        "historical-issue-review",
        "completed",
        workflow="issue",
        created="2026-07-16",
        updated="2026-07-16",
    )
    archived_task = archived_task.replace("status: completed", "status: archived", 1)
    archived_task = archived_task.replace("archived: null", "archived: 2026-07-16", 1)
    archived_task = archived_task.replace(
        "## 2. 当前状态\n\ncompleted",
        "## 2. 当前状态\n\narchived",
        1,
    )
    write(
        tmp_path / ".codestable/tasks/archived/2026-07-16-historical-issue-review.md",
        archived_task,
    )

    for invalid_frontmatter in (
        "doc_type: feature-review\nissue: 2026-07-16-historical-issue-review\nreviewer: subagent",
        "doc_type: issue-review\nissue: 2026-07-16-other-issue\nreviewer: subagent",
        "doc_type: issue-review\nissue: 2026-07-16-historical-issue-review\nreviewer: self",
    ):
        write(
            issue_dir / "historical-issue-review-code-review.md",
            "---\n"
            f"{invalid_frontmatter}\n"
            "status: passed\n"
            "---\n",
        )

        findings = codestable_common.missing_review_findings(
            tmp_path,
            [Path(".codestable/issues/2026-07-16-historical-issue-review")],
        )

        assert len(findings) == 1
        assert findings[0].severity == "P1"


def test_doctor_rejects_legacy_reviewer_for_post_cutoff_archive(tmp_path: Path) -> None:
    import codestable_common

    feature_dir = tmp_path / ".codestable/features/2026-07-17-current-review"
    feature_dir.mkdir(parents=True)
    write(
        feature_dir / "current-review-checklist.yaml",
        "steps:\n  - id: one\n    status: done\n",
    )
    write(
        feature_dir / "current-review-review.md",
        "---\n"
        "doc_type: feature-review\n"
        "feature: 2026-07-17-current-review\n"
        "status: passed\n"
        "reviewer: subagent+ocr\n"
        "---\n",
    )
    archived_task = runtime_task_document("current-review", "completed")
    archived_task = archived_task.replace("status: completed", "status: archived", 1)
    archived_task = archived_task.replace("archived: null", "archived: 2026-07-17", 1)
    archived_task = archived_task.replace(
        "## 2. 当前状态\n\ncompleted",
        "## 2. 当前状态\n\narchived",
        1,
    )
    write(
        tmp_path / ".codestable/tasks/archived/2026-07-17-current-review.md",
        archived_task,
    )

    findings = codestable_common.missing_review_findings(
        tmp_path,
        [Path(".codestable/features/2026-07-17-current-review")],
    )

    assert len(findings) == 1
    assert findings[0].severity == "P1"


def test_doctor_rejects_body_spoofed_canonical_reviewer(tmp_path: Path) -> None:
    import codestable_common

    feature_dir = tmp_path / ".codestable/features/2026-07-17-body-spoof"
    feature_dir.mkdir(parents=True)
    (feature_dir / "body-spoof-checklist.yaml").write_text(
        "steps:\n  - id: one\n    status: done\n",
        encoding="utf-8",
    )
    (feature_dir / "body-spoof-review.md").write_text(
        "---\n"
        "doc_type: feature-review\n"
        "status: passed\n"
        "reviewer: self\n"
        "---\n\n"
        "```yaml\nreviewer: subagent\n```\n",
        encoding="utf-8",
    )

    findings = codestable_common.missing_review_findings(
        tmp_path,
        [Path(".codestable/features/2026-07-17-body-spoof")],
    )

    assert len(findings) == 1
    assert findings[0].severity == "P1"


def test_workflow_next_unit_cli_applies_issue_archive_gate(tmp_path: Path) -> None:
    issue_dir = tmp_path / ".codestable/issues/2026-07-17-cli-issue"
    issue_dir.mkdir(parents=True)
    write_completed_issue_evidence(issue_dir)
    write(
        tmp_path / ".codestable/tasks/active/cli-issue.md",
        runtime_task_document("cli-issue", "completed", workflow="issue", owner_skill="cs-issue"),
    )
    stamp_review_shas(tmp_path, issue_dir / "cli-issue-review.md", "cli-issue")

    completed = subprocess.run(
        [
            sys.executable,
            str(TOOLS / "codestable-workflow-next.py"),
            "unit",
            "--workflow",
            "issue",
            "--unit",
            str(issue_dir),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)

    assert result["status"] == "continue"
    assert result["next_action"] == "cs-task archive"
    assert result["evidence"]["task"] == "cli-issue"


def test_issue_next_does_not_archive_without_workflow_evidence(tmp_path: Path) -> None:
    issue_dir = tmp_path / ".codestable/issues/2026-07-17-empty-issue"
    issue_dir.mkdir(parents=True)
    write(
        tmp_path / ".codestable/tasks/active/empty-issue.md",
        task_document("empty-issue", "completed"),
    )

    result = workflow_next.issue_next(issue_dir)

    assert result["status"] == "continue"
    assert result["next_action"] == "cs-issue --stage report"
    assert result["next_action"] != "cs-task archive"


def test_issue_next_rejects_unconfirmed_workflow_evidence(tmp_path: Path) -> None:
    issue_dir = tmp_path / ".codestable/issues/2026-07-17-draft-issue"
    write_completed_issue_evidence(issue_dir)
    report_path = issue_dir / "draft-issue-report.md"
    report_path.write_text(
        report_path.read_text(encoding="utf-8").replace(
            "status: confirmed",
            "status: draft",
        ),
        encoding="utf-8",
    )

    result = workflow_next.issue_next(issue_dir)

    assert result["status"] == "blocked"
    assert result["next_action"] == "fix-issue-workflow-evidence"


def test_workflow_next_unit_cli_accepts_verified_refactor_archive(tmp_path: Path) -> None:
    refactor_dir = tmp_path / ".codestable/refactors/2026-07-17-cli-refactor"
    refactor_dir.mkdir(parents=True)
    write_completed_refactor_evidence(refactor_dir)
    create_valid_archive(
        tmp_path,
        "cli-refactor",
        workflow="refactor",
        owner_skill="cs-refactor",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(TOOLS / "codestable-workflow-next.py"),
            "unit",
            "--workflow",
            "refactor",
            "--unit",
            str(refactor_dir),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)

    assert result["status"] == "complete"
    assert result["final_answer_allowed"] is True


def test_refactor_next_does_not_archive_without_workflow_evidence(tmp_path: Path) -> None:
    refactor_dir = tmp_path / ".codestable/refactors/2026-07-17-empty-refactor"
    refactor_dir.mkdir(parents=True)
    create_valid_archive(tmp_path, "empty-refactor")

    result = workflow_next.refactor_next(refactor_dir)

    assert result["status"] == "continue"
    assert result["next_action"] == "cs-refactor --stage design"


def test_refactor_next_rejects_unapproved_design(tmp_path: Path) -> None:
    refactor_dir = tmp_path / ".codestable/refactors/2026-07-17-draft-refactor"
    write_completed_refactor_evidence(refactor_dir)
    design_path = refactor_dir / "draft-refactor-refactor-design.md"
    design_path.write_text(
        design_path.read_text(encoding="utf-8").replace(
            "status: approved",
            "status: draft",
        ),
        encoding="utf-8",
    )

    result = workflow_next.refactor_next(refactor_dir)

    assert result["status"] == "blocked"
    assert result["next_action"] == "fix-refactor-design-evidence"


def test_local_override_skills_and_entry_spines_are_packaged() -> None:
    assert (SKILLS / "cs-task/SKILL.md").is_file()
    assert (TOOLS / "codestable-task-runtime.py").is_file()

    for skill_name in ("cs-feat", "cs-issue", "cs-refactor", "cs-epic", "cs-goal"):
        skill_text = (SKILLS / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert "Task" in skill_text
        assert "cs-code-review" in skill_text

    audit_text = (SKILLS / "cs-audit/SKILL.md").read_text(encoding="utf-8")
    assert "纯扫描强制创建 Task" in audit_text
    assert "目标 workflow" in audit_text
