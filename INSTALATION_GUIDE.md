# LLM Island System — Installation Guide

How to introduce the LLM Island System into a project.
Read `LLMISLAND_SPEC.md` alongside this guide — it contains the full format
reference for every file you will create here.

---

## Before You Start

The LLM Island System ships with the following files — these live in the
system's own repository, not in your project:

| File | Purpose |
|------|---------|
| `README.md` | Overview of the system. Read this first. |
| `LLMISLAND_SPEC.md` | The full format specification. Every LLM reads this. |
| `INSTALATION_GUIDE.md` | This file. How to introduce the system into a project. |
| `CONTRIBUTING.md` | How to contribute to the spec itself. |

What you add to **your project**:

| File | Purpose |
|------|---------|
| `LLMISLAND_SPEC.md` | Copy from the system repo. The LLM reads this each session. |
| `connections.llmainland` | Created in Step 2 below. One per project, at the root. |
| `<file>.llmisland` | One per source file, created alongside the file. |

Do not copy `README.md` or `INSTALATION_GUIDE.md` into your project.
They describe the island system itself, not your project.
Point contributors to the system's own repository for those.

The `connections.llmainland` is created in Step 2 of whichever scenario applies.

---

## Scenario A: Greenfield Project

You are starting a new project from zero. This is the easiest scenario.

### Step 1 — Copy the spec into your project root

Copy `LLMISLAND_SPEC.md` from the system repository into your project root.
This is the only system file your project needs. Your project's own README
should mention the island system and link to the system repository for reference.

```
your-project/
  LLMISLAND_SPEC.md    ← copied from the island system repo
  connections.llmainland
  <your source files>
  <your source files>.llmisland
```

### Step 2 — Create connections.llmainland before writing code

The mainland is the architecture before it is the implementation. Create it first,
even if most fields are placeholders. Declare the layers you intend to have, the
architectural rules you intend to enforce, and any known contracts.

A minimal starting mainland:

```
---ARCHITECTURE---
project:        my-project
version:        0
last-verified:  2026-01-01
description:    One sentence describing what this project does.

layers:
  core:         []
  presentation: []
  test:         []

load-order:
  - ? (to be determined as files are created)

architectural-rules:
  - AR-001: (add your first rule here, even if tentative)

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

### Step 3 — Create islands alongside files

Every time you create a source file, create its island immediately.
Populate all fields. Mark unknowns with `?`. Mark fields not applicable with `N/A`.
Set `status: generated` until you have reviewed it.

Add the file's connections to the mainland as you go.

### Step 4 — First verification pass

After your first working version, do a pass over all islands:
- Resolve any `?` fields that can now be answered
- Promote `status: generated` to `status: verified`
- Confirm all mainland connections are accurate
- Declare your first formal contracts in the mainland

From this point, propagation discipline applies to every change.

---

## Scenario B: Legacy Adoption

You have an existing codebase. You want to add the island system without
disrupting ongoing work.

### Step 1 — Copy the spec into your project root

```
your-project/
  LLMISLAND_SPEC.md    ← copied from the island system repo
```

### Step 2 — Generation pass (LLM does this, minimal human time)

Ask an LLM to read every source file and generate islands for all of them.
The LLM should follow this process for each file:

1. Read the source file completely
2. Read all tests that reference this file
3. Read git history for this file if available
4. Generate the island, marking all inferences explicitly
5. Use `status: generated`, `confidence: low` for everything uncertain
6. Use `?` for every field that cannot be determined from the code alone

The LLM then generates a first-pass `connections.llmainland` from the observable
import/export graph. All connections start as `strength: ?` until reviewed.

Do not skip files. An undocumented connection in the mainland is a blind spot.
A missing island for a file that has connections is an invalid mainland.

### Step 3 — Create connections.llmainland

The generation pass produces a first-pass mainland from observable structure.
It will be missing:
- Architectural rules (the LLM cannot infer intent)
- Formal contracts (the LLM cannot infer what invariants are load-bearing)
- Connection strength ratings above `?`
- Architectural memory

This is expected. The mainland starts partial and gets completed in Step 4.

### Step 4 — Verification pass (human + LLM, focused time investment)

This is where institutional knowledge is transferred into the system.
The LLM presents targeted questions — not open-ended, not "what does this do."
Specific, binary or constrained questions derived from the low-confidence islands.

Examples of good verification questions:
- "This function appears to handle PAL region timing based on the constants
  used. Is that correct, or is there another reason for these values?"
- "I cannot determine why this module exists independently rather than being
  part of the core module. What requirement drove the separation?"
- "This connection breaks silently when severed. Should it be rated critical or high?"

Human answers are incorporated immediately. Islands are promoted from
`generated` to `verified` as fields are confirmed.

For fields that genuinely cannot be answered — no one knows, documentation
is lost — leave them as `?`. Honest incompleteness is valid. Fabricated
certainty is not.

### Step 5 — Declare contracts

After islands stabilize, work with the human to declare contracts in the mainland.
Ask: "What are the invariants in this system that, if broken, cause silent failures
that tests do not catch?"

Each answer becomes a CONTRACT entry. These are the most valuable part of the
mainland for long-running projects.

### Step 6 — Integrate into ongoing work

From this point, the propagation discipline applies to all new work.
Islands are updated as part of tasks, not as a separate maintenance burden.
The mainland is checked at the start of every task.

Remaining `?` fields are resolved opportunistically as people work in those areas.

---

## Scenario C: Archaeological Mode

No original authors are available. The people working on the codebase are
discovering its intent from its behavior. This applies to:

- Preservation and emulation projects
- Abandoned open-source codebases being revived
- Reverse engineering
- Codebases where the team has completely turned over

### The epistemic shift

In standard legacy adoption, the generation pass produces guesses and the
verification pass replaces them with author knowledge. In archaeological mode,
there are no authors. The generation pass produces hypotheses and the
verification pass evaluates those hypotheses against available evidence.

The difference is in the confidence and evidence fields:

Standard legacy memory entry:
```
HISTORICAL-DECISIONS:
  - id: HD-001
    decision:  canvas chosen over DOM elements for rendering
    reason:    DOM approach caused reflow jank on mobile
    date:      2024-01-05
    outcome:   stable
    evidence:  git:b2e1a09
