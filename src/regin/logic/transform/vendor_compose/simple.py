"""Vendor compose simple functions — type bridging and frontmatter assembly.

CC=1-3 functions. Structure-type imports only.

Type-bridging functions that convert universal render types to Anthropic
render types. The pass_through function handles sections with identical
structure in both formats — the JSON round-trip re-validates through the
target type's schema. compose_identity is the one section where the vendor
adds new information: it replaces the abstract capability_tier with the
resolved model (the concrete Anthropic model name).
"""

from pydantic import BaseModel

from regin.structure.gen.schema import agent_universal_render as render
from regin.structure.gen.schema import agent_anthropic_render as anthr


def pass_through(
    source_section: BaseModel | None,
    target_type: type[BaseModel],
) -> BaseModel | None:
    """Round-trip a section from universal to anthropic type. None in -> None out.

    The JSON round-trip (dump universal -> validate as Anthropic) is intentional.
    It ensures the Anthropic schema's validation rules are applied, even though
    the field structure is identical. If the Anthropic schema ever diverges from
    the universal schema, this function will catch the mismatch at validation time.
    """
    if source_section is None:
        return None
    return target_type.model_validate_json(
        source_section.model_dump_json(by_alias=True)
    )


def compose_identity(
    source: render.Identity,
) -> anthr.IdentityAnthropic:
    """Compose Anthropic identity from universal identity.

    Pass-through with type conversion. Model resolution is handled
    separately at the frontmatter level.
    """
    return anthr.IdentityAnthropic(
        title=anthr.AgentTitle(anthr.TitleString(source.title.root)),
        role_identity=anthr.StringText(source.role_identity.root),
        role_responsibility=anthr.RoleResponsibility(source.role_responsibility.root),
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


def collect_tool_names(merged_tools: anthr.ToolPathEntries | None) -> set[str]:
    """Collect unique tool names from merged entries, always including Bash.

    Bash is always included because it is the base tool that all agents have
    access to. The merged_tools entries provide additional tool names from
    grant explosion. The sorted, deduplicated set becomes the frontmatter
    tools list that declares which tools the agent may invoke.
    """
    names: set[str] = {"Bash"}
    if merged_tools is not None:
        for entry in merged_tools.root:
            names.add(entry.tool.value)
    return names


def compose_frontmatter(
    identity: anthr.IdentityAnthropic,
    description: anthr.AgentDescription,
    model: anthr.AnthropicModel,
    hooks: anthr.HooksConfig,
    merged_tools: anthr.ToolPathEntries | None,
) -> anthr.Frontmatter:
    """Compose frontmatter — the Anthropic-specific YAML preamble.

    Frontmatter has no universal equivalent — it declares the agent's identity,
    model, tools, permission mode, and hooks in the format that the Anthropic
    runtime consumes. permission_mode is always bypassPermissions because
    regin-managed agents handle their own permission enforcement via hooks
    rather than the interactive permission dialog.
    """
    return anthr.Frontmatter(
        name=identity.title,
        description=description,
        model=model,
        permission_mode=anthr.PermissionMode.bypassPermissions,
        tools=anthr.FrontmatterTools(
            [anthr.PascalString(name) for name in sorted(collect_tool_names(merged_tools))]
        ),
        hooks=hooks,
    )
