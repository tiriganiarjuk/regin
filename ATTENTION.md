# ATTENTION — the nornir readers return the gate contract

The nornir readers (`read_{json,yaml,toml,toon,xml,markdown}_validate_json`) were rebuilt and
redeployed to `~/ai/tools/lib`. `read(file_path, schema_name, schema_dir)` returns the same shape
every nornir gate returns:

```
{"ok": bool, "data": str | None, "error": {"type": str, "message": str} | None}
```

- `ok` true → `data` is the validated JSON string, on its way into `Model.model_validate_json`.
- `ok` false → `error.type` names the failure class, `error.message` is the educational text.

| `error.type` | Meaning |
|---|---|
| `read_error` | the file could not be read |
| `parse_error` | the file is not valid in its format |
| `conversion_error` | the converted JSON was invalid (an engine fault) |
| `schema_error` | the schema could not be loaded or compiled |
| `validation_error` | the data does not match the schema |
| `cache_error` | the validator cache failed (an engine fault) |

## What breaks here

This project's wrapper passes the reader's return value on as a `str`, so every read through it
fails until the wrapper is fixed:

- `src/regin/logic/impure/registry/ffi.py` — `read_registry`, consumed by `registry/simple.py`

How it shows: every run completes L0–L7 and stops at L8 `anthropic_resolve` with
`ValidationError: 1 validation error for ToolRegistry — JSON input should be string`, raised at
`registry/simple.py:26`, where the reader's result dict is handed to
`ToolRegistry.model_validate_json` as if it were the JSON text. Seen running
`uv run --project ~/ai/smidja/regin regin ~/ai/spaces/bragi/definitions/agents/agent-quality-auditor.toml -o <dir>`.

What waits on it: every agent regeneration. Bragi's agent templates and prompt sources were
corrected (bragi `029e255`) and reach the generated agents only through a Regin run, then Galdr.

The reader also has a CLI face — `read_toml_validate_json <file> <schema_name> <schema_dir>`:
the validated JSON on stdout and exit 0, or the failure class on stderr's first line and exit 1.

## The fix

Type the result at the wrapper: a frozen model of the contract in `structure/`, validated from
the reader's return, and the caller branches on `ok` and `error.type`. Decide per call site what
each `error.type` means for this project — hard failure, held back, reported.

Delete this file when the fix is in.
