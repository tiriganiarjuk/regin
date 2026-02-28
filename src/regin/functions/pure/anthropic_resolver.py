"""Resolve universal-render into Anthropic platform render format.

Input: AgentUniversalRender (12 sections)
Output: AgentAnthropicRender (13 sections: 8 pass-through, 3 modified, 2 created)

8 transform steps per ANTHROPIC_RENDER_DESIGN.md.
"""

import json

from regin.structures.anthropic_render import (
    AgentAnthropicRender,
    AntiPatterns as AntiPatternsOut,
    Constraints as ConstraintsOut,
    CriticalRules,
    Dispatcher as DispatcherOut,
    DisplayEntry,
    DisplayEntries,
    DisplayTools,
    Examples as ExamplesOut,
    Frontmatter,
    FrontmatterTools,
    HookAction,
    HookActions,
    HookArguments,
    HooksConfig,
    IdentityAnthropic,
    Input as InputOut,
    Instructions as InstructionsOut,
    Output as OutputOut,
    ReturnFormat as ReturnFormatOut,
    SecurityBoundaryAnthropic,
    WritingOutputAnthropic,
)
from regin.structures.enums import Capability, CapabilityTier
from regin.structures.resolved_tool import ResolvedTool
from regin.structures.universal_render import (
    AgentUniversalRender,
    EnforcementExplicitGrants,
    EnforcementImplicitGrants,
    EnforcementOutputTool,
    Identity,
)
from regin.structures.tool_registry import ToolRegistryEntry
from regin.structures.vendor_lookup import ANTHROPIC
from regin.functions.pure.tool_discovery import discover_custom_tool


# ---------------------------------------------------------------------------
# Step 1: Model resolution
# ---------------------------------------------------------------------------

def resolve_model(capability_tier: str) -> str:
    """Map capability_tier enum value to vendor model name."""
    tier = CapabilityTier(capability_tier)
    return ANTHROPIC.tier_to_model[tier].value


# ---------------------------------------------------------------------------
# Step 3: Explode grants → tools × paths
# ---------------------------------------------------------------------------

def extract_capability_paths(
    grants: EnforcementExplicitGrants | EnforcementImplicitGrants,
) -> dict[Capability, list[str]]:
    """Extract {Capability: [path_str]} from a typed grants model."""
    result: dict[Capability, list[str]] = {}
    for cap in Capability:
        bucket = getattr(grants, cap.value, None)
        if bucket is not None:
            result[cap] = [path.root for path in bucket.root]
    return result


