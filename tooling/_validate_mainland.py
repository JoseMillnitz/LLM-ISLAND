"""Mainland file format validation.

Package-private. Validates ``connections.llmainland`` for required
architecture fields, the bootstrap-mode enum, and verifies that
declared CONNECTION endpoints reference real islands. Skips
intentionally-external endpoints: parenthetical placeholders, dotfiles
(e.g. ``.llmpropstts``), and the mainland's own filename.

The public entry point ``validate_mainland`` is re-exported from
``tooling.validate``.
"""

from __future__ import annotations

import re
from pathlib import Path

from tooling._enums import (
    BOOTSTRAP_MODE_ENUM,
    REQUIRED_ARCHITECTURE_FIELDS,
    REQUIRED_MAINLAND_SECTIONS,
)
from tooling._validate_island import (
    block_for,
    enum_token,
    find_kv,
    section_lines,
)
from tooling.common import MAINLAND_NAME
from tooling.types import Finding


def validate_mainland(root: Path, island_paths: set[Path]) -> list[Finding]:
    path = root / MAINLAND_NAME
    if not path.exists():
        return []
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        findings.append(Finding(
            file=str(path), line=None, severity="error",
            code="encoding-error",
            message=f"Could not read as UTF-8: {exc}",
        ))
        return findings

    lines = text.splitlines()
    sections = section_lines(lines)
    for sec in REQUIRED_MAINLAND_SECTIONS:
        if sec not in sections:
            findings.append(Finding(
                file=str(path), line=None, severity="error",
                code="missing-mainland-section",
                message=f"Mainland missing section '{sec}'.",
            ))
    if any(f.code == "missing-mainland-section" for f in findings):
        return findings

    arch = block_for(sections, lines, "---ARCHITECTURE---") or []
    for field_name in REQUIRED_ARCHITECTURE_FIELDS:
        if find_kv(arch, field_name) is None:
            findings.append(Finding(
                file=str(path), line=None, severity="error",
                code="missing-architecture-field",
                message=f"ARCHITECTURE missing required field '{field_name}:'.",
            ))

    bm = find_kv(arch, "bootstrap-mode")
    if bm:
        token = enum_token(bm[1])
        if token and token not in BOOTSTRAP_MODE_ENUM:
            findings.append(Finding(
                file=str(path), line=bm[0], severity="error",
                code="bad-enum",
                message=f"bootstrap-mode invalid: '{token}'.",
            ))

    # CONNECTION endpoints must reference real islands or be exempt.
    connections_block = block_for(sections, lines, "---CONNECTIONS---") or []
    island_basenames = {p.name[:-len(".llmisland")] for p in island_paths}
    for ln, raw in connections_block:
        m = re.match(r"^\s*CONNECTION:\s*(\S+)\s*->\s*(\S+)", raw)
        if not m:
            continue
        for endpoint in (m.group(1), m.group(2)):
            # Skip non-file endpoints:
            #   "(dynamic)", "(external — ...)" — explicit untargeted
            #   ".llmpropstts" — runtime-only state file
            #   "connections.llmainland" — mainland is not islanded
            #   anything without a recognized extension
            if (endpoint.startswith("(")
                    or endpoint.startswith(".")
                    or endpoint == MAINLAND_NAME):
                continue
            base = Path(endpoint).name
            if base not in island_basenames and "." in base:
                findings.append(Finding(
                    file=str(path), line=ln, severity="warning",
                    code="connection-no-island",
                    message=(
                        f"CONNECTION endpoint '{endpoint}' has no "
                        f"matching island. Mark as external/dynamic if "
                        f"intentional."
                    ),
                ))
    return findings
