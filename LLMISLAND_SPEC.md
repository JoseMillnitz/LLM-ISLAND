# LLM Island System — Specification v0.3-rc8
# A semantic companion layer for codebases, optimized for LLM reasoning

For background — what this system is, what it is not, and the
intellectual origin (Akita's work on LLM-optimal language design) —
see `README.md`.

For the dated changelog of every release, see `VERSION_HISTORY.md`.

This file is the routing entrypoint for the spec. Every operational
section now lives under `SPEC/`. Read only the modules your task
requires; the table below maps tasks to modules.

The `SPEC/` directory router is at `SPEC/README.md`.

---

## TOPIC TABLE

| If your task is | Read |
|-----------------|------|
| Understand the trust model and core principles | `SPEC/00_OVERVIEW.md` |
| Create or edit an island file | `SPEC/01_HEADER.md` (HEADER) + `SPEC/02_SYMBOLS.md` (SYMBOLS) + `SPEC/03_RISKS_MEMORY.md` (RISKS, MEMORY) |
| Assess a subjective field (confidence, fragility, severity, strength, break-impact) | `SPEC/02_SYMBOLS.md` — FIELD DECISION CRITERIA |
| Edit `connections.llmainland` or do selective mainland reads | `SPEC/04_MAINLAND.md` |
| Validate an island (rules, status, staleness) | `SPEC/05_VALIDITY.md` |
| Decide what update tier a change requires | `SPEC/06_TIERS.md` |
| Resume or start a propagation cascade | `SPEC/07_PROPAGATION.md` |
| Bootstrap a new or legacy project, or pick a boot mode | `SPEC/08_BOOTSTRAP.md` |
| Understand maintenance obligations and memory management | `SPEC/09_MAINTENANCE.md` |
| Handle monorepo / dynamic deps / cycles / cross-language | `SPEC/10_EDGE_CASES.md` |
| Touch a security-sensitive file | `SPEC/11_SECURITY.md` |
| Adopt the system in a project, or wind it down honestly | `SPEC/12_ADOPTION.md` |
| Onboard, scenario-by-scenario procedures, anti-patterns | `SPEC/13_REFERENCE.md` |

---

## VERSION HISTORY

The dated changelog moved to `VERSION_HISTORY.md`. Read that file for
the per-release rationale, the source attributions (Gemini / Grok /
Mistral / Codex / Antigravity), and the issue-to-release mapping.

---

END OF SPEC v0.3-rc8
