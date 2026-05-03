# LLM Island System — Specification v0.3-rc3
# A semantic companion layer for codebases, optimized for LLM reasoning

For background — what this system is, what it is not, and the
intellectual origin (Akita's work on LLM-optimal language design) —
see `README.md`.

For the dated changelog of every release, see `VERSION_HISTORY.md`.

This file is the routing entrypoint for the spec. Some sections live
here (the topic table immediately below, plus sections not yet split
into modules). The rest live under `SPEC/`. Read only what your task
requires.

---

## TOPIC TABLE

| If your task is | Read |
|-----------------|------|
| Understand the trust model and core principles | `SPEC/00_OVERVIEW.md` |
| Create or edit an island file | `SPEC/01_HEADER.md` (HEADER) + `SPEC/02_SYMBOLS.md` (SYMBOLS) + `SPEC/03_RISKS_MEMORY.md` (RISKS, MEMORY) |
| Assess a subjective field (confidence, fragility, severity, strength, break-impact) | `SPEC/02_SYMBOLS.md` — FIELD DECISION CRITERIA |
| Edit `connections.llmainland` or do selective mainland reads | `SPEC/04_MAINLAND.md` |
| Validate an island (rules, status, staleness) | `SPEC/05_VALIDITY.md` |
| Decide what update tier a change requires | `SPEC/06_TIERS.md` |
| Resume or start a propagation cascade | `SPEC/07_PROPAGATION.md` |
| Bootstrap a new or legacy project | This file — BOOTSTRAPPING + BOOT MODES |
| Understand maintenance obligations | This file — MAINTENANCE PROTOCOL |
| Handle monorepo / dynamic deps / cycles / FFI | This file — STRUCTURAL EDGE CASES |
| Touch a security-sensitive file | This file — SECURITY REVIEW GATES |
| Adopt the system in a project | This file — ADOPTION AND SUSTAINABILITY |

The `SPEC/` directory router is at `SPEC/README.md`. The remaining
"This file" rows move into `SPEC/` in v0.3-rc4.

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

## ADOPTION AND SUSTAINABILITY

The island system requires sustained workflow change: update islands as
part of every commit, run staleness checks, review human edits, declare
contracts. This is not just individual discipline — it is organizational
commitment that has to survive team turnover, management indifference,
and the natural entropy of any process that is not automated or enforced.

### MINIMUM VIABLE ADOPTION

Do not adopt the island system below this threshold of commitment:
  - At least one person is responsible for mainland consistency
  - Island updates are attached to an existing process checkpoint
    (PR review, sprint close, release checklist)
  - A staleness checker runs before each LLM session
  - The team agrees to maintain islands for at least the core and
    orchestration layers

Partial adoption below this threshold is MORE dangerous than no adoption.
Islands that look authoritative but are stale mislead LLMs more than no
islands at all.

### MAINLAND CONSISTENCY (named responsibility, not a job title)

Assign mainland consistency as a responsibility to someone on the team.
This does not require a dedicated role:

  The consistency owner:
  - Reviews mainland changes (connections, contracts, architectural rules)
  - Resolves conflicts when multiple LLM sessions produce contradictions
  - Ensures staleness checks run before LLM sessions
  - Decides when to archive vs. delete stale islands

In solo projects, the developer handles this naturally. In small teams,
it can be rotating or informal. In larger teams, assign it per
architectural area.

This is a good practice, not a prerequisite for adoption. Do not create
a dedicated job title for it.

### ABANDONMENT PROTOCOL

If a team stops maintaining islands:

  DO NOT leave stale islands in place. A stale island that looks current
  is more dangerous than no island at all — it is an authoritative-looking
  lie that new developers and LLMs will trust.

  Options, ranked from preferred to acceptable:

  1. Archive — add `status: abandoned` to every island HEADER and
     `maintenance-status: abandoned` to the mainland's ARCHITECTURE
     section. Islands stay readable for archaeological context but are
     never trusted as ground truth.
  2. Partial — archive islands for files no longer maintained; keep
     islands for actively developed files. Mark each archived island
     with `status: abandoned`.
  3. Delete — remove all `.llmisland` files and `connections.llmainland`.
     Honest, but loses any genuine archaeological value the islands held.

  Leaving stale islands unmarked is the only wrong answer.

### TYING UPDATES TO EXISTING PROCESS

Do not create a separate "island update" process. Attach island updates
to existing checkpoints where they will not slip:

  - PR review checklist: "are all touched-file islands current at the
    correct tier?"
  - Sprint close: "any propagation cascades open in `.llmpropstts`?"
  - Release checklist: "any human-unreviewed islands in the release branch?"

A separate process atrophies. An attached one survives.

---

## SECURITY REVIEW GATES

Islands and the mainland describe exactly where load-bearing invariants live
and what security trade-offs were made. This information is valuable context
AND a potential attack surface.

### WHEN SECURITY REVIEW IS REQUIRED

An island requires `maintained-by: security-reviewed` when:
  - The RISKS section contains `severity: high` or `severity: critical`
  - The island is bound to a security-related mainland CONTRACT
  - The file handles authentication, authorization, encryption, or
    user-supplied input parsing

An island may have `maintained-by: llm` or `human-reviewed` when:
  - No security surfaces are declared
  - All security surfaces have `severity: low` or `medium` with tested guards

A code change to a `security-reviewed` island downgrades `maintained-by` back
to `llm` until the security reviewer re-confirms the island.

### ADVERSARIAL INJECTION WARNING

Island content is trusted by the LLM as ground truth. In multi-contributor
or open-source projects, adversarial editing of islands is a real threat.

A malicious actor (or compromised LLM session) could:
  - Claim a vulnerable function is safe via a false RISKS entry
  - Add a false HISTORICAL-DECISIONS entry redirecting development
  - Weaken an ACTIVE-CONSTRAINTS entry to permit an insecure pattern

The more authoritative islands become, the more valuable they are as an
injection target. Mitigation: for security-sensitive projects, island edits
to security-related files should go through the same review process as
code changes. The `maintained-by: security-reviewed` status is the minimum
signal that this review has occurred.

### OPEN-SOURCE PROJECTS

For open-source or broad-access projects, consider what island content
should be public vs. private:
  - SYMBOLS, HEADER, CONNECTIONS: generally safe to publish
  - Detailed security trade-off history in HISTORICAL-DECISIONS may expose
    vulnerability reasoning that aids attackers
  - ACTIVE-CONSTRAINTS about security workarounds: evaluate case by case

The spec does not require hiding islands. It requires awareness that
islands in security-critical areas are both the most valuable and the
most sensitive documentation in the project.

---

## STRUCTURAL EDGE CASES

Real codebases include monorepos, plugin systems, runtime-discovered
dependencies, and circular references. The base format assumes none of
these. This section extends it.

### MONOREPOS

The default is one mainland per project. Monorepos contain multiple
projects. For monorepos, create `workspace.llmainland` at the repo root:

```
---WORKSPACE---
repo:          my-monorepo
sub-projects:
  - path: packages/frontend
    mainland: packages/frontend/connections.llmainland
  - path: packages/backend
    mainland: packages/backend/connections.llmainland
  - path: packages/shared
    mainland: packages/shared/connections.llmainland

inter-project-connections:
  - from: packages/frontend
    to:   packages/shared
    uses: [types.ts, utils.ts]
    strength: critical
  - from: packages/backend
    to:   packages/shared
    uses: [types.ts, validation.ts]
    strength: critical
```

Each sub-project has its own mainland and islands. The workspace file
declares only cross-project connections. An LLM working on a task reads
only the relevant sub-project's mainland, plus any inter-project
connections that involve files it will touch.

### DYNAMIC DEPENDENCIES

Some files have dependencies determined at runtime: dynamic imports, eval,
plugin architectures, decorator-based registration, hot module replacement.

For these files, add to the island HEADER:

```
dynamic-boundary: true
dynamic-note:     plugins loaded via require(config.pluginPaths[i]) at startup;
                  dependency graph is config-determined, not code-determined
```

For dynamic connections in the mainland:

```
CONNECTION: app.js -> (dynamic)
  uses:         plugins loaded from config
  why:          plugin architecture
  direction:    orchestration -> ?
  strength:     ?
  break-impact: specific plugins fail to load — degraded but functional
  dynamic:      true
  dynamic-note: plugin set determined by runtime config; connections are
                a superset of possible links, not actual links
```

Dynamic connections are not errors — they are honest uncertainty. They tell
future sessions: "this part of the graph cannot be statically determined."

### DEPENDENCY CYCLES

Real codebases have cycles. The island system does not prohibit them — it
requires them to be declared.

For cyclic connections, set:

```
CONNECTION: A.js -> B.js
  uses:       processData()
  direction:  core -> core
  strength:   high
  cycle:      true
  cycle-note: B calls back into A via event emitter on 'data-ready';
              A processes and re-invokes B for next batch
```

A declared cycle is knowledge. An undeclared cycle is a surprise. Cycles
are not inherently invalid, but they increase propagation risk and require
extra care during refactors.

### EXPANDED CROSS-LANGUAGE BOUNDARIES

The `language-boundary` field as a single string (e.g., "python -> c via
ctypes") is sufficient for simple FFI. For non-trivial cross-language
contracts, use the expanded sub-section format:

```
language-boundary:
  from:              python
  to:                c
  mechanism:         ctypes
  data-types:        [float array (frame buffer), int (context handle)]
  error-semantics:   C returns -1 on error; Python raises RuntimeError
  version-coupling:  render_core.so must match header version
```

Sub-fields:
  from / to:         source and target languages
  mechanism:         how the boundary is crossed (ctypes, JNI, FFI, REST, gRPC)
  data-types:        types crossing the boundary and their representations
  error-semantics:   how errors propagate across the boundary
  version-coupling:  whether the two sides must be version-matched

The single-string format remains valid for simple boundaries. Use the
expanded format when the boundary is architecturally significant or when
data marshaling, error semantics, or version coupling are load-bearing.

---

## CROSS-LANGUAGE PIPELINES

The island system is language agnostic. These rules apply at language boundaries.

Each file in each language gets its own island in that language's terms.
The mainland models the boundary explicitly in the connection:

  CONNECTION: orchestrator.py -> renderer.c
    uses:              render_frame(), init_context()
    why:               Python orchestration delegates rendering to C for performance
    direction:         bridge -> core
    language-boundary: python -> c via ctypes
    strength:          critical
    break-impact:      all rendering fails

The island for orchestrator.py describes what it calls and what it expects
from the C side in Python terms.

The island for renderer.c describes what it exports and what it expects
from callers in C terms.

Neither island needs to understand the other language. The mainland holds
the translation contract between them.

If the C layer is later rewritten in Assembly:
  1. renderer.c island is updated (or a renderer.asm island is created)
  2. The mainland connection is updated: language-boundary: python -> asm via nasm
  3. The CONTRACT governing the boundary behavior stays unchanged
  4. What the caller expects from the function does not change
  5. The considerations log records: "renderer.c rewritten to renderer.asm,
     interface preserved, performance boundary unchanged"

The semantic contract survives the implementation rewrite.

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

## VERSION HISTORY

The dated changelog moved to `VERSION_HISTORY.md`. Read that file for
the per-release rationale, the source attributions (Gemini / Grok /
Mistral / Codex / Antigravity), and the issue-to-release mapping.

---

END OF SPEC v0.3-rc3
