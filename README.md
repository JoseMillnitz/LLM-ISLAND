<p align="center">
  <img src="assets/logo.png" alt="LLM Island System" width="320">
</p>

<h1 align="center">LLM Island System</h1>

<p align="center"><em>A semantic companion layer for codebases, optimized for LLM reasoning.</em></p>

<p align="center">
  <a href="VERSION_HISTORY.md"><img alt="Version" src="https://img.shields.io/badge/version-0.3%20Ouroboros-blueviolet"></a>
  <a href="SPEC/"><img alt="Spec" src="https://img.shields.io/badge/spec-modular-blue"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-AGPL--3.0-orange"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-blue">
  <img alt="Deps" src="https://img.shields.io/badge/deps-stdlib%20only-success">
</p>

---

LLMs working on codebases start cold every session. They re-derive *what does this file do*, *who depends on it*, *what breaks if I change X* from scratch — by reading code, simulating execution, and inferring intent. This costs tokens, introduces errors, and gets worse as codebases grow.

The LLM Island System externalizes that reasoning into structured companion files alongside your code. Instead of re-deriving impact, the LLM re-reads it. The answer to **"what is the total transitive impact of changing this?"** is already written down.

---

## What it is — and what it isn't

| It is | It is not |
|---|---|
| A pre-computed reasoning layer for LLMs | A new programming language |
| A semantic contract registry | A documentation system for humans |
| An architectural memory system | A test framework or build tool |
| A change-impact oracle | A runtime or compiler |
| A mid-term bridge until something better exists | A replacement for code |

Language-agnostic. LLM-first. Adoptable today on any codebase. Replaceable when something more fundamental arrives.

---

## How it works

Every source file gets a companion island file:

```
renderer.js                   ← your code, unchanged
renderer.js.llmisland         ← semantic companion
```

A single mainland at the project root aggregates the architectural graph:

```
connections.llmainland
```

The island describes everything the code alone does not make obvious — what each exported symbol does, its full effect declaration, who calls it, what its load-bearing constraints are, and a stratified memory log of decisions made and lessons learned.

The mainland describes intended architecture, all connections between files with explicit break-impact, and formal contracts — invariants whose violation causes silent failures.

Together they let an LLM answer, without reading and simulating the entire codebase from scratch:

- What is the blast radius of changing this function?
- What contracts does this change risk violating?
- Has this approach been tried before?
- What are the load-bearing constraints I must not break?

### File format at a glance

