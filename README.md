# Regin

DAG pipeline resolver for agent definitions. Each branch transforms exactly the delta between two checkpoint schemas — nothing more. Compiled Rust gates handle all checkpoint I/O.

**Part of the agent definition pipeline:** [Verdandi](https://github.com/tiriganiarjuk/verdandi) → [Draupnir](https://github.com/tiriganiarjuk/draupnir) → [Nornir](https://github.com/tiriganiarjuk/nornir) Gates → Regin → Galdr

## What This Is

Regin processes agent definition TOML files through a directed acyclic graph of gated transformation stages, producing platform-ready render formats from a single source definition.

## The Delta Principle

Every branch in the DAG does exactly one thing: transform the delta between its input checkpoint schema and its output checkpoint schema.

```
checkpoint.toml
       │
  gate_in (read TOML → validate → return JSON)
       │
     { Δ }  ← Python: only the delta
       │
  gate_out (validate JSON → write TOML)
       │
checkpoint.toml
```

The input gate reads the file and validates it. The output gate validates and writes the result. The Python code in between is *only* the difference — what the output schema requires that the input schema does not yet contain. If the delta is zero (e.g. filesystem path verification), there is no Python at all — a passthrough gate handles everything.

This means the work function for each branch is minimal by design. The complexity lives in the pure functions it calls, not in the harness. The harness is identical for every branch: `gate_in(path) → work(json) → gate_out(path)`.

## Zero-Trust I/O Boundary

Gates are compiled Rust/PyO3 modules (built in [Nornir](https://github.com/tiriganiarjuk/nornir)) that embed JSON Schemas at compile time. They read and write every checkpoint:

- **Input gates** read TOML from disk, validate against their embedded schema, convert to JSON, and return it
- **Output gates** receive JSON, validate against their embedded schema, convert to TOML, and write to disk
- **Passthrough gates** read, validate (injecting schema defaults, or checking that paths exist), and write — no Python involvement

Python code between gates works on validated JSON and typed models. Reading, writing and validating structure belong to the gates; a guardrail system analyses every Python file and flags file access outside them.

## Checkpoint-Centric Design

Gates are named after the schema they validate, not the branch they belong to. `gate_paths_verified_input` serves five different branches. It does not know or care which branch calls it. The checkpoint file on disk is the interface — the output gate writes it, any input gate that validates the same schema can read it.

Every checkpoint on disk is TOML. Every gate converts TOML↔JSON at the boundary. Python always works with JSON. The format on disk is always TOML. No exceptions.

## The DAG Shape

The pipeline is a DAG, not a linear sequence. A module is named for what it operates on and what it does (`paths_resolve`, `content_reduce`, `render_regroup`); the graph is stated once, in `src/regin/cli.py`.

- **Trunk** — inject schema defaults, make workspace-relative paths absolute, verify the paths exist
- **Fan-out** — four content reducers (instructions, examples, guardrails, success criteria) each resolve file includes into inline content. Independently, the permissions branch resolves security declarations into calculated grants.
- **Content merges** — execution merge and criteria merge, then includes merge
- **Convergence** — content and permissions combine into a single universal format
- **Regroup** — domain-oriented sections reorganise into consumption-oriented sections
- **Vendor resolution** — one branch per vendor (currently Anthropic)

The content reducers and the permissions branch share no data until convergence. Each reads the same verified checkpoint and writes its own.

## Usage

```bash
uv run regin <input.toml> -o <output_dir>
```

After schema changes, regenerate Pydantic models before running the pipeline:

```bash
uv run python src/regin/generate_structures.py
```

## Licence

Copyright (c) 2025–2026 John Oker-Blom

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See [LICENSE](LICENSE) for the full licence text.
