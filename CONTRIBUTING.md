# Contributing to the LLM Island System

Thank you for wanting to improve this. The system is young — v0.1 — and
there are known gaps, edge cases not yet mapped, and scenarios not yet tested
against real codebases. Contributions that close those gaps are the most
valuable thing you can do.

---

## What This Project Is

The LLM Island System is a specification, not a tool. The primary artifact is
`LLMISLAND_SPEC.md`. Everything else — this guide, the README, the installation
guide — exists to help people understand and adopt that specification.

Contributions can be to:
- The spec itself (format changes, new fields, new scenarios, clarifications)
- The supporting documents (installation guide, README, this file)
- Tooling built on top of the spec (validators, visualizers, generators)
- Real-world experience reports (what worked, what didn't, what was missing)

---

## What We Most Need

In rough priority order:

**1. Real-world validation reports**
The spec was designed in a single session against one project (SUDOKILL, a
browser-based puzzle game in vanilla JS). It has not yet been stress-tested
against large Python codebases, Rust projects, mixed C/Assembly pipelines,
monorepos, or microservice architectures. If you adopt it and find something
that doesn't fit — a scenario the format can't express, a field that's always
wrong, a case where the propagation protocol breaks down — that report is
extremely valuable. Open an issue describing the scenario, what the format
produced, and what you needed instead.

**2. Edge case documentation**
Known gaps:
- Monorepos with shared modules across multiple projects
- Generated code (how do you island a file that is itself generated?)
- Test frameworks with global setup/teardown that affects all test islands
- Files that are simultaneously source and configuration (e.g. `package.json`)
- Circular dependencies that exist in real codebases regardless of whether
  they should

If you encounter an edge case and figure out a workable approach, document it.
Even if you are not sure the approach is right, sharing it starts the conversation.

**3. Tooling**
The spec is designed to be machine-readable. Things that would accelerate
adoption significantly:
- A validator that reads `.llmisland` files and reports validity errors
- A staleness checker that compares `last-verified` against file modification times
- A visualizer that renders the mainland as a dependency graph
- A generator that produces skeleton islands from source file analysis
- A query tool: "show me everything affected by changing this function"

Tooling should treat `LLMISLAND_SPEC.md` as its source of truth for validation
rules, not hardcode them. The spec will evolve and tooling should follow it.

**4. Spec clarifications and amendments**
If a field definition is ambiguous, if two parts of the spec contradict each
other, if an example is misleading, or if a rule has an obvious exception that
isn't handled — open an issue or a pull request.

**5. Translations**
The spec is currently in English. The intellectual origin (Akita's work) is
Brazilian Portuguese. If you can produce a high-quality translation that
preserves the precision of the field definitions, that broadens adoption.

---

## How to Contribute

### Reporting a problem or gap

Open an issue. Include:
- What you were trying to do (the scenario)
- What the spec told you to do (the format/rule you followed)
- What was wrong or missing about the result
- If you found a workaround, what it was

Do not open issues for "I wish the format looked different aesthetically."
The format is LLM-first. Human ergonomics are a secondary concern by design.
Open an issue if something is ambiguous, contradictory, or expressively
insufficient — not if it's visually unappealing.

### Proposing a spec change

Spec changes are the highest-stakes contribution. A bad change to the spec
propagates to every project using it.

Before opening a pull request for a spec change:
1. Open an issue first describing the problem and the proposed solution
2. Wait for discussion — especially from people who have applied the spec
   to real codebases
3. If there is rough consensus, open the PR

A spec change PR must include:
- The change to `LLMISLAND_SPEC.md`
- An update to the version history section at the bottom of the spec
- If the change adds a new field: an example showing the field in use
- If the change modifies an existing field: a note on backward compatibility
  (does it break existing islands? do old islands need migration?)
- If the change removes a field: a strong justification, because removal is
  a breaking change

### Contributing tooling

Tooling contributions are welcome as separate repositories. The system repo
does not need to host all tooling — it should link to notable tools.

If you build a tool:
- Document which version of the spec it targets
- Make the spec version a visible, queryable property of the tool
- When the spec changes, update the tool or mark it as targeting an older version

### Contributing real-world experience

The most useful contribution from someone who has adopted the system is a
write-up of their experience. What project? What language(s)? What phase did
they start from? What worked well? What required workarounds? What was missing?

These reports directly inform spec evolution. They are as valuable as code.

---

## Versioning and Backward Compatibility

The spec uses semantic versioning: `v<major>.<minor>`.

**Minor version** (`v0.1` → `v0.2`): additive changes only. New optional fields,
new scenarios documented, clarifications. Existing valid islands remain valid.

**Major version** (`v0.x` → `v1.0`, or `v1.x` → `v2.0`): breaking changes.
Fields renamed, removed, or given stricter validation. Existing islands may
need migration. Major version bumps require a migration guide.

While the spec is at `v0.x`, minor breaking changes are acceptable without a
major version bump — the system is still being validated. Once it reaches `v1.0`,
the stability contract tightens.

Every island file should eventually declare the spec version it was written
against. This is planned for a future minor version.

---

## Principles for Spec Evolution

Changes to the spec should be evaluated against these questions:

**Does this serve LLMs or humans?**
The format is LLM-first. If a proposed change makes the format easier for
humans to read but harder for LLMs to parse or generate, it should be
rejected or moved to tooling (e.g. a human-readable visualizer layer).

**Does this stay language agnostic?**
A change that only makes sense for one language family does not belong in the
core spec. It belongs in a language-specific extension or a best-practices
document for that language.

**Does this address a load-bearing gap?**
Changes should close gaps where the current format cannot express something
that matters for LLM reasoning. Cosmetic or organizational improvements to
things that already work are low priority.

**Does this preserve honest incompleteness?**
The system's integrity depends on `?` and `N/A` being first-class values.
Any change that makes it easier to hide uncertainty rather than declare it
should be rejected.

**Does this keep maintenance costs low?**
If a change makes islands take significantly longer to update, it will cause
phase 4 rot — islands that fall out of date because updating them is too
burdensome. The marginal value of any new field must be weighed against the
maintenance cost it adds.

---

## Attribution

The LLM Island System is heavily based on the ideas of Fábio Akita, from his
article *"AI Agents: Qual seria a melhor Linguagem de Programação para LLMs?"*
(akitaonrails.com, February 2026), which itself synthesized responses from
Claude and GPT on the question of what a programming language optimized for
LLMs rather than humans would look like.

Contributors to this specification are building on that foundation. If your
contribution draws on additional intellectual sources, cite them.

---

## A Note on This Being a Mid-Term Solution

This system is explicitly a bridge, not a destination. The long-term answer
to the problem it solves is a programming language or IR natively designed for
LLM authorship — where dependency graphs, effect declarations, provenance, and
formal contracts are language primitives, not companion files.

That language does not yet exist in production-ready form.

If you are working on something in that space — a language, a compiler, an IR
format — and you see the island system as a stepping stone toward it, we would
like to know. The island files are, in a sense, a proof of concept for what
those native primitives would need to express. The field definitions, the
validity rules, the propagation protocol — all of these could inform the design
of something more fundamental.

Contributions that explicitly connect the island system to longer-term research
in this direction are welcome and will be highlighted.
