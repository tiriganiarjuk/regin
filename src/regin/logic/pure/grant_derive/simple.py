"""Grant derive simple functions — raw path/capability extraction.

CC=1-3. Import from primitive only within this module.

Collectors that extract raw path strings and capability sets from the resolved
agent definition. These are the input stage of grant derivation — they normalize
the heterogeneous source fields (SecurityPaths, SecurityIo, Capabilities) into
uniform sets that composed-level functions can intersect and collapse.

The agent definition expresses paths and capabilities in domain-specific typed
fields (paths_allowed_read, io_scratch_tempdir, capabilities_requested, etc.).
This module flattens them into raw string sets and capability enum sets that
the intersection and containment algorithms can operate on uniformly.
"""

from regin.structure.gen.schema.agent_paths_resolved import (
    Capabilities,
    SecurityIo,
    SecurityPaths,
)


def extract_read_paths(paths: SecurityPaths) -> list[str]:
    """Extract author-declared read path boundaries.

    Read paths define where the agent may observe. They feed into the explicit
    grant intersection: each read path is crossed with read-tier capabilities
    (read, search, inspect) to produce path-scoped grants.
    """
    return [entry.root for entry in paths.paths_allowed_read.root] if paths.paths_allowed_read else []


def extract_write_paths(paths: SecurityPaths) -> list[str]:
    """Extract author-declared write path boundaries.

    Write paths define where the agent may mutate. They feed into the explicit
    grant intersection with ALL capability tiers (read + write), since writing
    to a path implies the ability to read from it.
    """
    return [entry.root for entry in paths.paths_allowed_write.root] if paths.paths_allowed_write else []


def extract_requested(caps: Capabilities | None) -> set[Capabilities]:
    """Extract the author's requested capability set.

    Requested capabilities are the agent author's statement of intent — "I need
    read, search, and write capability." This set is intersected with path
    declarations to produce explicit grants. An empty/None capabilities section
    means the agent requests no explicit capabilities (it may still receive
    implicit grants from IO declarations).
    """
    return {Capabilities(capability.value) for capability in caps.capabilities_requested.root} if caps else set()


def build_raw_grants(reads: set[str], writes: set[str]) -> dict[str, set[str]]:
    """Build the intermediate grant dict before containment collapse.

    Keys are capability names ("read", "write"); values are path sets.
    Empty capabilities are excluded to keep downstream grant models sparse —
    a capability with no paths should not appear in the model at all, not
    appear with an empty list.
    """
    raw_grants: dict[str, set[str]] = {}
    if reads:
        raw_grants["read"] = reads
    if writes:
        raw_grants["write"] = writes
    return raw_grants


def collect_implicit_writes(io_section: SecurityIo, workspace_name: str) -> set[str]:
    """Collect implicit write paths from scratch tempdir declarations.

    Scratch tempdirs generate implicit write grants because the agent needs
    to write intermediate results there. The resolved path format is
    /tmp/{workspace}/{dirname}/ — matching the tempdir convention used
    throughout the pipeline.
    """
    writes: set[str] = set()
    if io_section.io_scratch_tempdir:
        writes.add(f"/tmp/{workspace_name}/{io_section.io_scratch_tempdir.root}/")
    return writes
