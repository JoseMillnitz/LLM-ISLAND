# LLM Island System — Installation Guide

How to introduce the LLM Island System into a project.

---

## Files in this system

Files that live in the **system repository** (not copied into your project):

| File | Purpose |
|------|---------|
| `README.md` | Overview. Read this first. |
| `LLMISLAND_SPEC.md` | Full format reference. Read when implementing or unsure. |
| `LLM_BOOT.md` | Paste at the start of every LLM session. |
| `INSTALATION_GUIDE.md` | This file. |
| `CONTRIBUTING.md` | How to contribute to the spec. |
| `MODES/MODE_INCREMENTAL.md` | Full detail for Mode 1 — the default mode. |
| `MODES/MODE_CONNECTION.md` | Full detail for Mode 2 — structural overview. |
| `MODES/MODE_FULLMAP.md` | Full detail for Mode 3 — full audit. |
| `SCENARIOS/SCENARIO_GREENFIELD.md` | New project with no existing code. |
| `SCENARIOS/SCENARIO_LEGACY.md` | Existing code, no islands yet. |
| `SCENARIOS/SCENARIO_ARCHAEOLOGY.md` | No authors available, intent must be inferred. |
| `SCENARIOS/SCENARIO_CROSSLANG.md` | Multiple languages or pipeline stages. |
| `EXAMPLES/example.llmisland` | Annotated island example — use as a template. |
| `EXAMPLES/example.llmainland` | Annotated mainland example — use as a template. |
| `EXAMPLES/example.llwasland` | Annotated wasland example — use as a template. |

Files that go into **your project**:

| File | Purpose |
|------|---------|
| `LLMISLAND_SPEC.md` | Copy from system repo. LLM reads this when it needs format details. |
| `LLM_BOOT.md` | Copy from system repo. Paste into every LLM session. |
| `MODES/` | Copy the whole folder. LLM_BOOT.md references these files. |
| `SCENARIOS/` | Copy the whole folder. LLM_BOOT.md references these files. |
| `EXAMPLES/` | Copy the whole folder. Mode and scenario files reference these. |
| `connections.llmainland` | Created as part of setup. One per project at the root. |
| `*.llmisland` | One per source file. Created as part of normal work. |
| `*.llwasland` | Optional. Created when HISTORICAL-DECISIONS exceeds 20 entries. |

---

## Setup in 3 steps

**Step 1 — Copy the system files into your project root.**

```
your-project/
  LLMISLAND_SPEC.md
  LLM_BOOT.md
  MODES/
    MODE_INCREMENTAL.md
    MODE_CONNECTION.md
    MODE_FULLMAP.md
  SCENARIOS/
    SCENARIO_GREENFIELD.md
    SCENARIO_LEGACY.md
    SCENARIO_ARCHAEOLOGY.md
    SCENARIO_CROSSLANG.md
  EXAMPLES/
    example.llmisland
    example.llmainland
    example.llwasland
```

**Step 2 — Identify your situation and read the right scenario file.**

| Situation | File to read |
|-----------|-------------|
| New project, no code yet | `SCENARIOS/SCENARIO_GREENFIELD.md` |
| Existing code, no islands yet | `SCENARIOS/SCENARIO_LEGACY.md` |
| Old code, no authors available | `SCENARIOS/SCENARIO_ARCHAEOLOGY.md` |
| Multiple languages or build pipeline | `SCENARIOS/SCENARIO_CROSSLANG.md` |

**Step 3 — Paste `LLM_BOOT.md` at the start of every LLM session.**

The boot file is a decision tree. It asks two questions: what is your situation,
and do islands already exist? Based on the answers, it points to exactly one mode
file and possibly one scenario file. The LLM reads only those files — not the
whole spec.

---

## Integrating with your LLM instruction file

If your project has a `CLAUDE.md`, `AGENTS.md`, or similar file, add:

```markdown
## LLM Island System

This project uses the LLM Island System (v0.2).

At the start of every session, paste the contents of `LLM_BOOT.md`.
It will tell you which mode to use and what to read.

When completing any task that modifies a source file:
1. Update the file's `.llmisland` — this is part of done, not optional.
2. Update `connections.llmainland` if any connection changed.
3. If the mainland changed, check all bound islands for staleness.
```

---

## Setup checklist

- [ ] System files copied into project root
- [ ] `connections.llmainland` created (even as MVM — see `EXAMPLES/example.llmainland`)
- [ ] `LLM_BOOT.md` in project root and referenced in LLM instruction file
- [ ] Scenario file identified and read
- [ ] First islands created for the most critical files

---

## What the file extensions mean

| Extension | Meaning |
|-----------|---------|
| `.llmisland` | Semantic companion to a source file |
| `.llmainland` | Architectural graph for the project (one file: `connections.llmainland`) |
| `.llwasland` | Archive of historical decisions — W is M upside down; these decisions *was* in land |

