# Spec Module 01 - Island Format and HEADER

Per-file island file structure plus the HEADER section field reference. Read this when creating or editing an island.

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
generation-pass: false
read-reason:    task-driven
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
  When confidence is medium or high, RULE 8 requires a brief inline rationale
  showing the evidence (see MAINTENANCE PROTOCOL).

confidence-review-due
  Optional. Format: <version> or <date>
  When this version or date is reached without the confidence being
  explicitly re-reviewed, the island's confidence should be treated as
  decayed by one level (high → medium, medium → low).
  This prevents archaeological fossilization: old uncontradicted islands
  being treated as reliable simply because they survived.
  Set this field when:
    - Creating inferred islands in archaeological projects
    - Setting confidence: medium or high without strong evidence
    - bootstrap-mode is archaeological and confidence rises above low
  For task-driven islands with confidence: high backed by tests, this field
  is not needed (write N/A or omit).

generation-pass
  true | false
  Set to true when an island was created in a bulk generation pass (e.g.,
  legacy bootstrapping, full-map mode, automated pipeline). When true, all
  subjective values in this island are hypotheses until individually verified.
  A future session encountering generation-pass: true should treat every
  subjective field (confidence, fragility, severity, strength) as provisional
  regardless of what value is written.
  Set to false (or omit, defaulting to false) when the island was created or
  reviewed as part of a specific task with focused attention.

read-reason
  One of: task-driven | opportunistic | audit
  Tells future sessions why this island was created or last updated.

  task-driven    — created or updated as part of a specific task that
                   required reading this file. The normal case.
  opportunistic  — created or updated because the LLM read this file beyond
                   what the task strictly required. The content may be less
                   carefully reviewed than task-driven islands.
  audit          — created as part of a full mapping pass (Mode 3) or a
                   deliberate review session.

  This field supports the DETECTABLE FAILURE principle (CORE PRINCIPLE 9):
  if an LLM violates stop-early and reads extra files, setting read-reason:
  opportunistic makes the violation visible and tells future sessions to
  treat the island with appropriate caution.

last-verified
  Format: <version-or-id>-<date> or <date> if no version system exists.
  Required when status is verified.

maintained-by
  One of: llm | human-reviewed | human-unreviewed | security-reviewed
  human-unreviewed means a human edited this island and it has not yet been
  reviewed by an LLM. This is a temporary state — it must be resolved before
  the island is used as ground truth.
  security-reviewed means this island has been reviewed by a human with
  security expertise. Required for islands with severity >= high in the
  RISKS section, or for islands bound to security-related contracts.
  A code change to a security-reviewed island downgrades it to llm until
  re-reviewed by the security reviewer.

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
