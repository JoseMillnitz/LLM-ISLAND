"""Island file format validation.

Package-private. Walks one ``*.llmisland`` file and emits Findings for
every structural rule violation declared in ``SPEC/05_VALIDITY.md``.
The public entry point ``validate_island`` is re-exported from
``tooling.validate``.

Format-only: this catches missing fields, bad enums, and structural
gaps — not semantics. See ``tooling/validate.py.llmisland`` AC-001.
"""

from __future__ import annotations

import re
from pathlib import Path

from tooling._enums import (
    BOOL_ENUM,
    CONFIDENCE_ENUM,
    LAYER_ENUM,
    MAINTAINED_BY_ENUM,
    READ_REASON_ENUM,
    REQUIRED_HEADER_FIELDS,
    REQUIRED_ISLAND_SECTIONS,
    REQUIRED_RISK_CATEGORIES,
    SEVERITY_ENUM,
    STATUS_ENUM,
)
from tooling._validate_symbols import iter_symbol_blocks, validate_one_symbol
from tooling.common import is_example_path, parse_last_verified, source_for_island
from tooling.types import Finding


# ---------------------------------------------------------------------------
# Section / field helpers
# ---------------------------------------------------------------------------

def section_lines(lines: list[str]) -> dict[str, int]:
    """Return ``{sentinel -> 1-indexed line number}`` for every ``---NAME---`` line."""
    out: dict[str, int] = {}
    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("---") and stripped.endswith("---"):
            out[stripped] = idx
    return out


def slice_block(lines: list[str], start: int, end: int | None) -> list[tuple[int, str]]:
    end_idx = (end - 1) if end is not None else len(lines)
    return [(n, lines[n - 1]) for n in range(start + 1, end_idx + 1)]


def find_kv(block: list[tuple[int, str]], key: str) -> tuple[int, str] | None:
    prefix = f"{key}:"
    for lineno, raw in block:
        line = raw.strip()
        if line.startswith("#") or not line:
            continue
        if line.startswith(prefix) and not raw.startswith((" ", "\t")):
            return lineno, line[len(prefix):].strip()
    return None


def block_for(section_map: dict[str, int], lines: list[str], name: str) -> list[tuple[int, str]] | None:
    if name not in section_map:
        return None
    ordered = sorted(section_map.items(), key=lambda kv: kv[1])
    start = section_map[name]
    end = None
    for _, lineno in ordered:
        if lineno > start:
            end = lineno
            break
    return slice_block(lines, start, end)


def enum_token(value: str) -> str:
    """Strip RULE 8 inline rationale and trailing comment from a value.

    SPEC/02_SYMBOLS.md RULE 8 allows ``field: value (rationale: ...)``.
    The enum value is always the first whitespace-delimited token before
    any ``(`` or ``#``.
    """
    head = value.split("(", 1)[0].split("#", 1)[0]
    return head.strip().split()[0] if head.strip() else ""


# ---------------------------------------------------------------------------
# Header / symbols / risks / memory validators
# ---------------------------------------------------------------------------

def _validate_header(
    block: list[tuple[int, str]], path: Path, findings: list[Finding]
) -> dict[str, tuple[int, str]]:
    values: dict[str, tuple[int, str]] = {}
    for field_name in REQUIRED_HEADER_FIELDS:
        kv = find_kv(block, field_name)
        if kv is None:
            findings.append(Finding(
                file=str(path), line=None, severity="error",
                code="missing-header-field",
                message=f"HEADER missing required field '{field_name}:'",
            ))
        else:
            values[field_name] = kv

    for opt in ("generation-pass", "read-reason", "confidence-review-due",
                "dynamic-boundary"):
        kv = find_kv(block, opt)
        if kv is not None:
            values[opt] = kv

    def expect_enum(field: str, allowed: set[str]) -> None:
        if field not in values:
            return
        token = enum_token(values[field][1])
        if token and token not in allowed:
            findings.append(Finding(
                file=str(path), line=values[field][0], severity="error",
                code="bad-enum",
                message=f"HEADER {field}: invalid value '{token}'.",
            ))

    expect_enum("layer", LAYER_ENUM)
    expect_enum("status", STATUS_ENUM)
    expect_enum("confidence", CONFIDENCE_ENUM)
    expect_enum("maintained-by", MAINTAINED_BY_ENUM)
    expect_enum("read-reason", READ_REASON_ENUM)
    expect_enum("generation-pass", BOOL_ENUM)
    expect_enum("dynamic-boundary", BOOL_ENUM)

    status = values.get("status", (None, ""))[1]
    last_verified = values.get("last-verified", (None, ""))[1]
    if status == "verified":
        if not last_verified or last_verified in {"?", "N/A", ""}:
            findings.append(Finding(
                file=str(path), line=values.get("last-verified", (None, ""))[0],
                severity="error", code="missing-last-verified",
                message="status: verified but last-verified is missing.",
            ))
        elif parse_last_verified(last_verified) is None:
            findings.append(Finding(
                file=str(path), line=values.get("last-verified", (None, ""))[0],
                severity="error", code="invalid-last-verified",
                message=f"last-verified '{last_verified}' is not parseable.",
            ))

    header_file = values.get("file", (None, ""))[1]
    if header_file and Path(header_file).name != source_for_island(path).name:
        findings.append(Finding(
            file=str(path), line=values.get("file", (None, ""))[0],
            severity="warning", code="file-mismatch",
            message=(
                f"HEADER.file basename '{Path(header_file).name}' does not "
                f"match companion source '{source_for_island(path).name}'."
            ),
        ))

    return values


