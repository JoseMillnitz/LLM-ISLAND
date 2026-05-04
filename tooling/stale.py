"""Staleness and confidence-decay checks.

Two subcommands:

* ``check-stale`` compares each island's ``last-verified`` against the
  modification timestamp of its companion source file. Islands whose
  source was modified after the recorded verification date are flagged
  STALE. This is the hard dependency that ``SPEC/05_VALIDITY.md`` calls
  for in any project where humans edit source files outside LLM sessions.

* ``check-decay`` operationalizes ``confidence-review-due``: when the
  declared review threshold (a date or a version) has been reached and
  the island has not been re-reviewed, the field's confidence is
  considered decayed by one level. The check flags islands that need
  the downgrade.

Standard library only.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from tooling.common import (
    is_example_path,
    iter_islands,
    parse_last_verified,
    read_header_field,
    source_for_island,
)
from tooling.types import Finding, Report


# ---------------------------------------------------------------------------
# check-stale
# ---------------------------------------------------------------------------

def cmd_check_stale(args: argparse.Namespace) -> Report:
    root = Path(args.directory).resolve()
    findings: list[Finding] = []
    counts = {"fresh": 0, "stale": 0, "missing-source": 0,
              "invalid-last-verified": 0, "no-verification-date": 0}

    if not root.exists():
        findings.append(Finding(
            file=str(root), line=None, severity="error",
            code="root-not-found",
            message=f"Root does not exist: {root}",
        ))
        return Report(command="check-stale", ok=False, findings=findings, summary=counts)

    for island in iter_islands(root, args.include_examples):
        last_verified_raw = read_header_field(island, "last-verified")
        status = read_header_field(island, "status")
        verified_date = parse_last_verified(last_verified_raw)
        source = source_for_island(island)

        if not source.exists():
            severity = "warning" if is_example_path(island) else "error"
            findings.append(Finding(
                file=str(island), line=None, severity=severity,
                code="missing-source",
                message=f"Companion source not found: {source}",
            ))
            counts["missing-source"] += 1
            continue

        if status == "verified" and verified_date is None:
            findings.append(Finding(
                file=str(island), line=None, severity="error",
                code="invalid-last-verified",
                message="status: verified but last-verified is missing or unparseable.",
            ))
            counts["invalid-last-verified"] += 1
            continue

        if verified_date is None:
            findings.append(Finding(
                file=str(island), line=None, severity="info",
                code="no-verification-date",
                message="No usable last-verified date; cannot check freshness.",
            ))
            counts["no-verification-date"] += 1
            continue

        source_mtime = date.fromtimestamp(source.stat().st_mtime)
        if source_mtime > verified_date:
            findings.append(Finding(
                file=str(island), line=None, severity="warning",
                code="stale",
                message=(
                    f"Source modified {source_mtime.isoformat()} "
                    f"after last-verified {verified_date.isoformat()}."
                ),
            ))
            counts["stale"] += 1
        else:
            counts["fresh"] += 1

    ok = (counts["stale"] == 0
          and counts["invalid-last-verified"] == 0
          and counts["missing-source"] == 0)
    return Report(command="check-stale", ok=ok, findings=findings, summary=counts)


def setup_check_stale(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "directory", nargs="?", default=".",
        help="Directory to scan recursively. Defaults to the current dir.",
    )


# ---------------------------------------------------------------------------
# check-decay
# ---------------------------------------------------------------------------

def cmd_check_decay(args: argparse.Namespace) -> Report:
    root = Path(args.directory).resolve()
    today = date.today()
    findings: list[Finding] = []
    counts = {"current": 0, "decay-due": 0, "missing-due": 0, "untracked": 0}

    if not root.exists():
        findings.append(Finding(
            file=str(root), line=None, severity="error",
            code="root-not-found",
            message=f"Root does not exist: {root}",
        ))
        return Report(command="check-decay", ok=False, findings=findings, summary=counts)

    for island in iter_islands(root, args.include_examples):
        due_raw = read_header_field(island, "confidence-review-due")
        status = read_header_field(island, "status")
        confidence = read_header_field(island, "confidence")

        if not due_raw or due_raw in {"?", "N/A"}:
            # Inferred or generated islands at medium/low confidence really
            # should set this; flag the absence as a recommendation.
            if status in {"inferred", "generated"} and confidence in {"medium", "low"}:
                findings.append(Finding(
                    file=str(island), line=None, severity="warning",
                    code="missing-confidence-review-due",
                    message=(
                        f"status: {status}, confidence: {confidence} "
                        f"but confidence-review-due is not set. Recommended "
                        f"for inferred/generated islands."
                    ),
                ))
                counts["missing-due"] += 1
            else:
                counts["untracked"] += 1
            continue

        due_date = parse_last_verified(due_raw)
        if due_date is not None:
            if today >= due_date:
                findings.append(Finding(
                    file=str(island), line=None, severity="warning",
                    code="decay-due",
                    message=(
                        f"confidence-review-due {due_date.isoformat()} reached "
                        f"on {today.isoformat()}; downgrade confidence by one level."
                    ),
                ))
                counts["decay-due"] += 1
            else:
                counts["current"] += 1
            continue

        # Could not parse as a date; try as a version string if --version was given.
        if args.version:
            due_v = due_raw.lstrip("v").strip()
            cur_v = args.version.lstrip("v").strip()
            if cur_v >= due_v:
                findings.append(Finding(
                    file=str(island), line=None, severity="warning",
                    code="decay-due-version",
                    message=(
                        f"confidence-review-due {due_raw} reached at version "
                        f"{args.version}; downgrade confidence by one level."
                    ),
                ))
                counts["decay-due"] += 1
            else:
                counts["current"] += 1
        else:
            counts["untracked"] += 1

    ok = counts["decay-due"] == 0
    return Report(command="check-decay", ok=ok, findings=findings, summary=counts)


def setup_check_decay(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "directory", nargs="?", default=".",
        help="Directory to scan recursively. Defaults to the current dir.",
    )
    parser.add_argument(
        "--version", default=None, metavar="VERSION",
        help="Current project version (e.g. v0.4) for version-threshold checks.",
    )


# ---------------------------------------------------------------------------
# Subcommand registry (consumed by llmisland_tooling.py)
# ---------------------------------------------------------------------------

SUBCOMMANDS = {
    "check-stale": (
        setup_check_stale,
        cmd_check_stale,
        "Find islands whose source was modified after their last-verified date.",
    ),
    "check-decay": (
        setup_check_decay,
        cmd_check_decay,
        "Find islands whose confidence-review-due date or version has passed.",
    ),
}
