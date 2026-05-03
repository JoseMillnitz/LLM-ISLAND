# Spec Module 04 - Mainland Format and Selective Read

The connections.llmainland format (architecture, connections, contracts, architecture-memory) plus the selective read protocol that controls how an LLM consumes the mainland on a large project. Read this when editing the mainland or planning what to read at session start.

---

## MAINLAND FILE STRUCTURE

```
---ARCHITECTURE---
project:        SUDOKILL
version:        7
last-verified:  2024-03-15
description:    Browser-based deduction puzzle. Vanilla JS, Canvas, JSON data.
                No framework, no bundler, no server-side code.

bootstrap-mode: greenfield
bootstrap-date: 2024-01-01

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
    self-checkable: true
  - AR-002: data.js is pure — no I/O, no side effects, no async
    self-checkable: true
  - AR-003: dependency direction is always toward core — presentation must not
            be imported by core
    self-checkable: true
  - AR-004: game.js is the only module permitted to hold mutable game state
    self-checkable: true
  - AR-005: all user-visible strings must go through I18n.t() — never hardcoded
    self-checkable: false (requires visual review or string extraction tooling)

---CONNECTIONS---

CONNECTION: renderer.js -> data.js
  uses:         SHAPES, cellRoom
  why:          cell geometry is derived from shape definitions
  direction:    presentation -> core
  strength:     high
  break-impact: renderer cannot draw any cells — total visual failure
  cycle:        false

CONNECTION: generator.js -> data.js
  uses:         SHAPES, cellRoom, roomDefs
  why:          level generation requires grid geometry and room definitions
  direction:    core -> core
  strength:     critical
  break-impact: level generation fails completely — no puzzle can be created
  cycle:        false

CONNECTION: game.js -> generator.js
  uses:         LevelGenerator.generate()
  why:          game state machine triggers generation on new game
  direction:    orchestration -> core
  strength:     critical
  break-impact: new game fails — no new puzzles possible
  cycle:        false

CONNECTION: python_pipeline.py -> render_core.c
  uses:         render_frame(), init_context()
  why:          Python orchestration delegates frame rendering to C for performance
  direction:    bridge -> core
  language-boundary:
    from:              python
    to:                c
    mechanism:         ctypes
    data-types:        [float array (frame buffer), int (context handle)]
    error-semantics:   C returns -1 on error; Python raises RuntimeError
    version-coupling:  render_core.so must match header version
  strength:     critical
  break-impact: all rendering fails
  cycle:        false

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

CONTRACT: auth-enforcement
  condition:    FEATURE_FLAG_AUTH=true
  statement:    all API endpoints must validate auth token
  owned-by:     middleware/auth.js
  enforced-by:  tests/auth.test.js
  islands-bound:[middleware/auth.js, routes/*.js]
  violation-consequence: unauthenticated access to all endpoints
  fragility:    critical

CONTRACT FIELD NOTES:
  condition (optional)
    A runtime predicate. When present, the contract applies only when the
    condition is true. Use for feature-flagged invariants and environment-
    conditional rules. An LLM that does not know the runtime context should
    treat the contract as ACTIVE (the safer assumption).
    Examples: condition: FEATURE_FLAG_AUTH=true
              condition: NODE_ENV=production
    When absent: the contract applies unconditionally.

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

## SELECTIVE READ PROTOCOL (MAINLAND)

On small projects, reading the entire mainland at session start is free. On
large projects with hundreds of files, it is catastrophically expensive —
consuming context before any source code is touched.

The mainland has an internal read-priority structure. Follow this protocol.

### ALWAYS READ (before any task)

  - ARCHITECTURE section: project, version, bootstrap-mode
  - architectural-rules — must not be violated by your changes
  - ACTIVE-CONSTRAINTS in ARCHITECTURE-MEMORY — read before touching anything

### READ FOR TOUCHED FILES (after identifying which files the task involves)

  - CONTRACTS where islands-bound includes any file you will touch
  - CONNECTIONS entries where either endpoint is a file you will touch

### SKIP BY DEFAULT (read only when investigating)

  - HISTORICAL-DECISIONS in ARCHITECTURE-MEMORY — read only when investigating
    a bug or understanding why a design decision was made
  - SUPERSEDED in ARCHITECTURE-MEMORY — read only for archaeological context
  - CONNECTIONS entries for files unrelated to the current task

### NOTE ON SPLITTING THE MAINLAND

The mainland stays in one file. Do not split it into a `.history` companion
file even at large scale. The selective read protocol above solves the
reading cost without splitting. A separate history file creates a different
problem: an LLM managing a large project may archive load-bearing decisions
that simply have not been referenced recently, making them invisible.
Invisible means forgotten. The read protocol controls what gets read; it
does not need to control what exists.

---
