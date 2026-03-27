# LLM Island System — Specification v0.1
# A semantic companion layer for codebases, optimized for LLM reasoning

---

## INTELLECTUAL ORIGIN

This specification is heavily based on the ideas of Fábio Akita, specifically his
article "AI Agents: Qual seria a melhor Linguagem de Programação para LLMs?"
(February 9, 2026, akitaonrails.com). That article — itself a synthesis of
responses from Claude and GPT — explored what a programming language optimized
for LLMs rather than humans would look like. The core insight: the features
humans find most ergonomically unpleasant (formal effect declarations, queryable
dependency graphs, rich semantic metadata, embedded provenance, bidirectional
traceability) are exactly what an LLM needs to reason about code reliably.

Akita's prototype described a four-layer system: a human specification layer, an
AI-native AST format, a human-readable projection, and a semantic edit protocol.
The LLM Island System does not implement that vision — it draws from it.

## THIS IS A MID-TERM SOLUTION

This system is not a programming language for LLMs that compiles. It does not
replace source code. It does not introduce a new runtime or toolchain.

What it does is sit alongside whatever language and tooling you already use and
give the LLM a pre-computed semantic layer that it would otherwise have to derive
from scratch every session.

The ideal long-term solution — described in Akita's article — is a language
natively designed for LLM authorship: an IR-rich format where dependency graphs,
effect declarations, provenance, and formal contracts are primitives, not
afterthoughts. That language does not yet exist in a form ready for production use.
Until it does, or until something equivalent emerges, developers and LLMs working
together need a practical bridge.

The LLM Island System is that bridge. It is a mid-term answer to a problem that
has a better long-term answer not yet built. It is designed to be useful today,
to be adoptable without changing your language or toolchain, and to be replaceable
when something more fundamental arrives. If and when a production-ready LLM-native
language exists, the island files become the migration path — they already contain
the semantic information that language would treat as native primitives.

Use this system knowing what it is: a pragmatic approximation of a better future,
useful enough to matter now.

---

## WHY THIS EXISTS

LLMs working on codebases face a structural problem: every session starts cold.
The LLM must re-derive "what does this file do", "who depends on it", "what breaks
if I change X" from scratch — by reading code, simulating execution, and inferring
intent. This is expensive in tokens, unreliable across sessions, and gets worse as
codebases grow.

This system solves that by externalizing the reasoning. Instead of re-deriving
impact, the LLM re-reads it. Instead of inferring intent, the LLM finds it
declared. The answer to "what is the total transitive impact of changing this
type?" is already written down. You just need to read it.

The insight comes from Akita's exploration of what a programming language designed
for LLMs rather than humans would look like. The answer involves rich semantic
metadata, bidirectional traceability, formal effect declarations, queryable
dependency graphs, and embedded provenance. Languages cannot easily be replaced —
but a companion file layer can provide all of these things alongside any existing
language.

This is that layer.

It is NOT:
- A replacement for code
- A documentation system for humans
- A test framework
- A build tool
- A new programming language

It IS:
- A pre-computed reasoning layer for LLMs
- A semantic contract registry
- An architectural memory system
- A change-impact oracle
- A mid-term bridge until something better exists

---

## CORE PRINCIPLES

1. SELF-CONTAINED — every island must be understandable with zero external context.
   An LLM reading an island for the first time, with no prior project knowledge,
   must be able to answer: what does this file do, what does it depend on, what
   depends on it, what are the load-bearing constraints, what breaks if I change X.

2. HONEST INCOMPLETENESS — a partial island is valid. Silence where there should
   be a declaration is not. Use explicit markers: ? for unknown, N/A for not
   applicable. Never leave a field blank.

3. LOAD-BEARING FOCUS — document what tooling cannot catch. If a compiler, type
   system, or test suite already enforces something, it does not need to be in the
   island. Islands exist for the things that fall through those gaps.

4. STRATIFIED MEMORY — active constraints, historical decisions, and superseded
   decisions are distinct layers. An LLM working on a task reads the active layer.
   It reads the historical layer to understand the solution space. The superseded
   layer is archaeological record — never deleted, rarely read.

