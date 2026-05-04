# Spec Module 08 - Bootstrap and Boot Modes

Greenfield + legacy bootstrapping protocols, the three boot modes (Incremental / Connection-First / Full Mapping), the Minimum Viable Mainland template, confidence-gated expansion, expansion triggers, the stop-early rule, and the bootstrap-mode field. Read this when adopting the system in a new or existing project, or when picking which mode to operate in for a session.

---

## BOOTSTRAPPING A NEW PROJECT (GREENFIELD)

When starting from zero on a new project:

1. Create connections.llmainland first. Declare the architecture even before
   files exist. This is the design before it is the implementation.

2. As each file is created, create its island. Populate what is known.
   Mark unknown fields with ?. Mark uncertain inferences with confidence: low.

3. After the first working version, do a verification pass. Update all ?
   fields that can now be answered. Promote generated islands to verified.

4. From this point, propagation discipline applies to every change.

---

## BOOTSTRAPPING A LEGACY CODEBASE

When adding the island system to an existing project that has no islands:

PHASE 1 — GENERATION PASS (automated, no human required)
  Read every source file. Generate islands marked status: generated.
  Read tests. Populate test links where inferable.
  Read commit history if available. Populate evidence fields.
  Generate connections.llmainland from observable imports/exports.
  Mark all islands confidence: low until reviewed.
  Flag every field that could not be determined with ?.

PHASE 2 — VERIFICATION PASS (human + LLM collaboration)
  For each island with ? fields or confidence: low, present targeted questions.
  Do not ask open questions ("what does this do?").
  Ask specific binary or constrained questions:
    "This function appears to handle PAL timing. Is that correct?"
    "I cannot determine why this module exists. What requirement drove it?"
  Record answers. Promote islands to verified as questions are resolved.
  Unresolvable unknowns stay as ? — honest incompleteness is valid.

PHASE 3 — MAINLAND CONTRACTS
  After islands stabilize, declare contracts in the mainland.
  Ask: "what are the invariants that, if broken, cause silent failures?"
  These become CONTRACT entries.
  Ask: "what architectural rules must never be violated?"
  These become architectural-rules entries.

ARCHAEOLOGICAL MODE (when no author knowledge is available):
  For projects where no one knows the original intent (preservation work,
  abandoned codebases, reverse engineering):
  - All islands start as status: inferred, confidence: low
  - HISTORICAL-DECISIONS entries are research journal entries, not author records
    Format: "We believed X. Evidence found: Y. Current hypothesis: Z."
  - As understanding grows, entries move from inferred to verified
  - Never fabricate certainty. ? is always valid.

---

## BOOT MODES

The default mental model of "read every file → generate every island → verify"
is correct for full audits but wrong for everyday use. On first contact with a
project, an LLM that reads the entire codebase before producing anything useful
is burning tokens, taking too long, and probably discouraging adoption.

The island system supports three explicit boot modes. The LLM must choose or be
instructed which mode to use. When no mode is specified, use MODE 1.

---

### MODE 1 — INCREMENTAL (DEFAULT)

Also called: Task-Driven Boot.

Philosophy: map only what is needed to complete the current task. Expand only
when a task demands it. Stop as soon as the task can be completed safely.

Process:
  1. Create the Minimum Viable Mainland (see below) — structure only, no source
     files read yet
  2. Wait for a task
  3. When a task arrives, identify which files it touches
  4. Read only those files. Generate islands for only those files.
  5. Generate only the direct connections those files require in the mainland
  6. Complete the task. Update the islands as part of completion.
  7. Repeat — the system grows as tasks are worked

Allowed in this mode:
  - Partial islands (status: partial)
  - Unknown fields (?)
  - Low confidence entries (confidence: low)
  - Mainland with empty CONNECTIONS and CONTRACTS sections

Rules:
  - Do not read files unrelated to the current task
  - Do not generate islands preemptively
  - Stop expanding when the task can be completed safely
  - Prefer local reasoning over global scanning

When to use:
  - Default for all new project adoptions
  - Ongoing development sessions
  - Any session where the full codebase is not the subject of the task

---

### MODE 2 — CONNECTION-FIRST

Also called: Structural Boot.

Philosophy: understand the architecture before understanding behavior. Build
the dependency graph from imports and exports without reading function bodies.

Process:
  1. Scan all files for imports and exports only — do not read implementations
  2. Build the mainland CONNECTIONS section from this scan
  3. Create shallow islands for all files: HEADER only, SYMBOLS marked as ?
  4. Identify the critical path: core and orchestration files first, then
     bridges, then leaf nodes (presentation, test)
  5. Deepen islands along the critical path when tasks require it

