#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
TEXT_CODE_BLOCK_RE = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
PLACEHOLDER_RE = re.compile(r"\{([A-Z0-9_]+)\}")
MODEL_RE = re.compile(r"^model:\s*(.+?)\s*$", re.MULTILINE)
READONLY_RE = re.compile(r"^readonly:\s*(.+?)\s*$", re.MULTILINE)
PREDEFINED_HIGH_REASONING_MODELS = frozenset(
    {
        "gpt-5.6-sol[reasoning=max]",
    }
)


@dataclass(frozen=True)
class RuntimeCapabilities:
    exposed_named_agents: tuple[str, ...] = ()
    supports_generic_subagent: bool = False
    supports_model_selection: bool = False
    generic_subagent_inherits_parent_model: bool = False
    supports_readonly_subagent: bool = True


@dataclass(frozen=True)
class AgentContract:
    body: str
    model: str | None
    readonly: bool


@dataclass(frozen=True)
class DispatchPlan:
    dispatch_kind: str
    logical_agent_type: str
    dispatch_target: str | None
    readonly: bool
    requested_model: str | None
    model_handling: str
    bridge_message: str | None
    unavailable_reason: str | None


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def is_predefined_high_reasoning_model(model: str | None) -> bool:
    if model is None:
        return False

    normalized_model = model.strip().lower()
    return normalized_model in PREDEFINED_HIGH_REASONING_MODELS


def load_agent_contract(agent_prompt_path: Path) -> AgentContract:
    raw_text = agent_prompt_path.read_text(encoding="utf-8")
    frontmatter_match = FRONTMATTER_RE.match(raw_text)
    frontmatter = frontmatter_match.group(1) if frontmatter_match else ""
    body = raw_text[frontmatter_match.end() :].lstrip() if frontmatter_match else raw_text

    model_match = MODEL_RE.search(frontmatter)
    readonly_match = READONLY_RE.search(frontmatter)

    declared_model = model_match.group(1).strip().strip('"\'') if model_match else None
    declared_readonly = parse_bool(readonly_match.group(1)) if readonly_match else False

    return AgentContract(body=body, model=declared_model, readonly=declared_readonly)


def extract_task_template_body(task_template_path: Path) -> str:
    template_markdown = task_template_path.read_text(encoding="utf-8")
    text_blocks = TEXT_CODE_BLOCK_RE.findall(template_markdown)
    if not text_blocks:
        raise ValueError(f"No ```text``` block found in {task_template_path}")
    return text_blocks[-1].strip() + "\n"


def fill_placeholders(template_body: str, placeholder_values: Mapping[str, str]) -> str:
    placeholder_names = sorted(set(PLACEHOLDER_RE.findall(template_body)))
    missing_names = [name for name in placeholder_names if name not in placeholder_values]
    if missing_names:
        missing_list = ", ".join(missing_names)
        raise ValueError(f"Missing placeholder values: {missing_list}")

    filled_body = template_body
    for placeholder_name in placeholder_names:
        filled_body = filled_body.replace("{" + placeholder_name + "}", placeholder_values[placeholder_name])
    return filled_body


def build_native_bridge_message(agent_body: str, filled_task_body: str) -> str:
    return (
        "Your task is to perform the following. Follow the instructions below exactly.\n\n"
        "<agent-instructions>\n"
        f"{agent_body.rstrip()}\n"
        "</agent-instructions>\n\n"
        "<task-instructions>\n"
        f"{filled_task_body.rstrip()}\n"
        "</task-instructions>\n\n"
        "Execute this now. Output ONLY the structured response requested above.\n"
    )