5. LANGUAGE AGNOSTIC — the format works for any source language or mixed-language
   pipeline. Python calling C calling Assembly. A single project with six languages.
   The mainland models cross-language boundaries explicitly.

6. LLM-FIRST — the format is optimized for machine generation and parsing. Human
   readability is a tooling concern, not a format constraint. When human ergonomics
   and LLM clarity conflict, LLM clarity wins.

7. PROPAGATION DISCIPLINE — when code changes, its island changes. When a
   connection changes, the mainland changes. When the mainland changes, that is a
   signal to check all islands bound to the affected connection. This propagation
   is not optional — a stale island is a lie.

---

## FILE NAMING

  <source-file>.<ext>.llmisland      companion to each source file
  connections.llmainland             one per project, always at project root

Examples:
  renderer.js.llmisland
  generator.py.llmisland
  render_core.c.llmisland
  connections.llmainland

One island per source file. One mainland per project. No exceptions.

---

## ISLAND FILE STRUCTURE

Four sections, always in this order: HEADER, SYMBOLS, RISKS, MEMORY.

Delimiters:     ---SECTION_NAME---
Fields:         KEY: value
Multi-line:     indented continuation
Lists:          - item
Unknown:        ?
Not applicable: N/A

---

## SECTION 1: HEADER

Describes the file as a whole.

```
---HEADER---
file:           renderer.js
language:       javascript
role:           Canvas drawing — scene grid, player grid, cell types, long-press ring
layer:          presentation
status:         verified
confidence:     high
last-verified:  v7-2024-03-15
maintained-by:  llm
exports:
  - drawSceneGrid
  - drawPlayerGrid
  - drawCell
  - drawLongPressRing
imports:
  - i18n.js  :: I18n.t()
  - data.js  :: SHAPES, cellRoom
depends-on:
  - game.js  :: calls drawSceneGrid on state change
  - input.js :: triggers redraws on interaction
translation-boundary: none
```

FIELD REFERENCE:

file
  Exact filename as it appears on disk.

language
  Source language. For compiled or transpiled artifacts, list both:
  language: c -> mips-assembly
  language: typescript -> javascript

role
  One or two sentences. What this file does, not how. Not a list of functions.

layer
  Architectural layer. Allowed values:
    core          — domain logic, algorithms, data structures
    presentation  — rendering, display, visual output
    input         — user input, event handling
    data          — data loading, persistence, serialization
    io            — network, filesystem, external services
    orchestration — coordinates other modules, holds state machines
    i18n          — internationalization, localization
    test          — test files only
    config        — configuration, constants, environment
    build         — build scripts, tooling
    bridge        — cross-language or cross-system boundaries

status
  One of: verified | generated | inferred | stale | partial

  verified   — island was reviewed against the actual code and confirmed accurate
  generated  — produced automatically, not yet reviewed
  inferred   — produced archaeologically from behavior, not from author knowledge
  stale      — source file has changed since last-verified
  partial    — known to be incomplete; acceptable when bootstrapping

confidence
  One of: high | medium | low
  Reflects certainty of the content, especially for inferred islands.

last-verified
  Format: <version-or-id>-<date> or <date> if no version system exists.
  Required when status is verified.

maintained-by
  One of: llm | human-reviewed | human-unreviewed
  human-unreviewed means a human edited this island and it has not yet been
  reviewed by an LLM. This is a temporary state — it must be resolved before
  the island is used as ground truth.

exports
  All public symbols this file exposes. One per line.

imports
  All direct dependencies with the specific symbols used.
  Format: - <file> :: <symbol>, <symbol>
  Not just the file — the exact symbols. This is required.

depends-on
  Reverse dependency: who imports or uses this file, and why.
  Format: - <file> :: <reason>

translation-boundary
  If this file is part of a cross-language pipeline, declare it here.
  none if not applicable.
  Otherwise: translation-boundary: c -> wasm via emscripten

---

## SECTION 2: SYMBOLS