Critical path tiers (from Gemini's analysis):
  Tier 1 — core and orchestration: entry points, state holders, domain logic
  Tier 2 — bridges: cross-language boundaries, external service adapters
  Tier 3 — leaf nodes: presentation, test files, configuration

Shallow island format for this mode:

```
---HEADER---
file:           renderer.js
language:       javascript
role:           ?
layer:          presentation
status:         partial
confidence:     low
last-verified:  N/A
maintained-by:  llm
exports:        ?
imports:        ?
depends-on:     ?
translation-boundary: none

---SYMBOLS---
(deferred — populate when a task touches this file)

---RISKS---
security:               ?
regression-sensitivity: ?
platform-sensitivity:   ?

---MEMORY---
ACTIVE-CONSTRAINTS:
  - none yet
HISTORICAL-DECISIONS:
  - none yet
SUPERSEDED:
  - none yet
```

When to use:
  - Large legacy codebases where architecture is unknown
  - Pre-mapping before a major refactoring session
  - When asked to give an architectural overview without a specific task
  - When a human wants to understand the dependency graph before diving in

---

### MODE 3 — FULL MAPPING

Also called: Full Review Mode.

Philosophy: complete semantic mapping of the entire system. Every file read,
every island fully populated, every contract declared.

Process:
  1. Read all source files
  2. Read all tests
  3. Generate all islands with full HEADER, SYMBOLS, RISKS, and MEMORY
  4. Generate the full mainland including CONNECTIONS and CONTRACTS
  5. Mark all uncertainty explicitly — ? for unknowns, confidence: low where
     inferences were made
  6. Perform the verification pass

Costs:
  - High token usage
  - Slow — not suitable for a quick task
  - Requires a focused, uninterrupted session

When to use:
  - Full system audits
  - Pre-refactoring planning on a system with no existing islands
  - Archaeological analysis (combined with archaeological mode)
  - Critical systems where incomplete islands are unacceptable before work begins
  - When explicitly requested by a human ("do a full mapping pass")

Do NOT use this mode by default. It is the most expensive option and only
justified when completeness is the explicit goal.

---

### MINIMUM VIABLE MAINLAND (MVM)

Before any boot mode begins, the LLM should create this minimal mainland.
It establishes structure without requiring knowledge of any source file.

```
---ARCHITECTURE---
project:        ?
version:        0
last-verified:  <today>
description:    ?

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
    self-checkable: ? (can an LLM verify this by reading code?)

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

This is always valid. An MVM mainland with no connections is not an error —
it is an honest starting state. It becomes invalid only if connections are
added without corresponding islands.

---

### CONFIDENCE-GATED EXPANSION

In Modes 1 and 2, the LLM expands its understanding based on confidence:

  confidence: low
    Do not propagate changes beyond the current file.
    Ask targeted questions or mark unknowns with ?.
    Do not update the mainland until confidence rises.

  confidence: medium
    Proceed locally. Update the current island and its direct connections.
    Do not cascade changes to downstream islands without verification.

  confidence: high
    Safe to propagate changes through the mainland.
    Safe to update all bound islands.
    Safe to update contracts if they are affected.

---

### EXPANSION TRIGGERS

In Modes 1 and 2, expand to new files only when one of these is true:

  - A dependency is required to complete the current task
  - A contract might be violated by the current change
  - A symbol's behavior is unclear and the ambiguity blocks the task
  - A connection is missing in the mainland and the missing link matters now

Do not expand speculatively. Expansion has a cost — token usage, time, and
the risk of creating low-quality islands under time pressure.

---

### STOP-EARLY RULE

Mandatory for all non-full-mapping modes:

  Stop reading files as soon as the current task can be completed safely.

This is not laziness — it is discipline. An LLM that reads 40 files to
complete a task that required 3 is wasting resources and accumulating
low-confidence islands that may need to be corrected later. Quality of
reasoning over quantity of files read.

FALLBACK STATE — when stop-early is violated:
  If you read more files than the task strictly required (it happens),
  mark any islands created or modified from those extra reads as:
    read-reason: opportunistic
  This tells future sessions: "this island was not task-driven — treat it
  with appropriate caution." An opportunistic island is not wrong by
  definition, but it was not created with the same focused attention as a
  task-driven one. This fallback supports CORE PRINCIPLE 9 (DETECTABLE
  FAILURE): a stop-early violation that leaves no trace is invisible to
  the next session; an opportunistic marker makes it recoverable.

---

### BOOT MODE SUMMARY

  Mode              When to use                          Token cost   Completeness
  ──────────────    ─────────────────────────────────    ──────────   ────────────
  1 — Incremental   Default. Any task-driven session.    Low          Grows over time
  2 — Connection    Architecture overview. Pre-mapping.  Medium       Structural only
  3 — Full Mapping  Audits. Explicit full-scan request.  High         Complete

---

## BOOTSTRAP-MODE FIELD

The mainland ARCHITECTURE section carries two fields that persist the epistemic
history of the project's island layer for all future sessions:

  bootstrap-mode: greenfield | legacy | archaeological | unknown
  bootstrap-date: <date when islands were first created>

bootstrap-mode values and their implications:

  greenfield
    Islands were created alongside code from the start.
    verified islands can be trusted as high quality.
    Treat as a normally maintained project.

  legacy
    Islands were added to existing code after the fact.
    Some islands may be generated or confidence: low.
    Verify low-confidence islands before acting on them.

  archaeological
    No author knowledge was available when islands were created.
    All islands are hypotheses until explicitly promoted to verified.
    Treat confidence: medium the way you would treat confidence: low elsewhere.
    A session 50 in an archaeological project is not the same as session 50
    in a greenfield project — the islands have different epistemic weight.
    confidence: high in an archaeological project requires
      `confirmed-by-behavior: <evidence>` in the MEMORY section. Surviving
      metadata is not the same thing as verified metadata.
    Aggressively use confidence-review-due to keep uncertainty visible.

  unknown
    The bootstrap mode was not recorded. Treat all islands as confidence: low.

This field prevents a greenfield project from being misread as legacy after
the first session, and prevents an archaeological project from being treated
as verified after inferences are promoted.

---
