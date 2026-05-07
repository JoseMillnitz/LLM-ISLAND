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

The current spec is **v0.3 — Ouroboros**.

The codename is the project's structure: tooling for the project that
has the project for the tooling. The mainland describes the tooling,
the tooling validates the mainland, the islands describe the tools
that read the islands. v0.3 is the release where that loop closes for
the first time.

What v0.3 ships:

- **All 14 issues from adversarial review resolved.** Gemini, Grok, and
  Mistral attacked the v0.2 spec; every cataloged issue was resolved
  across the v0.2.1—v0.2.14 release chain.
- **Tiered update obligations** (Tier A / B / C) replace the
  all-or-nothing maintenance rule.
- **Propagation cascades** are tracked in a separate `.llmpropstts`
  file managed by `llmisland_tooling.py`, not the mainland.
- **New island fields** for v0.2.x format extensions: `generation-pass`,
  `read-reason`, `runtime-dependencies`, `confidence-review-due`,
  `dynamic-boundary`, `cycle`, `self-checkable` (architectural-rules),
  `condition` (CONTRACTS), `security-reviewed` (maintained-by).
- **Two new core principles:** UNCERTAINTY OVER PLAUSIBILITY and
  DETECTABLE FAILURE.
- **Modular spec.** `LLMISLAND_SPEC.md` is now a 47-line router with a
  topic table; the operational content lives under `SPEC/` as 14
  focused modules.
- **Reference tooling** (`llmisland_tooling.py` + `tooling/` package):
  8 subcommands — `check-stale`, `check-decay`, `spec`, `prop-start`,
  `prop-done`, `prop-status`, `prop-finish`, `validate-rules`,
  `validate`. Standard library only; no third-party dependencies.
- **Self-applied.** Mix is the first project to describe itself with
  the system. Every Python source under `tooling/` ships with a
  hand-written `.llmisland`; `connections.llmainland` describes the
  tooling architecture; the validator passes mix's own metadata
  cleanly. The system contains itself.
- **File-size discipline** (~200 / ~300 / 400+) added to
  `CONTRIBUTING.md` and applied across the project.

Read `VERSION_HISTORY.md` for the dated changelog of every release.

---

## Where this is going

v0.3 closes the prompting + reference-tooling design space. The forward
work is about making the system cheaper to use, easier to integrate,
and easier to install. None of the directions below are committed —
they signal where the project is headed, not what is queued. They span
multiple future versions; there is no roadmap yet that pins them to
specific releases.

**Less LLM context per task.** Most current cost is the LLM reading
and writing islands directly. Two shifts to reduce that:
- A `bootstrap` subcommand that creates a fresh project's MVM mainland
  and starter island templates from a template, so an LLM does not
  have to read `EXAMPLES/` to remember the format.
- Field-level tooling for routine island updates: an `island update
  FILE --field last-verified --value v0.3-2026-05-07` style command
  instead of the LLM rewriting the file. Same shape for bumping
  versions, marking `maintained-by`, etc.

**API entrypoints for non-CLI integration.** Today the tool is invoked
from the command line. To plug into IDEs, CI runners, or non-Python
toolchains, the project needs entrypoints (HTTP and/or library) that
expose every CLI capability programmatically. The spec is already
language-agnostic; the API surface should preserve that — a non-Python
caller should be able to validate, route, or update without
reimplementing the regex parsers.

**Cross-platform without a runtime.** The tooling currently needs
Python 3.10+. For broader adoption that is a real friction. Three open
candidates, no decision yet:
- PyInstaller / Nuitka — bundle the existing Python tooling. Easy but
  produces large binaries and is fragile on Windows.
- Rewrite in a binary-producing language (Go, Rust). Single static
  binary, zero runtime dependencies. Substantial work but solves the
  friction completely.
- Hybrid — Python for the reference implementation, a separate static
  binary for the most-invoked subcommands (validate, check-stale,
  spec --topic).
The locked principle for now: standard library only, so any future
binary path stays small.

**Programmatic adoption.** Today the system needs hand-authored
islands per file. Future: auto-island generation from source ASTs,
runtime hooks for existing projects, IDE integration. Would change
the bootstrap story — `bootstrap-mode: legacy` projects could be
picked up automatically rather than requiring a phase-1 generation
pass.

**Documentation islands.** v0.3's tooling layer is islanded; spec
docs are not (per the locked tooling-only scope). A future release
could extend the format to handle markdown-as-source so the system
describes its own documentation. The project's `bootstrap-mode` would
flip to `greenfield`.

**Cross-pollination from existing tools.** The mainland is essentially
a dependency graph; the considerations log is essentially append-only
event history. There's likely value in absorbing patterns from tools
that do these well — visualization layers like `graphify` for the
mainland graph, append-only event-history conventions for the
considerations log — once the core is stable. The specific ideas to
pick up are not yet enumerated; this is a "see what fits later"
direction, not a queued task.

**Deferred-tooling backlog.** `connections.llmainland` MHD-005 lists
five ideas from the fork `tooling_idea_*.md` files that did not make
v0.3 because their prerequisites were not ready: File Edit Hook,
Human Island Editor, Security Integrity Checker, Mainland Slicer,
Subjective Field Linter. Each gets built when its prerequisite
design lands.

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
