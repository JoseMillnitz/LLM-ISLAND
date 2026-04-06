# Scenario — Legacy Adoption
# Read this only when adding islands to an existing codebase for the first time.

---

## SITUATION

Existing codebase with no islands. Authors are available or recent enough that
intent can be recovered through questions.

---

## RECOMMENDED APPROACH: START INCREMENTAL, NOT FULL

Do not do a full mapping pass on day one. Use Mode 1 (Incremental) and let
islands grow as tasks are worked. The alternative — generating all islands
upfront — produces many low-quality islands under time pressure.

The exception: if the human explicitly asks for a full mapping pass, use
Mode 3 (Full Mapping) instead.

---

## FIRST SESSION PROCESS (INCREMENTAL PATH)

Step 1 — Scan file tree and imports/exports only.
  Build the MVM mainland with the CONNECTIONS section populated.
  Do not read function bodies yet.
  Mark all connection strengths as `?`.

Step 2 — Ask the human to identify the 3-8 most critical files.
  "Which files are the entry points, state holders, or most frequently changed?"
  These are Tier 1. Create full islands for these files first.

Step 3 — Create shallow islands for all other files.
  HEADER only, SYMBOLS deferred, `status: partial`, `confidence: low`.
  See EXAMPLES/example.llmisland.

Step 4 — Ask the human for the load-bearing invariants.
  "What are the things in this codebase that, if broken, cause silent failures
  that tests do not catch?"
  Each answer becomes a CONTRACT entry in the mainland.

Step 5 — From this point, follow Mode 1 for all further work.
  Islands deepen opportunistically as tasks touch files.

---

## VERIFICATION PASS (WHEN READY)

When shallow islands have accumulated and confidence is low on many of them,
schedule a verification pass with the human:

- Present targeted questions, not open-ended ones.
  Good: "This function appears to handle PAL timing. Is that correct?"
  Bad:  "What does this module do?"

- Promote islands from `generated` to `verified` as fields are confirmed.
- Unresolvable fields stay as `?` — honest incompleteness is valid.

---

## KEY RULE

Prioritize depth on the most critical files over breadth across all files.
A fully verified island for `game.js` is more valuable than 30 shallow
islands for every file in the project.
