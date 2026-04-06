# Mode 3 — Full Mapping
# Read this only when explicitly asked for a full audit or complete island generation.
# This mode is expensive. Do not use it by default.

---

## PHILOSOPHY

Complete semantic mapping of the entire system. Every file read, every island
fully populated, every contract declared. Used for audits, pre-refactoring
planning, and archaeological analysis.

---

## WHEN TO USE THIS MODE

Only when one of these is explicitly true:
- The human asked for a "full audit" or "full mapping pass"
- Pre-refactoring planning on a system with no existing islands
- Archaeological analysis (combine with SCENARIOS/SCENARIO_ARCHAEOLOGY.md)
- The human said "generate all islands"

Do NOT use this mode for normal development sessions.
Do NOT use this mode just because the codebase is unfamiliar.
Mode 1 (Incremental) handles unfamiliar codebases better and cheaper.

---

## PROCESS

Phase 1 — Read all source files and tests.
Phase 2 — Generate all islands with full HEADER, SYMBOLS, RISKS, and MEMORY.
  Mark all inferences with `confidence: low` and `evidence: inferred-from-*`.
  Use `?` for every field that cannot be determined from code alone.
  Do not fabricate certainty.
Phase 3 — Generate the full mainland.
  CONNECTIONS from observable imports/exports.
  CONTRACTS: leave as `?` — declare them with human in Phase 4.
  architectural-rules: leave as `?` — declare them with human in Phase 4.
Phase 4 — Verification pass with human.
  Present targeted questions for low-confidence fields.
  Ask: "what invariants here cause silent failures when broken?"
  Those answers become CONTRACT entries.
  Ask: "what architectural rules must never be violated?"
  Those answers become architectural-rules entries.
Phase 5 — Promote verified islands from `generated` to `verified`.

---

## QUALITY BAR FOR THIS MODE

In Mode 3, shallow islands are not acceptable. If you are doing a full pass,
populate every section. If a file is genuinely unknowable without human input,
mark it `status: inferred, confidence: low` — but do not skip the SYMBOLS section.
Make your best inference and declare it as such.

---

## WHEN DONE

- [ ] Islands exist for every source file
- [ ] All islands have fully populated HEADER, SYMBOLS, RISKS, MEMORY
- [ ] Mainland has full CONNECTIONS section
- [ ] Verification pass completed with human
- [ ] CONTRACTS declared for load-bearing invariants
- [ ] architectural-rules declared
- [ ] All `?` fields that could not be resolved are documented as targeted
       questions for the next human session