def resolve_task_agent_dispatch(
    logical_agent_type: str,
    agent_prompt_path: Path,
    task_template_path: Path,
    placeholder_values: Mapping[str, str],
    runtime_capabilities: RuntimeCapabilities,
) -> DispatchPlan:
    agent_contract = load_agent_contract(agent_prompt_path)
    has_safe_predefined_model = is_predefined_high_reasoning_model(agent_contract.model)

    if (
        logical_agent_type in runtime_capabilities.exposed_named_agents
        and agent_contract.readonly
        and has_safe_predefined_model
    ):
        return DispatchPlan(
            dispatch_kind="named_task_agent",
            logical_agent_type=logical_agent_type,
            dispatch_target=logical_agent_type,
            readonly=agent_contract.readonly,
            requested_model=agent_contract.model,
            model_handling="plugin_model_honored",
            bridge_message=None,
            unavailable_reason=None,
        )

    if runtime_capabilities.supports_generic_subagent and runtime_capabilities.supports_readonly_subagent:
        task_template_body = extract_task_template_body(task_template_path)
        filled_task_body = fill_placeholders(task_template_body, placeholder_values)
        bridge_message = build_native_bridge_message(agent_contract.body, filled_task_body)

        if runtime_capabilities.supports_model_selection and has_safe_predefined_model:
            requested_model = agent_contract.model
            model_handling = "plugin_model_honored"
        elif runtime_capabilities.generic_subagent_inherits_parent_model:
            requested_model = None
            model_handling = "parent_model_inherited"
        else:
            unavailable_reason = (
                "Reviewer model cannot be pinned to a predefined high-reasoning model, "
                "and parent-model inheritance is not guaranteed"
            )
            return DispatchPlan(
                dispatch_kind="self_review_fallback",
                logical_agent_type=logical_agent_type,
                dispatch_target=None,
                readonly=True,
                requested_model=None,
                model_handling="self_review_current_model",
                bridge_message=None,
                unavailable_reason=unavailable_reason,
            )

        return DispatchPlan(
            dispatch_kind="native_subagent_bridge",
            logical_agent_type=logical_agent_type,
            dispatch_target="generalPurpose",
            readonly=True,
            requested_model=requested_model,
            model_handling=model_handling,
            bridge_message=bridge_message,
            unavailable_reason=None,
        )

    unavailable_reason = "Runtime does not expose a named task agent or a readonly generic subagent bridge"
    return DispatchPlan(
        dispatch_kind="self_review_fallback",
        logical_agent_type=logical_agent_type,
        dispatch_target=None,
        readonly=True,
        requested_model=None,
        model_handling="self_review_current_model",
        bridge_message=None,
        unavailable_reason=unavailable_reason,
    )


def parse_placeholder_values(values: list[str]) -> dict[str, str]:
    parsed_values: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Placeholder must use KEY=VALUE syntax: {value}")
        key, raw_value = value.split("=", 1)
        parsed_values[key] = raw_value
    return parsed_values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve a CodeStable Task-agent contract into a runtime dispatch plan.")
    parser.add_argument("--logical-agent-type", required=True, help="Logical agent type, for example codestable-code-reviewer.")
    parser.add_argument("--agent-prompt-file", required=True, help="Path to the plugin-level agent prompt markdown file.")
    parser.add_argument("--task-template-file", required=True, help="Path to the skill-local task template markdown file.")
    parser.add_argument("--named-agent", action="append", default=[], help="Named agents exposed by the runtime. Repeat as needed.")
    parser.add_argument("--supports-generic-subagent", action="store_true", help="Whether the runtime exposes a generic Subagent tool.")
    parser.add_argument("--supports-model-selection", action="store_true", help="Whether the runtime allows selecting a subagent model.")
    parser.add_argument(
        "--generic-subagent-inherits-parent-model",
        action="store_true",
        help="Whether an unpinned generic subagent is guaranteed to inherit the parent agent model.",
    )
    parser.add_argument("--no-readonly-subagent", action="store_true", help="Use when the runtime cannot launch readonly subagents.")
    parser.add_argument("--placeholder", action="append", default=[], help="Placeholder replacement in KEY=VALUE form. Repeat as needed.")
    parser.add_argument("--json", action="store_true", help="Print the resolved plan as JSON.")
    args = parser.parse_args(argv)

    placeholder_values = parse_placeholder_values(args.placeholder)
    runtime_capabilities = RuntimeCapabilities(
        exposed_named_agents=tuple(args.named_agent),
        supports_generic_subagent=args.supports_generic_subagent,
        supports_model_selection=args.supports_model_selection,
        generic_subagent_inherits_parent_model=args.generic_subagent_inherits_parent_model,
        supports_readonly_subagent=not args.no_readonly_subagent,
    )

    plan = resolve_task_agent_dispatch(
        logical_agent_type=args.logical_agent_type,
        agent_prompt_path=Path(args.agent_prompt_file),
        task_template_path=Path(args.task_template_file),
        placeholder_values=placeholder_values,
        runtime_capabilities=runtime_capabilities,
    )

    if args.json:
        print(json.dumps(asdict(plan), indent=2, ensure_ascii=False))
    else:
        print(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
