# LLM Island System — Attack Analysis & Open Issues
# Status: ACTIVE — do not resolve without updating this file
# Source: stress-test responses from Gemini, Grok, Mistral (all three received)
# Version this targets: v0.2

---

## HOW TO USE THIS FILE

This file catalogs known weaknesses in the LLM Island System identified by
adversarial review. Each issue has a severity, a source, a diagnosis, and a
proposed mitigation direction. Issues are NOT closed until a concrete change
to the spec or tooling addresses them. Acknowledging a problem is not closing it.

Severity levels:
  CRITICAL   — will cause system failure in real-world use
  HIGH       — significant degradation in most real codebases
  MEDIUM     — real problem but manageable with discipline
  LOW        — edge case or philosophical concern

---

## ISSUE-001: Maintenance Tax — Islands Double Every Code Change

Severity: CRITICAL
Sources: Gemini (#5), Grok (#1)

Diagnosis:
  The rule "island update is part of task completion" is correct in principle
  but catastrophic at velocity. Every code change requires: update source +
  update island + possibly update mainland + possibly update bound islands.
  Fast iteration (bug fixes, experiments, hotfixes) becomes structurally slower.
  Humans will skip. LLMs will hallucinate fields to appear done. Both produce
  a drifting parallel layer that becomes worse than no layer at all.
  Grok frames this precisely: "the classic documentation tax problem dressed
  in LLM clothing."

Mitigation direction:
  - Define a minimum viable update: not every change requires a full island
    update. A change that does not affect exports, effects, or connections
    requires only a `last-verified` timestamp update.
  - Tier the update obligation by change scope:
      Tier A (internal logic only) → update last-verified only
      Tier B (export behavior changed) → update affected SYMBOLS
      Tier C (signature or connection changed) → full update + mainland
  - The spec must make "partial update" a first-class valid outcome, not a
    shortcut. The current spec implies any update short of complete is wrong.

Status: OPEN

---

## ISSUE-002: Propagation Cascade — No Atomicity, No Resume

Severity: CRITICAL
Sources: Gemini (#2), Grok (#2)

Diagnosis:
  A change to a core file can cascade to 40+ dependent islands. LLMs have
  output token limits. A cascade that hits the limit mid-way leaves the graph
  in a contradictory state: half the islands describe the old contract, half
  the new one. The system has no concept of "propagation in progress" — no
  way to mark which islands have been updated and which haven't, and no way
  for a future session to resume the cascade rather than starting over.
  Grok: "staleness cascades like a virus" — one missed update poisons
  downstream reasoning with no graceful degradation.

Mitigation direction:
  - Add a `propagation-in-progress` state to the mainland with an explicit
    list of islands still requiring update.
  - Add a cascade size threshold: if updating a contract would affect > N
    islands, surface this to the human as a "large-impact change" before
    the cascade begins. Human confirms before propagation starts.
  - Add "propagation resume" to LLM_BOOT.md: check for in-progress
    propagation at session start before doing anything else.
  - Consider: cascades above the threshold require human-triggered tooling,
    not LLM propagation.

Status: OPEN

---

## ISSUE-003: Hallucination Fossilization

Severity: CRITICAL
Sources: Gemini (#3), Grok (#3)

Diagnosis:
  LLMs are trained to be helpful and complete. Outputting `?` feels like
  failure. Models will hallucinate plausible-sounding values for subjective
  fields (fragility-note, confidence, break-impact) rather than declaring
  uncertainty. The deeper problem: once a hallucinated value exists in an
  island, it becomes the new canonical source. Future sessions cite it as
  historical fact. A wrong `break-impact` that sounds authoritative will
  prevent a valid refactor for months. The system amplifies hallucination
  because it treats island content as ground truth.
  Gemini: "fighting the innate urge to fill in the blank is notoriously difficult."
  Grok: "a single hallucinated active constraint can survive for months."

Mitigation direction:
  - Add explicit decision criteria for all subjective fields. Not just value
    labels but decision trees:
      confidence: high = human explicitly confirmed this field
      confidence: medium = inferred from call sites or tests, not confirmed
      confidence: low = inferred from code structure alone
    Without criteria, LLMs pick by feel and picks are inconsistent.
  - Add a `generation-pass` flag: islands created in a single automated pass
    should carry a marker that tells future sessions "this island was generated
    in bulk — treat all values as hypotheses until individually verified."
  - Consider: subjective fields should require a brief `rationale` subfield
    when set to anything above `low`. Forces the LLM to show its reasoning,
    making hallucinations detectable.

Status: OPEN

---

## ISSUE-004: Stale Island Detection — No Native Mechanism

Severity: HIGH
Sources: Gemini (#4), Grok (#2, #10)

Diagnosis:
  The system relies on `last-verified` + human/LLM discipline to detect stale
  islands. But an LLM cannot compare `last-verified` against filesystem
  modification timestamps without tooling. A hotfix pushed via IDE without
  updating the island looks identical to a fresh island. The LLM will trust
  it and reason from wrong information.
  Gemini: "without an automated staleness checker, I will blindly trust the
  outdated island and write broken code."

Mitigation direction:
  - Explicitly declare in the spec: a staleness checker (script or CI hook)
    comparing `last-verified` against file modification times is NOT optional
    for any project where humans edit files outside of LLM sessions. It is a
    hard dependency, not a nice-to-have.
  - Add a staleness detection step to LLM_BOOT.md for sessions in projects
    where the LLM has file system access: "before reading any island, verify
    last-verified against source file modification date."
  - For projects without file system access: require humans to run a staleness
    check before starting an LLM session.
  - Provide a reference staleness checker script in CONTRIBUTING.md as a
    minimum viable tool, not just a wish.

Status: OPEN

---

## ISSUE-005: Subjective Fields — No Decision Criteria

Severity: HIGH
Sources: Gemini (#3), implicitly Grok (#3)

Diagnosis:
  Fields like `confidence`, `fragility`, and `severity` have value labels but
  no decision criteria. An LLM assessing "medium fragility" on Tuesday may
  assess the same code as "high fragility" on Wednesday based on prompt phrasing.
  This introduces phantom churn — islands that change not because the code
  changed but because the LLM's mood changed. Consistency requires criteria,
  not just labels.

Mitigation direction:
  - Add a FIELD DECISION CRITERIA section to the spec with explicit rules
    for each subjective field:
      fragility: high = a change here has broken something in this project before
                        OR the field is used in 5+ places with no type enforcement
      fragility: medium = inferred risk from call site complexity or effect breadth
      fragility: low = isolated, well-tested, no cross-file mutation
  - Same for confidence, severity, strength.
  - These criteria make assessments reproducible across sessions and models.

Status: OPEN

---

## ISSUE-006: Context Window at Scale — Mainland Bloat

Severity: HIGH
Sources: Gemini (#1), Grok (#4)

Diagnosis:
  In enterprise codebases with hundreds of files, `connections.llmainland`
  becomes massive. Reading it in full at session start consumes context before
  any source code is touched. The spec says "read the mainland" without
  acknowledging that this is free on small projects and catastrophically
  expensive on large ones.

Mitigation direction:
  - Add selective read protocol to the mainland format: internal section
    markers that allow targeted reads.
    "Read CONTRACTS section before touching any file."
    "Read only the CONNECTIONS entries for files you will touch."
    "Read ACTIVE-CONSTRAINTS in ARCHITECTURE-MEMORY before any change."
    "Skip HISTORICAL-DECISIONS unless investigating a bug."
  - Consider splitting the mainland into sub-files at scale:
      connections.llmainland          (core architecture + contracts)
      connections.llmainland.history  (architecture memory)
    This mirrors the .llwasland pattern for islands.
  - The mainland's MVM template should already have these section markers so
    projects start with navigable structure.

Status: OPEN

---

## ISSUE-007: Self-Control as Architecture

Severity: HIGH
Source: Grok (#5)

Diagnosis:
  The entire system depends on an LLM following rules across sessions that it
  has no memory of having written or committed to. The model that writes
  LLM_BOOT.md is not the model that follows it next session. Stop-early,
  mode selection, question discipline, propagation protocol — all of these run
  counter to LLM training incentives (thoroughness, helpfulness, completion).
  A rule that conflicts with training will be violated under pressure.

Mitigation direction:
  - This is partially architectural (unsolvable by spec alone) and partially
    addressable through format design.
  - The spec should acknowledge this explicitly: "the system is not self-
    enforcing. The rules exist to create a recoverable failure mode, not to
    prevent failure. When an LLM violates stop-early or skips a propagation,
    the damage should be detectable and repairable, not silent."
  - Design for detectable failure rather than prevented failure.
  - Question discipline and stop-early rules should include explicit fallback
    states: "if you read more files than the task required, mark those islands
    as generated/unreviewed so future sessions know they were not task-driven."

Status: OPEN

---

## ISSUE-008: Structural Edge Cases — Monorepos, Dynamic Code, Cycles

Severity: HIGH
Source: Grok (#6)

Diagnosis:
  The spec assumes:
  - One project = one mainland. Monorepos break this.
  - Dependencies are static and discoverable. Dynamic imports, eval,
    decorators, plugin architectures, hot-reload break this.
  - Dependency graphs are acyclic. Real codebases have cycles.
  - Cross-language boundaries are describable with a single field.
    Non-trivial FFI, ABI concerns, data marshaling, error propagation
    across language boundaries are not captured.

Mitigation direction:
  - Monorepos: define a `workspace.llmainland` at the repo root that declares
    sub-project mainlands and their inter-project connections.
  - Dynamic code: introduce a `dynamic-boundary` annotation for files whose
    dependency graph cannot be statically determined. These files have islands
    that explicitly declare "connections are runtime-determined" rather than
    pretending static connections are complete.
  - Cycles: the CONNECTIONS format should allow cycle annotations:
      CONNECTION: A -> B
        cycle: true
        cycle-note: B calls back into A via event system
  - Cross-language: expand the `language-boundary` field into a sub-section
    with: data types crossing the boundary, error semantics, version coupling.

Status: OPEN

---

## ISSUE-009: Archaeological Fossilization

Severity: MEDIUM
Sources: Grok (#9), Gemini (implicit in #3)

Diagnosis:
  Inferred islands start as `confidence: low` hypotheses but the distinction
  blurs over time. A `confidence: low` island that has never been contradicted
  starts being treated as reliable simply because it's old. The system has no
  mechanism to keep archaeological uncertainty visible as time passes. Wrong
  historical decisions get promoted from hypothesis to fact not by evidence
  but by survival.

Mitigation direction:
  - Add `confidence-decay` concept: an island whose confidence has not been
    explicitly reviewed after N major version increments automatically
    downgrades. Not implemented automatically (requires tooling) but declarable:
      confidence-review-due: v15  (downgrade if not reviewed by version 15)
  - Archaeological projects should carry a project-level flag in the mainland:
      `bootstrap-mode: archaeological` already exists — extend its implications.
    Any island in an archaeological project that reaches `confidence: high`
    without a `confirmed-by-behavior` evidence entry should be flagged as
    suspicious by the validator.

Status: OPEN

---

## ISSUE-010: The Mid-Term Trap

Severity: LOW (philosophical, not operational)
Source: Grok (#8)

Diagnosis:
  By making LLMs "work well enough" with islands, the system may reduce urgency
  to build the real solution (an LLM-native language with native primitives for
  dependency graphs, effect declarations, provenance). Successful workarounds
  delay proper solutions. The spec acknowledges being mid-term but does not
  reckon with the possibility that it makes the long-term solution less likely.

Mitigation direction:
  - No spec change addresses this directly.
  - The CONTRIBUTING.md should explicitly invite research contributions that
    connect island format decisions to LLM-native language design.
  - The island format should be designed with migration in mind: every field
    should have an obvious mapping to what a native primitive would look like,
    so the islands become a migration path rather than a dead end.

Status: ACKNOWLEDGED — no spec change needed until Mistral response reviewed

---

## ISSUE-011: Human-LLM Handoff Rot

Severity: MEDIUM
Source: Grok (#7)

Diagnosis:
  `maintained-by: human-unreviewed` is a weak signal. The incorrect island is
  live and potentially acted upon before the next LLM session reviews it. The
  review happens in arrears, not at the point of edit. Humans who edit islands
  directly and introduce inconsistencies create a source of arguments rather
  than clarity.

Mitigation direction:
  - Add a session-start check: if any island has `maintained-by: human-unreviewed`,
    the LLM must review it before starting the declared task. Not after.
    This is already implied but not stated explicitly enough.
  - Consider: human edits to islands should be done through a structured
    template/form that forces the required fields, reducing the inconsistency
    surface. This is a tooling contribution, not a spec change.

Status: OPEN

---

## PENDING — MISTRAL RESPONSE NOT YET RECEIVED

The above captures Gemini and Grok. Mistral's response may surface additional
issues. This file should be updated before any spec changes are made.

---

## CROSS-CUTTING THEMES

These themes appear across multiple issues and should inform the next spec version:

1. TOOLING IS NOT OPTIONAL
   Multiple issues reduce to: the spec assumes discipline that only tooling can
   enforce. A minimum viable toolset (staleness checker, format validator,
   propagation tracker) should be declared as required infrastructure, not as
   aspirational contributions. The spec should state what happens when this
   tooling does not exist (degraded trust level on all islands).

2. DESIGN FOR DETECTABLE FAILURE, NOT PREVENTED FAILURE
   The system will be violated. Rules will be skipped. Hallucinations will
   occur. The goal should not be preventing these — it should be making them
   visible and recoverable rather than silent and cumulative.

3. GRADUATED TRUST, NOT BINARY TRUST
   The current model treats islands as either ground truth or stale. Real
   islands exist on a spectrum. A field-level confidence model (not just
   file-level status) would allow "the HEADER is verified but the SYMBOLS
   were inferred" — more honest and more useful than treating the whole
   island as one trust level.

4. MINIMUM VIABLE UPDATE MUST BE FIRST-CLASS
   The current spec implies any update short of complete is a shortcut.
   This is wrong and will cause maintenance tax. Tiered update obligations
   by change scope are necessary for velocity.

5. DECISION CRITERIA OVER VALUE LABELS
   Every subjective field needs explicit criteria, not just allowed values.
   This is the only path to cross-session and cross-model consistency.

---

## VERSION LOG

Created: v0.2 review cycle
Sources: Gemini attack response, Grok attack response
Pending: Mistral attack response
Next action: decide


---

## ISSUE-012: Security — Metadata as Attack Surface and Adversarial Injection

Severity: HIGH
Source: Mistral (#6) — unique, not raised by Gemini or Grok

Diagnosis:
  Two distinct threats neither Gemini nor Grok identified:

  Threat A — information exposure: Islands and the mainland describe exactly
  where load-bearing invariants live, what security trade-offs were made, and
  what was rejected and why. In an open-source project or one with broad repo
  access, this is a detailed map of where to attack. A mainland for a
  security-critical system describes its own weakest points.

  Threat B — adversarial injection: A malicious actor (or a compromised LLM
  session) could write a plausible-looking island entry claiming a vulnerable
  function is safe, or that an insecure pattern is a documented design
  decision. The LLM trusts island content as ground truth. A well-crafted
  false ACTIVE-CONSTRAINTS entry or HISTORICAL-DECISIONS entry could redirect
  development toward a vulnerability for months before detection. This is not
  just stale islands — it is active deception through the trust surface the
  system creates. The more authoritative islands become, the more valuable
  they are as an injection target.

Mitigation direction:
  - Add a `security-reviewed` value to `maintained-by`, distinct from
    `human-reviewed`. Security-sensitive islands require this level before
    being trusted for code generation that touches security boundaries.
  - Islands that describe security surfaces (RISKS section, severity >= high)
    should require a higher review gate — not just LLM review but explicit
    human security review.
  - For open-source or broad-access projects: document which parts of the
    island system should NOT be public (e.g., detailed security trade-off
    history in HISTORICAL-DECISIONS).
  - Cryptographic signatures are heavy for v0.3 but the concept is correct:
    islands in security-critical areas need tamper evidence. At minimum, a
    hash of the island content stored in the mainland connection entry so
    drift is detectable.
  - The spec should explicitly warn: "island content is trusted by the LLM
    as ground truth — adversarial editing of islands is a real threat in
    multi-contributor or open-source contexts."

Status: OPEN

---

## ISSUE-013: Constraint Compliance Gap — Reading a Rule ≠ Following It

Severity: HIGH
Source: Mistral (#7) — distinct from ISSUE-003 (hallucination)

Diagnosis:
  ISSUE-003 covers LLMs hallucinating plausible-sounding values rather than
  using ?. This is a different failure mode: the LLM reads a constraint
  correctly and then generates code that violates it anyway because the
  training-pattern for "how to solve this type of problem" overrides the
  stated rule.

  Mistral's example is precise: the mainland says "no direct database access
  from the frontend." The LLM reads this, acknowledges it, then generates
  frontend code with a direct DB call because that is the pattern its training
  associates with the task type. The constraint was read. It was not followed.

  The island system assumes that reading a constraint is equivalent to
  respecting it. That assumption is structurally wrong. Islands are advisory
  to the LLM, not enforced. There is no mechanism that prevents generation of
  code violating a declared architectural rule.

Mitigation direction:
  - This is the strongest argument for the validator tooling: generated code
    should be checked against mainland architectural-rules before being
    presented to the human, not just generated and hoped to be compliant.
  - In the spec: add a step to the MODE_INCREMENTAL new feature flow — after
    generating code, explicitly re-read the relevant architectural-rules and
    verify the generated code does not violate them before declaring done.
  - The mainland's architectural-rules section should distinguish between
    rules the LLM can self-check (e.g., "no import from presentation to core"
    — detectable by reading imports) and rules that require runtime or external
    validation (e.g., "this endpoint must authenticate all requests").
  - Long term: the validator tool should take generated diffs and check them
    against architectural-rules automatically.

Status: OPEN

---

## ISSUE-014: Runtime Configuration as Invisible Dependency

Severity: MEDIUM
Source: Mistral (#10, specific case) — extends ISSUE-008 but distinct

Diagnosis:
  ISSUE-008 covers dynamic imports, eval, circular dependencies. This is a
  specific gap within that space that deserves separate treatment: a function
  whose behavior changes based on a runtime value — an environment variable,
  a feature flag, a config file value — has a dependency the island system
  cannot capture. The CONNECTIONS section models code imports. It has no
  vocabulary for "this function's behavior depends on ENV_VAR_X at runtime."

  An LLM reading the island for such a function will reason from an incomplete
  model. The island says the function reads from user-store and returns User.
  The reality is: in production with FEATURE_FLAG_NEW_AUTH=true, it also
  checks an auth service and can return Unauthorized. The island is not stale
  — the code hasn't changed. But the island is wrong for the runtime context
  the human is asking about.

Mitigation direction:
  - Add a `runtime-dependencies` field to SYMBOLS entries:
      runtime-dependencies:
        - ENV_VAR_X :: changes return type when set to "strict"
        - FEATURE_FLAG_AUTH :: adds auth check to call path when true
  - For projects with extensive feature flags, add a `config-dependencies`
    section to the island RISKS section noting which runtime configurations
    materially change the file's behavior.
  - The mainland CONTRACTS section should be able to declare environment-
    conditional contracts:
      CONTRACT: auth-enforcement
        condition: FEATURE_FLAG_AUTH=true
        statement: all API endpoints must validate auth token
  - This is a format extension, not a discipline problem. The current format
    simply has no place to put this information.

Status: OPEN

---

## ISSUE-015: Adoption and Cultural Sustainability

Severity: MEDIUM
Source: Mistral (#9) — Grok gestured at this, Mistral frames it fully

Diagnosis:
  The system requires a sustained workflow change: update islands as part of
  every commit, run staleness checks, review human edits, declare contracts.
  This is not just individual discipline — it is organizational commitment
  that has to survive team turnover, management indifference, and the natural
  entropy of any process that is not automated or enforced.

  Mistral's "metadata steward" concept is useful: without a named owner for
  mainland consistency, the mainland drifts by committee neglect. In a solo
  or small team context this is one person. In a larger org it needs explicit
  assignment.

  The adoption curve also has a specific failure mode: teams adopt the system
  during an enthusiastic period, build some islands, then abandon it when
  velocity pressure hits. The remaining islands are worse than none — they
  are authoritative-looking lies that new developers and LLMs will trust.

Mitigation direction:
  - The spec or CONTRIBUTING.md should define a minimum viable adoption level:
    below this level of maintenance commitment, do not adopt the system.
    Partial adoption is more dangerous than no adoption.
  - Define the "mainland steward" role explicitly — not as a full-time job
    but as a named responsibility: who reviews mainland changes, who resolves
    conflicts, who runs staleness checks.
  - Tie island updates to existing process checkpoints where possible: PR
    review, sprint close, release checklist. Do not create a separate process
    — attach to existing ones.
  - Document the abandonment failure mode explicitly: "if your team stops
    maintaining islands, do not leave stale islands in place. Either archive
    them with a clear STALE marker at the top, or delete them. A deleted
    island is honest. A stale island that looks current is a trap."

Status: OPEN

---

## CROSS-SOURCE CONFIRMATION (MISTRAL ADDITIONS)

The following existing issues were confirmed independently by all three sources.
Severity ratings unchanged but confidence in them increases.

  ISSUE-001 (Maintenance Tax)       — Gemini, Grok, Mistral (#1, #8)
  ISSUE-002 (Propagation Cascade)   — Gemini, Grok, Mistral (#2 scalability)
  ISSUE-004 (Staleness Detection)   — Gemini, Grok, Mistral (#1 failure modes)
  ISSUE-006 (Context/Mainland Bloat)— Gemini, Grok, Mistral (#2)
  ISSUE-008 (Edge Cases)            — Gemini, Grok, Mistral (#3, #10)
  ISSUE-010 (Mid-Term Trap)         — Grok, Mistral (#8 long-term maintainability)

---

## MISTRAL RISK MATRIX (for reference)

Mistral produced a likelihood/impact matrix. Incorporated here as a secondary
severity signal alongside the primary severity ratings above.

  Category              Biggest Risks                           Likelihood  Impact
  ──────────────────    ──────────────────────────────────────  ──────────  ──────
  Human Factors         Metadata decay, bootstrapping mistakes  High        High
  Scalability           Mainland bloat, archival growth         Medium      High
  Cross-Language        Broken contracts, generated code gaps   High        High
  Tooling Gaps          Manual processes, no CI/CD integration  Medium      Medium
  Security              Metadata exposure, adversarial edits    Low         High
  LLM Misuse            Ignores or misreads metadata            Medium      High
  Adoption Barriers     Cultural resistance, lack of enforcement High       Medium
  Edge Cases            Dynamic behavior, runtime config        High        Medium

Notable: Security rated Low likelihood but High impact — consistent with
treating it as a background concern for most projects but a critical concern
for security-sensitive ones.

---

## UPDATED STATUS

Analysis complete. All three LLM responses received and synthesized.
Total issues cataloged: 15
  CRITICAL: 3 (001, 002, 003)
  HIGH:     6 (004, 005, 006, 007, 008, 012, 013)
  MEDIUM:   4 (009, 011, 014, 015)
  LOW:      1 (010)
  ACKNOWLEDGED (no spec change): 1 (010)

Next action: decide which issues to address in v0.3 and which to defer.
Recommended priority order based on severity and cross-source confirmation:
  1. ISSUE-001 — tiered update obligations (changes the core discipline model)
  2. ISSUE-002 — propagation atomicity (prevents graph corruption)
  3. ISSUE-003 — decision criteria for subjective fields (reduces hallucination)
  4. ISSUE-006 — mainland selective read protocol (scalability)
  5. ISSUE-013 — constraint compliance gap (closes trust assumption)
  6. ISSUE-004 — staleness detection declared as hard dependency
  7. ISSUE-014 — runtime-dependencies field (format extension)
  8. ISSUE-012 — security review gate for sensitive islands
