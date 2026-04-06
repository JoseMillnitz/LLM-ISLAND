# Mode 2 — Connection-First
# Read this only when asked for an architectural overview with no specific task.

---

## PHILOSOPHY

Understand structure before behavior. Build the dependency graph from
imports and exports without reading function bodies. Create shallow islands
as placeholders. Deepen only when tasks later require it.

---

## PROCESS

1. Scan every source file for imports and exports only. Do not read bodies.
2. Build `connections.llmainland` CONNECTIONS section from this scan.
   Use `strength: ?` for all connections — you cannot rate strength without
   reading behavior.
3. Create shallow islands for all files (HEADER only, SYMBOLS marked as `?`).
   Use the shallow island template from EXAMPLES/example.llmisland.
4. Identify the critical path and note it in the mainland:

   Tier 1 — core and orchestration: entry points, state holders, domain logic
   Tier 2 — bridge: cross-language boundaries, external service adapters
   Tier 3 — leaf nodes: presentation, test files, configuration

5. Report the architecture to the human. Ask if any area needs deeper analysis.
6. Deepen islands only for areas the human identifies as priorities.

---

## SHALLOW ISLAND TEMPLATE

See `EXAMPLES/example.llmisland` for the full format.
In this mode, create islands with:

```
status:     partial
confidence: low
```

And mark SYMBOLS as deferred:

```
---SYMBOLS---
(deferred — populate when a task touches this file)
```

---

## WHAT TO DECLARE IN THE MAINLAND

After the scan, the mainland should have:
- `layers` populated with actual files assigned to each layer
- `load-order` if discoverable from the import graph
- `CONNECTIONS` with all observable file-to-file dependencies
- `architectural-rules` left as `?` — you cannot infer intent from structure alone
- `CONTRACTS` left empty — contracts require human input to declare

---

## WHEN DONE

- [ ] `connections.llmainland` created with full CONNECTIONS section
- [ ] Shallow islands created for all source files
- [ ] Critical path tiers identified and noted
- [ ] Human informed which areas have low confidence and need verification
- [ ] No bodies read unnecessarily — SYMBOLS sections deferred
