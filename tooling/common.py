"""Shared filesystem and parsing helpers for the tooling/ package.

Anything used by more than one subcommand lives here OR in
``tooling/types.py`` (for the ``Finding`` / ``Report`` dataclasses).
Subcommand modules stay focused on their own logic.

Standard library only.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Iterable

ISLAND_SUFFIX = ".llmisland"
MAINLAND_NAME = "connections.llmainland"


def is_example_path(path: Path) -> bool:
    """True iff ``path`` is inside a top-level ``EXAMPLES/`` directory.

    Example islands ship as documentation; subcommands skip them by
    default and treat their failures as warnings rather than errors.
    """
    return "EXAMPLES" in path.parts


def iter_islands(root: Path, include_examples: bool) -> Iterable[Path]:
    """Yield every ``*.llmisland`` file under ``root``.

    Skips ``EXAMPLES/`` paths unless ``include_examples`` is True.
    """
    for path in root.rglob(f"*{ISLAND_SUFFIX}"):
        if not include_examples and is_example_path(path):
            continue
        yield path


def source_for_island(island_path: Path) -> Path:
    """Return the companion source path for an island.

    ``renderer.js.llmisland`` -> ``renderer.js``
    """
    source_name = island_path.name[: -len(ISLAND_SUFFIX)]
    return island_path.with_name(source_name)


def find_project_root(start: Path) -> Path:
    """Walk up from ``start`` looking for ``connections.llmainland``.

    Returns the directory that contains it. If none is found, returns
    ``start`` resolved (subcommands then operate on the cwd by default).
    """
    current = start.resolve()
    while True:
        if (current / MAINLAND_NAME).exists():
            return current
        parent = current.parent
        if parent == current:
            return start.resolve()
        current = parent


def read_header_field(path: Path, field_name: str) -> str | None:
    """Read the first ``field_name: value`` line from an island file.

    Intentionally shallow: only matches top-level header fields. Nested
    fields like ``effects.io`` need section-aware parsing and belong in
    ``validate.py`` (rc8). Returns None if the file cannot be read or
    the field is absent.
    """
    prefix = f"{field_name}:"
    try:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if line.startswith(prefix):
                return line[len(prefix):].strip()
    except OSError:
        return None
    return None


def parse_last_verified(value: str | None) -> date | None:
    """Extract a ``YYYY-MM-DD`` date from a ``last-verified`` string.

    Accepts bare dates and version-prefixed dates:
      ``2024-03-15``           -> 2024-03-15
      ``v7-2024-03-15``        -> 2024-03-15
      ``v0.3-rc5-2026-05-03``  -> 2026-05-03

    Returns None for ``?``, ``N/A``, missing input, or unparseable
    strings. Takes the first ``YYYY-MM-DD`` substring found.
    """
    if not value or value in {"?", "N/A"}:
        return None
    match = re.search(r"(\d{4}-\d{2}-\d{2})", value)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None