One entry per exported symbol.
For test files: one entry per test suite or logical test group.

```
---SYMBOLS---

SYMBOL: drawSceneGrid
kind:           function
pure:           false
total:          true
latency-budget: N/A
effects:
  reads:    canvas-context, SHAPES, cellRoom, sceneGrid
  mutates:  canvas-context (draw calls only)
  allocs:   minimal — path objects per cell, bounded by active cell count
  throws:   never
  async:    false
  io:       canvas write
called-by:
  - game.js :: renderFrame() :: on every state update
calls:
  - drawCell      :: for each active cell in sceneGrid
  - I18n.t()      :: room label lookup per visible room
expects:
  - canvas context must be initialized before call
  - sceneGrid must be non-null
  - SHAPES[currentShape] must exist in data.js
tests:
  unit:       none — canvas drawing not unit tested
  regression: regression_tests.js :: Suite 2 "renderer produces stable output"
  security:   none
business-rule: N/A
fragility:    medium
fragility-note: cell coordinate calculation depends on SHAPES layout;
                shape changes in data.js cascade directly here
```

FIELD REFERENCE:

SYMBOL: <name>
  The exported symbol name exactly as it appears in code.

kind
  One of: function | class | type | constant | module | hook | middleware

pure
  true if: no side effects AND same inputs always produce same outputs.
  false otherwise. When in doubt, false.

total
  true if: always terminates AND never throws/panics.
  false otherwise. If false and the symbol can non-terminate, explain in
  fragility-note.

latency-budget
  Expected or required execution time. N/A if not constrained.
  Examples: 50ms | <1 frame (16ms) | N/A

effects
  Complete declaration of everything this symbol can do.
  All six subfields are required. Use none explicitly, never leave blank.

  reads:    — what data sources it reads from
  mutates:  — what it modifies (be specific: which fields, which objects)
  allocs:   — what it allocates and whether bounded or unbounded
  throws:   — what errors/exceptions it can produce, or never
  async:    — true or false
  io:       — any I/O: network, filesystem, canvas, DOM, audio, etc., or none

called-by
  Format: - <file> :: <function> :: <context/when>
  Who calls this symbol, from where, and under what condition.

calls
  Format: - <symbol> :: <why/when>
  What this symbol directly calls and why.

expects
  Preconditions the caller must ensure. These are invariants the symbol
  does not check internally — it assumes they hold.

tests
  Explicit links. Required fields: unit, regression, security.
  Use none explicitly — never leave blank.
  Format: <test-file> :: <suite-name>

business-rule
  For test file symbols: REQUIRED. State the contract being asserted as a
  declaration, not a procedure.
  Good:  "player-placed confirmed cells are the only cells counted in verify"
  Bad:   "calls verifyBoard() and checks the result"
  For non-test symbols: N/A

fragility
  One of: low | medium | high
  LLM judgment of how likely a change here is to cascade unexpectedly.

fragility-note
  Required when fragility is medium or high.
  One or two sentences. Why is it fragile? What specifically can go wrong?

---

## SECTION 3: RISKS

File-level risk declarations. Concerns that apply to the whole file.

```
---RISKS---

security:
  - surface:     user input reaches drawCell via input.js coordinate path
    guarded-by:  NaN guard on cell coords in input.js
    test:        security_tests.js :: Suite 1 "invalid coordinates rejected"
    severity:    low

  - surface:     canvas state pollution between renders if context not reset
    guarded-by:  explicit context.clearRect at start of drawSceneGrid
    test:        none
    severity:    medium

regression-sensitivity:
  - any change to cell sizing formula breaks visual regression baselines
  - coordinate system changes cascade to input.js hit detection

platform-sensitivity:
  - canvas API behavior differs between desktop and mobile viewport
  - long-press ring is touch-specific — no equivalent desktop path
```

FIELD REFERENCE:

security
  List of security surfaces this file exposes or participates in.
  Each entry requires all four fields: surface, guarded-by, test, severity.
  severity values: low | medium | high | critical
  A medium-or-above surface with no guarded-by AND no test is an invalid island.