```
---HEADER---
file:           renderer.js
language:       javascript
role:           Canvas drawing — scene grid, player grid, cell types
layer:          presentation
status:         verified
last-verified:  v7-2024-03-15

---SYMBOLS---

SYMBOL: drawSceneGrid
kind:     function
pure:     false
total:    true
effects:
  reads:    canvas-context, SHAPES, sceneGrid
  mutates:  canvas-context (draw calls only)
  throws:   never
  async:    false
  io:       canvas write
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

Full format reference: [`LLMISLAND_SPEC.md`](LLMISLAND_SPEC.md) is the routing entrypoint; operational content lives under [`SPEC/`](SPEC/) as 14 focused modules.

---

## Key properties

| Property | What it means |
|---|---|
| **Language agnostic** | Works for JavaScript, Python, C, Rust, Assembly, or any mixture. Cross-language pipeline boundaries are modeled explicitly. |
| **LLM-first format** | Optimized for machine generation and parsing. Human readability is a tooling concern — a visualizer can be built on top. Density and unambiguity over prose. |
| **Honest incompleteness** | A partial island is valid. Silence where there should be a declaration is not. `?` marks unknowns; `N/A` marks not-applicable. The system never fabricates certainty. |
| **Propagation discipline** | When code changes, its island changes. When a connection changes, the mainland changes. When the mainland changes, bound islands are checked. Stale islands are lies. |
| **Stratified memory** | Active constraints (must be respected), historical decisions (why the design is this way), superseded (archaeological record, never deleted). When historical decisions exceed 20 entries, they archive to `.llwasland`. |
| **Boot modes** | An LLM doesn't need to read the whole codebase to start. Mode 1 (Incremental, default) maps only what the task requires. Mode 2 (Connection-First) builds the dependency graph without bodies. Mode 3 (Full Mapping) is reserved for audits. Paste `LLM_BOOT.md` at session start. |

The LLM is the primary author and maintainer of island files. Humans may edit them, but edits are flagged as `maintained-by: human-unreviewed` until an LLM reviews them and confirms they match what the system expects.

---

## Status — v0.3 Ouroboros

The codename names the structure: tooling for the project that has the project for the tooling. The mainland describes the tooling, the tooling validates the mainland, the islands describe the tools that read the islands. v0.3 is the release where that loop closes for the first time — the snake reaches its tail.

What shipped:

- **All 14 issues from adversarial review resolved.** Gemini, Grok, and Mistral attacked the v0.2 spec; every cataloged issue was addressed across v0.2.1—v0.2.14.
- **Tiered update obligations** (Tier A / B / C) replace the all-or-nothing maintenance rule.
- **Propagation cascades** are tracked in a separate `.llmpropstts` file managed by `llmisland_tooling.py`, not the mainland.
- **New island fields**: `generation-pass`, `read-reason`, `runtime-dependencies`, `confidence-review-due`, `dynamic-boundary`, `cycle`, `self-checkable`, `condition`, `security-reviewed`.
- **Two new core principles**: UNCERTAINTY OVER PLAUSIBILITY and DETECTABLE FAILURE.
- **Modular spec.** `LLMISLAND_SPEC.md` is now a 47-line topic-table router; the operational content lives under [`SPEC/`](SPEC/) as 14 focused modules.
- **Reference tooling** — 8 subcommands, standard library only, Python 3.10+:
  ```
  check-stale     check-decay     spec
  prop-start      prop-done       prop-status     prop-finish
  validate-rules  validate
  ```
- **Self-applied.** This project is the first to describe itself with the system: every Python source under [`tooling/`](tooling/) ships with a hand-written `.llmisland`; [`connections.llmainland`](connections.llmainland) describes the tooling architecture; the validator passes its own metadata cleanly.
- **File-size discipline** (~200 / ~300 / 400+) added to [`CONTRIBUTING.md`](CONTRIBUTING.md) and applied across the project.

Full dated changelog: [`VERSION_HISTORY.md`](VERSION_HISTORY.md).

---

## Try the tooling

```bash
# Validate every island and the mainland
python llmisland_tooling.py validate .

# Compare every island's last-verified against source mtime
python llmisland_tooling.py check-stale .

# Look up a spec module by topic (skips the routing table round-trip)
python llmisland_tooling.py spec --topic propagation

# Start a propagation cascade
python llmisland_tooling.py prop-start --cascade game.js input.js \
    --origin "renderer.js Tier C change"

# Extract self-checkable architectural rules for LLM compliance review
python llmisland_tooling.py validate-rules --diff path/to/change.diff
```

Standard library only. No `pip install`. Every subcommand accepts `--json` for CI integration.

---

## Where this is going

v0.3 closes the prompting + reference-tooling design space. Forward work is about making the system cheaper to use, easier to integrate, and easier to install. None of the directions below are committed; they signal where the project is headed, not what is queued. They span multiple future versions; there is no roadmap pinning them yet.

| Direction | What |
|---|---|
| **Less LLM context per task** | Bootstrap script for example/MVM generation; field-level island update commands so an LLM doesn't rewrite whole files. |
| **API entrypoints** | HTTP and/or library bindings so non-Python callers (IDEs, CI, other languages) can plug in without reimplementing the parser. Stay language-agnostic. |
| **Cross-platform without a runtime** | PyInstaller bundle, Go/Rust rewrite, or a hybrid (most-invoked subcommands as a static binary; reference impl stays in Python). Open question. |
| **Programmatic adoption** | Auto-island generation from source ASTs; runtime hooks for existing projects; IDE integration. |
| **Documentation islands** | Extend the format so spec docs describe themselves. Lets `bootstrap-mode` flip from `legacy` to `greenfield` project-wide. |
| **Cross-pollination** | Visualization patterns from existing graph tools (`graphify` and similar); event-history conventions for the considerations log. |
| **Deferred-tooling backlog** | Five items from `connections.llmainland` MHD-005: File Edit Hook, Human Island Editor, Security Integrity Checker, Mainland Slicer, Subjective Field Linter. |

---

## Repo layout

```
LLMISLAND_SPEC.md         routing entrypoint with topic table (47 lines)
VERSION_HISTORY.md        dated changelog
README.md                 this file
CONTRIBUTING.md           contribution guide + file-size discipline
INSTALATION_GUIDE.md      step-by-step adoption
LLM_BOOT.md               paste at session start; decision tree
LICENSE                   AGPL-3.0

