"""Vendor compose primitives — single-expression constructors.

CC=1 functions. No branches. No cross-module dependencies.

Single-expression constructors for vendor-specific sections. Currently
Anthropic-only. If a second vendor is added, this module would be split
into vendor-specific primitive modules, but the universal-to-vendor boundary
would remain at the same pipeline point (after L7 regroup, in L8).
"""

from regin.structure.gen.schema import agent_anthropic_render as anthr


def compose_security_boundary(
    filesystem_permissions: anthr.FilesystemPermissions | None,
    workspace_path: str,
) -> anthr.SecurityBoundaryAnthropic:
    """Anthropic security boundary — adds filesystem permissions to universal model.

    Filesystem permission entries are a human-readable summary of
    tool/command grants per path, generated in L8 for inclusion in the
    rendered prompt so the agent knows what tools are available where.
    """
    return anthr.SecurityBoundaryAnthropic(
        workspace_path=anthr.PathExistsAbsolute(workspace_path),
        filesystem_permissions=filesystem_permissions,
    )