```

Archaeological memory entry:
```
HISTORICAL-DECISIONS:
  - id: HD-001
    decision:  canvas appears to have been chosen over DOM elements
    reason:    hypothesis: DOM jank on mobile — supported by git:b2e1a09 comment
               and by the absence of any CSS positioning classes in the codebase
    date:      inferred ~2024-01 from commit clustering
    outcome:   stable — no DOM rendering code exists anywhere
    evidence:  inferred-from-comments, inferred-from-codebase-absence
```

### Status in archaeological mode

All islands start as `status: inferred`, `confidence: low`.

As evidence accumulates:
- Confirmed hypotheses: promote `confidence`, eventually promote `status: verified`
- Wrong hypotheses: move to SUPERSEDED, add new corrected entry, record what
  changed the assessment

Never delete wrong entries. They are part of the research record.

### Behavioral contracts in archaeological mode

Contracts are derived from observed behavior, not author intent. Add `confidence`
and `evidence` fields to contract entries to reflect epistemic status.

---

## Scenario D: Mixed-Language Pipeline

### One island per file, regardless of language

Every source file gets an island in the terms of its own language. A Python
orchestrator and a C renderer are each described in their own terms.

### The mainland models the boundary

```
CONNECTION: orchestrator.py -> renderer.c
  uses:              render_frame(), init_context()
  why:               Python delegates frame rendering to C for performance
  direction:         bridge -> core
  language-boundary: python -> c via ctypes
  strength:          critical
  break-impact:      all rendering fails
```

### Bridge files get the bridge layer

Files whose primary purpose is translating between languages are assigned
`layer: bridge` in their island header.

### Contracts survive implementation rewrites

If the C renderer is later rewritten in Assembly:
1. The mainland connection is updated: `language-boundary: python -> asm via nasm`
2. The CONTRACT governing boundary behavior stays unchanged
3. The considerations log records the rewrite as a HISTORICAL-DECISION

The semantic contract at the boundary outlives the implementation language.

---

## Integrating with Your LLM Instruction File

If your project uses a `CLAUDE.md`, `AGENTS.md`, or similar file, add a section:

```markdown
## LLM Island System

This project uses the LLM Island System for semantic context.

Before starting any task:
1. Read `LLMISLAND_SPEC.md` — the authoritative format reference
2. Read `connections.llmainland` — the architectural graph
3. Read the `.llmisland` file for any file you will touch

When completing any task that modifies a source file:
1. Update the file's `.llmisland` — this is part of done, not optional
2. Update `connections.llmainland` if any connection changed
3. If the mainland changed, check all bound islands for staleness
```

---

## Setup Checklist

**Files present:**
- [ ] `LLMISLAND_SPEC.md` at project root
- [ ] `README.md` referencing the island system
- [ ] `connections.llmainland` at project root

**Mainland validity:**
- [ ] All files with connections have a `.llmisland`
- [ ] All CONTRACT entries reference tests that exist
- [ ] No architectural-rule is violated by a declared connection
- [ ] `last-verified` is present

**Island validity (per island):**
- [ ] No required field is blank — unknowns use `?` or `N/A`
- [ ] `fragility: medium/high` entries have `fragility-note`
- [ ] Security surfaces at severity `medium`+ have `guarded-by` or `test`
- [ ] Test file islands have `business-rule` on every SYMBOL entry
- [ ] `status` and `last-verified` are present and consistent

**Workflow:**
- [ ] LLM instruction file references the spec
- [ ] Island update is part of task completion, not separate from it

---

## Troubleshooting

**"I don't know what to put in a field."**
Use `?`. Honest incompleteness is valid. Never fabricate certainty.

**"The island is getting very long."**
Apply the load-bearing filter: only document what tooling cannot catch.
If a compiler or test already enforces it, it does not belong in the island.

**"Updating the island feels like overhead."**
The island is too detailed. Islands capture load-bearing semantics, not
everything the code does. If updates consistently take too long, review
whether your SYMBOL entries are re-documenting what the code already says.

**"The mainland references a file with no island."**
Invalid mainland. Create the island before the next task on either file.

**"Someone edited an island and I'm not sure if it's accurate."**
Set `maintained-by: human-unreviewed`. Treat as `status: partial` until
reviewed. Review it as part of the next task on that file.

**"We have no git."**
Use date-based evidence identifiers: `evidence: task-2026-03-15-refactor`.
The entry must be understandable without the reference.