regression-sensitivity
  Plain statements of what changes are known to trigger regression failures.
  Written as statements. Be specific about what change causes what breakage.

platform-sensitivity
  Anything that behaves differently across platforms, runtimes, environments,
  browser versions, operating systems, or screen sizes.

If a category has no entries, write:
  security: none
  regression-sensitivity: none
  platform-sensitivity: none

---

## SECTION 4: MEMORY

The stratified considerations log.

```
---MEMORY---

ACTIVE-CONSTRAINTS:
  - id: AC-001
    constraint: cell coordinate origin is top-left; changing this breaks
                input.js hit detection and all visual regression baselines
    established: 2024-01-10
    evidence:    git:a3f9c12

  - id: AC-002
    constraint: drawLongPressRing must complete within one animation frame —
                it is called inside requestAnimationFrame
    established: 2024-02-03
    evidence:    inferred-from-call-site

HISTORICAL-DECISIONS:
  - id: HD-001
    decision:  canvas chosen over DOM elements for cell rendering
    reason:    DOM approach caused reflow jank on mobile at puzzle sizes above 6x6
    date:      2024-01-05
    outcome:   current implementation stable on both desktop and mobile
    evidence:  git:b2e1a09

SUPERSEDED:
  - id: SD-001
    was:            cells were rendered as absolutely positioned divs
    replaced-by:    canvas rendering (see HD-001)
    superseded-date: 2024-01-05
    keep-because:   explains why no CSS cell classes exist anywhere in codebase
```

FIELD REFERENCE:

ACTIVE-CONSTRAINTS
  Things currently true that MUST be respected by anyone touching this file.
  An LLM must read all active constraints before proposing any change.
  This list must stay small. If it exceeds 10 entries, the design has a
  problem — consider refactoring to reduce fragility.

  id:          AC-<number>, unique per island
  constraint:  the rule, stated precisely
  established: date or version when this was determined
  evidence:    git:<id> | inferred-from-<source> | N/A

HISTORICAL-DECISIONS
  Explains why the current design exists. Context, not rules.
  An LLM reads these to understand the solution space before proposing changes.
  "We tried X, it failed because Y, that is why we use Z."

  id:       HD-<number>
  decision: what was decided
  reason:   why
  date:     when
  outcome:  what resulted — is it still working, or did it need revision?
  evidence: git:<id> | inferred-from-<source> | N/A

SUPERSEDED
  Past decisions that no longer apply. NEVER deleted.
  Always carry keep-because — the reason the record is preserved.

  id:              SD-<number>
  was:             what was true before
  replaced-by:     what replaced it
  superseded-date: when
  keep-because:    why this record has ongoing archaeological value

evidence field values:
  git:<commit-id>            — git is available and commit exists
  inferred-from-<source>     — derived from behavior, comments, or documentation
  inferred-from-call-site    — derived from reading call sites
  inferred-from-tests        — derived from reading test assertions
  inferred-from-comments     — derived from existing code comments
  N/A                        — no evidence available; entry is best-effort

NOTE: git IDs are optional supplementary evidence, not the primary record.
The entry must be fully understandable without git access.

---

## MAINLAND FILE STRUCTURE

