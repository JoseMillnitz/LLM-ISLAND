# Spec Module 00 - Overview

Core principles and file naming. Read this when you are new to the system, when you need the trust model, or when deciding whether an idea belongs in islands, mainland, or tooling.

---

## CORE PRINCIPLES

1. SELF-CONTAINED — every island must be understandable with zero external context.
   An LLM reading an island for the first time, with no prior project knowledge,
   must be able to answer: what does this file do, what does it depend on, what
   depends on it, what are the load-bearing constraints, what breaks if I change X.

2. HONEST INCOMPLETENESS — a partial island is valid. Silence where there should
   be a declaration is not. Use explicit markers: ? for unknown, N/A for not
   applicable. Never leave a field blank.

3. LOAD-BEARING FOCUS — document what tooling cannot catch. If a compiler, type
   system, or test suite already enforces something, it does not need to be in the
   island. Islands exist for the things that fall through those gaps.

4. STRATIFIED MEMORY — active constraints, historical decisions, and superseded
   decisions are distinct layers. An LLM working on a task reads the active layer.
   It reads the historical layer to understand the solution space. The superseded
   layer is archaeological record — never deleted, rarely read.

5. LANGUAGE AGNOSTIC — the format works for any source language or mixed-language
   pipeline. Python calling C calling Assembly. A single project with six languages.
   The mainland models cross-language boundaries explicitly.

6. LLM-FIRST — the format is optimized for machine generation and parsing. Human
   readability is a tooling concern, not a format constraint. When human ergonomics
   and LLM clarity conflict, LLM clarity wins.

7. PROPAGATION DISCIPLINE — when code changes, its island changes. When a
   connection changes, the mainland changes. When the mainland changes, that is a
   signal to check all islands bound to the affected connection. This propagation
   is not optional — a stale island is a lie.

8. UNCERTAINTY OVER PLAUSIBILITY — when uncertain about a value, use ?. A
   plausible guess that sounds authoritative is worse than declared uncertainty
   because it becomes canonical. Future sessions will cite a hallucinated value
   as historical fact. A wrong break-impact that sounds confident will prevent
   a valid refactor for months. ? is always the correct answer when the evidence
   does not support a specific value.

9. DETECTABLE FAILURE — the system is not self-enforcing. Rules exist to
   create recoverable failure modes, not to prevent failure. When an LLM
   violates stop-early, skips a propagation, or reads more files than needed,
   the damage must be detectable and repairable, not silent. Design every
   rule with the question: "when this rule is broken, how will a future
   session discover the violation?" If the answer is "it will not", the rule
   needs a fallback state that makes the violation visible.

---

## FILE NAMING

  <source-file>.<ext>.llmisland      companion to each source file
  connections.llmainland             one per project, always at project root

Examples:
  renderer.js.llmisland
  generator.py.llmisland
  render_core.c.llmisland
  connections.llmainland

One island per source file. One mainland per project. No exceptions.

---
