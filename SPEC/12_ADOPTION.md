# Spec Module 12 - Adoption and Sustainability

Minimum viable adoption floor, mainland consistency role, abandonment protocol, and how to attach island maintenance to existing process checkpoints. Read this before committing your project to the system, or when deciding how to wind it down.

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
