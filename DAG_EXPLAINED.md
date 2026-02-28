# Regin — The Pipeline DAG

## The Shape

```
                      ┌────────────────┐
                      │ Raw Definition │
                      │    (Red 1)     │
                      └───────┬────────┘
                              │
                      ┌───────▼────────┐
                      │ Paths Resolve  │
                      │    Level 1     │
                      └───────┬────────┘
                              │
                      ┌───────▼────────┐
                      │  Paths Verify  │
                      │    Level 2     │
                      │    (Red 3)     │
                      └───────┬────────┘
                              │
        ┌─────────┬───────────┼───────────┬──────────┐
        │         │           │           │          │
        ▼         ▼           ▼           ▼          ▼
   ┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌────────────┐
   │  Instr. ││  Examp. ││  Guard. ││  Succ.  ││ Permissions│
   │  Reduce ││  Reduce ││  Reduce ││  Reduce ││  Resolve   │
   │   L3    ││   L3    ││   L3    ││   L3    ││     L3     │
   └────┬────┘└────┬────┘└────┬────┘└────┬────┘└──────┬─────┘
        │          │          │          │            │
        └────┬─────┘          └────┬─────┘            │
             │                     │                  │
             ▼                     ▼                  │
       ┌───────────┐         ┌───────────┐            │
       │ Execution │         │ Criteria  │            │
       │   Merge   │         │   Merge   │            │
       │    L4     │         │    L4     │            │
       └─────┬─────┘         └─────┬─────┘            │
             │                     │                  │
             └──────────┬──────────┘                  │
                        │                             │
                        ▼                             │
                 ┌─────────────┐                      │
                 │  Includes   │                      │
                 │   Merge     │                      │
                 │ L5 (Red 4)  │                      │
                 └──────┬──────┘                      │
                        │                   (Red 5)   │
                        └──────────────┬──────────────┘
                                       │
                              ┌────────▼─────────┐
                              │    Universal     │
                              │      Merge       │
                              │   L6 (Red 6)     │
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │     Render       │
                              │     Regroup      │
                              │   L7 (Red 7)     │
                              └────────┬─────────┘
                                       │
                         ┌─────────────┼──────────── ─ ─
                         │             │
                  ┌──────▼───────┐ ┌───▼──────────┐
                  │  Anthropic   │ │    Future    │
                  │   Resolve    │ │   Vendors    │
                  │ L8 (Red 8)   │ │     L8       │
                  └──────────────┘ └──────────────┘
```

## What the Levels Mean

The level number is the DAG depth — how many completed steps separate this node from the raw input. It encodes exactly one thing: **what must finish before this can start.**

- **Same level = independent.** Nothing at level N depends on anything else at level N. They can run in any order or in parallel.
- **Higher level = depends on lower.** A level N node requires at least one level N-1 node to have completed.
- **Level number is NOT execution order.** The DAG has parallelism. Sequential numbering would hide it.

## The Levels

### Level 1 — Paths Resolve

Single node. Converts workspace-relative paths to absolute paths. Every downstream node needs absolute paths, so this runs first.

- **Input:** Raw definition TOML (Red 1 — authored by definition writers)
- **Output:** Paths-resolved TOML (Red 2)
- **Gate in:** `gate_raw_definition_input` (reads TOML, returns JSON)
- **Gate out:** `gate_paths_resolved_output` (takes JSON, writes TOML)

### Level 2 — Paths Verify

Single node. Verifies every absolute path actually exists on disk. This is a Nornir gate that checks filesystem presence — no Python transform, pure gate validation.

- **Input:** Paths-resolved TOML (Red 2)
- **Output:** Paths-verified TOML (Red 3)
- **Gate:** `gate_paths_verified` (passthrough — reads TOML, validates paths exist, writes TOML)

Red 3 is the last shared ancestor. Everything below branches from here.

### Level 3 — Fan-Out (Content Branch + Permissions Branch)

Five independent nodes from the same Red 3 input. Two branches diverge here.

**Content branch** (four parallel reducers):

Each reducer resolves `{include: "path/to/file.md"}` references into inline content. The include file is read, parsed (Markdown split at H2, or structured TOML/JSON), and the reference is replaced with the resolved content. The definition gets smaller in reference count and larger in content.

| Node | What it reduces | Gate in | Gate out |
|------|----------------|---------|----------|
| Instructions Reduce | `execution.execution_instructions` | `gate_paths_verified_input` | `gate_instructions_reduced_output` |
| Examples Reduce | `execution.execution_examples` | `gate_paths_verified_input` | `gate_examples_reduced_output` |
| Guardrails Reduce | `criteria.guardrails` | `gate_paths_verified_input` | `gate_guardrails_reduced_output` |
| Success Reduce | `criteria.success_criteria` + `criteria.failure_criteria` | `gate_paths_verified_input` | `gate_success_reduced_output` |

**Permissions branch** (one node):

Runs the 6-phase security resolution algorithm (A-F). Reads security declarations from the definition and produces an `enforcement` section with explicit grants, implicit grants, and output tool configuration.

| Node | What it produces | Gate in | Gate out |
|------|-----------------|---------|----------|
| Permissions Resolve | `enforcement` section | `gate_paths_verified_input` | `gate_permissions_resolved_output` |

