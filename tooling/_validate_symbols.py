"""Per-SYMBOL validation for ``---SYMBOLS---`` entries.

Package-private. Pulled out of ``_validate_island.py`` so each file
stays under the project's file-size rule. Validates one SYMBOL block
at a time: required fields (kind, pure, total, latency-budget,
fragility), enum tokens, fragility-note when fragility >= medium,
business-rule for test-layer symbols, and the effects/tests subfield
completeness rules from ``SPEC/02_SYMBOLS.md``.
"""

from __future__ import annotations

import re
from pathlib import Path

from tooling._enums import BOOL_ENUM, FRAGILITY_ENUM, SYMBOL_KIND_ENUM
from tooling.types import Finding


def iter_symbol_blocks(symbols_block: list[tuple[int, str]]) -> list[tuple[int, list[tuple[int, str]]]]:
    """Split the SYMBOLS section into per-symbol blocks. Each block starts
    at a ``SYMBOL: <name>`` line and runs until the next one (or the end).
    """
    starts = [(ln, txt) for ln, txt in symbols_block
              if re.match(r"^\s*SYMBOL:\s*\S+", txt)]
    if not starts:
        return []
    indices = [ln for ln, _ in starts]
    out: list[tuple[int, list[tuple[int, str]]]] = []
    for i, start in enumerate(indices):
        end = indices[i + 1] if i + 1 < len(indices) else None
        block = [(ln, txt) for ln, txt in symbols_block
                 if ln >= start and (end is None or ln < end)]
        out.append((start, block))
    return out


def validate_one_symbol(
    start: int, block: list[tuple[int, str]], path: Path, layer: str | None,
    enum_token, findings: list[Finding],
) -> None:
    """Validate one SYMBOL entry. ``enum_token`` is injected from
    ``_validate_island`` to avoid a circular import."""
    def get(pat: str) -> str | None:
        for _, txt in block:
            if txt.lstrip().startswith("#"):
                continue
            m = re.match(pat, txt.strip())
            if m:
                return m.group(1).strip()
        return None

    requirements = [
        ("kind", r"^kind:\s*(.+)$", SYMBOL_KIND_ENUM),
        ("pure", r"^pure:\s*(.+)$", BOOL_ENUM),
        ("total", r"^total:\s*(.+)$", BOOL_ENUM),
        ("fragility", r"^fragility:\s*(\S+)", FRAGILITY_ENUM),
    ]
    values: dict[str, str | None] = {}
    for name, pattern, allowed in requirements:
        value = get(pattern)
        token = enum_token(value) if value else None
        values[name] = token
        if value is None:
            findings.append(Finding(
                file=str(path), line=start, severity="error",
                code=f"missing-{name}",
                message=f"SYMBOL entry missing '{name}:'.",
            ))
        elif allowed and token not in allowed:
            findings.append(Finding(
                file=str(path), line=start, severity="error",
                code="bad-enum",
                message=f"SYMBOL {name}: invalid value '{token}'.",
            ))

    if get(r"^latency-budget:\s*(.+)$") is None:
        findings.append(Finding(
            file=str(path), line=start, severity="error",
            code="missing-latency",
            message="SYMBOL entry missing 'latency-budget:'.",
        ))

    if values["fragility"] in {"medium", "high"}:
        note = get(r"^fragility-note:\s*(.+)$")
        if not note or note in {"N/A", "?", ""}:
            findings.append(Finding(
                file=str(path), line=start, severity="error",
                code="missing-fragility-note",
                message="fragility >= medium but fragility-note missing or N/A.",
            ))

    if layer == "test":
        rule = get(r"^business-rule:\s*(.+)$")
        if not rule or rule in {"N/A", "?", ""}:
            findings.append(Finding(
                file=str(path), line=start, severity="error",
                code="missing-business-rule",
                message="test layer SYMBOL must declare business-rule (not N/A).",
            ))

    found_effects: set[str] = set()
    for ln, txt in block:
        m = re.match(r"^\s+(reads|mutates|allocs|throws|async|io):\s*(\S.*)?$", txt)
        if m:
            found_effects.add(m.group(1))
            if not (m.group(2) or "").strip():
                findings.append(Finding(
                    file=str(path), line=ln, severity="error",
                    code="blank-effects-field",
                    message=f"effects.{m.group(1)} is blank (use 'none').",
                ))
    missing_effects = {"reads", "mutates", "allocs", "throws", "async", "io"} - found_effects
    if missing_effects:
        findings.append(Finding(
            file=str(path), line=start, severity="error",
            code="missing-effects-fields",
            message=f"SYMBOL effects missing: {', '.join(sorted(missing_effects))}",
        ))

    found_tests: set[str] = set()
    for ln, txt in block:
        m = re.match(r"^\s+(unit|regression|security):\s*(\S.*)?$", txt)
        if m:
            found_tests.add(m.group(1))
            if not (m.group(2) or "").strip():
                findings.append(Finding(
                    file=str(path), line=ln, severity="error",
                    code="blank-tests-field",
                    message=f"tests.{m.group(1)} is blank (use 'none').",
                ))
    missing_tests = {"unit", "regression", "security"} - found_tests
    if missing_tests:
        findings.append(Finding(
            file=str(path), line=start, severity="warning",
            code="missing-tests-fields",
            message=f"SYMBOL tests missing: {', '.join(sorted(missing_tests))}",
        ))
