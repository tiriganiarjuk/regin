"""Pipeline error types for Regin."""


class GateValidationError(Exception):
    """A gate rejected its input or output."""


class SectionMismatch(Exception):
    """Shared sections differ between two branch inputs during a merge."""


class BlockingCheckFailure(Exception):
    """A permissions phase-B blocking constraint was violated."""


class PermissionResolutionError(Exception):
    """An unrecoverable error during permissions resolution."""


class CustomToolNotFound(Exception):
    """Agent requires a custom output tool but none matched the registry."""
