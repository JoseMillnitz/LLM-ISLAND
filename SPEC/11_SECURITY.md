# Spec Module 11 - Security Review Gates

When security-reviewed maintained-by is required, the adversarial injection threat model, and open-source publishing guidance for sensitive island content. Read this when touching a high or critical security surface, or when deciding which island sections to keep private.

---

## SECURITY REVIEW GATES

Islands and the mainland describe exactly where load-bearing invariants live
and what security trade-offs were made. This information is valuable context
AND a potential attack surface.

### WHEN SECURITY REVIEW IS REQUIRED

An island requires `maintained-by: security-reviewed` when:
  - The RISKS section contains `severity: high` or `severity: critical`
  - The island is bound to a security-related mainland CONTRACT
  - The file handles authentication, authorization, encryption, or
    user-supplied input parsing

An island may have `maintained-by: llm` or `human-reviewed` when:
  - No security surfaces are declared
  - All security surfaces have `severity: low` or `medium` with tested guards

A code change to a `security-reviewed` island downgrades `maintained-by` back
to `llm` until the security reviewer re-confirms the island.

### ADVERSARIAL INJECTION WARNING

Island content is trusted by the LLM as ground truth. In multi-contributor
or open-source projects, adversarial editing of islands is a real threat.

A malicious actor (or compromised LLM session) could:
  - Claim a vulnerable function is safe via a false RISKS entry
  - Add a false HISTORICAL-DECISIONS entry redirecting development
  - Weaken an ACTIVE-CONSTRAINTS entry to permit an insecure pattern

The more authoritative islands become, the more valuable they are as an
injection target. Mitigation: for security-sensitive projects, island edits
to security-related files should go through the same review process as
code changes. The `maintained-by: security-reviewed` status is the minimum
signal that this review has occurred.

### OPEN-SOURCE PROJECTS

For open-source or broad-access projects, consider what island content
should be public vs. private:
  - SYMBOLS, HEADER, CONNECTIONS: generally safe to publish
  - Detailed security trade-off history in HISTORICAL-DECISIONS may expose
    vulnerability reasoning that aids attackers
  - ACTIVE-CONSTRAINTS about security workarounds: evaluate case by case

The spec does not require hiding islands. It requires awareness that
islands in security-critical areas are both the most valuable and the
most sensitive documentation in the project.

---
