# Spec Module 03 - RISKS and MEMORY

The RISKS and MEMORY sections of an island. Read this when documenting security surfaces, regression sensitivity, platform sensitivity, runtime config dependencies, or the considerations log (active constraints, historical decisions, superseded).

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

config-dependencies
  Runtime configuration that materially changes the file's behavior at the
  file level. Use this for feature-flag-heavy systems or environment-
  conditioned flows that are too broad to repeat under every symbol's
  runtime-dependencies field. List values, not internal mechanism.
  Example:
    config-dependencies:
      - FEATURE_FLAG_AUTH :: when true, all routes in this file enforce auth
      - DATABASE_URL :: file fails to load if unset

If a category has no entries, write:
  security: none
  regression-sensitivity: none
  platform-sensitivity: none
  config-dependencies: none

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
