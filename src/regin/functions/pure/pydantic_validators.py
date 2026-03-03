"""Pydantic BeforeValidator for path coercion.

When used with model_validate_json(json, context={'workspace': path}),
transforms relative paths (./...) to absolute paths (/workspace/...).

Without context, passes values through unchanged — the subsequent
pattern constraint determines which path type matches.
"""

from pydantic import ValidationInfo


def coerce_to_absolute(value: str, info: ValidationInfo) -> str:
    """Resolve a relative path to absolute using workspace from context."""
    if info.context and value.startswith("./"):
        workspace = info.context.get("workspace", "")
        if workspace:
            return f"{workspace}/{value[2:]}"
    return value
