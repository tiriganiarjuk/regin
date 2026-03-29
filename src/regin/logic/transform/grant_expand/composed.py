"""Grant expansion composed functions — capability explosion into tools/commands.

CC=4+ functions. Import from simple and primitive.

The core "explosion" logic that fans out abstract capabilities into concrete
tool and command grants. This is called "explosion" because one capability
can map to multiple tools:
  - search -> Grep + Glob + find
  - inspect -> Read + ls + du + wc + stat + diff + tree

The explosion tables in collect_explicit_tools and collect_explicit_commands
are the definitive mapping between the capability model and the Anthropic
tool/command model.

Implicit grants expand to tools only, never commands — this is a deliberate
security decision: implicit grants are system-inferred (from IO/schema/context
declarations), not author-requested. Granting command-level access (raw shell
commands) based on inference would be too permissive.
"""

from regin.structure.gen.schema.agent_anthropic_render import (
    CommandNameUnix,
    CommandPathEntries,
    HooksConfig,
    ToolNameAnthropic,
    ToolPathEntries,
)
from regin.structure.gen.schema.agent_universal_render import (
    AgentUniversalRender,
    EnforcementExplicitGrants,
    EnforcementImplicitGrants,
)
from regin.structure.model.grant_entries import GrantEntries
from regin.structure.model.resolved_tool import ResolvedTool

from regin.logic.transform.grant_expand.simple import (
    build_hooks,
    extract_paths,
    merge_into_commands,
    merge_into_tools,
)


def collect_explicit_tools(
    grants: EnforcementExplicitGrants,
) -> dict[ToolNameAnthropic, set[str]]:
    """Explode the 6 explicit capabilities into Anthropic tool grants.

    Capability-to-tool mapping:
      read    -> Read (file content access)
      search  -> Grep + Glob (content matching + file pattern matching)
      inspect -> Read (file content, shared with read capability)
      write   -> Write (file creation/overwrite)
      edit    -> Edit (in-place file modification)
      append  -> Edit (append is a form of in-place modification)

    Note: inspect shares the Read tool with read — the distinction is in
    the path sets, not the tool names. Append maps to Edit, not a separate
    tool — Anthropic's Edit tool handles both operations.
    """
    result: dict[ToolNameAnthropic, set[str]] = {}
    if grants.read:
        paths = extract_paths(grants.read.root)
        result.setdefault(ToolNameAnthropic.Read, set()).update(paths)
    if grants.search:
        paths = extract_paths(grants.search.root)
        result.setdefault(ToolNameAnthropic.Grep, set()).update(paths)
        result.setdefault(ToolNameAnthropic.Glob, set()).update(paths)
    if grants.inspect:
        paths = extract_paths(grants.inspect.root)
        result.setdefault(ToolNameAnthropic.Read, set()).update(paths)
    if grants.write:
        result.setdefault(ToolNameAnthropic.Write, set()).update(
            extract_paths(grants.write.root)
        )
    if grants.edit:
        result.setdefault(ToolNameAnthropic.Edit, set()).update(
            extract_paths(grants.edit.root)
        )
    if grants.append:
        result.setdefault(ToolNameAnthropic.Edit, set()).update(
            extract_paths(grants.append.root)
        )
    return result


def collect_explicit_commands(
    grants: EnforcementExplicitGrants,
) -> dict[CommandNameUnix, set[str]]:
    """Explode explicit capabilities into Unix command grants.

    Only search and inspect map to commands:
      search  -> find (recursive file discovery)
      inspect -> ls, du, wc, stat, diff, tree (filesystem metadata inspection)

    Read/write/edit/append use only Anthropic tools because their operations
    are mediated by the tool protocol, not raw shell access.
    """
    result: dict[CommandNameUnix, set[str]] = {}
    if grants.search:
        paths = extract_paths(grants.search.root)
        result.setdefault(CommandNameUnix.find, set()).update(paths)
    if grants.inspect:
        paths = extract_paths(grants.inspect.root)
        for command in (CommandNameUnix.ls, CommandNameUnix.du, CommandNameUnix.wc,
                        CommandNameUnix.stat, CommandNameUnix.diff, CommandNameUnix.tree):
            result.setdefault(command, set()).update(paths)
    return result


def explode_implicit(
    grants: EnforcementImplicitGrants,
) -> tuple[ToolPathEntries | None, CommandPathEntries | None]:
    """Fan out implicit grants to tool entries only — never commands.

    Implicit grants are system-inferred (from IO/schema/context declarations),
    not author-requested. Granting command-level access (find, ls, etc.) based
    on inference would be too permissive — the agent can read/write/edit the
    files it needs, but cannot run arbitrary shell commands against those paths
    unless the author explicitly requests search or inspect capabilities.

    Always returns None for the command component.
    """
    tool_mapping: dict[ToolNameAnthropic, set[str]] = {}
    if grants.read:
        tool_mapping.setdefault(ToolNameAnthropic.Read, set()).update(
            extract_paths(grants.read.root)
        )
    if grants.write:
        tool_mapping.setdefault(ToolNameAnthropic.Write, set()).update(
            extract_paths(grants.write.root)
        )
    if grants.edit:
        tool_mapping.setdefault(ToolNameAnthropic.Edit, set()).update(
            extract_paths(grants.edit.root)
        )
    return merge_into_tools(tool_mapping), None


def resolve_grants_and_hooks(
    source: AgentUniversalRender,
    resolved_tool: ResolvedTool | None,
) -> tuple[ToolPathEntries | None, CommandPathEntries | None, HooksConfig]:
    """Three-step grant resolution: explode, merge, build hooks.

    Steps:
    1. Explode explicit grants from security_boundary.capabilities into
       tool + command entries
    2. Explode implicit grants from implicit_grants.capabilities into
       tool-only entries
    3. Merge both into the HooksConfig via GrantEntries

    The return tuple provides explicit entries separately for display building
    (in L8's build_display), while the hooks combine everything.
    """
    output_tool_name = resolved_tool.tool_name if resolved_tool else None
    if source.security_boundary and source.security_boundary.capabilities:
        caps = source.security_boundary.capabilities
        explicit_tools = merge_into_tools(collect_explicit_tools(caps))
        explicit_commands = merge_into_commands(collect_explicit_commands(caps))
    else:
        explicit_tools, explicit_commands = None, None
    implicit_tools, implicit_commands = (
        explode_implicit(source.implicit_grants.capabilities)
        if source.implicit_grants
        else (None, None)
    )
    entries = GrantEntries(
        explicit_tools=explicit_tools,
        explicit_commands=explicit_commands,
        implicit_tools=implicit_tools,
        implicit_commands=implicit_commands,
    )
    hooks = build_hooks(entries, output_tool_name)
    return explicit_tools, explicit_commands, hooks
