# Scenario — Greenfield
# Read this only when starting a brand new project with no existing code.

---

## SITUATION

New project. No source files yet, or only a few just created.
The island system is being set up from the beginning.

---

## PROCESS

Step 1 — Create `connections.llmainland` before writing code.
  The mainland is the architecture before it is the implementation.
  Use the MVM template from your mode file, but fill in what you know:
  - Give the project a name and description
  - Declare the layers you intend to have
  - Add the architectural rules you intend to enforce, even if tentative
  - Leave CONNECTIONS and CONTRACTS empty — they will be filled as files are created

Step 2 — As each source file is created, create its island immediately.
  Do not write a file and add the island later.
  Populate all fields. Mark unknowns with `?`. Set `status: generated`.
  See EXAMPLES/example.llmisland for the format.

Step 3 — Add each new file's connections to the mainland as you go.
  Do not batch this. Update the mainland when the file is created.

Step 4 — After the first working version, do a verification pass.
  Resolve `?` fields that can now be answered.
  Promote `status: generated` to `status: verified` where confirmed.
  Declare the first formal contracts in the mainland.

Step 5 — From this point, follow Mode 1 (Incremental) for all further work.

---

## KEY RULE

In greenfield, the island grows with the code. An island written at file creation
is cheap and high quality. An island written retroactively is expensive and
lower quality. Never defer island creation to "later."
