# Regin

DAG pipeline resolver for agent definitions. Transforms raw TOML definitions through gated stages into platform-ready render formats.

**Part of the agent definition pipeline:** [Verdandi](https://github.com/johnny111272/verdandi) → [Draupnir](https://github.com/johnny111272/draupnir) → [Nornir](https://github.com/johnny111272/nornir) Gates → Regin → Galdr

## What This Is

Regin processes agent definition TOML files through a series of validated transformation stages. The pipeline is a directed acyclic graph, not a linear sequence — content and permissions branches run independently until convergence, enforcing separation of concerns at the pipeline level.

Every stage boundary is enforced by a compiled Rust/PyO3 gate module (built in Nornir) that validates data against embedded JSON Schemas. Python code between gates transforms only the delta between checkpoint schemas. Gates handle all file I/O — Python code never touches the filesystem.

## Key Concepts

**Gate I/O boundary.** The uniform pattern for every branch: gate in → transform → gate out. Python receives validated typed data, transforms it, and returns typed data. The gate writes the result. This separation means the Python transformation code is pure and testable.

**Generated structures.** Most Pydantic models in `structures/` are generated from JSON Schemas by `generate_structures.py`. Manual edits are silently overwritten on regeneration.

**DAG, not linear.** Step naming encodes the topology: `level{N}_{branch}_{operation}.py` — same level number means parallel execution. The content branch (L3–L5) and permissions branch (L3) run independently until convergence at L6.

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
