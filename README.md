# LLM Island System

A semantic companion layer for codebases, designed to make LLM-assisted development faster, cheaper, and more reliable — without replacing any existing language, tool, or workflow.

---

## What problem does this solve?

LLMs working on codebases start cold every session. They re-derive "what does this file do", "who depends on it", "what breaks if I change X" from scratch — by reading code, simulating execution, and inferring intent. This costs tokens, introduces errors, and gets worse as codebases grow.

The LLM Island System externalizes that reasoning into structured companion files that live alongside your code. Instead of re-deriving impact, the LLM re-reads it. The answer to **"what is the total transitive impact of changing X?"** is already written down.

---

## What it is not

This is **not** a new programming language. It does not compile. It does not replace your existing stack.

It is a **mid-term pragmatic solution** — a structured metadata layer that can be adopted today, on any codebase, in any language, and immediately improves how LLMs reason about that code. It exists because a true LLM-native programming language (one where formal specifications, effect tracking, dependency graphs, and provenance are first-class primitives) does not yet exist in a form ready for production use.

When such a language eventually exists and reaches production maturity, this system will have served its purpose. Until then, it solves most of the same problems at the cost of discipline rather than compiler enforcement.

The intellectual foundation for this system comes from Akita's writing on what a programming language optimized for LLMs would look like — specifically the insight that the things LLMs need most (semantic metadata, bidirectional traceability, formal effect declarations, queryable dependency graphs, embedded provenance) are exactly the things that human-oriented language design has consistently removed because humans experience them as friction. See: [akitaonrails.com — AI Agents: Qual seria a melhor Linguagem de Programação para LLMs?](https://akitaonrails.com/2026/02/09/ai-agents-qual-seria-a-melhor-linguagem-de-programacao-para-llms/)

---

## How it works

Every source file gets a companion island file:

```
renderer.js          ← your code, unchanged
renderer.js.llmisland  ← semantic companion
```

A single mainland file at project root aggregates the full dependency graph:

```
connections.llmainland
```

The island describes everything about the file that the code alone does not make obvious: what each exported symbol does, its full effect declaration, who calls it, what its active constraints are, and a stratified memory log of decisions made and lessons learned.

The mainland describes the intended architecture, all connections between files with explicit break-impact, and formal contracts — invariants that, if violated, cause silent failures.

Together they let an LLM answer:
- What is the blast radius of changing this function?
- What contracts does this change risk violating?
- Has this approach been tried before?
- What are the load-bearing constraints I must not break?

Without reading and simulating the entire codebase from scratch.

---

## Key properties

**Language agnostic.** Works for JavaScript, Python, C, Rust, Assembly, or any mixture. Cross-language pipeline boundaries are modeled explicitly in the mainland.

**LLM-first format.** The format is optimized for machine generation and parsing. Human readability is a tooling concern — a visualizer can be built on top of the standard. The format itself prioritizes density and unambiguity over prose.

**Honest incompleteness.** A partial island is valid. Silence where there should be a declaration is not. Unknown fields use `?`. Not applicable uses `N/A`. The system never fabricates certainty.

**Propagation discipline.** When code changes, its island changes. When a connection changes, the mainland changes. When the mainland changes, all bound islands are checked. This chain keeps the system accurate over time.

**Stratified memory.** The considerations log has three layers: active constraints (must be respected now), historical decisions (explains why the design is this way), and superseded decisions (archaeological record, never deleted). Active constraints stay small. When historical decisions exceed 20 entries, they are archived to a `.llwasland` file — the memory of what the island *was*.

**Boot modes.** An LLM does not need to read the whole codebase to start working. Mode 1 (Incremental, the default) maps only what the current task requires. Mode 2 (Connection-First) builds the architectural graph from imports/exports without reading bodies. Mode 3 (Full Mapping) is reserved for audits. Paste `LLM_BOOT.md` at session start to enforce the right mode automatically.

---

## File format at a glance

```
---HEADER---
file:         renderer.js
language:     javascript
role:         Canvas drawing — scene grid, player grid, cell types
layer:        presentation
status:       verified
last-verified: v7-2024-03-15

---SYMBOLS---

SYMBOL: drawSceneGrid
kind:     function
pure:     false
total:    true
effects:
  reads:   canvas-context, SHAPES, sceneGrid
  mutates: canvas-context (draw calls only)
  throws:  never
  async:   false
  io:      canvas write
called-by:
  - game.js :: renderFrame() :: on every state update
fragility:    medium
fragility-note: cell coordinate calculation depends on SHAPES layout

---RISKS---
security: none
regression-sensitivity:
  - cell sizing formula changes break visual regression baselines

---MEMORY---

ACTIVE-CONSTRAINTS:
  - id: AC-001
    constraint: coordinate origin is top-left; changing this breaks
                input.js hit detection and all regression baselines
    established: 2024-01-10
```

