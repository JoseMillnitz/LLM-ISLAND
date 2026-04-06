# Scenario — Archaeological Mode
# Read this only when no original authors are available and intent must be
# inferred from behavior. Examples: preservation projects, abandoned codebases,
# reverse engineering, complete team turnover.

---

## SITUATION

Existing codebase. No one currently working on it knows the original intent.
Understanding must be built from evidence: code behavior, tests, comments,
commit messages, forum posts, issue trackers — whatever survives.

---

## EPISTEMIC SHIFT

In standard legacy adoption, you transfer author knowledge into islands.
In archaeological mode, you build and test hypotheses. The difference is in
how confidence and evidence are treated.

Standard mode:
  A human confirms "canvas was chosen over DOM for performance."
  → Record as fact. `evidence: git:b2e1a09`

Archaeological mode:
  No one knows. You infer from absence of CSS classes, a comment in a commit,
  and the performance-sensitive call site.
  → Record as hypothesis. `confidence: low`
  → `evidence: inferred-from-comments, inferred-from-codebase-absence`

---

## PROCESS

Step 1 — Collect all available evidence before generating islands.
  Read: source files, tests, commit messages, README files, issue trackers,
  forum posts, documentation fragments, any comments in code.
  Do not read everything at once — use Mode 1 or Mode 2 as appropriate.

Step 2 — Generate islands with explicit epistemic markers.
  All islands start as `status: inferred`, `confidence: low`.
  Every HISTORICAL-DECISIONS entry is a research journal entry:
    "We believed X. Evidence found: Y. Current hypothesis: Z."
  Every evidence field uses `inferred-from-<source>` notation.

Step 3 — Test hypotheses against behavior.
  When a hypothesis predicts behavior and the behavior matches: raise confidence.
  When a hypothesis is wrong: move to SUPERSEDED, add corrected entry.
  Never delete wrong hypotheses — they are part of the research record.

Step 4 — Declare behavioral contracts (not author-intent contracts).
  Contracts here are derived from observed behavior, not stated intent.
  Add `confidence` and `evidence` fields to contract entries.

---

## EVIDENCE NOTATION

  inferred-from-code           — derived from reading the implementation
  inferred-from-tests          — derived from test assertions
  inferred-from-comments       — derived from code comments
  inferred-from-call-site      — derived from how the symbol is called
  inferred-from-absence        — derived from what is NOT present
  inferred-from-commit-<id>    — derived from a commit message
  inferred-from-docs           — derived from surviving documentation
  confirmed-by-behavior        — hypothesis was tested and confirmed

---

## STATUS PROGRESSION IN THIS MODE

  inferred   → verified      hypothesis confirmed by evidence accumulation
  inferred   → corrected     hypothesis proven wrong; old entry superseded,
                              new entry added with corrected understanding

Never promote an island from `inferred` to `verified` without explicit
confirming evidence. Confidence growth without evidence is fabrication.

---

## KEY RULE

Honest uncertainty is the highest-value output in archaeological mode.
A well-documented `confidence: low` hypothesis is more useful than a
fabricated `confidence: high` certainty. The goal is to make what is
unknown explicit, not to make it invisible.