SPEC/                     14 modular spec files + README routing table
MODES/                    detailed mode-1/2/3 process notes
SCENARIOS/                bootstrapping scenarios (greenfield/legacy/...)
EXAMPLES/                 annotated .llmisland / .llmainland / .llwasland
assets/                   logo and other static images

connections.llmainland    tooling architecture mainland (project root)
llmisland_tooling.py      CLI orchestrator
llmisland_tooling.py.llmisland
tooling/                  subcommand modules + their islands
```

---

## Adopting it

See [`INSTALATION_GUIDE.md`](INSTALATION_GUIDE.md) for the step-by-step.

> [!IMPORTANT]
> Before committing your project, read [`SPEC/12_ADOPTION.md`](SPEC/12_ADOPTION.md) on the minimum viable adoption floor. Partial adoption below that floor is more dangerous than no adoption — stale islands become authoritative-looking lies that mislead LLMs more than no islands at all.

---

## Known limitations

The system was adversarially reviewed by Gemini, Grok, and Mistral during the v0.2 cycle. All 14 cataloged issues were resolved across v0.2.1—v0.2.14 (resolutions recorded in [`VERSION_HISTORY.md`](VERSION_HISTORY.md)). What remains is intentional scope:

**The system works best when:**
- LLM sessions are the primary development mode, not occasional assistance
- The team is small and disciplined, or solo
- The project is greenfield or has a focused scope
- A staleness checker (`llmisland_tooling.py check-stale`) runs before every session

**Mid-term framing.** The long-term answer is a programming language or IR natively designed for LLM authorship — where dependency graphs, effect declarations, provenance, and formal contracts are language primitives, not companion files. Until that exists in production-ready form, this layer approximates it. Island files are designed to be a migration path, not a dead end.

**Acknowledged philosophical concern (ISSUE-010, the "mid-term trap").** By making the workaround viable, the system may delay urgency to build the real solution. Acknowledged, not resolved. Contributions that connect island fields to native primitives in a future LLM-first language are welcome.

---

## Acknowledgments

The intellectual foundation comes from **Fábio Akita**'s writing on what a programming language optimized for LLMs would look like — specifically the insight that the things LLMs need most (semantic metadata, bidirectional traceability, formal effect declarations, queryable dependency graphs, embedded provenance) are exactly the things human-oriented language design has consistently removed because humans experience them as friction.

See: [akitaonrails.com — *AI Agents: Qual seria a melhor Linguagem de Programação para LLMs?*](https://akitaonrails.com/2026/02/09/ai-agents-qual-seria-a-melhor-linguagem-de-programacao-para-llms/)

The v0.2 → v0.3 release chain was driven by adversarial-review responses from **Gemini**, **Grok**, and **Mistral** (cataloged across v0.2.1—v0.2.14) and shaped by parallel implementation work from **GPT-Codex** and **Claude Sonnet + Gemini in Antigravity**. Their tooling sketches and prompting roadmaps were absorbed into this project's design as `HISTORICAL-DECISIONS` entries.

---

## License

AGPL-3.0. See [LICENSE](LICENSE).