Full format specification: see `LLMISLAND_SPEC.md`.

---

## Who maintains island files?

**The LLM is the primary author and maintainer.** Island files are updated as part of every task that touches the corresponding source file. A task is not complete until affected islands are current.

Humans may edit island files, but edits are flagged as `maintained-by: human-unreviewed` until an LLM reviews them and confirms they match what the system expects. The LLM will confront inconsistencies — the human clarifies, the island is updated.

---

## Compatibility with existing practices

The system is additive. It does not change your code, your tests, your build system, or your version control workflow. It adds files alongside what you already have.

It aligns naturally with Extreme Programming: collective code ownership becomes safe because any agent can read an island and immediately understand the context; refactoring starts with reading active constraints instead of simulating impact; test islands declare business rules as formal contracts rather than just coverage.

---

## Status

This is version **0.2** of the specification. Changes from v0.1: three boot modes
added (Incremental, Connection-First, Full Mapping), Minimum Viable Mainland
template, confidence-gated expansion rules, stop-early rule, `.llwasland` archive
format replacing `.llmhistory`. See `LLMISLAND_SPEC.md` for the full specification,
validity rules, status progression model, and bootstrapping guides.

**v0.3 is in planning.** The spec was stress-tested by three LLMs asked to attack
its weaknesses. Their responses are cataloged in `ATTACK_ANALYSIS.md`. That file
is the v0.3 roadmap.

---

## Known Limitations

This system was adversarially reviewed by Gemini, Grok, and Mistral. Their
findings are fully documented in `ATTACK_ANALYSIS.md`. The honest summary:

**The system works best when:**
- LLM sessions are the primary development mode, not occasional assistance
- The team is small and disciplined, or solo
- The project is greenfield or has a focused scope
- At minimum a staleness-checker script runs in CI

**The system's known structural weaknesses (v0.2):**

*Maintenance tax* — updating islands on every change costs real velocity. v0.3
will introduce tiered update obligations so not every change requires a full
island update.

*Propagation atomicity* — a cascade of updates across many islands can hit LLM
output limits mid-way, leaving the graph in a contradictory state. v0.3 will
add an in-progress propagation state and a cascade size threshold.

*Hallucination fossilization* — LLMs fill in plausible-sounding values for
subjective fields rather than using `?`. Once written, these become canonical.
v0.3 will add explicit decision criteria for all subjective fields.

*No native staleness detection* — without tooling that compares `last-verified`
against file modification timestamps, stale islands look identical to fresh ones.
This is a hard dependency on tooling, not discipline.

*Constraint compliance gap* — an LLM reading a rule and an LLM following it are
not the same thing. The system is advisory, not enforced. Generated code must be
validated against architectural rules, not just hoped to comply.

*Adversarial injection* — island content is trusted as ground truth. In
multi-contributor or open-source contexts, malicious or accidental corruption of
island files is a real threat. Security-sensitive islands need higher review gates.

None of these are hidden or being ignored. They are the v0.3 agenda.

---

## Files in this system

| File | Purpose |
|------|---------|
| `LLMISLAND_SPEC.md` | Full specification — read this before implementing |
| `LLM_BOOT.md` | Paste at the start of every LLM session — tells the LLM which boot mode to use |
| `INSTALATION_GUIDE.md` | Step-by-step guide for introducing the system to a project |
| `CONTRIBUTING.md` | How to contribute to the spec |
| `ATTACK_ANALYSIS.md` | Adversarial review findings — known weaknesses and v0.3 roadmap |
| `README.md` | This file |

| Folder | Purpose |
|--------|---------|
| `MODES/` | Detailed instructions for each boot mode |
| `SCENARIOS/` | Bootstrapping guides for greenfield, legacy, archaeological, and cross-language projects |
| `EXAMPLES/` | Annotated example `.llmisland`, `.llmainland`, and `.llwasland` files |

File types used in projects:

| Extension | Purpose |
|-----------|---------|
| `.llmisland` | Semantic companion to a source file |
| `.llmainland` | Architectural graph for the project (one file: `connections.llmainland`) |
| `.llwasland` | Archive of historical decisions when an island's memory grows too large |
