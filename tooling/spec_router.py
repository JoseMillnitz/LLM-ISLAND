"""Context router for the SPEC/ directory.

One subcommand: ``spec --topic TOPIC``. Maps a short topic keyword to
the appropriate ``SPEC/NN_*.md`` module and prints its content directly.
This eliminates the round-trip of "read the topic table in
``LLMISLAND_SPEC.md``, then read the module" — saves tokens for every
session that needs to consult the spec.

When ``--json`` is set, the file content is returned as a string in the
Report summary. Without ``--json``, the content is printed to stdout
verbatim.

Standard library only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tooling.common import find_project_root
from tooling.types import Finding, Report


# Map short keywords to the SPEC/ filename. Multiple keys can point at the
# same file; the matcher in cmd_spec normalizes input (lowercase, strip
# separators) before lookup.
SPEC_TOPIC_MAP: dict[str, str] = {
    # 00 — Overview
    "overview":       "00_OVERVIEW.md",
    "principles":     "00_OVERVIEW.md",
    "naming":         "00_OVERVIEW.md",
    "core":           "00_OVERVIEW.md",

    # 01 — HEADER
    "header":         "01_HEADER.md",
    "island":         "01_HEADER.md",
    "format":         "01_HEADER.md",

    # 02 — SYMBOLS + decision criteria
    "symbols":        "02_SYMBOLS.md",
    "criteria":       "02_SYMBOLS.md",
    "fragility":      "02_SYMBOLS.md",
    "confidence":     "02_SYMBOLS.md",
    "severity":       "02_SYMBOLS.md",
    "strength":       "02_SYMBOLS.md",
    "breakimpact":    "02_SYMBOLS.md",

    # 03 — RISKS / MEMORY
    "risks":          "03_RISKS_MEMORY.md",
    "memory":         "03_RISKS_MEMORY.md",
    "constraints":    "03_RISKS_MEMORY.md",

    # 04 — Mainland
    "mainland":       "04_MAINLAND.md",
    "connections":    "04_MAINLAND.md",
    "contracts":      "04_MAINLAND.md",
    "selectiveread":  "04_MAINLAND.md",

    # 05 — Validity
    "validity":       "05_VALIDITY.md",
    "status":         "05_VALIDITY.md",
    "stale":          "05_VALIDITY.md",
    "staleness":      "05_VALIDITY.md",

    # 06 — Tiers
    "tiers":          "06_TIERS.md",
    "tier":           "06_TIERS.md",
    "update":         "06_TIERS.md",

    # 07 — Propagation
    "propagation":    "07_PROPAGATION.md",
    "cascade":        "07_PROPAGATION.md",
    "llmpropstts":    "07_PROPAGATION.md",
    "resume":         "07_PROPAGATION.md",

    # 08 — Bootstrap + boot modes
    "bootstrap":      "08_BOOTSTRAP.md",
    "modes":          "08_BOOTSTRAP.md",
    "bootmodes":      "08_BOOTSTRAP.md",
    "mvm":            "08_BOOTSTRAP.md",
    "expansion":      "08_BOOTSTRAP.md",
    "stopearly":      "08_BOOTSTRAP.md",

    # 09 — Maintenance
    "maintenance":    "09_MAINTENANCE.md",
    "rules":          "09_MAINTENANCE.md",
    "llwasland":      "09_MAINTENANCE.md",

    # 10 — Edge cases / cross-language
    "monorepo":       "10_EDGE_CASES.md",
    "dynamic":        "10_EDGE_CASES.md",
    "cycles":         "10_EDGE_CASES.md",
    "edge":           "10_EDGE_CASES.md",
    "edgecases":      "10_EDGE_CASES.md",
    "crosslang":      "10_EDGE_CASES.md",
    "language":       "10_EDGE_CASES.md",
    "ffi":            "10_EDGE_CASES.md",

    # 11 — Security
    "security":       "11_SECURITY.md",
    "adversarial":    "11_SECURITY.md",
    "securityreview": "11_SECURITY.md",

    # 12 — Adoption
    "adoption":       "12_ADOPTION.md",
    "abandonment":    "12_ADOPTION.md",
    "sustainability": "12_ADOPTION.md",

    # 13 — Reference
    "xp":             "13_REFERENCE.md",
    "reference":      "13_REFERENCE.md",
    "antipatterns":   "13_REFERENCE.md",
    "quick":          "13_REFERENCE.md",
    "scenarios":      "13_REFERENCE.md",
}


def _normalize(topic: str) -> str:
    """Lowercase and strip separators so 'check-stale' == 'checkstale'."""
    return topic.lower().replace("-", "").replace("_", "").replace(" ", "").strip()


def _resolve_topic(topic: str) -> tuple[str | None, list[str]]:
    """Return (filename, candidate_keys). filename is None on no match."""
    norm = _normalize(topic)
    if norm in SPEC_TOPIC_MAP:
        return SPEC_TOPIC_MAP[norm], [norm]
    matches = [k for k in SPEC_TOPIC_MAP if norm in k or k in norm]
    if len(matches) == 1:
        return SPEC_TOPIC_MAP[matches[0]], matches
    return None, matches


def cmd_spec(args: argparse.Namespace) -> "int | Report":
    norm = _normalize(args.topic)
    filename, matches = _resolve_topic(args.topic)

    if filename is None:
        if matches:
            findings = [Finding(
                file=args.topic, line=None, severity="info",
                code="ambiguous-topic",
                message=(
                    f"Topic '{args.topic}' is ambiguous. Candidates: "
                    f"{', '.join(matches)}. Be more specific."
                ),
            )]
            return Report(command="spec", ok=False, findings=findings,
                          summary={"input": args.topic, "candidates": matches})
        # Fully unknown — list available files
        files = sorted(set(SPEC_TOPIC_MAP.values()))
        findings = [Finding(
            file=args.topic, line=None, severity="info",
            code="unknown-topic",
            message=f"Unknown topic. SPEC files available: {', '.join(files)}",
        )]
        return Report(command="spec", ok=False, findings=findings,
                      summary={"input": args.topic,
                               "available_topics": sorted(SPEC_TOPIC_MAP.keys())})

    if args.spec_dir:
        spec_dir = Path(args.spec_dir).resolve()
    else:
        spec_dir = find_project_root(Path.cwd()) / "SPEC"

    spec_file = spec_dir / filename
    if not spec_file.exists():
        findings = [Finding(
            file=str(spec_file), line=None, severity="error",
            code="spec-file-missing",
            message=(
                f"Spec file not found at {spec_file}. "
                f"Pass --spec-dir if SPEC/ is somewhere unusual."
            ),
        )]
        return Report(command="spec", ok=False, findings=findings,
                      summary={"resolved_to": filename})

    content = spec_file.read_text(encoding="utf-8", errors="replace")

    if getattr(args, "json", False):
        return Report(
            command="spec", ok=True, findings=[],
            summary={"topic": args.topic, "resolved_to": filename,
                     "file": str(spec_file), "content": content},
        )

    # Print directly to stdout — the user wants the file content, not
    # a meta-formatted Report wrapper around it.
    print(content)
    return 0


def setup_spec(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--topic", required=True, metavar="TOPIC",
        help=(
            "Topic keyword. Examples: header, symbols, mainland, tiers, "
            "propagation, bootstrap, maintenance, security, adoption, "
            "edge, reference. Run with an unknown topic to see all keys."
        ),
    )
    parser.add_argument(
        "--spec-dir", default=None, metavar="DIR",
        help="Directory containing the SPEC/ modules. Auto-detected by default.",
    )


SUBCOMMANDS = {
    "spec": (
        setup_spec,
        cmd_spec,
        "Print the SPEC/ module that covers a given topic.",
    ),
}
