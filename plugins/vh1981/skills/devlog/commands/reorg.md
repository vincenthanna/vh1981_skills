# Command: Reorg — detailed procedures

Read this file when the user invokes `/devlog reorg <action> ...`. SKILL.md
carries the routing and the one-line summaries; this file has the steps.

Subactions: `rename`, `archive`, `cleanup`, `readme`. `move` is reserved but not
yet implemented — if asked, tell the user it is unavailable.

Common to every reorg action: resolve the active project first, and record what
was done as ONE line in the latest history entry's `Changes` (meta/housekeeping
rule — no new investigation doc).

## reorg rename <old> <new>

Renames a project directory and fixes every cross-reference to it.

1. Sanitize `<new>` (same rule as `create`). Verify `docs/devlog/<old>/` exists
   and `docs/devlog/<new>/` does not.
2. `git mv docs/devlog/<old> docs/devlog/<new>` (or `mv` if not git-tracked).
3. Find every reference: `grep -rln "docs/devlog/<old>" docs/`.
4. **Show the match list and get the user's approval before substituting.**
5. On approval, replace `docs/devlog/<old>` → `docs/devlog/<new>` in each file.
6. Verify no stale refs remain: `grep -rln "docs/devlog/<old>" docs/` returns empty.
7. If `docs/devlog/.active` held `<old>`, rewrite it to `<new>`.
8. Update `<new>/README.md`'s title/header if it embedded the old name.
9. Append one line to `<new>/history/`'s latest entry: "Renamed from `<old>`".

## reorg archive <path>

Isolates an obsolete/superseded doc or subtopic without deleting it.

1. `<path>` is a file or subtopic directory under a project. Verify it exists.
2. If anything outside the project references it (`grep -rln`), warn, list the
   referrers, and get the user's confirmation before proceeding.
3. Move it to `<project>/_archived/` (create the directory if needed).
4. Append to `<project>/_archived/_log.md`:
   `- <date> | <original path> | <reason>` — the reason is required
   (e.g. "superseded by `04_...`").
5. `list` ignores `_archived/`.

## reorg cleanup

Inspects the active project and proposes hygiene fixes — **proposal only, never
auto-executes.**

1. Detect only verifiable, structural signals:
   - duplicate `NN_` prefixes in the same directory
   - broken cross-references (a `docs/devlog/...` path that no longer resolves)
   - empty `.md` files
   Do NOT auto-detect "obsolete" or "near-duplicate" by meaning — that is a
   judgment call and produces false positives.
2. Output a table of proposed actions (rename / archive / renumber), each row
   with its concrete reason.
3. Execute ONLY the rows the user approves. Never `rm` directly — removal goes
   through `reorg archive`.

## reorg readme

Fully regenerates `docs/devlog/<project>/README.md`'s machine-owned region.

1. Read all investigation docs and the latest history entry.
2. Rebuild the `<!-- AUTO-GENERATED -->` … `<!-- /AUTO-GENERATED -->` region:
   the `Entries` table (one row per `NN_*.md`, with its title/summary) and the
   `Remaining / Next` summary (`[Critical]` + `[High]` items across investigation
   docs, each tagged with its source file).
3. Never touch anything outside the AUTO-GENERATED markers — the title, Scope,
   Out of scope, and all prose are user-owned.