def explode_to_tool_paths(
    cap_paths: dict[Capability, list[str]],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Explode capability×paths into tool×paths and command×paths."""
    tool_paths: dict[str, set[str]] = {}
    command_paths: dict[str, set[str]] = {}
    for cap, paths in cap_paths.items():
        for tool in ANTHROPIC.capability_to_tools.get(cap, ()):
            tool_paths.setdefault(tool.value, set()).update(paths)
        for cmd in ANTHROPIC.capability_to_commands.get(cap, ()):
            command_paths.setdefault(cmd.value, set()).update(paths)
    return tool_paths, command_paths


def merge_path_sets(
    left: dict[str, set[str]],
    right: dict[str, set[str]],
) -> dict[str, set[str]]:
    """Merge two name→paths dicts, unioning path sets per name."""
    merged: dict[str, set[str]] = {}
    for key in set(left) | set(right):
        merged[key] = left.get(key, set()) | right.get(key, set())
    return merged


# ---------------------------------------------------------------------------
# Step 4: Security boundary display
# ---------------------------------------------------------------------------

def relativize_path(abs_path: str, workspace_prefix: str) -> str:
    """Strip workspace prefix, prepend ./ for relative path display."""
    if abs_path.startswith(workspace_prefix):
        return "./" + abs_path[len(workspace_prefix):]
    return abs_path


def build_display_entries(
    explicit_tools: dict[str, set[str]],
    explicit_commands: dict[str, set[str]],
    workspace_path: str,
) -> DisplayEntries:
    """Build display entries: explicit grants collapsed by relative path."""
    path_to_tools: dict[str, set[str]] = {}
    prefix = workspace_path.rstrip("/") + "/"
    all_grants = {**explicit_tools, **explicit_commands}
    for tool_or_cmd, paths in all_grants.items():
        for abs_path in paths:
            rel = relativize_path(abs_path, prefix)
            path_to_tools.setdefault(rel, set()).add(tool_or_cmd)
    entries = [
        DisplayEntry(path=rel, tools=DisplayTools(root=sorted(tools)))
        for rel, tools in sorted(path_to_tools.items())
    ]
    return DisplayEntries(root=entries)


# ---------------------------------------------------------------------------
# Step 5: Build hooks
# ---------------------------------------------------------------------------

def build_tool_hook_rules(
    merged_tools: dict[str, set[str]],
) -> list[HookAction]:
    """Build one hook rule per tool with dedicated allowed paths."""
    return [
        HookAction(
            matcher=tool_name,
            type="command",
            binary="hook_validate_tools",
            arguments=HookArguments(root=sorted(paths)),
        )
        for tool_name, paths in sorted(merged_tools.items())
    ]


def build_bash_hook_rule(
    merged_commands: dict[str, set[str]],
    custom_tool: ResolvedTool | None,
) -> HookAction | None:
    """Build a single Bash hook rule for commands + custom tool."""
    all_paths: list[str] = []
    if custom_tool:
        all_paths.append(custom_tool.tool_name)
    for cmd_name in sorted(merged_commands):
        for path in sorted(merged_commands[cmd_name]):
            all_paths.append(path)
    if not all_paths:
        return None
    return HookAction(
        matcher="Bash",
        type="command",
        binary="hook_validate_bash",
        arguments=HookArguments(root=all_paths),
    )


def build_hooks_config(
    merged_tools: dict[str, set[str]],
    merged_commands: dict[str, set[str]],
    custom_tool: ResolvedTool | None,
) -> HooksConfig:
    """Build Claude Code PreToolUse hook configuration."""
    rules = build_tool_hook_rules(merged_tools)
    bash_rule = build_bash_hook_rule(merged_commands, custom_tool)
    if bash_rule:
        rules.append(bash_rule)
    return HooksConfig(PreToolUse=HookActions(root=rules))


# ---------------------------------------------------------------------------
# Step 6: Compose frontmatter
# ---------------------------------------------------------------------------

def unwrap_root(value: object) -> object:
    """Unwrap nested RootModel wrappers to get the raw value."""
    while hasattr(value, "root"):
        value = value.root
    return value


def cross_boundary(source: object, target_type: type) -> object:
    """Convert a Pydantic model across schema boundaries via JSON roundtrip."""
    raw = json.loads(source.model_dump_json(by_alias=True, exclude_none=True))
    return target_type.model_validate(raw)


def build_frontmatter(
    model: AgentUniversalRender,
    vendor_model: str,
    merged_tools: dict[str, set[str]],
    hooks_config: HooksConfig,
) -> Frontmatter:
    """Compose frontmatter section for the TOML header."""
    tool_names = sorted(set(merged_tools.keys()) | {"Bash"})
    return Frontmatter(
        name=str(unwrap_root(model.identity.title)),
        description=str(unwrap_root(model.identity.description)),
        tools=FrontmatterTools(root=tool_names),
        model=vendor_model,
        permission_mode="bypassPermissions",
        hooks=hooks_config,
    )


# ---------------------------------------------------------------------------
# Step 7: Create critical rules
# ---------------------------------------------------------------------------

def build_critical_rules(
    workspace_path: str,
    custom_tool: ResolvedTool | None,
    output_tool: EnforcementOutputTool | None,
) -> CriticalRules:
    """Create the critical_rules section — end-of-lifecycle fields."""
    if custom_tool is None:
        return CriticalRules(
            workspace_path=workspace_path,
            has_output_tool=False,
        )
    return CriticalRules(
        workspace_path=workspace_path,
        has_output_tool=True,
        tool_name=custom_tool.tool_name,
        name_needed=(
            output_tool.enforcement_output_tool_name_needed
            if output_tool else None
        ),
        batch_size=(
            output_tool.enforcement_output_tool_batch_size
            if output_tool else None
        ),
    )


# ---------------------------------------------------------------------------
# Step 8: Populate writing output
# ---------------------------------------------------------------------------

def build_writing_output(
    custom_tool: ResolvedTool | None,
    output_tool: EnforcementOutputTool | None,
) -> WritingOutputAnthropic | None:
    """Build resolved writing_output section. None when no custom tool."""
    if custom_tool is None or output_tool is None:
        return None
    return WritingOutputAnthropic(
        tool_name=custom_tool.tool_name,
        invocation_variant=custom_tool.invocation_variant,
        invocation_display=custom_tool.invocation_display,
        name_needed=output_tool.enforcement_output_tool_name_needed,
        name_pattern=output_tool.enforcement_output_tool_name_pattern,
        batch_size=output_tool.enforcement_output_tool_batch_size,
        schema_path=output_tool.enforcement_output_tool_schema_path,
        file_path=output_tool.enforcement_output_tool_file_path,
        directory_path=output_tool.enforcement_output_tool_directory_path,
    )


# ---------------------------------------------------------------------------
# Identity builder
# ---------------------------------------------------------------------------

def build_identity_anthropic(
    identity: Identity,
    vendor_model: str,
) -> IdentityAnthropic:
    """Build identity_anthropic: replace capability_tier with model."""
    raw = json.loads(
        identity.model_dump_json(by_alias=True, exclude_none=True),
    )
    raw.pop("capability_tier", None)
    raw["model"] = vendor_model
    return IdentityAnthropic.model_validate(raw)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def resolve(
    universal_render_json: str,
    registry: tuple[ToolRegistryEntry, ...],
) -> str:
    """Resolve universal-render JSON into anthropic-render JSON."""
    model = AgentUniversalRender.model_validate_json(universal_render_json)

    output_tool = (
        model.writing_output.writing_output
        if model.writing_output else None
    )
    workspace_path = (
        model.security_boundary.workspace_path.root
        if model.security_boundary else ""
    )

    vendor_model = resolve_model(model.identity.capability_tier.value)
    custom_tool = discover_custom_tool(output_tool, registry, model)

    explicit_caps = extract_capability_paths(
        model.security_boundary.capabilities,
    ) if model.security_boundary else {}
    implicit_caps = extract_capability_paths(
        model.implicit_grants.capabilities,
    ) if model.implicit_grants else {}

    explicit_tools, explicit_commands = explode_to_tool_paths(explicit_caps)
    implicit_tools, implicit_commands = explode_to_tool_paths(implicit_caps)
    display = build_display_entries(
        explicit_tools, explicit_commands, workspace_path,
    )
    merged_tools = merge_path_sets(explicit_tools, implicit_tools)
    merged_commands = merge_path_sets(explicit_commands, implicit_commands)
    hooks_config = build_hooks_config(
        merged_tools, merged_commands, custom_tool,
    )

    result = AgentAnthropicRender(
        identity=build_identity_anthropic(model.identity, vendor_model),
        security_boundary=SecurityBoundaryAnthropic(
            has_grants=len(display.root) > 0,
            display=display,
        ),
        critical_rules=build_critical_rules(
            workspace_path, custom_tool, output_tool,
        ),
        frontmatter=build_frontmatter(
            model, vendor_model, merged_tools, hooks_config,
        ),
        input=cross_boundary(model.input, InputOut),
        output=cross_boundary(model.output, OutputOut),
        return_format=cross_boundary(model.return_format, ReturnFormatOut),
        dispatcher=cross_boundary(model.dispatcher, DispatcherOut),
        instructions=cross_boundary(model.instructions, InstructionsOut),
        examples=(
            cross_boundary(model.examples, ExamplesOut)
            if model.examples else None
        ),
        constraints=(
            cross_boundary(model.constraints, ConstraintsOut)
            if model.constraints else None
        ),
        anti_patterns=(
            cross_boundary(model.anti_patterns, AntiPatternsOut)
            if model.anti_patterns else None
        ),
        writing_output=build_writing_output(custom_tool, output_tool),
    )
    return result.model_dump_json(by_alias=True, exclude_none=True)
