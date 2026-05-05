"""Propagation cascade state management.

Four subcommands managing the ``.llmpropstts`` file at the project root:

* ``prop-start --cascade <files>``  - create the cascade state file with
  the listed islands as pending; refuses to clobber an existing cascade.
* ``prop-done --island <file>``     - move one island from pending to
  completed; deletes ``.llmpropstts`` if the pending list becomes empty.
* ``prop-status``                   - print current state and progress.
* ``prop-finish [--force]``         - delete ``.llmpropstts`` (refuses
  if pending islands remain unless ``--force`` is set).

The on-disk format is fixed (see SPEC/07_PROPAGATION.md). This module
is the canonical writer; manual edits work but are discouraged because
they bypass the auto-finish behavior of ``prop-done``.

Standard library only.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from tooling.common import find_project_root
from tooling.types import Finding, Report

PROPSTTS_FILE = ".llmpropstts"


# ---------------------------------------------------------------------------
# Read / write helpers
# ---------------------------------------------------------------------------

def _read(root: Path) -> dict | None:
    """Parse ``.llmpropstts`` into a dict, or None if absent."""
    path = root / PROPSTTS_FILE
    if not path.exists():
        return None

    data: dict = {"status": "unknown", "started": "", "origin": "",
                  "pending": [], "completed": []}
    current_list: str | None = None

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("status:"):
            data["status"] = stripped.split(":", 1)[1].strip()
            current_list = None
        elif stripped.startswith("started:"):
            data["started"] = stripped.split(":", 1)[1].strip()
            current_list = None
        elif stripped.startswith("origin:"):
            data["origin"] = stripped.split(":", 1)[1].strip()
            current_list = None
        elif stripped == "pending:":
            current_list = "pending"
        elif stripped == "completed:":
            current_list = "completed"
        elif stripped.startswith("- ") and current_list is not None:
            item = stripped[2:].strip()
            if item and item != "none":
                data[current_list].append(item)

    return data


def _write(root: Path, data: dict) -> None:
    lines = [
        f"status: {data.get('status', 'in-progress')}",
        f"started: {data.get('started', '')}",
        f"origin: {data.get('origin', '?')}",
        "pending:",
    ]
    pending = data.get("pending", [])
    if pending:
        lines.extend(f"  - {item}" for item in pending)
    else:
        lines.append("  - none")
    lines.append("completed:")
    completed = data.get("completed", [])
    if completed:
        lines.extend(f"  - {item}" for item in completed)
    else:
        lines.append("  - none")

    (root / PROPSTTS_FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalize_island(name: str) -> str:
    """Append ``.llmisland`` suffix if missing. Tolerates both forms."""
    if name.endswith(".llmisland"):
        return name
    return name + ".llmisland"


# ---------------------------------------------------------------------------
# prop-start
# ---------------------------------------------------------------------------

def cmd_prop_start(args: argparse.Namespace) -> Report:
    root = find_project_root(Path.cwd())
    findings: list[Finding] = []
    summary = {"created": False, "pending_count": 0,
               "file": str(root / PROPSTTS_FILE)}

    existing = _read(root)
    if existing is not None:
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="error",
            code="cascade-already-open",
            message=(
                f"{PROPSTTS_FILE} already exists with status: "
                f"{existing.get('status')}. Run prop-status to inspect, "
                f"prop-finish [--force] to clear it."
            ),
        ))
        summary["existing_status"] = existing.get("status", "unknown")
        return Report(command="prop-start", ok=False,
                      findings=findings, summary=summary)

    islands = [_normalize_island(name) for name in args.cascade]
    data = {
        "status": "in-progress",
        "started": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "origin": args.origin if args.origin else "?",
        "pending": islands,
        "completed": [],
    }
    _write(root, data)

    summary["created"] = True
    summary["pending_count"] = len(islands)
    summary["pending"] = islands
    summary["origin"] = data["origin"]
    findings.append(Finding(
        file=str(root / PROPSTTS_FILE), line=None, severity="info",
        code="cascade-created",
        message=f"Cascade created with {len(islands)} pending island(s).",
    ))
    return Report(command="prop-start", ok=True, findings=findings, summary=summary)


def setup_prop_start(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--cascade", nargs="+", required=True, metavar="FILE",
        help="Source or island filenames to include as pending.",
    )
    parser.add_argument(
        "--origin", default=None,
        help="Description of what triggered the cascade "
             "(e.g. 'renderer.js Tier C change').",
    )


# ---------------------------------------------------------------------------
# prop-done
# ---------------------------------------------------------------------------

def cmd_prop_done(args: argparse.Namespace) -> Report:
    root = find_project_root(Path.cwd())
    findings: list[Finding] = []
    summary = {"file": str(root / PROPSTTS_FILE)}

    data = _read(root)
    if data is None:
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="error",
            code="no-cascade",
            message=f"{PROPSTTS_FILE} does not exist; no cascade to update.",
        ))
        return Report(command="prop-done", ok=False, findings=findings, summary=summary)

    island = _normalize_island(args.island)

    if island in data["completed"]:
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="info",
            code="already-done",
            message=f"{island} is already in completed list.",
        ))
        summary["pending_remaining"] = len(data["pending"])
        return Report(command="prop-done", ok=True, findings=findings, summary=summary)

    if island not in data["pending"]:
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="error",
            code="not-in-pending",
            message=(
                f"{island} not found in pending list. "
                f"Pending: {data['pending']}"
            ),
        ))
        summary["pending"] = data["pending"]
        return Report(command="prop-done", ok=False, findings=findings, summary=summary)

    data["pending"].remove(island)
    data["completed"].append(island)

    if not data["pending"]:
        (root / PROPSTTS_FILE).unlink()
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="info",
            code="cascade-complete",
            message=f"{island} done; cascade complete; {PROPSTTS_FILE} deleted.",
        ))
        summary["cascade_complete"] = True
        summary["pending_remaining"] = 0
        return Report(command="prop-done", ok=True, findings=findings, summary=summary)

    _write(root, data)
    findings.append(Finding(
        file=str(root / PROPSTTS_FILE), line=None, severity="info",
        code="island-marked-done",
        message=(
            f"{island} done. "
            f"{len(data['pending'])} pending, "
            f"{len(data['completed'])} completed."
        ),
    ))
    summary["pending_remaining"] = len(data["pending"])
    summary["completed_count"] = len(data["completed"])
    return Report(command="prop-done", ok=True, findings=findings, summary=summary)


def setup_prop_done(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--island", required=True, metavar="ISLAND",
        help="Island filename (e.g. game.js.llmisland; "
             "trailing suffix is added automatically if missing).",
    )


# ---------------------------------------------------------------------------
# prop-status
# ---------------------------------------------------------------------------

def cmd_prop_status(args: argparse.Namespace) -> Report:
    root = find_project_root(Path.cwd())
    findings: list[Finding] = []

    data = _read(root)
    if data is None:
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="info",
            code="no-cascade",
            message=f"{PROPSTTS_FILE} does not exist. No cascade in progress.",
        ))
        return Report(command="prop-status", ok=True, findings=findings,
                      summary={"cascade_open": False})

    pending = data["pending"]
    completed = data["completed"]
    total = len(pending) + len(completed)

    summary = {
        "cascade_open": True,
        "status": data["status"],
        "started": data["started"],
        "origin": data["origin"],
        "progress": f"{len(completed)}/{total}",
        "pending_count": len(pending),
        "completed_count": len(completed),
        "pending": pending,
        "completed": completed,
    }
    findings.append(Finding(
        file=str(root / PROPSTTS_FILE), line=None, severity="info",
        code="cascade-status",
        message=(
            f"status: {data['status']}; progress: "
            f"{len(completed)}/{total}; origin: {data['origin']}"
        ),
    ))
    return Report(command="prop-status", ok=True, findings=findings, summary=summary)


def setup_prop_status(parser: argparse.ArgumentParser) -> None:
    # No flags beyond the common ones.
    pass


# ---------------------------------------------------------------------------
# prop-finish
# ---------------------------------------------------------------------------

def cmd_prop_finish(args: argparse.Namespace) -> Report:
    root = find_project_root(Path.cwd())
    findings: list[Finding] = []
    summary = {"file": str(root / PROPSTTS_FILE), "deleted": False}

    if not (root / PROPSTTS_FILE).exists():
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="info",
            code="no-cascade",
            message=f"{PROPSTTS_FILE} does not exist; nothing to clean up.",
        ))
        return Report(command="prop-finish", ok=True, findings=findings, summary=summary)

    data = _read(root)
    pending = data["pending"] if data else []
    if pending and not args.force:
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="warning",
            code="pending-remain",
            message=(
                f"{len(pending)} island(s) still pending: {pending}. "
                f"Re-run with --force to delete anyway, or use prop-done "
                f"to mark them complete."
            ),
        ))
        summary["pending_remaining"] = len(pending)
        return Report(command="prop-finish", ok=False, findings=findings, summary=summary)

    (root / PROPSTTS_FILE).unlink()
    summary["deleted"] = True
    if pending:
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="warning",
            code="cascade-force-closed",
            message=(
                f"{len(pending)} pending island(s) abandoned at "
                f"--force close: {pending}"
            ),
        ))
        summary["abandoned_pending"] = pending
    else:
        findings.append(Finding(
            file=str(root / PROPSTTS_FILE), line=None, severity="info",
            code="cascade-closed",
            message=f"{PROPSTTS_FILE} deleted.",
        ))
    return Report(command="prop-finish", ok=True, findings=findings, summary=summary)


def setup_prop_finish(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--force", action="store_true",
        help="Delete .llmpropstts even if pending islands remain. "
             "Marks the cascade as abandoned.",
    )


# ---------------------------------------------------------------------------
# Subcommand registry
# ---------------------------------------------------------------------------

SUBCOMMANDS = {
    "prop-start": (
        setup_prop_start, cmd_prop_start,
        "Create .llmpropstts with the given islands as pending cascade.",
    ),
    "prop-done": (
        setup_prop_done, cmd_prop_done,
        "Mark an island as completed in the current cascade. "
        "Auto-deletes .llmpropstts when pending becomes empty.",
    ),
    "prop-status": (
        setup_prop_status, cmd_prop_status,
        "Show current cascade progress from .llmpropstts.",
    ),
    "prop-finish": (
        setup_prop_finish, cmd_prop_finish,
        "Delete .llmpropstts. Refuses if pending remain unless --force.",
    ),
}
