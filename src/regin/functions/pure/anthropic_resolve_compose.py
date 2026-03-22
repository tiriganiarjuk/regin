"""Steps 6, 7, 8 — Compose created and modified sections for anthropic render."""

from regin.structures.resolved_tool import ResolvedTool
from regin.structures.schema import agent_universal_render as render
from regin.structures.schema import agent_anthropic_render as anthr


def compose_identity(
    source: render.Identity, model: anthr.AnthropicModel,
) -> anthr.IdentityAnthropic:
    """Identity with resolved model replacing capability_tier."""
    return anthr.IdentityAnthropic(
        title=anthr.AgentTitle(anthr.TitleString(source.title.root)),
        description=anthr.AgentDescription(source.description.root),
        role_identity=anthr.StringText(source.role_identity.root),
        role_responsibility=anthr.RoleResponsibility(source.role_responsibility.root),
        model=model,
        role_description=(
            anthr.RoleDescription(source.role_description.root)
            if source.role_description else None
        ),
        role_expertise=(
            anthr.RoleExpertise.model_validate_json(
                source.role_expertise.model_dump_json(by_alias=True)
            ) if source.role_expertise else None
        ),
    )


def compose_security_boundary(
    display: anthr.DisplayEntries | None,
    workspace_path: str,
) -> anthr.SecurityBoundaryAnthropic:
    """Security boundary with display entries and workspace path."""
    return anthr.SecurityBoundaryAnthropic(
        workspace_path=anthr.PathExistsAbsolute(workspace_path),
        display=display,
    )


def compose_frontmatter(
    identity: anthr.IdentityAnthropic,
    model: anthr.AnthropicModel,
    hooks: anthr.HooksConfig,
    merged_tools: anthr.ToolPathEntries | None,
) -> anthr.Frontmatter:
    """Compose frontmatter from resolved data."""
    tool_names: set[str] = {"Bash"}
    if merged_tools is not None:
        for entry in merged_tools.root:
            tool_names.add(entry.tool.value)

    return anthr.Frontmatter(
        name=identity.title,
        description=identity.description,
        model=model,
        permission_mode=anthr.PermissionMode.bypassPermissions,
        tools=anthr.FrontmatterTools(
            [anthr.PascalString(name) for name in sorted(tool_names)]
        ),
        hooks=hooks,
    )


def compose_critical_rules(
    resolved_tool: ResolvedTool | None,
    writing_output: render.WritingOutput | None,
) -> anthr.CriticalRules:
    """Compose critical rules from tool resolution."""
    has_tool = resolved_tool is not None
    tool_name = None
    name_needed = None
    batch_size = None

    if has_tool and writing_output is not None:
        spec = writing_output.writing_output
        tool_name = anthr.ToolName(anthr.SnakeString(resolved_tool.tool_name))
        if spec.output_tool_name_needed is not None:
            name_needed = anthr.OutputToolNameNeeded(
                anthr.Boolean(spec.output_tool_name_needed.root)
            )
        if spec.output_tool_batch_size is not None:
            batch_size = anthr.OutputToolBatchSize(
                anthr.Integer(spec.output_tool_batch_size.root)
            )

    return anthr.CriticalRules(
        has_output_tool=anthr.Boolean(has_tool),
        tool_name=tool_name,
        name_needed=name_needed,
        batch_size=batch_size,
    )


def map_enforcement_fields(
    spec: render.EnforcementOutputTool,
) -> dict[str, anthr.FilenameTemplate | anthr.OutputToolBatchSize | anthr.OutputToolSchemaXAbs | anthr.PathAbsolute | None]:
    """Map enforcement output tool fields to anthropic render types."""
    return {
        "name_pattern": (
            anthr.FilenameTemplate(spec.output_tool_name_pattern.root)
            if spec.output_tool_name_pattern else None
        ),
        "batch_size": (
            anthr.OutputToolBatchSize(anthr.Integer(spec.output_tool_batch_size.root))
            if spec.output_tool_batch_size else None
        ),
        "schema_path": (
            anthr.OutputToolSchemaXAbs(spec.output_tool_schema_path.root)
            if spec.output_tool_schema_path else None
        ),
        "file_path": (
            anthr.PathAbsolute(spec.output_tool_file_path.root)
            if spec.output_tool_file_path else None
        ),
        "directory_path": (
            anthr.PathAbsolute(spec.output_tool_directory_path.root)
            if spec.output_tool_directory_path else None
        ),
    }


def compose_writing_output(
    resolved_tool: ResolvedTool | None,
    writing_output: render.WritingOutput | None,
) -> anthr.WritingOutputAnthropic | None:
    """Populate resolved writing output. Null when no custom tool."""
    if resolved_tool is None or writing_output is None:
        return None
    spec = writing_output.writing_output
    name_needed = (
        spec.output_tool_name_needed is not None
        and spec.output_tool_name_needed.root is True
    )
    fields = map_enforcement_fields(spec)

    return anthr.WritingOutputAnthropic(
        tool_name=anthr.ToolName(anthr.SnakeString(resolved_tool.tool_name)),
        invocation_variant=anthr.InvocationVariant(resolved_tool.invocation_variant),
        invocation_display=anthr.InvocationDisplay(resolved_tool.invocation_display),
        name_needed=anthr.OutputToolNameNeeded(anthr.Boolean(name_needed)),
        **fields,
    )
