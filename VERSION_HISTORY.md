# LLM Island System — Version History

This file is the dated changelog for the spec. The spec itself
(`LLMISLAND_SPEC.md` and the modules under `SPEC/`) is the normative
source. This file explains why specific rules and fields exist by
recording the release that introduced them.

---

## v0.3-rc6 — check-stale, check-decay, spec --topic

Three subcommands wired into the orchestrator. The first dogfood
discovery of the chain happened here: when running `check-stale .`
on mix itself, the rc5 islands correctly reported as stale because
their `last-verified` (2026-05-03) preceded their source mtime
(2026-05-04, the actual edit date). The tool caught a real
inconsistency in its own metadata.

Code added:
- `tooling/stale.py` (~225 LOC) — `cmd_check_stale` + `cmd_check_decay`,
  each with a `setup_*` parser configurator and a shared
  `SUBCOMMANDS` dict. check-stale compares last-verified vs source
  mtime; check-decay flags expired confidence-review-due (date or
  version threshold).
- `tooling/spec_router.py` (~210 LOC) — `cmd_spec` with a 60-key
  `SPEC_TOPIC_MAP` covering every SPEC/ module, plus fuzzy-match
  fallback for partial / unknown keys. Prints SPEC content directly
  when `--json` is absent; returns Report with content in summary
  when `--json` is set.
- `tooling/__init__.py` re-exports nothing (the orchestrator imports
  the submodules directly).

Orchestrator changes:
- `SUBCOMMAND_MODULES = (stale, spec_router)` tuple. `build_parser`
  iterates each module's `SUBCOMMANDS` dict to register subcommands.
  Adding a new subcommand module is a two-step change: write the
  module with a `SUBCOMMANDS` dict, append it to this tuple.
- Windows UTF-8 fix: `sys.stdout`/`sys.stderr` get wrapped in
  `TextIOWrapper(errors="replace")` when the default encoding is
  not UTF-8. Required because spec content includes em dashes,
  arrows, and accented characters that crash on Windows cp1252.

Islands and mainland:
- `tooling/stale.py.llmisland` — full HEADER/SYMBOLS/RISKS/MEMORY,
  documents 5 exports + 3 historical decisions (false-positive
  preference, positional directory arg, lexical version comparison).
- `tooling/spec_router.py.llmisland` — same structure, documents 4
  exports + 3 historical decisions (direct print vs JSON, fuzzy
  match fallback, --topic required).
- All 3 prior islands re-verified (last-verified bumped to
  v0.3-rc6-2026-05-04; called-by lists made concrete instead of
  forward-looking).
- `connections.llmainland` updated: 2 new files in `io` layer, 7
  new connections (stale -> common, stale -> types, spec_router ->
  common, spec_router -> types, orchestrator -> stale, orchestrator
  -> spec_router, spec_router -> SPEC/ as a dynamic external
  connection).

Smoke test results:
- `python llmisland_tooling.py --version` -> 0.3-rc6
- `python llmisland_tooling.py --help` -> lists check-stale, check-decay, spec
- `python llmisland_tooling.py check-stale` -> all 5 islands now fresh
- `python llmisland_tooling.py check-decay` -> ok (none expired)
- `python llmisland_tooling.py spec --topic header` -> prints
  `SPEC/01_HEADER.md`
- `python llmisland_tooling.py spec --topic xyzzy` -> unknown-topic
  Report with the full available-topics list

`.gitignore` not modified.

---

## v0.3-rc5 — tooling skeleton (orchestrator + common helpers + first islands)

First RC of the tooling phase. Lays the foundation for the subcommands
that land in rc6 → rc8: a thin CLI orchestrator at the project root,
a shared helpers module, and the first two islands. Also creates the
project mainland for the tooling layer (greenfield, scope = tooling
only — spec/docs are not islanded per locked decision in `notes.md`).

Files added:
- `llmisland_tooling.py` (138 lines) — argparse orchestrator. Builds
  the parser with shared parent options (`--json`,
  `--include-examples`), exposes `COMMANDS` for rc6+ subcommand
  registration, and `_emit` for uniform text/JSON output. No business
  logic.
