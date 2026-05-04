# Spec Module 10 - Structural Edge Cases and Cross-Language

Monorepos (workspace.llmainland), dynamic dependencies (dynamic-boundary), dependency cycles (cycle / cycle-note), expanded cross-language boundaries (mechanism, data-types, error-semantics, version-coupling), and the cross-language pipelines guidance. Read this when the project is a monorepo, has runtime-discovered edges, has known cycles, or crosses language boundaries.

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
