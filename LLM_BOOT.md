# LLM Island System — Boot
# Paste at the start of any session. Read once. Follow the decision tree.

---

## WHAT THIS PROJECT USES

This project uses the LLM Island System (v0.2).
Files: `.llmisland` (per source), `connections.llmainland` (root), `.llwasland` (archive).
Full spec: `LLMISLAND_SPEC.md` — read only when you need format details.

---

## STEP 1 — DO ISLANDS EXIST?

Check if `connections.llmainland` exists at the project root.

### YES — mainland exists

Read it now. Note:
- `bootstrap-mode` field — tells you the epistemic history of this project's islands
- `architectural-rules` — must not be violated by your changes
- `ACTIVE-CONSTRAINTS` in ARCHITECTURE-MEMORY — read before touching anything
- Any `CONTRACTS` relevant to files you will touch

Then go to STEP 2.

### NO — mainland does not exist

This is first boot. Read the scenario file for your situation, then return here:

  New project, no code yet          → `SCENARIOS/SCENARIO_GREENFIELD.md`
  Existing code, no islands yet     → `SCENARIOS/SCENARIO_LEGACY.md`
  Old code, no authors available    → `SCENARIOS/SCENARIO_ARCHAEOLOGY.md`
  Multiple languages or pipeline    → `SCENARIOS/SCENARIO_CROSSLANG.md`

When the scenario is done, continue to STEP 2.

---

## STEP 2 — WHAT IS THE BOOTSTRAP-MODE?

If `connections.llmainland` exists, check its `bootstrap-mode` field.
This tells you the epistemic status of existing islands before you work.

  bootstrap-mode: greenfield
    Islands were created alongside code from the start.
    `status: verified` islands can be trusted as high quality.
    Treat this like a normal maintained project.

  bootstrap-mode: legacy
    Islands were added to existing code after the fact.
    Some islands may be `status: generated` or `confidence: low`.
    Verify low-confidence islands before acting on them.

  bootstrap-mode: archaeological
    No author knowledge was available when islands were created.
    All islands are hypotheses until explicitly promoted to verified.
    Treat `confidence: medium` the way you would treat `confidence: low` elsewhere.
    Never assume a `status: verified` island here is as reliable as in greenfield.

  bootstrap-mode: unknown or field absent
    Treat all islands as `confidence: low` until you can assess them.

---

## STEP 3 — WHAT IS YOUR TASK TYPE?

Pick the one that best describes what you are about to do.

### A — Working on existing functionality (bug fix, improvement, refactor)

  Read: `MODES/MODE_INCREMENTAL.md`
  Then read the `.llmisland` for each file the task touches.
  Do not read unrelated files.

### B — Implementing a new feature

  Read: `MODES/MODE_INCREMENTAL.md` → section "NEW FEATURE FLOW"
  Identify which existing files the feature will connect to.
  Read their islands. Note their active constraints and contracts.
  Create islands for new files as you create the files.
  Update mainland connections for each new dependency.

### C — Investigating a bug or unexpected behavior

  Read `connections.llmainland` contracts first.
  Identify which contracts the symptom could violate.
  Read islands for the bound files.
  Check HISTORICAL-DECISIONS — has this been attempted before?
  Then read source files only as needed.

### D — Architectural overview, no specific task

  Read: `MODES/MODE_CONNECTION.md`

### E — Full audit or full island generation

  Read: `MODES/MODE_FULLMAP.md`

---

## QUESTION DISCIPLINE

Before asking the human anything, apply this filter:

1. Can I proceed safely by marking the unknown as `?` and noting it?
   → If yes: do that. Do not ask.

2. Will the answer materially change what I do or produce?
   → If no: do not ask.

3. If I must ask — batch all questions into ONE message.
   Never ask one question, wait for the answer, then ask another.
   Present all blockers at once: "Before I proceed, I need to know: [1] [2] [3]"

4. Prefer a declared assumption over an inconsequential question.
   State the assumption explicitly: "I am assuming X. If that is wrong, tell me."
   This lets the human correct it without requiring them to answer first.

---

## ALWAYS TRUE — REGARDLESS OF TASK OR MODE

- Do not read files unrelated to the current task.
- Stop reading when the task can be completed safely.
- `?` is always valid. Silence is not.
- Island update is part of task completion — not after it.
- Stale islands are hypotheses, not ground truth. Flag before using.
- If unsure about format: check `LLMISLAND_SPEC.md`.

---

END OF BOOT