```
---ARCHITECTURE---
project:        SUDOKILL
version:        7
last-verified:  2024-03-15
description:    Browser-based deduction puzzle. Vanilla JS, Canvas, JSON data.
                No framework, no bundler, no server-side code.

layers:
  core:         [data.js, generator.js, clues.js]
  presentation: [renderer.js, ui.js, uiThemes.js]
  input:        [input.js]
  data:         [dataLoader.js]
  orchestration:[game.js]
  i18n:         [i18n.js]
  test:         [tests.js, tests_generator.js, tests_game.js, ...]

load-order:
  - i18n.js     :: MUST be first — all modules call I18n.t()
  - data.js
  - dataLoader.js
  - uiThemes.js
  - clues.js
  - generator.js
  - renderer.js
  - input.js
  - ui.js
  - game.js     :: entry point — DOMContentLoaded

architectural-rules:
  - AR-001: i18n.js has no dependencies — must never import any other module
  - AR-002: data.js is pure — no I/O, no side effects, no async
  - AR-003: dependency direction is always toward core — presentation must not
            be imported by core
  - AR-004: game.js is the only module permitted to hold mutable game state
  - AR-005: all user-visible strings must go through I18n.t() — never hardcoded

---CONNECTIONS---

CONNECTION: renderer.js -> data.js
  uses:         SHAPES, cellRoom
  why:          cell geometry is derived from shape definitions
  direction:    presentation -> core
  strength:     high
  break-impact: renderer cannot draw any cells — total visual failure

CONNECTION: generator.js -> data.js
  uses:         SHAPES, cellRoom, roomDefs
  why:          level generation requires grid geometry and room definitions
  direction:    core -> core
  strength:     critical
  break-impact: level generation fails completely — no puzzle can be created

CONNECTION: game.js -> generator.js
  uses:         LevelGenerator.generate()
  why:          game state machine triggers generation on new game
  direction:    orchestration -> core
  strength:     critical
  break-impact: new game fails — no new puzzles possible

CONNECTION: python_pipeline.py -> render_core.c
  uses:         render_frame(), init_context()
  why:          Python orchestration delegates frame rendering to C for performance
  direction:    bridge -> core
  language-boundary: python -> c via ctypes
  strength:     critical
  break-impact: all rendering fails

strength values:
  critical — system cannot function if broken
  high     — major feature loss if broken
  medium   — degraded experience if broken
  low      — cosmetic or minor impact if broken

---CONTRACTS---

CONTRACT: seed-determinism
  statement:    same seed + same settings + same data files = identical puzzle, always
  owned-by:     generator.js
  enforced-by:  regression_tests.js :: Suite 1 "seed determinism"
  islands-bound:[generator.js, dataLoader.js, data.js]
  violation-consequence: shared seed numbers produce different puzzles for
                         different players — core social feature breaks silently
  fragility:    critical

CONTRACT: i18n-completeness
  statement:    every key present in locale 'en' must be present in all locales
  owned-by:     i18n.js
  enforced-by:  i18n_tests.js :: all suites (data-driven)
  islands-bound:[i18n.js]
  violation-consequence: missing locale renders raw key to non-English users
  fragility:    medium

CONTRACT: player-state-cell-types
  statement:    only four valid cell states — null, confirmed, annotation, x
  owned-by:     game.js
  enforced-by:  tests_game.js
  islands-bound:[game.js, renderer.js, input.js]
  violation-consequence: renderer receives unknown type — silent failure or crash
  fragility:    high

---ARCHITECTURE-MEMORY---

ACTIVE-CONSTRAINTS:
  - id: MAC-001
    constraint:  JSON data file item order must never change — reordering breaks
                 seed determinism for all existing shared seeds
    applies-to:  [dataLoader.js, generator.js]
    established: 2024-01-15
    evidence:    git:c4d2e11

  - id: MAC-002
    constraint:  script load order is fixed and required — deviating causes
                 undefined symbol errors at runtime
    applies-to:  [all modules]
    established: 2024-01-01
    evidence:    N/A

HISTORICAL-DECISIONS:
  - id: MHD-001
    decision:  flat file structure with underscore-encoded logical paths
    reason:    no bundler — all files must be loadable via fetch() from root;
               path separators cannot appear in filenames served this way
    date:      2024-01-01
    outcome:   stable; naming convention encodes logical path in filename

SUPERSEDED:
  - none yet
```

---

## VALIDITY RULES

An island is INVALID if any of the following are true:
- Any required field is absent (silence is not allowed — use ? or N/A)
- fragility is medium or high without a fragility-note
- A security surface exists with no guarded-by AND no test AND severity >= medium
- status is verified but last-verified is absent
- maintained-by is human-unreviewed and more than one task cycle has passed
- A SYMBOL entry for a test file is missing business-rule

An island is STALE if:
- The source file has been modified since last-verified
- A mainland connection referencing this island has changed without a
  corresponding island update

