# Spec Module 07 - Propagation Protocol and Cascade State

The propagation protocol for code, mainland, file-create, and file-delete events. Plus the .llmpropstts cascade state file: format, tool commands, manual fallback, cascade threshold, and resume protocol. Read this when a change has downstream impact across multiple islands.

---

## PROPAGATION PROTOCOL

This is the discipline that keeps the system accurate over time.

WHEN CODE CHANGES:
  1. Determine the update tier (Tier A, B, or C — see UPDATE TIERS above)
  2. Apply the minimum required update for that tier
  3. Update last-verified to current version/date (all tiers)
  4. If Tier B or C: check if any exports changed signature, behavior, or effects
  5. If yes: check all depends-on entries and update their islands
  6. If a connection in the mainland is affected: update the connection (Tier C)
  7. If a contract is affected: update the contract and notify all islands-bound
  8. Before cascading updates to downstream islands, check the cascade size
     (see PROPAGATION STATE AND RESUME below). If the cascade exceeds the
     threshold, follow the large-impact protocol.

WHEN MAINLAND CHANGES:
  1. A mainland change is a signal — something architectural shifted
  2. Review all islands bound to the changed connection or contract
  3. Verify they are still accurate
  4. Update status on any that are now stale

WHEN ADDING A NEW FILE:
  1. Create the island before or alongside the file — not after
  2. Add its connections to the mainland immediately
  3. Update depends-on in any islands that will import it

WHEN DELETING A FILE:
  1. Remove its island
  2. Remove all connections referencing it from the mainland
  3. Update depends-on in islands that referenced it
  4. Add a SUPERSEDED entry to ARCHITECTURE-MEMORY explaining what replaced it

---

## PROPAGATION STATE AND RESUME

A cascade of updates across many islands can be interrupted — by output token
limits, session termination, or human decision. The system must make this
visible and resumable rather than leaving the graph in a contradictory state.

### PROPAGATION STATE FILE (.llmpropstts)

Propagation state is managed by a dedicated tool-generated file at the project
root, NOT stored in the mainland. This keeps the mainland clean and avoids
spending tokens writing transient operational state into a permanent
architectural document.

The file `.llmpropstts` is created and managed by the tooling
(see `llmisland_tooling.py`):

```
status: in-progress
started: 2026-04-19T15:00:00
origin: renderer.js (Tier C change)
pending:
  - game.js.llmisland
  - input.js.llmisland
  - ui.js.llmisland
completed:
  - data.js.llmisland
```

The LLM interacts via tool commands:
  llmisland_tooling prop-start --cascade <files>     creates .llmpropstts
  llmisland_tooling prop-done --island <file>        moves to completed
  llmisland_tooling prop-status                      reports progress
  llmisland_tooling prop-finish                      deletes .llmpropstts

WHEN NO TOOLING EXISTS:
  If the tool is unavailable, the LLM may write `.llmpropstts` manually.
  The format above is fixed — do not get creative with field names. When
  the cascade completes, delete the file.

### CASCADE PROTOCOL

When a Tier B or Tier C change triggers downstream island updates:

  1. Count the islands that need updating (the cascade size).
  2. If cascade size <= 10: proceed normally. Update all affected islands.
     No `.llmpropstts` is needed.
  3. If cascade size > 10: this is a LARGE-IMPACT CHANGE.
     a. Create `.llmpropstts` with status: in-progress and the full pending
        list (use the tool, or write it manually).
     b. Surface to the human: "This change affects [N] islands. Proceed
        with full cascade, or pause after the current batch?"
     c. Update islands in batches. After each batch, mark completed entries
        and update `.llmpropstts`.
     d. If the session ends before completion: `.llmpropstts` preserves
        the remaining work for the next session.
     e. When all islands are updated: delete `.llmpropstts`.

The threshold of 10 islands is a guideline. Projects may adjust it, but the
protocol (count, warn, batch, resume) applies regardless of the chosen number.

### PROPAGATION RESUME

At the start of any session, before normal task classification, check
whether `.llmpropstts` exists.

  1. If `.llmpropstts` exists with status: in-progress or failed:
     a. Read the pending list to see what remains.
     b. Resume the cascade BEFORE starting any new task.
        The graph is in a contradictory state — some islands describe the
        old contract, others the new one. New work on top of this state
        compounds the inconsistency.
     c. If the remaining cascade is too large for this session: update as
        many as possible and update `.llmpropstts`.
     d. When all pending islands are resolved: delete `.llmpropstts`.
  2. If `.llmpropstts` does not exist: proceed to the declared task normally.

### CASCADES BEYOND LLM CAPACITY

Some cascades are too large for any single LLM session. When a cascade affects
more islands than can be updated within the session's output limits:
  - Update what you can, leaving `.llmpropstts` in place.
  - Suggest to the human that tooling-assisted propagation may be appropriate
    for changes of this magnitude.
  - Do NOT attempt to complete a cascade that will be truncated mid-island.
    A half-updated island is worse than a clearly-marked pending one.

---
