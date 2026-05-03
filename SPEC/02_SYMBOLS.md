# Spec Module 02 - SYMBOLS and Field Decision Criteria

The SYMBOLS section reference plus the decision criteria for subjective fields (confidence, fragility, severity, strength, break-impact). Read this when populating SYMBOLS or assessing any subjective field.

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

runtime-dependencies
  Optional. List of runtime values that materially change this symbol's
  behavior without changing the source file: environment variables,
  feature flags, config keys.
  Format: - <name> :: <how behavior changes>
  Example:
    runtime-dependencies:
      - FEATURE_FLAG_NEW_AUTH :: when true, adds MFA check to auth flow
      - AUTH_PROVIDER :: changes OAuth provider (google | github | internal)
      - SESSION_TIMEOUT :: controls token expiry duration
  This field exists because the CONNECTIONS section models code imports
  but has no vocabulary for "this function's behavior depends on
  ENV_VAR_X at runtime." Without it, an LLM reasons from an incomplete
  model: the island says the function reads from user-store and returns
  User; the reality is that with FEATURE_FLAG_NEW_AUTH=true, it also
  checks an auth service and can return Unauthorized.
  Use `- none` (explicit) when the symbol has no runtime dependencies.

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

## FIELD DECISION CRITERIA

Subjective fields must be assessed using the criteria below, not by feel.
These criteria exist to make assessments reproducible across sessions, models,
and time. If you cannot satisfy the criteria for a given level, use the lower
level or ?.

### confidence

  high    — human explicitly confirmed this field OR verified against test
            evidence (e.g., a test asserts the behavior described)
  medium  — inferred from call sites, test coverage, or observable behavior;
            not confirmed by a human or definitive test
  low     — inferred from code structure alone (naming, file location, imports)

Note: confidence: high requires either human confirmation or test evidence.
An LLM that has only read the code cannot set confidence: high — only medium
at best. If you are uncertain, low is honest.

### fragility

  high    — a change here has broken something in this project before
            OR the symbol is used in 5+ call sites with no type enforcement
            OR the symbol crosses a language or system boundary
  medium  — inferred risk from call-site complexity, effect breadth, or
            implicit coupling (e.g., relies on shared mutable state)
  low     — isolated, well-tested, no cross-file mutation, few callers

Note: fragility: high based on "has broken before" requires evidence
(a git reference, a HISTORICAL-DECISIONS entry, or a test that was added
after the breakage). Without evidence, use medium.

### severity (security surfaces)

  critical — exploitable from untrusted input with no guard in place
  high     — exploitable but guarded; guard is untested or partial
  medium   — exploitable but guarded and tested
  low      — theoretical attack surface; practical exploitation unlikely

Note: severity reflects the current state, not the hypothetical worst case.
A surface that is guarded and tested is medium even if the unguarded version
would be critical.

### strength (mainland connections)

  critical — system cannot function if this connection breaks
             (e.g., entry point to core logic, only data source)
  high     — major feature loss if broken
             (e.g., rendering pipeline, authentication flow)
  medium   — degraded experience if broken
             (e.g., caching layer, non-critical UI component)
  low      — cosmetic or minor impact if broken
             (e.g., logging, analytics, optional display enhancement)

### break-impact (mainland connections)

Not a severity level but a statement. Write what actually breaks, not how
bad it is. Be specific:
  Good: "renderer cannot draw any cells — total visual failure"
  Bad:  "things break"
  Good: "seed determinism lost — shared seeds produce different puzzles"
  Bad:  "important feature affected"

If you cannot describe the specific failure, write:
  break-impact: ? (unable to determine specific failure mode)

---
