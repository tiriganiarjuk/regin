"""Resolve workspace-relative paths to absolute paths.

The single primitive: if a path starts with './', prepend workspace root.
Composed into section-level resolvers that reconstruct frozen models.
"""

from regin.structures.raw_definition import (
    AgentRawDefinition,
    Context,
    ContextAvailable,
    ContextItem,
    ContextRequired,
    ExampleEntries,
    ExampleEntry,
    ExampleGroup,
    ExecutionExamples,
    ExecutionInstructions,
    FailureCriteria,
    FailureItem,
    Guardrails,
    IncludeExample,
    IncludeExampleGroup,
    IncludeFailureCriteria,
    IncludeGuardrailsAntiPatterns,
    IncludeGuardrailsConstraints,
    IncludeInstruction,
    IncludeSuccessCriteria,
    PathAbsolute,
    PathExistsAbsolute,
    Return,
    SecurityIo,
    SecurityPaths,
    SecurityPathsAllowedRead,
    SecurityPathsAllowedWrite,
    SecuritySchema,
    SuccessCriteria,
    SuccessItem,
    UnionPathAny,
    UnionPathExistsAny,
)


def extract_str(value: str) -> str:
    """Unwrap nested RootModel wrappers to get the plain string.

    Union path types (UnionPathAny) wrap PathRelative|PathAbsolute which
    wrap str. Calling .root once gives the inner RootModel; we need the str.
    """
    current = value
    while hasattr(current, "root"):
        current = current.root
    return current


def resolve_path(workspace: str, path: str) -> str:
    """Prepend workspace root to a relative path."""
    raw = extract_str(path)
    if raw.startswith("./"):
        return f"{workspace.rstrip('/')}/{raw[2:]}"
    return raw


def wrap_path_any(resolved: str) -> UnionPathAny:
    """Wrap a resolved absolute path in UnionPathAny."""
    return UnionPathAny(root=PathAbsolute(root=resolved))


def wrap_path_exists(resolved: str) -> UnionPathExistsAny:
    """Wrap a resolved absolute path in UnionPathExistsAny."""
    return UnionPathExistsAny(root=PathExistsAbsolute(root=resolved))


def resolve_optional_any(workspace: str, path: UnionPathAny | None) -> UnionPathAny | None:
    """Resolve and wrap a path in UnionPathAny if present."""
    return wrap_path_any(resolve_path(workspace, path)) if path else None


def resolve_optional_exists(
    workspace: str, path: UnionPathExistsAny | None,
) -> UnionPathExistsAny | None:
    """Resolve and wrap a path in UnionPathExistsAny if present."""
    return wrap_path_exists(resolve_path(workspace, path)) if path else None


def resolve_security_io(workspace: str, security_io: SecurityIo) -> SecurityIo:
    """Resolve paths in the security IO section."""
    return security_io.model_copy(update={
        "security_io_input_file": resolve_optional_any(
            workspace, security_io.security_io_input_file,
        ),
        "security_io_input_directory": resolve_optional_any(
            workspace, security_io.security_io_input_directory,
        ),
        "security_io_output_file": resolve_optional_any(
            workspace, security_io.security_io_output_file,
        ),
        "security_io_output_directory": resolve_optional_any(
            workspace, security_io.security_io_output_directory,
        ),
    })


def resolve_security_schema(workspace: str, schema: SecuritySchema) -> SecuritySchema:
    """Resolve paths in the security schema section."""
    return schema.model_copy(update={
        "security_input_schema": resolve_optional_exists(
            workspace, schema.security_input_schema,
        ),
        "security_output_schema": resolve_optional_exists(
            workspace, schema.security_output_schema,
        ),
    })


def resolve_security_paths(workspace: str, paths: SecurityPaths) -> SecurityPaths:
    """Resolve paths in the security paths section."""
    updates: dict[str, SecurityPathsAllowedRead | SecurityPathsAllowedWrite] = {}
    if paths.security_paths_allowed_read:
        updates["security_paths_allowed_read"] = SecurityPathsAllowedRead(
            [wrap_path_any(resolve_path(workspace, entry)) for entry in paths.security_paths_allowed_read.root],
        )
    if paths.security_paths_allowed_write:
        updates["security_paths_allowed_write"] = SecurityPathsAllowedWrite(
            [wrap_path_any(resolve_path(workspace, entry)) for entry in paths.security_paths_allowed_write.root],
        )
    return paths.model_copy(update=updates) if updates else paths


def resolve_context_items(workspace: str, items: list[ContextItem]) -> list[ContextItem]:
    """Resolve paths in a list of context items."""
    return [
        item.model_copy(update={
            "context_path": wrap_path_any(resolve_path(workspace, item.context_path)),
        })
        for item in items
    ]


def resolve_context(workspace: str, context: Context) -> Context:
    """Resolve paths in the context section."""
    updates: dict[str, ContextRequired | ContextAvailable] = {}
    if context.context_required:
        updates["context_required"] = ContextRequired(
            resolve_context_items(workspace, context.context_required.root),
        )
    if context.context_available:
        updates["context_available"] = ContextAvailable(
            resolve_context_items(workspace, context.context_available.root),
        )
    return context.model_copy(update=updates) if updates else context


