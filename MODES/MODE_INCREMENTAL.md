# Mode 1 — Incremental (Default)
# Read this when you have a specific task: bug fix, improvement, refactor, or new feature.

---

## PHILOSOPHY

Map only what the task requires. Expand only when a dependency or contract demands it.
Stop as soon as the task can be completed safely.

---

## TASK TYPE: MAINTENANCE (bug fix, improvement, refactor)

1. Read `connections.llmainland` if not already read this session.
2. Identify which files the task touches.
3. For each file: read its `.llmisland`. If none exists, create one now (shallow is fine).
4. Read ACTIVE-CONSTRAINTS for all touched files.
5. Check if the task affects any mainland CONTRACTS.
6. Read only those source files. Do not open unrelated files.
7. Complete the task.
8. Update islands for every file touched.
9. If any connection changed: update `connections.llmainland`.
10. If mainland changed: flag any bound islands that may now be stale.

---

## TASK TYPE: NEW FEATURE

New features have a different flow because they introduce files, connections,
and possibly contracts that do not yet exist.

1. Read `connections.llmainland`. Understand the current architecture.
2. Identify which existing files the feature will connect to.
   Read their islands. Note active constraints and any relevant contracts.
3. Ask yourself: does this feature violate any existing architectural-rule?
   If yes: surface this to the human before writing any code.
4. Design the new file(s) and their connections before writing code.
   Create entries in the mainland for new connections, marked `strength: ?`.
5. As each new file is created, create its island alongside it.
   Do not write a file and defer the island.
6. For new files connecting to existing ones: update `depends-on` in the
   existing file's island.
7. After the feature is working: declare any new contracts it introduces.
   Ask: "is there a new invariant here that, if broken, causes a silent failure?"
8. Update mainland `last-verified`.

Key difference from maintenance: you are expanding the mainland, not just
updating it. Each new connection is a new edge in the architectural graph.

---

## MINIMUM VIABLE MAINLAND (MVM)

If `connections.llmainland` does not exist, create this before anything else:

```
---ARCHITECTURE---
project:        ?
version:        0
last-verified:  <today>
description:    ?
bootstrap-mode: greenfield
bootstrap-date: <today>

layers:
  core:         []
  presentation: []
  input:        []
  data:         []
  orchestration:[]
  io:           []
  i18n:         []
  test:         []
  bridge:       []

load-order:
  - ? (to be discovered)

architectural-rules:
  - AR-001: ? (to be declared after first pass)

---CONNECTIONS---
(none yet)

---CONTRACTS---
(none yet)

---ARCHITECTURE-MEMORY---
ACTIVE-CONSTRAINTS:
  - none yet
HISTORICAL-DECISIONS:
  - none yet
SUPERSEDED:
  - none yet
```

---

## EXPANSION TRIGGERS

Expand to a new file only when one of these is true:
- A dependency is required to complete the task
- A contract might be violated by the change
- A symbol's behavior is unclear and the ambiguity blocks progress
- A mainland connection is missing and the gap matters for this task

Do not expand speculatively.

---

## CONFIDENCE-GATED PROPAGATION

confidence: low    → mark unknowns (?), do not propagate to other islands
confidence: medium → proceed locally, do not cascade to downstream islands
confidence: high   → safe to propagate, update mainland, update bound islands

---

## STOP-EARLY RULE

Stop reading files as soon as the task can be completed safely.
Reading 40 files for a 2-file task is a failure mode, not thoroughness.

---

## WHEN DONE

- [ ] All touched files have updated islands
- [ ] `last-verified` updated on all changed islands
- [ ] Mainland updated if any connection changed
- [ ] New contracts declared if the feature introduced new load-bearing invariants
- [ ] Stale islands flagged if mainland changed
- [ ] No island left with `maintained-by: human-unreviewed` from this session