STALE islands are treated as HYPOTHESIS, not ground truth.
The LLM must flag staleness before acting on the island's content.

The mainland is INVALID if:
- Any CONNECTION references a file that has no island
- Any CONTRACT lists an enforced-by test that does not exist
- Any architectural-rule is violated by a declared connection
- last-verified is absent

---

## STATUS PROGRESSION

  generated  ->  verified       after LLM review confirms accuracy
  generated  ->  inferred       when source is legacy with no documentation
  inferred   ->  verified       when hypothesis is confirmed by evidence
  inferred   ->  corrected      when hypothesis is wrong
                                (old entry kept, new entry added, old marked superseded)
  verified   ->  stale          automatic, when source file changes
  stale      ->  verified       after island is updated and reviewed
  any        ->  partial        explicit downgrade when island is known incomplete

---

## PROPAGATION PROTOCOL

This is the discipline that keeps the system accurate over time.

WHEN CODE CHANGES:
  1. Update the island for the changed file
  2. Update last-verified to current version/date
  3. Check if any exports changed signature, behavior, or effects
  4. If yes: check all depends-on entries and update their islands
  5. If a connection in the mainland is affected: update the connection
  6. If a contract is affected: update the contract and notify all islands-bound

WHEN MAINLAND CHANGES:
  1. A mainland change is a signal — something architectural shifted
  2. Review all islands bound to the changed connection or contract
  3. Verify they are still accurate
  4. Update status on any that are now stale

WHEN ADDING A NEW FILE:
  1. Create the island before or alongside the file — not after
  2. Add its connections to the mainland immediately
  3. Update depends-on in any islands that will import it

WHEN DELETING A FILE:
  1. Remove its island
  2. Remove all connections referencing it from the mainland
  3. Update depends-on in islands that referenced it
  4. Add a SUPERSEDED entry to ARCHITECTURE-MEMORY explaining what replaced it

---

## BOOTSTRAPPING A NEW PROJECT (GREENFIELD)

When starting from zero on a new project:

1. Create connections.llmainland first. Declare the architecture even before
   files exist. This is the design before it is the implementation.

2. As each file is created, create its island. Populate what is known.
   Mark unknown fields with ?. Mark uncertain inferences with confidence: low.

3. After the first working version, do a verification pass. Update all ?
   fields that can now be answered. Promote generated islands to verified.

4. From this point, propagation discipline applies to every change.

---

## BOOTSTRAPPING A LEGACY CODEBASE

When adding the island system to an existing project that has no islands:

PHASE 1 — GENERATION PASS (automated, no human required)
  Read every source file. Generate islands marked status: generated.
  Read tests. Populate test links where inferable.
  Read commit history if available. Populate evidence fields.
  Generate connections.llmainland from observable imports/exports.
  Mark all islands confidence: low until reviewed.
  Flag every field that could not be determined with ?.

PHASE 2 — VERIFICATION PASS (human + LLM collaboration)
  For each island with ? fields or confidence: low, present targeted questions.
  Do not ask open questions ("what does this do?").
  Ask specific binary or constrained questions:
    "This function appears to handle PAL timing. Is that correct?"
    "I cannot determine why this module exists. What requirement drove it?"
  Record answers. Promote islands to verified as questions are resolved.
  Unresolvable unknowns stay as ? — honest incompleteness is valid.

PHASE 3 — MAINLAND CONTRACTS
  After islands stabilize, declare contracts in the mainland.
  Ask: "what are the invariants that, if broken, cause silent failures?"
  These become CONTRACT entries.
  Ask: "what architectural rules must never be violated?"
  These become architectural-rules entries.

ARCHAEOLOGICAL MODE (when no author knowledge is available):
  For projects where no one knows the original intent (preservation work,
  abandoned codebases, reverse engineering):
  - All islands start as status: inferred, confidence: low
  - HISTORICAL-DECISIONS entries are research journal entries, not author records
    Format: "We believed X. Evidence found: Y. Current hypothesis: Z."
  - As understanding grows, entries move from inferred to verified
  - Never fabricate certainty. ? is always valid.

