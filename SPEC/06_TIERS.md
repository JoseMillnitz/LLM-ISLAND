# Spec Module 06 - Update Tiers

Tier A / B / C update obligations proportional to change scope. The tier determination decision tree. Read this before updating an island so you know how much update is honest for the change you made.

---

## UPDATE TIERS

Not every code change requires a full island rewrite. The update obligation is
proportional to the change scope. Determine the tier before updating.

### TIER DETERMINATION

Ask these questions in order. Stop at the first YES.

  1. Did a function signature, export list, import list, or mainland connection
     change?
     → YES: Tier C (full update)

  2. Did the observable behavior, effects, or return semantics of any exported
     symbol change — even if the signature is the same?
     → YES: Tier B (symbol update)

  3. Is this an internal-only change — refactoring, bug fix, performance
     improvement — where exports, effects, and connections are unchanged?
     → YES: Tier A (timestamp update)

If uncertain which tier applies, choose the higher tier. Upgrading from A to B
is always safe. Downgrading from C to A risks silent staleness.

### TIER A — INTERNAL LOGIC ONLY

The change does not affect any exported symbol's signature, behavior, effects,
or any connection in the mainland.

Required updates:
  - last-verified → current version/date
  - status → verified (if it was stale)

Optional updates:
  - fragility-note, if the internal change resolves or introduces fragility
  - MEMORY entries, if the change resolves an active constraint or records a
    decision worth preserving

NOT required:
  - SYMBOLS section rewrite
  - Mainland connection updates
  - Downstream island checks

Examples:
  - Bug fix in internal helper, no change to exports
  - Performance optimization that does not change effects or return values
  - Refactoring internal variable names

### TIER B — EXPORT BEHAVIOR CHANGED

An exported symbol's behavior, effects, or return semantics changed, but the
function signatures and connection graph are the same.

Required updates:
  - last-verified → current version/date
  - status → verified
  - SYMBOLS section: update the affected symbol(s) only
  - RISKS section: update if the behavior change affects security or
    regression surfaces

NOT required:
  - Full island rewrite (untouched symbols stay as-is)
  - Mainland connection updates (graph unchanged)

Required propagation:
  - Check all called-by entries for the changed symbol
  - If a caller depends on the old behavior: update that caller's island

### TIER C — FULL UPDATE

Signatures, export lists, import lists, or mainland connections changed.

Required updates:
  - last-verified → current version/date
  - status → verified
  - Full island review: HEADER (exports, imports, depends-on), SYMBOLS, RISKS
  - Mainland: update affected CONNECTIONS
  - Mainland: check affected CONTRACTS
  - Downstream islands: update depends-on and called-by in all affected islands
  - MEMORY: record the change if it is architecturally significant

### WHEN A FULL UPDATE CANNOT BE COMPLETED HONESTLY

If a Tier C change is required but time pressure prevents a complete update:
  - Update what you can.
  - Set status: partial on the island — this is honest.
  - Do NOT set status: verified on an incomplete update.
  - A partial island is valid. A verified-but-wrong island is a lie.

A tiered update is a first-class valid outcome, not a shortcut. The system
explicitly permits narrow updates when the change scope is narrow.

---
