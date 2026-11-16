# Regin — Context Refresh Protocol

## STOP. Read this before writing any code.

You have context from a compaction summary or from earlier in this session. You feel like you understand this project well enough to start working. **You are almost certainly wrong.**

After compaction, you have a summary — not understanding. The summary preserves conclusions but loses reasoning, constraints, and the specific shapes of things. You will produce output that looks right, compiles, and silently violates the project's architecture because the summary told you WHAT but not HOW or WHY NOT.

**This has happened before.** Previous sessions in this project have produced output that compiled, passed review, and implemented the wrong architecture — work that had to be thrown away.

None of them felt uncertain while doing it.

**The test:** Can you state three specific constraints of this project that diverge from how you'd normally write this code? Not "I should be careful" — actual constraints, with reasons. If you can't, you don't have enough context to write code. Orient via the CONTEXT_MAP `@import`ed below before proceeding — start with its orientation gate.

---
<!-- ═══════════════════════════════════════════════════════════════════════ -->
<!-- EVERYTHING ABOVE THIS LINE IS STANDARDIZED — DO NOT MODIFY            -->
<!-- EVERYTHING BELOW THIS LINE IS PROJECT-SPECIFIC                        -->
<!-- ═══════════════════════════════════════════════════════════════════════ -->
---

## Project Instructions

- **A stage is the delta between two checkpoint schemas.** Before reading or writing a stage, compare the schema it reads with the schema it writes. What the second requires that the first lacks is the whole job.
- **Change a shape at its source.** A model or a schema is changed in the Verdandi YAML and carried forward by the cascade. Generated output is overwritten on the next generation.
- **Data enters and leaves through a compiled gate or reader.** A file with no gate or no schema goes to the user as a request for one; it waits at the door until then.
- **Order lives in the wiring.** A module is named for what it operates on and what it does; a checkpoint is named for the state it holds. The graph is stated once, where the stages are called.
- **Write one file at a time.** Feedback arrives automatically on every write and points at one thing when the write is one file. Follow its direction.
- **Confirm a change by running the pipeline on a real definition into a scratch directory.** Every stage's output gate and the next stage's input gate check the result.

---

## How you orient — first time or recovery (same thing)

Orienting and recovering are one act: read the project's main documents, **routed by the
`CONTEXT_MAP` auto-included below** — start with its **orientation gate**, which *is* the
recovery-source list. If already verifiably oriented you needn't re-read everything; the map
always tells you where things live.

---

@CONTEXT_MAP.md