def resolve_return(workspace: str, return_config: Return) -> Return:
    """Resolve return_schema path if present."""
    if not return_config.return_schema:
        return return_config
    return return_config.model_copy(update={
        "return_schema": wrap_path_exists(resolve_path(workspace, return_config.return_schema)),
    })


def resolve_guardrails(workspace: str, guardrails: Guardrails) -> Guardrails:
    """Resolve include paths in the guardrails section."""
    updates: dict[str, IncludeGuardrailsConstraints | IncludeGuardrailsAntiPatterns] = {}
    if guardrails.include_guardrails_constraints:
        source = guardrails.include_guardrails_constraints
        updates["include_guardrails_constraints"] = source.model_copy(update={
            "include": wrap_path_exists(resolve_path(workspace, source.include)),
        })
    if guardrails.include_guardrails_anti_patterns:
        source = guardrails.include_guardrails_anti_patterns
        updates["include_guardrails_anti_patterns"] = source.model_copy(update={
            "include": wrap_path_exists(resolve_path(workspace, source.include)),
        })
    return guardrails.model_copy(update=updates) if updates else guardrails


def resolve_success_criteria_items(
    workspace: str, items: list[SuccessItem | IncludeSuccessCriteria],
) -> list[SuccessItem | IncludeSuccessCriteria]:
    """Resolve include paths in success criteria items."""
    return [
        item.model_copy(update={
            "include": wrap_path_exists(resolve_path(workspace, item.include)),
        })
        if isinstance(item, IncludeSuccessCriteria) else item
        for item in items
    ]


def resolve_failure_criteria_items(
    workspace: str, items: list[FailureItem | IncludeFailureCriteria],
) -> list[FailureItem | IncludeFailureCriteria]:
    """Resolve include paths in failure criteria items."""
    return [
        item.model_copy(update={
            "include": wrap_path_exists(resolve_path(workspace, item.include)),
        })
        if isinstance(item, IncludeFailureCriteria) else item
        for item in items
    ]


def resolve_instruction_includes(
    workspace: str, instructions: ExecutionInstructions,
) -> ExecutionInstructions:
    """Resolve include paths in instruction list."""
    return ExecutionInstructions([
        item.model_copy(update={
            "include": wrap_path_exists(resolve_path(workspace, item.include)),
        })
        if isinstance(item, IncludeInstruction) else item
        for item in instructions.root
    ])


def resolve_example_entries(
    workspace: str, entries: list[ExampleEntry | IncludeExample],
) -> list[ExampleEntry | IncludeExample]:
    """Resolve include paths in example entries."""
    return [
        entry.model_copy(update={
            "include": wrap_path_exists(resolve_path(workspace, entry.include.root)),
        })
        if isinstance(entry, IncludeExample) else entry
        for entry in entries
    ]


def resolve_example_includes(
    workspace: str, examples: ExecutionExamples,
) -> ExecutionExamples:
    """Resolve include paths in example groups and entries."""
    resolved = []
    for group in examples.root:
        if isinstance(group, IncludeExampleGroup):
            resolved.append(group.model_copy(update={
                "include": wrap_path_exists(resolve_path(workspace, group.include)),
            }))
        elif isinstance(group, ExampleGroup) and group.example_entries:
            resolved.append(group.model_copy(update={
                "example_entries": ExampleEntries(resolve_example_entries(
                    workspace, group.example_entries.root,
                )),
            }))
        else:
            resolved.append(group)
    return ExecutionExamples(resolved)


def resolve_all_paths(model: AgentRawDefinition) -> AgentRawDefinition:
    """Resolve all workspace-relative paths to absolute paths."""
    workspace = extract_str(model.security.security_paths.security_paths_workspace)

    security = model.security.model_copy(update={
        "security_io": resolve_security_io(workspace, model.security.security_io),
        "security_schema": resolve_security_schema(workspace, model.security.security_schema),
        "security_paths": resolve_security_paths(workspace, model.security.security_paths),
        "context": resolve_context(workspace, model.security.context),
    })

    task = model.task.model_copy(update={
        "return_": resolve_return(workspace, model.task.return_),
    })

    execution = model.execution.model_copy(update={
        "execution_instructions": resolve_instruction_includes(
            workspace, model.execution.execution_instructions,
        ),
        "execution_examples": resolve_example_includes(
            workspace, model.execution.execution_examples,
        ),
    })

    criteria = model.criteria.model_copy(update={
        "guardrails": resolve_guardrails(workspace, model.criteria.guardrails),
        "success_criteria": SuccessCriteria(resolve_success_criteria_items(
            workspace, model.criteria.success_criteria.root,
        )),
        "failure_criteria": FailureCriteria(resolve_failure_criteria_items(
            workspace, model.criteria.failure_criteria.root,
        )),
    })

    return model.model_copy(update={
        "security": security,
        "task": task,
        "execution": execution,
        "criteria": criteria,
    })