# SYMBOL block iteration and per-SYMBOL validation live in
# tooling/_validate_symbols.py to keep this file under the file-size rule.


def _validate_risks(
    block: list[tuple[int, str]], path: Path, status: str | None,
    findings: list[Finding],
) -> None:
    for cat in REQUIRED_RISK_CATEGORIES:
        if find_kv(block, cat) is None:
            findings.append(Finding(
                file=str(path), line=None, severity="error",
                code="missing-risk-category",
                message=f"RISKS missing category '{cat}:'.",
            ))
    if find_kv(block, "config-dependencies") is None and status != "partial":
        findings.append(Finding(
            file=str(path), line=None, severity="warning",
            code="missing-config-dependencies",
            message="RISKS missing 'config-dependencies:' (added in v0.2.13).",
        ))

    sec_kv = find_kv(block, "security")
    if sec_kv is None:
        return
    sec_line, sec_value = sec_kv
    if sec_value in {"none", "?", ""}:
        return

    entries: list[dict[str, tuple[int, str]]] = []
    current: dict[str, tuple[int, str]] | None = None
    for ln, raw in block:
        if ln <= sec_line:
            continue
        if not raw.startswith((" ", "\t", "-")) and ":" in raw:
            break
        m_surface = re.match(r"^\s*-\s*surface:\s*(.+)$", raw)
        if m_surface:
            if current:
                entries.append(current)
            current = {"surface": (ln, m_surface.group(1).strip())}
            continue
        if current is None:
            continue
        m_field = re.match(r"^\s*(guarded-by|test|severity):\s*(.+)$", raw)
        if m_field:
            current[m_field.group(1)] = (ln, m_field.group(2).strip())
    if current:
        entries.append(current)

    for entry in entries:
        for key in ("surface", "guarded-by", "test", "severity"):
            if key not in entry or not entry[key][1]:
                findings.append(Finding(
                    file=str(path),
                    line=entry.get("surface", (sec_line, ""))[0],
                    severity="error", code="missing-security-field",
                    message=f"security entry missing '{key}'.",
                ))
        sev = entry.get("severity", (None, ""))[1]
        if sev and sev not in SEVERITY_ENUM:
            findings.append(Finding(
                file=str(path),
                line=entry.get("severity", (sec_line, ""))[0],
                severity="error", code="bad-enum",
                message=f"security severity invalid: '{sev}'.",
            ))
        guarded = entry.get("guarded-by", (None, ""))[1]
        test = entry.get("test", (None, ""))[1]
        if sev in {"medium", "high", "critical"}:
            no_guard = guarded in {"none", "N/A", "?", ""}
            no_test = test in {"none", "N/A", "?", ""}
            if no_guard and no_test:
                findings.append(Finding(
                    file=str(path),
                    line=entry.get("severity", (sec_line, ""))[0],
                    severity="error", code="unguarded-security-surface",
                    message=f"severity: {sev} has no guarded-by AND no test.",
                ))


def _validate_memory(block: list[tuple[int, str]], path: Path,
                     findings: list[Finding]) -> None:
    required = ("ACTIVE-CONSTRAINTS:", "HISTORICAL-DECISIONS:", "SUPERSEDED:")
    found = {label: False for label in required}
    for _, raw in block:
        line = raw.strip()
        if line in required:
            found[line] = True
    for label, present in found.items():
        if not present:
            findings.append(Finding(
                file=str(path), line=None, severity="warning",
                code="missing-memory-block",
                message=f"MEMORY block heading '{label}' not found.",
            ))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def validate_island(path: Path) -> list[Finding]:
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
    for required in REQUIRED_ISLAND_SECTIONS:
        if required not in sections:
            findings.append(Finding(
                file=str(path), line=None, severity="error",
                code="missing-section",
                message=f"Missing section '{required}'.",
            ))
    if any(f.code == "missing-section" for f in findings):
        return findings

    header_block = block_for(sections, lines, "---HEADER---") or []
    symbols_block = block_for(sections, lines, "---SYMBOLS---") or []
    risks_block = block_for(sections, lines, "---RISKS---") or []
    memory_block = block_for(sections, lines, "---MEMORY---") or []

    header_values = _validate_header(header_block, path, findings)
    layer = header_values.get("layer", (None, ""))[1]
    status = header_values.get("status", (None, ""))[1]

    companion = source_for_island(path)
    if not companion.exists():
        severity = "warning" if is_example_path(path) else "error"
        findings.append(Finding(
            file=str(path), line=None, severity=severity,
            code="missing-source",
            message=f"Companion source not found: {companion}",
        ))

    if status != "partial":
        for start, block in iter_symbol_blocks(symbols_block):
            validate_one_symbol(start, block, path, layer, enum_token, findings)

    _validate_risks(risks_block, path, status, findings)
    _validate_memory(memory_block, path, findings)
    return findings
