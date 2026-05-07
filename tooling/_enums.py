"""Enum sets and required-field lists used by the validator.

Package-private (underscore prefix). Pulled out of ``validate.py`` so
the validator's main file can stay under the project's file-size rule.

Every constant here corresponds to a value or required-set declared in
the spec under ``SPEC/01_HEADER.md``, ``SPEC/02_SYMBOLS.md``,
``SPEC/03_RISKS_MEMORY.md``, or ``SPEC/04_MAINLAND.md``. When the spec
adds or renames a value, update the matching set here.
"""

from __future__ import annotations

# Island HEADER enums
LAYER_ENUM = {
    "core", "presentation", "input", "data", "io", "orchestration",
    "i18n", "test", "config", "build", "bridge",
}
STATUS_ENUM = {
    "verified", "generated", "inferred", "stale", "partial", "abandoned",
}
CONFIDENCE_ENUM = {"high", "medium", "low"}
MAINTAINED_BY_ENUM = {
    "llm", "human-reviewed", "human-unreviewed", "security-reviewed",
}
READ_REASON_ENUM = {"task-driven", "opportunistic", "audit"}

# SYMBOL enums
SYMBOL_KIND_ENUM = {
    "function", "class", "type", "constant", "module", "hook", "middleware",
}
FRAGILITY_ENUM = {"low", "medium", "high"}

# RISKS / mainland enums
SEVERITY_ENUM = {"low", "medium", "high", "critical"}
BOOTSTRAP_MODE_ENUM = {"greenfield", "legacy", "archaeological", "unknown"}

# Generic
BOOL_ENUM = {"true", "false"}

# ---------------------------------------------------------------------------
# Required-section / required-field lists
# ---------------------------------------------------------------------------

REQUIRED_ISLAND_SECTIONS = [
    "---HEADER---", "---SYMBOLS---", "---RISKS---", "---MEMORY---",
]

# Minimum required header fields. Optional v0.2.x extensions
# (generation-pass, read-reason, confidence-review-due, dynamic-boundary)
# are checked only when present.
REQUIRED_HEADER_FIELDS = [
    "file", "language", "role", "layer", "status", "confidence",
    "last-verified", "maintained-by",
    "exports", "imports", "depends-on", "translation-boundary",
]

REQUIRED_RISK_CATEGORIES = [
    "security", "regression-sensitivity", "platform-sensitivity",
]
# config-dependencies is treated as a warning-when-missing rather than an
# error (added in v0.2.13; older islands may not have it yet).

REQUIRED_MAINLAND_SECTIONS = [
    "---ARCHITECTURE---", "---CONNECTIONS---",
    "---CONTRACTS---", "---ARCHITECTURE-MEMORY---",
]

REQUIRED_ARCHITECTURE_FIELDS = [
    "project", "version", "last-verified", "description",
    "bootstrap-mode", "bootstrap-date",
    "layers", "load-order", "architectural-rules",
]
