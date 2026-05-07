"""Format validator subcommand.

One subcommand: ``validate``. Walks every ``*.llmisland`` under the
project root and validates structure, required fields, enum values,
and the structural rules from ``SPEC/05_VALIDITY.md``. Also validates
``connections.llmainland`` if present.

This module is the orchestration shell. The actual checks live in
package-private modules to keep each file under the project's
file-size rule:

* ``tooling/_enums.py``             — ENUM sets and required-field lists
* ``tooling/_validate_island.py``   — per-island validation
* ``tooling/_validate_mainland.py`` — mainland validation

Format-only by design (see ``tooling/validate.py.llmisland`` AC-001):
this catches missing fields and bad enums, not whether a rationale is
honest or whether security review actually happened.

Standard library only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tooling._validate_island import validate_island
from tooling._validate_mainland import validate_mainland
from tooling.common import iter_islands
from tooling.types import Finding, Report


def cmd_validate(args: argparse.Namespace) -> Report:
    root = Path(args.directory).resolve()
    if not root.exists():
        return Report(
            command="validate", ok=False,
            findings=[Finding(
                file=str(root), line=None, severity="error",
                code="root-not-found",
                message=f"Root does not exist: {root}",
            )],
            summary={},
        )

    all_findings: list[Finding] = []
    island_paths: set[Path] = set()
    counts = {"islands": 0, "errors": 0, "warnings": 0, "infos": 0}

    for island in iter_islands(root, args.include_examples):
        island_paths.add(island)
        counts["islands"] += 1
        all_findings.extend(validate_island(island))

    if not args.no_mainland:
        all_findings.extend(validate_mainland(root, island_paths))

    severity_counter = {"error": "errors", "warning": "warnings", "info": "infos"}
    for f in all_findings:
        counts[severity_counter.get(f.severity, "infos")] += 1

    ok = counts["errors"] == 0
    return Report(command="validate", ok=ok,
                  findings=all_findings, summary=counts)


def setup_validate(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "directory", nargs="?", default=".",
        help="Project root to scan recursively. Defaults to the current dir.",
    )
    parser.add_argument(
        "--no-mainland", action="store_true",
        help="Skip validating connections.llmainland even if present.",
    )


SUBCOMMANDS = {
    "validate": (
        setup_validate, cmd_validate,
        "Validate island and mainland format against the spec "
        "(SPEC/05_VALIDITY.md).",
    ),
}
