# SPEC/ — Modular Specification

The normative specification is split across this directory so an LLM
session does not need to load the entire spec to find a single rule.
Read only the modules required by the task.

`../LLMISLAND_SPEC.md` is the routing entrypoint. It carries shared
content (CORE PRINCIPLES, FILE NAMING) and a topic table that maps
common tasks to the right module.

## Modules

| File | Topic |
|------|-------|
| [00_OVERVIEW.md](00_OVERVIEW.md) | Core principles and file naming. Trust model. Mental model. |
| [01_HEADER.md](01_HEADER.md) | `.llmisland` file structure and HEADER section field reference. |
| [02_SYMBOLS.md](02_SYMBOLS.md) | SYMBOLS section field reference plus FIELD DECISION CRITERIA for subjective fields. |
| [03_RISKS_MEMORY.md](03_RISKS_MEMORY.md) | RISKS and MEMORY sections (security, regression, platform, config; active constraints / historical / superseded). |
| [04_MAINLAND.md](04_MAINLAND.md) | `connections.llmainland` format plus the SELECTIVE READ PROTOCOL. |
| [05_VALIDITY.md](05_VALIDITY.md) | Validity rules, status progression, and the staleness detection obligation. |
| [06_TIERS.md](06_TIERS.md) | Update tiers A/B/C and the tier determination decision tree. |
| [07_PROPAGATION.md](07_PROPAGATION.md) | Propagation protocol and the `.llmpropstts` cascade state file. |

More modules land in v0.3-rc4: bootstrap and boot modes, maintenance
protocol, structural edge cases, cross-language pipelines, security
review gates, adoption and sustainability, and the quick reference /
anti-patterns block.

## Read order for new readers

1. `../LLMISLAND_SPEC.md` (router + CORE PRINCIPLES)
2. `00_OVERVIEW.md` if you need the trust model in detail
3. The task-specific module(s) — pick from the table above

Do not load every module. The split exists so you do not have to.