The permissions branch has no dependency on the content branch. It reads the same Red 3 input and produces Red 5 independently.

### Level 4 — Content Merges

Two merge nodes within the content branch. Each takes two level-3 outputs and combines them.

| Node | Input A | Input B | Gates in | Gate out |
|------|---------|---------|----------|----------|
| Execution Merge | Instructions-reduced | Examples-reduced | `gate_instructions_reduced_input` + `gate_examples_reduced_input` | `gate_execution_merged_output` |
| Criteria Merge | Guardrails-reduced | Success-reduced | `gate_guardrails_reduced_input` + `gate_success_reduced_input` | `gate_criteria_merged_output` |

Merge nodes verify that shared sections (`indirect`, `task`, `security`) are identical between their two inputs before combining. This catches drift — if the same definition diverged during parallel reduction, the merge detects it.

### Level 5 — Includes Merge

Single node. Final content branch merge.

- **Input A:** Execution-merged (instructions + examples)
- **Input B:** Criteria-merged (guardrails + success/failure)
- **Output:** Includes-merged TOML (Red 4)
- **Gates in:** `gate_execution_merged_input` + `gate_criteria_merged_input`
- **Gate out:** `gate_includes_merged_output`

Red 4 contains the complete definition with all includes resolved to inline content. The content branch is done.

### Level 6 — Universal Merge (Convergence)

The two branches rejoin. Content (Red 4) and permissions (Red 5) converge into a single document.

- **Input A:** Includes-merged TOML (Red 4, content branch)
- **Input B:** Permissions-resolved TOML (Red 5, permissions branch)
- **Output:** Universal-format TOML (Red 6)
- **Gate in A:** `gate_includes_merged_input`
- **Gate in B:** `gate_permissions_resolved_input`
- **Gate out:** `gate_universal_format_output`

Verifies shared sections match between the two branches (same check as level 4 merges). Takes execution + criteria from Red 4, enforcement from Red 5.

Red 6 is the platform-agnostic universal format. Everything that matters about the agent definition is in one document, fully resolved, all paths absolute, all includes inline, all permissions calculated.

### Level 7 — Render Regroup

Single node. Regroups from 6 domain-oriented sections (indirect, task, security, execution, criteria, enforcement) into 12 consumption-oriented sections designed for template rendering (identity, input, output, return_format, dispatcher, security_boundary, implicit_grants, constraints, anti_patterns, instructions, examples, writing_output).

- **Input:** Universal-format TOML (Red 6)
- **Output:** Universal-render TOML (Red 7)
- **Gate in:** `gate_universal_format_input`
- **Gate out:** `gate_universal_render_output`

Red 7 is still platform-agnostic. It reorganizes the data for consumption but adds no vendor-specific knowledge.

### Level 8 — Fan-Out (Vendor Resolvers)

Platform-specific resolution. Each vendor resolver reads the same Red 7 input and applies vendor-specific lookup tables to produce a deployment-ready render format.

| Node | Vendor | What it produces | Gate in | Gate out |
|------|--------|-----------------|---------|----------|
| Anthropic Resolve | Claude Code | `anthropic_render.toml` (Red 8) | `gate_universal_render_input` | `gate_anthropic_render_output` |
| *(future)* | OpenCode | `opencode_render.toml` | `gate_universal_render_input` | TBD |

The Anthropic resolver applies three lookup tables:
- **capability → tools**: Maps abstract capabilities (read, search, write...) to concrete vendor tools (Read, Grep, Glob, Write, Edit, Bash)
- **capability → commands**: Maps capabilities to allowed shell commands (find, ls, diff...)
- **tier → model**: Maps capability tiers (standard, complex-reasoning...) to model names (haiku, sonnet, opus)

Most sections pass through unchanged. The resolver adds: frontmatter, hooks, security boundary display, critical rules, writing output configuration, and model name.

## The Diamond Shape

The DAG is a diamond pattern, used twice:

1. **First diamond (levels 2-6):** Fan-out at Red 3 into content + permissions branches, converge at Red 6.
2. **Second fan-out (level 7-8):** Fan-out at Red 7 into per-vendor resolvers.

The second fan-out does not converge — each vendor produces an independent output consumed by its own template renderer (Galdr).

## File Naming Convention

Step modules are named `level{N}_{branch}_{operation}.py`:

```
level1_paths_resolve.py
level2_paths_verify.py
level3_content_instructions_reduce.py
level3_content_examples_reduce.py
level3_content_guardrails_reduce.py
level3_content_success_reduce.py
level3_permissions_resolve.py
level4_content_execution_merge.py
level4_content_criteria_merge.py
level5_content_includes_merge.py
level6_universal_merge.py
level7_render_regroup.py
level8_anthropic_resolve.py
```

- **Level number** = DAG depth (what must finish first)
- **Branch name** = which fork (`content_`, `permissions_`, `anthropic_`, or omitted for trunk)
- **Operation name** = what the node does

An `ls` of the steps directory teaches the DAG. Same-level files teach parallelism. Branch prefixes teach which fork. No sequential numbering lies.
