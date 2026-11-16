<!-- ═══════════════════════════════════════════════════════════════════════ -->
<!-- DO NOT EDIT THIS BLOCK. Before editing ANY part of this file, you MUST  -->
<!-- first read /Users/johnny/ai/CONTEXT_MANAGEMENT_SYSTEM.md — it defines  -->
<!-- what this file is for and what may NOT go in it.                        -->
<!--                                                                          -->
<!-- This file is a MAP (a router), not a source. Its only job is to tell    -->
<!-- you WHERE the context lives — it never holds the context, state, or     -->
<!-- progress itself. Reading this map does NOT orient you; you are NOT      -->
<!-- oriented until you have read the Orientation-gate docs it points to, in -->
<!-- the order given.                                                         -->
<!--                                                                          -->
<!-- THE WHITELIST RULE: if a doc is not in this map, it is not for           -->
<!-- orientation — do not read it. A stale doc is UNLINKED or DELETED, never -->
<!-- flagged in place. No freshness tags. No "do-not" guards. No state.       -->
<!-- Behavioral rules live in CLAUDE.md, not here.                            -->
<!--                                                                          -->
<!-- This file is LOW-CHURN. It changes only when how-to-get-oriented        -->
<!-- changes — i.e. a doc is added or removed. It is not a worklog and is    -->
<!-- not regenerated per session.                                            -->
<!-- ═══════════════════════════════════════════════════════════════════════ -->

# CONTEXT_MAP — Regin

## Purpose

The definition resolver: it takes an agent definition as authored and resolves it into one frozen, gate-validated artifact — answering *what is this agent*, never how it reads.

---

## Orientation gate — read these, in this order, to be oriented

1. `~/ai/smidja/galdr/context/AGENT_BUILD_SYSTEM.md` — why the pipeline exists at all: determinism as the goal, and the double gate that makes an LLM-written transform safe to have in a pipeline.
2. `~/ai/smidja/galdr/context/REGIN_ELEMENT.md` — Regin's own reason for being: the delta principle, the uniform runner, why checkpoints are written to disk, and why L7 regroups.

> **This is a DAG, not a sequence.** It is the single thing every previous reader got
> wrong, and module names no longer encode order at all — the shape lives only in the
> wiring. Read the graph before you read any branch.

3. `BRANCH_EXPLAINED.md` — the branch pattern: what every stage has in common, and why they are interchangeable in form.
4. `src/regin/cli.py` — short, and the only place the ordering exists. `run_trunk`, `run_fanout`, `run_convergence` name the shape directly.

> The next four are read by you, personally, in this context — never delegated to a
> subagent, never absorbed via a summary.

5. `WHY_THIS_FEELS_WRONG.md` — the frame: what this environment is, and why it will feel over-constrained until you understand it.
6. `EVERY_CHECK_IS_A_PROXY.md` — why the feedback steers where it steers. Read before the next one, so the level system reads as engineering rather than as limits.
7. `THE_LEVEL_SYSTEM.md` — zones, levels, and the decision procedure for where every piece of code lives.
8. `HOW_DATA_ENTERS.md` — the boundary: how external data becomes typed, and why unknown data never gets in.

**Proof:** before writing anything, state (a) which stages run in parallel and how you know, (b) what *"Delta: NONE — the gate IS the branch"* means and why that is a legitimate stage rather than a stub, and (c) one thing you would have written that this architecture forbids.

---

## Refresh guide — want X → read Y

| Need | Read |
|------|------|
| what a single branch must do | `BRANCH_EXPLAINED.md`, then the two checkpoint schemas it sits between — the delta between them *is* the job |
| where a field goes through L7 and L8 | `src/regin/logic/transform/section_regroup/` and `src/regin/logic/transform/vendor_compose/`, read against the universal-format, universal-render and anthropic-render schemas |
| how to run it | `src/regin/cli.py` — the CLI is the truth; `uv run regin <input.toml> -o <dir>` |
| where a function goes / what zone / what level | `THE_LEVEL_SYSTEM.md` |
| how external data becomes typed / a shape has no model | `HOW_DATA_ENTERS.md` |
| what the gates guarantee, and the four gate patterns | `~/ai/smidja/galdr/context/NORNIR_GATES_ELEMENT.md` |
| which gates exist, each one's kind and schema | `~/ai/smidja/nornir/gates/gate_recipes.toml` |
| what the checkpoint schemas allow | `~/ai/smidja/verdandi/agent-builder/output/*.schema.json` |
| what consumes the output | `~/ai/smidja/galdr/context/GALDR_ELEMENT.md` — `anthropic_render.toml` is Galdr's data axis |
| the models under `structure/gen/` | generated from the schemas; editing them does nothing. Change the Verdandi YAML and run the cascade |
| the full forward cascade after an edit | `~/ai/smidja/galdr/context/AGENT_BUILD_SYSTEM.md` § The forward cascade |
| current state / what's left to build | `PLAN.md` (+ `git log`) |