---

## MAINTENANCE PROTOCOL (ONGOING)

The island system only works if it is maintained. These rules make maintenance
automatic rather than a separate task:

RULE 1: Island update is part of task completion, not separate from it.
  A task that modifies a file is not complete until its island is updated.
  "Done" means: code works + tests pass + island is current.

RULE 2: Stale islands must be flagged before use.
  If an island is stale, the LLM states this before acting on its content.
  The LLM may use a stale island as a starting hypothesis but must verify
  the relevant sections before trusting them.

RULE 3: The mainland is checked at the start of every task.
  Before touching any file, read the mainland. Understand the architectural
  context. Check if the task involves any contracts. Check the active
  constraints for all files that will be touched.

RULE 4: Active constraints are reviewed when updating an island.
  When updating an island, verify that all ACTIVE-CONSTRAINTS still apply.
  If a constraint has been resolved by a refactor, move it to SUPERSEDED.
  Do not accumulate stale constraints in the active layer.

RULE 5: Considerations log entries must meet the load-bearing filter.
  Only add a MEMORY entry if: an LLM working on this file in a fresh session,
  with no prior context, would be likely to make the same mistake.
  If a compiler, type system, or test already catches the issue, it does not
  belong in MEMORY.

RULE 6: Human edits require LLM review before the island is trusted.
  A human may edit an island. When this happens, set maintained-by to
  human-unreviewed. The next LLM session must review the edit, confirm it
  matches what an LLM expects, and either accept it (setting maintained-by
  back to llm or human-reviewed) or flag inconsistencies to the human.

---

## MANAGING MEMORY OVER TIME

After years of active development, a considerations log can accumulate hundreds
of entries. This section defines how to keep it useful.

STRATIFICATION DISCIPLINE:
  ACTIVE-CONSTRAINTS must be pruned at every island update.
    Ask: is this still true? Is it still load-bearing?
    If resolved: move to SUPERSEDED.
    If no longer fragile (tooling now catches it): move to SUPERSEDED.
    Target: fewer than 10 active constraints per island.

  HISTORICAL-DECISIONS grow over time. This is acceptable.
    They explain the shape of the solution space.
    An LLM can skim them — they do not need to be read in detail every session.
    Prune only if an entry has been fully superseded AND the superseded entry
    captures its essence.

  SUPERSEDED entries are never deleted.
    They are the archaeological record.
    They explain why things that seem missing are intentionally absent.
    They prevent the same mistake being made twice.

VERSION REFERENCES WITHOUT GIT:
  If no version control system exists, use date-based identifiers:
    evidence: task-2024-03-15-refactor-canvas
    evidence: review-2024-02-01
  The goal is temporal anchoring, not git dependency.
  A considerations entry must be understandable without the reference.
  The reference is supplementary, not load-bearing.

WHEN THERE ARE TOO MANY DECISIONS TO TRACK:
  If a file's HISTORICAL-DECISIONS exceeds 20 entries, create a companion
  file: <source-file>.<ext>.llmhistory
  Move older HISTORICAL-DECISIONS there.
  Keep only the 5 most recent and the most architecturally significant in
  the main island.
  The llmhistory file is never read automatically — only when deep
  archaeological context is needed.

---

## CROSS-LANGUAGE PIPELINES

The island system is language agnostic. These rules apply at language boundaries.

Each file in each language gets its own island in that language's terms.
The mainland models the boundary explicitly in the connection:

  CONNECTION: orchestrator.py -> renderer.c
    uses:              render_frame(), init_context()
    why:               Python orchestration delegates rendering to C for performance
    direction:         bridge -> core
    language-boundary: python -> c via ctypes
    strength:          critical
    break-impact:      all rendering fails

The island for orchestrator.py describes what it calls and what it expects
from the C side in Python terms.

The island for renderer.c describes what it exports and what it expects
from callers in C terms.

Neither island needs to understand the other language. The mainland holds
the translation contract between them.

