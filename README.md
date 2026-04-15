# Regin

DAG pipeline resolver for agent definitions. Each branch transforms exactly the delta between two checkpoint schemas — nothing more. Compiled Rust gates handle all file I/O. Python never touches the filesystem.

**Part of the agent definition pipeline:** [Verdandi](https://github.com/johnny111272/verdandi) → [Draupnir](https://github.com/johnny111272/draupnir) → [Nornir](https://github.com/johnny111272/nornir) Gates → Regin → Galdr

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

Gates are compiled Rust/PyO3 modules (built in [Nornir](https://github.com/johnny111272/nornir)) that embed JSON Schemas at compile time. They are the only components that touch the filesystem:

- **Input gates** read TOML from disk, validate against their embedded schema, convert to JSON, and return it
- **Output gates** receive JSON, validate against their embedded schema, convert to TOML, and write to disk
- **Passthrough gates** read, validate (including filesystem checks like path existence), and write — no Python involvement

Python code between gates never reads files, never writes files, never validates structure. The gates do all of this. This is not a convention — it is an architectural impossibility enforced by the fact that the I/O primitives exist only in the compiled gate modules.

## Checkpoint-Centric Design

Gates are named after the schema they validate, not the branch they belong to. `gate_paths_verified_input` serves five different branches. It does not know or care which branch calls it. The checkpoint file on disk is the interface — the output gate writes it, any input gate that validates the same schema can read it.

Every checkpoint on disk is TOML. Every gate converts TOML↔JSON at the boundary. Python always works with JSON. The format on disk is always TOML. No exceptions.

## The DAG Shape

The pipeline is a DAG, not a linear sequence. Step naming encodes the topology: `level{N}_{branch}_{operation}` — same level number means parallel execution.

- **Level 2** — Path resolution (relative → absolute)
- **Level 3** — Fan-out: four content reducers run in parallel (instructions, examples, guardrails, success criteria), each resolving file includes into inline content. Independently, the permissions branch resolves security declarations into calculated grants through a six-phase algorithm.
- **Levels 4–5** — Content merges: execution merge, criteria merge, then includes merge
- **Level 6** — Convergence: content and permissions branches combine into a single universal format
- **Level 7** — Regroup: domain-oriented sections reorganise into consumption-oriented sections
- **Level 8** — Fan-out: per-vendor resolution (currently Anthropic, extensible to others)

Content and permissions branches are independent until level 6. Breaking this independence creates implicit coupling — the architecture enforces it through separate checkpoint schemas.

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
