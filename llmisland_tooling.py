#!/usr/bin/env python3
"""LLM Island System — CLI orchestrator.

Single entrypoint. Constructs the argparse tree and dispatches subcommands
into the ``tooling/`` package. Holds no business logic of its own; every
subcommand's behavior lives in its own module.

Subcommands ship across the v0.3-rc5 → v0.3-rc8 release candidate chain:
  rc5: skeleton (this file + tooling/common.py); no subcommands wired yet.
  rc6: check-stale, check-decay, spec
  rc7: prop-start, prop-done, prop-status, prop-finish, validate-rules
  rc8: validate

Run ``python llmisland_tooling.py --help`` to see the currently wired
subcommands.

Standard library only. Python 3.10+.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import Callable

from tooling.types import Report

VERSION = "0.3-rc5"


# ---------------------------------------------------------------------------
# Subcommand registry
# ---------------------------------------------------------------------------
#
# rc6+ register handlers here. A handler is called with the parsed argparse
# Namespace and returns either:
#   - an int exit code (for handlers that print directly), OR
#   - a Report (the dispatcher formats it as text or JSON).
#
# Architectural-rule AR-002 (see connections.llmainland) governs this
# return shape. Validate-rules and validate.py will enforce it once they
# land.

CommandHandler = Callable[[argparse.Namespace], "int | Report"]
COMMANDS: dict[str, CommandHandler] = {}


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construct the full argparse tree.

    Shared options (``--json``, ``--include-examples``) live on a parent
    parser so every subcommand inherits them — see architectural-rule
    AR-003. New subcommands attach via ``parents=[common]`` so they get
    the shared flags for free.
    """
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON instead of text.")
    common.add_argument("--include-examples", action="store_true",
                        help="Also scan EXAMPLES/. Skipped by default "
                             "because example islands are documentation.")

    parser = argparse.ArgumentParser(
        prog="llmisland_tooling",
        description=f"LLM Island System CLI orchestrator (v{VERSION}).",
    )
    parser.add_argument("--version", action="version",
                        version=f"llmisland_tooling {VERSION}")

    # Subcommands attach here in rc6+. The ``parents=[common]`` pattern
    # is locked: do not let a subcommand define its own --json.
    parser.add_subparsers(dest="command", required=False,
                          parser_class=argparse.ArgumentParser)
    parser._common_parent = common  # type: ignore[attr-defined]

    return parser


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def _emit(result: "int | Report", as_json: bool) -> int:
    """Format and print a handler's result. Return the resolved exit code."""
    if isinstance(result, int):
        return result
    if as_json:
        print(json.dumps({
            "command": result.command,
            "ok": result.ok,
            "findings": [asdict(f) for f in result.findings],
            "summary": result.summary,
        }, indent=2))
    else:
        status = "ok" if result.ok else "fail"
        print(f"[{status}] {result.command}")
        for f in result.findings:
            loc = f":{f.line}" if f.line else ""
            print(f"  {f.severity.upper():7s} {f.code:30s} {f.file}{loc} - {f.message}")
        if result.summary:
            print("  summary:")
            for k, v in result.summary.items():
                print(f"    {k}: {v}")
    return 0 if result.ok else 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    handler = COMMANDS.get(args.command)
    if handler is None:
        print(f"Unknown subcommand: {args.command}", file=sys.stderr)
        return 2

    return _emit(handler(args), getattr(args, "json", False))


if __name__ == "__main__":
    raise SystemExit(main())