If the C layer is later rewritten in Assembly:
  1. renderer.c island is updated (or a renderer.asm island is created)
  2. The mainland connection is updated: language-boundary: python -> asm via nasm
  3. The CONTRACT governing the boundary behavior stays unchanged
  4. What the caller expects from the function does not change
  5. The considerations log records: "renderer.c rewritten to renderer.asm,
     interface preserved, performance boundary unchanged"

The semantic contract survives the implementation rewrite.

---

## XP ALIGNMENT

This system was designed to be compatible with Extreme Programming practices.
For teams using XP, here is the mapping:

  XP Practice              Island System Role
  ─────────────────────    ──────────────────────────────────────────────────
  Planning Game            mainland CONTRACTS declare what stories each module
                           serves; blast radius of story changes is readable
  Simple Design            partial islands are valid; complexity is earned
  Test First               test islands can be written before implementation
                           islands; the contract precedes the code
  Refactoring              active constraints are read before any refactor;
                           the impact is known, not simulated
  Collective Ownership     any LLM or developer can work on any file because
                           the island makes context self-contained
  Continuous Integration   mainland consistency check = semantic CI;
                           not "does it compile" but "does the architecture hold"
  Coding Standards         this spec IS the standard; consistent across projects
  Pair Programming         human-LLM island review gate is the async equivalent
  On-Site Customer         mainland CONTRACTS carry enough business context
                           to evaluate whether a change serves system intent
  Sustainable Pace         pre-computed reasoning = not burning tokens or
                           human attention re-deriving known things

---

## QUICK REFERENCE — WHAT TO DO IN EACH SCENARIO

STARTING A NEW FILE:
  Create the island. Populate all fields. Mark unknowns with ?.
  Add its connections to the mainland.
  Set status: generated until reviewed.

MODIFYING AN EXISTING FILE:
  Read its island first. Check ACTIVE-CONSTRAINTS.
  Make the change. Update the island.
  Update last-verified. Check if connections changed.
  If connections changed: update mainland.
  If mainland changed: check all bound islands for staleness.

READING AN UNFAMILIAR FILE:
  Read its island. Read the mainland connections for that file.
  Read the contracts it is bound to.
  Then read the code. The island tells you what to look for.

REFACTORING:
  Read the island. Read the mainland contracts for all affected files.
  Check all ACTIVE-CONSTRAINTS for all files you will touch.
  Perform the refactor. Update all affected islands.
  Update mainland if connections changed.
  Add a HISTORICAL-DECISIONS entry if the refactor resolved a known fragility.

INVESTIGATING A BUG:
  Read the mainland for the relevant area.
  Check which contracts could be violated by the symptom.
  Read the islands for the bound files.
  Check HISTORICAL-DECISIONS — has this been tried before?

ADDING A NEW DEPENDENCY:
  Update imports in the source file's island.
  Add to depends-on in the dependency's island.
  Add a CONNECTION to the mainland.
  Check if this violates any architectural-rules.

---

## ANTI-PATTERNS

DO NOT do these things:

- Leave a field blank. Use ? or N/A. Silence is not valid.
- Write narrative prose in structured fields. Be terse and specific.
- Document what the compiler or type system already enforces.
- Let a stale island be used as ground truth without flagging it.
- Write a business-rule for a test that only says what it calls.
- Let ACTIVE-CONSTRAINTS accumulate without pruning superseded ones.
- Treat git IDs as the primary record. Entries must stand alone.
- Skip the mainland update when a connection changes.
- Create an island after the task is done rather than as part of it.
- Fabricate certainty. If you do not know, write ?.

---

## VERSION HISTORY

v0.1 — initial specification
  Background: Akita's blog post on LLM-optimal language design (2026-02-09)
  XP principles integrated as framework alignment
  Designed to be language agnostic from inception
  Supports greenfield, legacy, archaeological, and cross-language scenarios
  Considerations log stratification: active / historical / superseded
  Freshness signal via last-verified + status progression
  Human edit gate via maintained-by field
  load-bearing filter for memory entry qualification

---

END OF SPEC v0.1