- `tooling/__init__.py` — package marker with one-paragraph orientation.
- `tooling/common.py` (134 lines) — shared helpers: `iter_islands`,
  `source_for_island`, `find_project_root`, `read_header_field`,
  `parse_last_verified`, `is_example_path`, plus `Finding` and `Report`
  dataclasses. Standard library only.
- `connections.llmainland` — first mainland in mix. Scope is
  declared explicitly: tooling layer only. 5 architectural rules
  (subcommand modularity, Report return shape, --json via parent
  parser, zero deps, file-size cap), 1 connection
  (`llmisland_tooling.py -> tooling/common.py`), 3 contracts
  (subcommand-return-shape, zero-dependency, shared-flags-via-parent),
  4 architecture-memory historical decisions documenting the locked
  design choices.
- `llmisland_tooling.py.llmisland` — first island in mix. Documents
  every export with full HEADER/SYMBOLS/RISKS/MEMORY sections.
- `tooling/common.py.llmisland` — second island. Same level of detail.

Smoke-tested:
```
$ python llmisland_tooling.py --version
llmisland_tooling 0.3-rc5
$ python llmisland_tooling.py --help
usage: llmisland_tooling [-h] [--version] {} ...
```

The empty `{}` in the subcommand list is correct for rc5: no subcommands
are registered yet. They land in rc6 (check-stale, check-decay, spec),
rc7 (prop-* + validate-rules), and rc8 (validate).

The mix project is now its own first demonstration of the system. Any
LLM working on the tooling layer reads the islands the same way it
would read islands on any other project.

---

## v0.3-rc4 — finish spec section extraction

Last RC of the prompting/spec phase. After this, every operational
section lives under `SPEC/`. `LLMISLAND_SPEC.md` is now a 47-line
router with a topic table.

- 6 more modules extracted from `LLMISLAND_SPEC.md`:
  - `SPEC/08_BOOTSTRAP.md`    — bootstrap (greenfield + legacy +
                                archaeological), boot modes (1/2/3),
                                MVM template, confidence-gated
                                expansion, expansion triggers,
                                stop-early rule, bootstrap-mode field
  - `SPEC/09_MAINTENANCE.md`  — 10 maintenance rules + managing memory
                                over time + .llwasland archival
  - `SPEC/10_EDGE_CASES.md`   — monorepos, dynamic deps, cycles,
                                expanded cross-language boundaries,
                                cross-language pipelines
  - `SPEC/11_SECURITY.md`     — security review gates, adversarial
                                injection threat model, open-source
                                publishing guidance
  - `SPEC/12_ADOPTION.md`     — minimum viable adoption floor,
                                mainland consistency role, abandonment
                                protocol
  - `SPEC/13_REFERENCE.md`    — XP alignment, quick reference (per-
                                scenario procedures), anti-patterns

- `LLMISLAND_SPEC.md` reduced from 953 → 47 lines. It is now purely
  the routing entrypoint: title, version, README+VERSION_HISTORY
  pointer, and the TOPIC TABLE that maps tasks to `SPEC/*` modules.
- TOPIC TABLE updated: every "This file — <SECTION>" row now points
  to its corresponding `SPEC/*` module.
- `SPEC/README.md` directory router updated with all 14 modules.

Note: `SPEC/08_BOOTSTRAP.md` is 363 lines — over the 300-line "yellow
line" but well under the 400-line red line. It groups bootstrap +
boot modes + MVM + expansion + stop-early because those topics are
heavily cross-referenced and a session reading any one usually needs
the others. Splitting now would create chatty cross-file references
that hurt LLM comprehension more than the file size does. Acceptable
under the file-size rule.

Tooling (the rc5+ chain) starts after this RC. The spec at v0.3-rc4
already references commands that do not exist yet (check-stale,
prop-*, validate-rules, etc.); the next RCs build them.

---

## v0.3-rc3 — operational sections to SPEC/

