"""Shared result types used across the tooling/ package.

``Finding`` and ``Report`` are the only cross-subcommand result types.
Subcommands MUST NOT define their own — see contract
``subcommand-return-shape`` in ``connections.llmainland``.

Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Finding:
    """One validation/check finding. Used across subcommands for uniform output.

    ``severity`` is one of ``"error"``, ``"warning"``, ``"info"``.
    """

    file: str
    line: int | None
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class Report:
    """Structured result returned by every subcommand.

    The orchestrator dispatcher serializes this either as JSON
    (``--json``) or as text via ``llmisland_tooling._emit``.

    ``ok``        - whether the subcommand believes the project passes its check.
    ``findings``  - list of Finding objects.
    ``summary``   - free-form, JSON-serializable per-subcommand details.
    """

    command: str
    ok: bool
    findings: list[Finding] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
