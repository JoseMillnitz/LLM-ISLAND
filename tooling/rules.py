"""Architectural-rule extraction for LLM-assisted compliance check.

One subcommand: ``validate-rules``. Extracts the
``architectural-rules`` block from ``connections.llmainland`` and
groups the entries by ``self-checkable: true | false``.

The tool itself does NOT validate code against rules — that requires
real semantic understanding the LLM has and the tool does not. Instead,
this command formats the rules so the LLM (or a human reviewer) can
verify a diff against them in one read. With ``--diff PATH``, the
diff content is appended to the output along with a short instruction
block telling the LLM to mark each rule PASS or FAIL.

Standard library only.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from tooling.common import MAINLAND_NAME, find_project_root
from tooling.types import Finding, Report

# Architecture rules look like:
#   - AR-001: <text>
#     self-checkable: true
# or
#   - AR-005: <multiline rule text>
#             continued indented
#     self-checkable: false (optional explanation)
#
# The block ends at the next top-level field or section sentinel.

_RULE_BLOCK_RE = re.compile(
    r"architectural-rules:\s*\n(.*?)(?=\n[A-Za-z][\w-]*:\s|\n---|\Z)",
    re.DOTALL,
)
_RULE_ENTRY_SPLIT = re.compile(r"(?m)^\s*-\s+AR-")
_SELF_CHECKABLE_RE = re.compile(r"self-checkable:\s*(true|false)\b", re.IGNORECASE)


def _extract_rules(text: str) -> tuple[list[str], list[str]]:
    """Return (self_checkable_lines, not_checkable_lines) extracted from
    a mainland file's text. Each entry is the rule's first line in the
    form ``AR-NNN: <text>``."""
    block_match = _RULE_BLOCK_RE.search(text)
    if block_match is None:
        return [], []

    block = block_match.group(1)
    # Re-attach the leading "AR-" that the split consumed.
    raw_entries = _RULE_ENTRY_SPLIT.split(block)
    self_checkable: list[str] = []
    not_checkable: list[str] = []

    for raw in raw_entries:
        entry = raw.strip()
        if not entry:
            continue
        # Ensure the AR- prefix; the split removed the leading "- AR-".
        # If the first token isn't "AR-", this fragment was the prefix
        # before the first rule and we skip it.
        if not entry.startswith("AR") and not entry.startswith("AR-"):
            # The split puts "001: ..." in entries after the first split
            # (because we matched "- AR-" and consumed it). Restore.
            entry = "AR-" + entry
        first_line = entry.splitlines()[0].strip()
        match = _SELF_CHECKABLE_RE.search(entry)
        is_self = match is not None and match.group(1).lower() == "true"
        if is_self:
            self_checkable.append(first_line)
        else:
            not_checkable.append(first_line)

    return self_checkable, not_checkable


def cmd_validate_rules(args: argparse.Namespace) -> Report:
    findings: list[Finding] = []
    summary: dict = {}

    if args.mainland:
        mainland_path = Path(args.mainland).resolve()
    else:
        mainland_path = find_project_root(Path.cwd()) / MAINLAND_NAME

    if not mainland_path.exists():
        findings.append(Finding(
            file=str(mainland_path), line=None, severity="error",
            code="mainland-missing",
            message=(
                f"Mainland not found at {mainland_path}. "
                f"Pass --mainland PATH if it lives elsewhere."
            ),
        ))
        return Report(command="validate-rules", ok=False,
                      findings=findings, summary=summary)

    text = mainland_path.read_text(encoding="utf-8", errors="replace")
    self_checkable, not_checkable = _extract_rules(text)

    summary["mainland"] = str(mainland_path)
    summary["self_checkable"] = self_checkable
    summary["not_checkable"] = not_checkable
    summary["self_checkable_count"] = len(self_checkable)
    summary["not_checkable_count"] = len(not_checkable)

    if not self_checkable and not not_checkable:
        findings.append(Finding(
            file=str(mainland_path), line=None, severity="warning",
            code="no-rules",
            message=(
                "No architectural-rules block found, or block is empty. "
                "RULE 9 (post-generation compliance) cannot be applied."
            ),
        ))
        return Report(command="validate-rules", ok=True,
                      findings=findings, summary=summary)

    for rule in self_checkable:
        findings.append(Finding(
            file=str(mainland_path), line=None, severity="info",
            code="rule-self-checkable",
            message=f"verify your changes against: {rule}",
        ))
    for rule in not_checkable:
        findings.append(Finding(
            file=str(mainland_path), line=None, severity="info",
            code="rule-not-checkable",
            message=f"requires runtime/human review: {rule}",
        ))

    if args.diff:
        diff_path = Path(args.diff).resolve()
        if not diff_path.exists():
            findings.append(Finding(
                file=str(diff_path), line=None, severity="error",
                code="diff-missing",
                message=f"Diff file not found: {diff_path}",
            ))
            return Report(command="validate-rules", ok=False,
                          findings=findings, summary=summary)

        diff_text = diff_path.read_text(encoding="utf-8", errors="replace")
        summary["diff_file"] = str(diff_path)
        summary["diff_content"] = diff_text
        summary["llm_instruction"] = (
            "Review the diff against each SELF-CHECKABLE rule above. "
            "For each rule: state PASS or FAIL and briefly explain why. "
            "If any rule FAILs, do not proceed with the change."
        )

    return Report(command="validate-rules", ok=True,
                  findings=findings, summary=summary)


def setup_validate_rules(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--mainland", default=None, metavar="PATH",
        help="Path to connections.llmainland. Auto-detected from cwd by default.",
    )
    parser.add_argument(
        "--diff", default=None, metavar="PATH",
        help="Path to a diff file. When given, the diff is included in the "
             "report summary along with an LLM instruction to PASS/FAIL "
             "each self-checkable rule.",
    )


SUBCOMMANDS = {
    "validate-rules": (
        setup_validate_rules,
        cmd_validate_rules,
        "Extract architectural-rules from the mainland for LLM-assisted "
        "compliance review (RULE 9 in MAINTENANCE PROTOCOL).",
    ),
}