- 4 more modules extracted from `LLMISLAND_SPEC.md`:
  - `SPEC/04_MAINLAND.md`     — MAINLAND FILE STRUCTURE + SELECTIVE READ PROTOCOL
  - `SPEC/05_VALIDITY.md`     — VALIDITY RULES + STALENESS DETECTION + STATUS PROGRESSION
  - `SPEC/06_TIERS.md`        — UPDATE TIERS (A/B/C)
  - `SPEC/07_PROPAGATION.md`  — PROPAGATION PROTOCOL + PROPAGATION STATE AND RESUME
  All under the 220-line target.
- TOPIC TABLE in `LLMISLAND_SPEC.md` updated: 4 rows that previously
  said "This file — <SECTION>" now point at the new SPEC/* modules.
- `SPEC/README.md` directory router updated with rows 04-07.
- Spec line count: 1472 → 953 (down 519).
- Remaining in `LLMISLAND_SPEC.md`: bootstrap, boot modes, maintenance,
  edge cases, cross-language, security gates, adoption, quick
  reference, anti-patterns. These go into `SPEC/08_*` through
  `SPEC/13_*` in rc4.

---

## v0.3-rc2 — SPEC/ scaffolding + island format modules

- `SPEC/` directory created with `SPEC/README.md` as the directory router.
- 4 island-format modules extracted from `LLMISLAND_SPEC.md`:
  - `SPEC/00_OVERVIEW.md`     — CORE PRINCIPLES + FILE NAMING
  - `SPEC/01_HEADER.md`       — ISLAND FILE STRUCTURE + Section 1: HEADER
  - `SPEC/02_SYMBOLS.md`      — Section 2: SYMBOLS + FIELD DECISION CRITERIA
  - `SPEC/03_RISKS_MEMORY.md` — Section 3: RISKS + Section 4: MEMORY
- `LLMISLAND_SPEC.md` becomes more router-like: TOPIC TABLE at the top
  pointing readers to either `SPEC/*` modules or remaining in-file
  sections. The remaining sections (mainland, tiers, propagation,
  validity, bootstrap, maintenance, edge cases, security, adoption,
  reference) are still in this file; they move out in rc3 and rc4.
- Spec line count: 2007 → ~1465 (with the new TOPIC TABLE block added).

---

## v0.3-rc1 — strip non-spec content

- Narrative preamble (intellectual origin, mid-term framing, why this
  exists) removed from spec — the same ground is covered by `README.md`.
  Spec now opens directly with CORE PRINCIPLES.
- Version history extracted into this file (`VERSION_HISTORY.md`). Spec
  ends with a pointer to it.
- `ATTACK_ANALYSIS.md` deleted from the project. The 15 issues it
  catalogued are addressed in v0.2.1 through v0.2.14; the document was
  the v0.3 roadmap and it has now done its job. The fork copies remain
  available as historical artifacts.

This release candidate is the first of a small chain that progressively
delivers the v0.3 restructure (modular `SPEC/` directory + tighter
routing) without a single oversized commit.

---

## v0.2.14 — adoption and sustainability

ADOPTION AND SUSTAINABILITY section added before SECURITY REVIEW GATES
  Minimum viable adoption floor: do not adopt below the maintenance
    threshold; partial adoption is more dangerous than no adoption
  Mainland consistency role: a named responsibility (not a job title)
  Abandonment protocol: archive (preferred), partial archive, or delete
    Leaving stale islands unmarked is the only wrong answer
  Attaching updates to existing process checkpoints (PR, sprint, release)
CONTRIBUTING.md preamble updated to point at the adoption floor before
  a project commits to the system
Addresses: ATTACK_ANALYSIS ISSUE-015 (Adoption and Cultural Sustainability)
Source: Mistral (#9), with Grok (#7) gesturing toward it

---

## v0.2.13 — runtime configuration dependencies

runtime-dependencies field added to SYMBOLS entries (optional)
  Captures env vars, feature flags, config keys that change behavior
    without changing source code
  Use `- none` (explicit) when there are no runtime dependencies
config-dependencies category added to RISKS section (file-level)
  For files where runtime configuration materially changes behavior
    across many symbols (feature-flag-heavy systems)
Mainland CONTRACTS now support an optional `condition` field
  Conditional contracts apply only when the runtime predicate is true
  LLMs without runtime context should treat conditional contracts as
    active (safer assumption)
Example mainland: auth-enforcement contract added showing the new format
Closes the gap where the format had no place to record "this function's
  behavior depends on ENV_VAR_X at runtime"
Addresses: ATTACK_ANALYSIS ISSUE-014 (Runtime Config as Invisible Dependency)
Source: Mistral (#10)

---

## v0.2.12 — human-LLM handoff protocol

LLM_BOOT.md: STEP 0C added — review human-unreviewed islands BEFORE
  starting any task that would touch the same file
RULE 6 in MAINTENANCE PROTOCOL clarified
  Review obligation is at session start, not after task completion
  Cross-references LLM_BOOT.md STEP 0C
Closes the gap where review-after-the-fact bakes inconsistencies into work
Addresses: ATTACK_ANALYSIS ISSUE-011 (Human-LLM Handoff Rot)
Source: Grok (#7)

---

## v0.2.11 — archaeological confidence decay

confidence-review-due field added to island HEADER (optional)
  Format: <version> or <date>
  When the threshold passes without explicit re-review, confidence
    decays one level (high → medium, medium → low)
  Required practice on inferred islands in archaeological projects
BOOTSTRAP-MODE FIELD: archaeological implications expanded
  confidence: high in archaeological projects requires
    `confirmed-by-behavior` evidence
  Aggressive use of confidence-review-due encouraged
  Surviving metadata != verified metadata
Addresses: ATTACK_ANALYSIS ISSUE-009 (Archaeological Fossilization)
Sources: Grok (#9), Gemini (implicit in #3)

---

## v0.2.10 — security review gates

security-reviewed value added to maintained-by enum
  Required for islands with severity >= high in RISKS section
  Required for islands bound to security-related contracts
  A code change to a security-reviewed island downgrades it to llm
    until the security reviewer re-confirms
SECURITY REVIEW GATES section added before STRUCTURAL EDGE CASES
  When security review is required vs. optional
  Adversarial injection warning for multi-contributor projects
  Open-source guidance for sensitive island content
RULE 10 added to MAINTENANCE PROTOCOL: security-sensitive trust gate
  Tasks touching high/critical surfaces require security-reviewed islands
Addresses: ATTACK_ANALYSIS ISSUE-012 (Security as Attack Surface)
Source: Mistral (#6)

---

## v0.2.9 — structural edge cases

STRUCTURAL EDGE CASES section added before CROSS-LANGUAGE PIPELINES
  Monorepos: workspace.llmainland with sub-project declarations
  Dynamic dependencies: dynamic-boundary + dynamic-note (island and connection)
  Dependency cycles: cycle + cycle-note annotations on connections
  Expanded cross-language boundaries: sub-section format with from, to,
    mechanism, data-types, error-semantics, version-coupling
Example CONNECTIONS updated with cycle: false on each entry
python_pipeline.py -> render_core.c connection updated to use the
  expanded language-boundary format
Addresses: ATTACK_ANALYSIS ISSUE-008 (Structural Edge Cases)
Source: Grok (#6)

---

## v0.2.8 — staleness detection as hard dependency

STALENESS DETECTION section added after VALIDITY RULES
  Hard dependency: a staleness checker is required for projects where
    humans edit files outside LLM sessions
  Acceptable mechanisms: pre-session script, CI hook, editor plugin,
    LLM with filesystem access
  LLM with filesystem access: verify timestamps before trusting islands
  LLM without filesystem access: require human-run checker first
  No checker fallback: degraded-trust mode — confidence: high reads as
    medium, confidence: medium reads as low
LLM_BOOT.md: STEP 0B added — staleness check before STEP 1
Aligns with the future llmisland_tooling.py check-stale subcommand
Addresses: ATTACK_ANALYSIS ISSUE-004 (Stale Island Detection)
Sources: Gemini (#4), Grok (#2, #10), Mistral (#1)

---

## v0.2.7 — constraint compliance verification

RULE 9 added to MAINTENANCE PROTOCOL: post-generation compliance check
  Re-read architectural-rules after generating code
  Verify self-checkable rules are not violated
  Fix violations before declaring done — do not leave them for the human
self-checkable sub-field added to architectural-rules format
  self-checkable: true  — LLM can verify by reading code
                          (imports, layers, dependency directions)
  self-checkable: false — requires runtime or external validation
                          (auth checks, runtime invariants)
Example mainland updated to use new architectural-rules format
MVM template updated with self-checkable: ? placeholder
MODE_INCREMENTAL.md WHEN DONE: step 13 added — verify compliance
Addresses: ATTACK_ANALYSIS ISSUE-013 (Constraint Compliance Gap)
Source: Mistral (#7)

---

## v0.2.6 — design for detectable failure

CORE PRINCIPLES: principle 9 added (DETECTABLE FAILURE)
  System is advisory, not enforced; rules create recoverable failure modes
  Every rule must answer: how will a future session discover a violation?
read-reason field added to island HEADER
  Values: task-driven | opportunistic | audit
  Makes stop-early violations visible to future sessions
STOP-EARLY RULE updated with fallback state for violations
  Extra-read islands marked as read-reason: opportunistic
Addresses: ATTACK_ANALYSIS ISSUE-007 (Self-Control as Architecture)
Source: Grok (#5)

---

## v0.2.5 — mainland selective read protocol

SELECTIVE READ PROTOCOL section added between MAINLAND FILE STRUCTURE
  and VALIDITY RULES
  Always-read tier: architectural-rules, ACTIVE-CONSTRAINTS, basics
  Per-file tier: CONTRACTS and CONNECTIONS for touched files only
  Skip-by-default tier: HISTORICAL-DECISIONS, SUPERSEDED, unrelated CONNECTIONS
Explicit guidance against splitting the mainland into a .history file —
  selective reads solve the cost; splitting risks invisible memory
RULE 3 in MAINTENANCE PROTOCOL rewritten for selective reading
LLM_BOOT.md STEP 1 updated to use the protocol instead of "read it now"
Addresses: ATTACK_ANALYSIS ISSUE-006 (Context Window / Mainland Bloat)
Sources: Gemini (#1), Grok (#4), Mistral (#2)

---

## v0.2.4 — decision criteria for subjective fields

FIELD DECISION CRITERIA section added between SYMBOLS and RISKS
  Decision trees for confidence, fragility, severity, strength
  break-impact guidance for specific vs. vague failure descriptions
  Each criterion is evidence-based, not feel-based
Cross-session and cross-model consistency: two LLMs assessing the same
  code should arrive at the same field values when applying these criteria
Note: confidence: high specifically requires human confirmation or test
  evidence — an LLM that has only read the code can reach medium at best
Note: fragility: high based on prior breakage requires evidence (git ref,
  HISTORICAL-DECISIONS entry, or test added after the breakage)
Addresses: ATTACK_ANALYSIS ISSUE-005 (Subjective Fields — No Decision Criteria)
Sources: Gemini (#3), Grok (#3, implicit)

---

## v0.2.3 — anti-hallucination mechanisms

CORE PRINCIPLES: principle 8 added (UNCERTAINTY OVER PLAUSIBILITY)
  ? is the correct answer when evidence does not support a specific value
  Plausible guesses that sound authoritative become canonical lies
generation-pass field added to island HEADER
  true when island was bulk-generated; subjective values are hypotheses
  Future sessions treat subjective fields as provisional when true
  Default: false (focused, task-driven authoring)
RULE 8 added to MAINTENANCE PROTOCOL: rationale required for subjective
  fields set above low (confidence, fragility, severity, strength)
  Format: field: value (rationale: explanation)
  Forces the LLM to show its work — hallucinations become detectable
Addresses: ATTACK_ANALYSIS ISSUE-003 (Hallucination Fossilization)
Sources: Gemini (#3), Grok (#3), Mistral (#1)

---

## v0.2.2 — propagation atomicity and resume

PROPAGATION STATE AND RESUME section added after PROPAGATION PROTOCOL
  .llmpropstts file format defined (lives at project root, NOT in mainland)
  Tool commands: prop-start, prop-done, prop-status, prop-finish
  Manual fallback documented for sessions without tooling
  CASCADE PROTOCOL: count → warn at threshold (10) → batch → resume
  PROPAGATION RESUME: session-start check before any task
  CASCADES BEYOND LLM CAPACITY: guidance for oversized cascades
PROPAGATION PROTOCOL step 8 added: check cascade size before propagating
LLM_BOOT.md: STEP 0 added — check .llmpropstts before any other step
Design choice: propagation state lives in a separate, tool-managed file
  rather than in the mainland. Transient operational state should not
  pollute architectural documentation; the mainland describes intent,
  .llmpropstts describes operations in flight.
Addresses: ATTACK_ANALYSIS ISSUE-002 (Propagation Cascade)
Sources: Gemini (#2), Grok (#2), Mistral (#2)

---

## v0.2.1 — tiered update obligations

UPDATE TIERS section added before PROPAGATION PROTOCOL
  Tier A (internal logic only) → update last-verified only
  Tier B (export behavior changed) → update affected SYMBOLS
  Tier C (signature/connection/contract changed) → full update + mainland
Tier determination decision tree (3 ordered questions)
RULE 1 in MAINTENANCE PROTOCOL rewritten to reference tiers
  Tier A updates declared as first-class valid outcomes, not shortcuts
VALIDITY RULES updated: tiered updates are valid when tier matches scope
PROPAGATION PROTOCOL step 1 now starts with tier determination
"When a full update cannot be completed honestly" subsection added
  status: partial as the honest alternative to verified-but-wrong
MODE_INCREMENTAL.md: maintenance flow updated for tier classification;
  WHEN DONE checklist updated for tier-based completion
Addresses: ATTACK_ANALYSIS ISSUE-001 (Maintenance Tax)
Sources: Gemini (#5), Grok (#1), Mistral (#1, #8)

---

## v0.2 — boot modes, session continuity, question discipline, .llwasland

Boot modes added: Incremental (default), Connection-First, Full Mapping
Task type branching in Mode 1: maintenance vs new feature flow
bootstrap-mode and bootstrap-date fields added to mainland ARCHITECTURE
  Prevents greenfield projects being misread as legacy after first session
  Preserves epistemic status of archaeological projects across sessions
BOOTSTRAP-MODE FIELD section added to spec
Question discipline formalized as RULE 7 in maintenance protocol
  ? marker as the primary tool for non-blocking unknowns
  Batch-all-questions rule against incremental interrogation
  Declared assumption preferred over inconsequential question
Minimum Viable Mainland (MVM) template introduced
Confidence-gated expansion rules added
Stop-early rule formalized
Expansion triggers defined
.llwasland replaces .llmhistory for archived HISTORICAL-DECISIONS
  (W is M upside down; these decisions "was" in land)
.llwasland format specification added
MODES/ directory: MODE_INCREMENTAL.md, MODE_CONNECTION.md, MODE_FULLMAP.md
SCENARIOS/ directory: GREENFIELD, LEGACY, ARCHAEOLOGY, CROSSLANG
EXAMPLES/ directory: annotated island, mainland, wasland examples
LLM_BOOT.md: decision tree replacing the old menu-style prompt
Boot modes contributed by synthesis of responses from Gemini, ChatGPT,
  and Grok when presented with the v0.1 spec for review
Critical path tier model (core → bridges → leaves) from Gemini
Three named modes and confidence-gated expansion from ChatGPT
Accelerated first-boot framing and pain point analysis from Grok

---

## v0.1 — initial specification

Background: Akita's blog post on LLM-optimal language design (2026-02-09)
XP principles integrated as framework alignment
Designed to be language agnostic from inception
Supports greenfield, legacy, archaeological, and cross-language scenarios
Considerations log stratification: active / historical / superseded
Freshness signal via last-verified + status progression
Human edit gate via maintained-by field
load-bearing filter for memory entry qualification
