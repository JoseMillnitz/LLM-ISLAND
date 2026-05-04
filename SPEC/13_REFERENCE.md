# Spec Module 13 - XP Alignment, Quick Reference, and Anti-Patterns

Mapping from XP practices to island system roles (compatibility framing), the quick reference of what to do in each scenario (starting a session, modifying a file, refactoring, investigating a bug, adding a dependency), and the anti-patterns block. Read this when onboarding to the system or when you want a one-page reminder of common procedures.

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

STARTING A SESSION (do this first, every time):
  1. Declare which boot mode you are using.
  2. If no mode is specified: use Mode 1 — Incremental.
  3. Create or read the MVM mainland before touching any source file.
  4. Read only the islands relevant to your task.
  5. Expand to other files only if the task demands it.

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
- Use Mode 3 (Full Mapping) when Mode 1 (Incremental) would suffice.
- Read the entire codebase before starting a task that touches 2 files.
- Expand to new files speculatively — only expand when a task demands it.
- Generate shallow islands during Mode 3 — if doing a full pass, do it fully.
- Forget to declare which boot mode you are using at the start of a session.
---
