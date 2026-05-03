# Spec Module 05 - Validity, Status, and Staleness

Validity rules for islands and the mainland, the status progression model, and the staleness detection obligation (hard dependency on tooling for any project where humans edit files outside LLM sessions). Read this when validating an island, when an island has changed status, or when the project lacks a staleness checker.

---

## VALIDITY RULES

An island is INVALID if any of the following are true:
- Any required field is absent (silence is not allowed — use ? or N/A)
- fragility is medium or high without a fragility-note
- A security surface exists with no guarded-by AND no test AND severity >= medium
- status is verified but last-verified is absent
- maintained-by is human-unreviewed and more than one task cycle has passed
- A SYMBOL entry for a test file is missing business-rule

An island with a TIERED UPDATE (see UPDATE TIERS) is VALID if:
- The update tier matches the actual change scope (Tier A, B, or C)
- All fields required by that tier are updated
- Fields outside the tier's scope are unchanged (not deleted, not guessed)
- last-verified is updated regardless of tier

A tiered update is a first-class valid outcome, not a shortcut. The system
explicitly permits narrow updates when the change scope is narrow.

An island is STALE if:
- The source file has been modified since last-verified
- A mainland connection referencing this island has changed without a
  corresponding island update

STALE islands are treated as HYPOTHESIS, not ground truth.
The LLM must flag staleness before acting on the island's content.

---

## STALENESS DETECTION

The spec defines staleness but the LLM cannot detect it on its own. An LLM
cannot compare `last-verified` against filesystem modification timestamps
without tooling. This section declares the detection obligation explicitly.

STALENESS DETECTION OBLIGATION:
  Any project where humans edit files outside of LLM sessions MUST have a
  staleness detection mechanism. This is a hard dependency, not a nice-to-have.

  Minimum viable detection: a script or CI hook that compares `last-verified`
  dates in all `.llmisland` files against the modification timestamps of their
  source files. Any mismatch is a staleness signal.

  Acceptable mechanisms:
    - A script run before each LLM session
      (`python llmisland_tooling.py check-stale .`)
    - A CI hook that blocks merges with stale islands
    - An editor plugin that flags stale islands on save
    - The LLM itself, if it has filesystem access and can read timestamps

WHEN THE LLM HAS FILESYSTEM ACCESS:
  Before reading any island, the LLM should verify that the source file's
  modification date is not newer than the island's `last-verified` date.
  If it is newer: treat the island as STALE, regardless of its `status` field.
  Flag the staleness to the human before proceeding.

WHEN THE LLM DOES NOT HAVE FILESYSTEM ACCESS:
  The human (or CI) must run the staleness checker before starting the LLM
  session. If no checker was run, the LLM should ask: "Have you verified that
  islands are current? If not, I will treat all islands as HYPOTHESIS."

WHEN NO CHECKER EXISTS:
  If the project has no staleness detection mechanism and humans edit files
  directly, all islands are HYPOTHESIS by default. The LLM should state this
  at the start of the session:
  "No staleness checker is configured. I will verify any island I use against
  the actual source file before relying on it."

  In this mode: treat declared `confidence: high` as operationally `medium` and
  `confidence: medium` as operationally `low`. The format does not override
  missing infrastructure.

The mainland is INVALID if:
- Any CONNECTION references a file that has no island
- Any CONTRACT lists an enforced-by test that does not exist
- Any architectural-rule is violated by a declared connection
- last-verified is absent

---

## STATUS PROGRESSION

  generated  ->  verified       after LLM review confirms accuracy
  generated  ->  inferred       when source is legacy with no documentation
  inferred   ->  verified       when hypothesis is confirmed by evidence
  inferred   ->  corrected      when hypothesis is wrong
                                (old entry kept, new entry added, old marked superseded)
  verified   ->  stale          automatic, when source file changes
  stale      ->  verified       after island is updated and reviewed
  any        ->  partial        explicit downgrade when island is known incomplete

---
