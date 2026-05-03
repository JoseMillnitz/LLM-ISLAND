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

The current spec is **v0.3-rc1** — the first of a small chain of release
candidates that progressively deliver v0.3.

The big shifts since v0.2:
- 14 issues from adversarial review (Gemini / Grok / Mistral) resolved across
  v0.2.1 through v0.2.14.
- Tiered update obligations (Tier A/B/C) replace the all-or-nothing rule.
- Propagation cascades are tracked in a separate `.llmpropstts` file
  managed by `llmisland_tooling.py`, not in the mainland.
- `generation-pass`, `read-reason`, `runtime-dependencies`,
  `confidence-review-due`, `dynamic-boundary`, `cycle`,
  `self-checkable` (architectural-rules), `condition` (CONTRACTS),
  `security-reviewed` (maintained-by) added.
- Two new core principles: UNCERTAINTY OVER PLAUSIBILITY and
  DETECTABLE FAILURE.
- File-size discipline (~200 / ~300 / 400+) added to `CONTRIBUTING.md`.

Read `VERSION_HISTORY.md` for the dated changelog of every release.

**Remaining v0.3 work** (release candidate chain):
- v0.3-rc2: split `LLMISLAND_SPEC.md` into modular `SPEC/` files
  (island format modules)
- v0.3-rc3: operational sections to `SPEC/` (mainland, tiers, propagation, validity)
- v0.3-rc4: remaining sections to `SPEC/`
- v0.3 final: router cleanup + cross-reference updates + tag

---

## Known Limitations

The system was adversarially reviewed by Gemini, Grok, and Mistral during
the v0.2 cycle. All 14 cataloged issues were resolved across v0.2.1 → v0.2.14
(the resolutions are recorded in `VERSION_HISTORY.md`). The remaining
limitations are not unsolved problems — they are intentional scope:

**The system works best when:**
- LLM sessions are the primary development mode, not occasional assistance
- The team is small and disciplined, or solo
- The project is greenfield or has a focused scope
- A staleness checker (e.g. `llmisland_tooling.py check-stale`) runs before
  every LLM session

**The system is a mid-term solution.** The long-term answer is a programming
language or IR natively designed for LLM authorship, where dependency graphs,
effect declarations, provenance, and formal contracts are language primitives.
Until that exists in production-ready form, this companion-file layer
approximates it. Island files are designed to be a migration path, not a
dead end.

**What is not yet automated.** The spec calls for tooling at several
points (staleness check, propagation cascade tracking, rule validation,
confidence decay, context routing). The reference implementation is
`llmisland_tooling.py` — built in the next phase. Until it lands, manual
fallbacks are documented in the spec for every tool-dependent behavior.

**Acknowledged philosophical concern (ISSUE-010, the "mid-term trap").**
By making the workaround viable, the system may delay urgency to build the
real solution. This is acknowledged, not resolved. Contributions that
explicitly connect island fields to native primitives in a future LLM-first
language are welcome.

---

## Files in this system

| File | Purpose |
|------|---------|
| `LLMISLAND_SPEC.md` | The normative specification — read this before implementing |
| `VERSION_HISTORY.md` | Dated changelog: every release with rationale and source attribution |
| `LLM_BOOT.md` | Paste at the start of every LLM session — tells the LLM which boot mode to use |
| `INSTALATION_GUIDE.md` | Step-by-step guide for introducing the system to a project |
| `CONTRIBUTING.md` | How to contribute to the spec, plus file-size discipline |
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
