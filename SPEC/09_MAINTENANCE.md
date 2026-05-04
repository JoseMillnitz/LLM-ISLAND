# Spec Module 09 - Maintenance Protocol and Memory Management

The 10 maintenance rules (proportional updates, stale flagging, selective reads, active-constraint pruning, load-bearing filter, human-edit review, question discipline, subjective-field rationale, post-generation compliance check, security gate, opportunistic-read marker), plus how to manage memory growth over time and when to archive into .llwasland. Read this when updating an island, reviewing maintenance obligations, or deciding what belongs in MEMORY.

---

## MAINTENANCE PROTOCOL (ONGOING)

The island system only works if it is maintained. These rules make maintenance
automatic rather than a separate task:

RULE 1: Island update scope is proportional to change scope.
  A task that modifies a file is not complete until its island is updated —
  but the depth of update depends on the tier (see UPDATE TIERS).
  Tier A changes require only a last-verified timestamp update.
  Tier B changes require updating affected SYMBOLS entries.
  Tier C changes require a full island and mainland update.
  "Done" means: code works + tests pass + island is current at the correct tier.
  A Tier A update on an internal-only change is a complete, valid update —
  not a shortcut, not technical debt, not something to feel guilty about.

RULE 2: Stale islands must be flagged before use.
  If an island is stale, the LLM states this before acting on its content.
  The LLM may use a stale island as a starting hypothesis but must verify
  the relevant sections before trusting them.

RULE 3: The mainland is read selectively at the start of every task.
  Before touching any file, follow the SELECTIVE READ PROTOCOL (see above).
  Always read: architectural-rules, ACTIVE-CONSTRAINTS, ARCHITECTURE basics.
  Then read CONTRACTS and CONNECTIONS only for files the task will touch.
  Skip HISTORICAL-DECISIONS and SUPERSEDED unless investigating a bug or
  understanding a past design decision.
  Do not read the whole mainland by reflex — on a large project, this
  consumes context before any source code is read.

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
  The review obligation is at SESSION START, not after task completion.
  If a human-unreviewed island describes a file the current task will
  touch, the LLM must review it BEFORE generating any code on top of it.
  The review-after-the-fact pattern bakes potential inconsistencies into
  the work. See LLM_BOOT.md STEP 0C.

RULE 7: Question discipline — do not ask more than necessary.
  Before asking the human anything, apply this filter:
  (a) Can I proceed safely by marking the unknown as ? and noting it?
      If yes: do that. Do not ask.
  (b) Will the answer materially change what I do or produce?
      If no: do not ask.
  (c) If asking is necessary: batch ALL questions into ONE message.
      Never ask one question, wait, then ask another.
      Present all blockers at once.
  (d) Prefer a declared assumption over an inconsequential question.
      State it explicitly: "I am assuming X. Correct me if wrong."
  An LLM that asks too many questions is as disruptive as one that assumes
  too much. The ? marker exists precisely to defer non-blocking unknowns.

RULE 8: Subjective fields require rationale above low.
  When setting confidence, fragility, severity, or strength to medium or
  above, include a brief rationale showing the evidence or reasoning.
  Format: field-name: value (rationale: brief explanation)
  Example:
    fragility: high (rationale: used in 7 call sites with no type guard;
                     a signature change here broke production in v3)
    confidence: medium (rationale: inferred from call-site patterns; no
                        test directly asserts the behavior)
  This forces the LLM to show its work, making hallucinated assessments
  detectable by future sessions. If you cannot state a rationale, the
  correct value is lower — or ?.
  Subjective fields where rationale applies: confidence, fragility, severity
  (security surfaces), strength (mainland connections).

RULE 9: Post-generation constraint compliance check.
  After generating or modifying code, before declaring the task done:
  1. Re-read the architectural-rules from the mainland.
  2. For each rule with self-checkable: true, verify the generated code
     does not violate it. Check imports, layer boundaries, dependency
     directions, and any other statically detectable constraints.
  3. For each rule with self-checkable: false, note it in the task
     completion: "external validation required for AR-XXX (<rule>)."
  4. If a violation is found in a self-checkable rule: fix it before
     declaring done. Do not note the violation and leave it for the
     human — fix it.
  This addresses the gap between reading a constraint and following it.
  Reading a rule is not the same as respecting it; the spec assumes they
  are close enough, and that assumption is structurally wrong without an
  explicit verification step.

RULE 10: Security-sensitive islands require a higher trust gate.
  If a task touches a security surface with severity high or critical, or
  a file bound to a security-related contract, do not treat a normal
  island as sufficient authority unless `maintained-by: security-reviewed`.
  If the gate is not met:
  - Do not generate code that depends on the island's RISKS or
    ACTIVE-CONSTRAINTS as ground truth.
  - Surface to the human: "this island touches a high-severity security
    surface but is not security-reviewed. I need either security review
    confirmation or independent verification before proceeding."
  See SECURITY REVIEW GATES section for the full gate criteria.

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
  file: <source-file>.<ext>.llwasland
  Move older HISTORICAL-DECISIONS there.
  Keep only the 5 most recent and the most architecturally significant in
  the main island.
  The .llwasland file is never read automatically — only when deep
  archaeological context is needed.

  The name is intentional: W is M upside down. These decisions "was" in land.
  The .llwasland is the memory of what the island used to know.

  Format: identical to the MEMORY section of a regular island — same fields,
  same stratification, same evidence requirements. It is not a dump. It is
  an archive with the same quality bar as the source island.

  When creating a .llwasland:
    - Move entries oldest-first
    - Add a header declaring which island it archives and the date of archival
    - Leave a SUPERSEDED stub in the source island pointing to it:
        SUPERSEDED:
          - id: SD-archive-001
            was: HISTORICAL-DECISIONS entries HD-001 through HD-015
            replaced-by: see renderer.js.llwasland
            superseded-date: 2026-03-01
            keep-because: archived to llwasland — not deleted

---
