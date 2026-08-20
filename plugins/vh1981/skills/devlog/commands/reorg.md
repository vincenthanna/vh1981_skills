# Command: Reorg — detailed procedures

Read this file when the user invokes `/devlog reorg <action> ...`. SKILL.md
carries the routing and the one-line summaries; this file has the steps.

Subactions: `rename`, `archive`, `cleanup`, `consolidate`, `readme`. `move` is
reserved but not yet implemented — if asked, tell the user it is unavailable.

Common to every reorg action: resolve the active project first, and record what
was done as ONE line in the latest history entry's `Changes` (meta/housekeeping
rule — no new investigation doc). **Exception**: `consolidate` never touches
`history/` — neither reading nor writing. See its own Recording step.

`cleanup` and `consolidate` are siblings that split on evidence type. `cleanup`
reports only mechanically decidable structural faults, so it has no false
positives. `consolidate` reports judgment calls about content, so every row must
carry its evidence and the user decides. Keeping them apart is what preserves
`cleanup`'s no-false-positive property — do not merge the two.

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
   - an investigation doc with no `Progress` section — `reference/writing.md`
     makes it mandatory, so its absence is a fault, not a judgment call
   - a project with no `README.md`
   Do NOT auto-detect "obsolete" or "near-duplicate" by meaning — that is a
   judgment call and produces false positives.
2. Output a table of proposed actions (rename / archive / renumber), each row
   with its concrete reason.
3. Execute ONLY the rows the user approves. Never `rm` directly — removal goes
   through `reorg archive`.

## reorg consolidate

Reads the project's accumulated investigation docs and proposes content-level
tidying **and compaction** — the judgment-call counterpart to `cleanup`. Same
contract: **proposal only, never auto-executes**, and nothing is deleted.

Compaction is the second half of the job. A long-running project accumulates
detailed write-ups of approaches that were evaluated and then left off the
mainstream path — rejected, regressed, deferred, or beaten by a sibling branch.
That detail is worth keeping and worth *not* reading every time: it is what
stops someone re-attempting a dead end. consolidate moves it to `rejected/` and
leaves a one-line verdict behind, so the mainstream doc stays readable and the
detail is one link away.

**Read scope — investigation docs only**: `<project>/*.md`,
`<project>/<subtopic>/*.md`, and `README.md`. Never `history/` (SKILL.md
"History is not context"), never `_archived/`. This is a full read of every
investigation doc and therefore expensive: run it only when the user asks for it
by name. `update` must never trigger it.

1. Detect these signals:

   | Signal | What to look for | Proposed action |
   |--------|------------------|-----------------|
   | duplicated fact | the same `file:line`, metric, or finding stated in 2+ docs | keep one canonical statement; replace the others with a cross-reference |
   | duplicated open item | the same `Remaining / Next` item carried by 2+ docs, often at conflicting priority tags | keep it in the doc that owns the work; cross-reference from the rest, and reconcile the tag |
   | stale open item | a `[Critical]` / `[High]` in `Remaining / Next` that a later doc's `Done`, a later finding, or the current code contradicts | move it to `Done`, or downgrade its tag |
   | superseded conclusion | an earlier doc's `Conclusion` that a later doc reverses | add a dated supersede note above the affected section — keep the original text |
   | off-mainstream detail | a mainstream doc carrying an extended write-up of an approach that was NOT adopted — rejected, regressed, deferred, or superseded by a sibling branch — where the detail runs past a few lines or has grown its own subsections, code blocks, or measurement tables | extract to `rejected/NN_<slug>.md`; leave a one-line verdict row behind (see "Extraction" below) |
   | oversized doc | a doc that now trips the split triggers in `reference/writing.md` | split the separable topic off into a new `NN_` file |
   | foldering threshold | 5–6+ investigation docs with 3+ sharing a topic-slug prefix | group those into a `<prefix>/` subtopic folder |

   Judge "the current code contradicts it" only from files actually read this
   run — never from memory of the codebase.

2. Output ONE table: `| file | signal | proposed action | evidence |`. Evidence
   is concrete — the `file:line` on both sides of a duplicate, the doc that
   reverses the conclusion, the count that trips a threshold. Emit no row you
   cannot evidence, and state the doc count you read so partial coverage is
   never mistaken for a clean bill.

3. Execute ONLY the rows the user approves.

   - **Never delete content.** Consolidating a duplicate moves the text into the
     canonical doc and leaves a cross-reference (path form in
     `reference/writing.md`) where it stood. Dropping a doc outright goes
     through `reorg archive`.
   - Preserve historical accuracy: a superseded conclusion gets a note, not a
     rewrite of what was believed at the time.
   - `Period` end dates follow the normal rule — any doc edited this run gets
     today's date from the SKILL.md context header.
   - After any approved row that adds, splits, moves, or renumbers a `NN_` file,
     run `reorg readme` so `Entries` and `Remaining / Next` match the tree.

4. **Extraction** — for approved `off-mainstream detail` rows:

   a. Create `<project>/rejected/NN_<slug>.md` — read `templates/rejected.md`
      and follow it. Move the detail verbatim; do not re-summarize it, and do
      not improve it. It is a record of what was actually tried.
   b. In the source doc, replace the extracted block with ONE row in a
      `Rejected approaches` table:

      | 기법 | Verdict | 이유 | 상세 |
      |------|---------|------|------|
      | 003b velocity gating | 폐기 | threshold 3.0이 느슨해 차단되는 매칭이 없었음 | `docs/devlog/<project>/rejected/01_velocity-gating.md` |

      **The reason stays in the mainstream doc.** Only the detail moves — a row
      that says just "폐기" without why fails the whole point, because the next
      person cannot tell whether their new idea is the same idea.
   c. A verdict that is already one line stays where it is, and an existing
      compact "rejected approaches" summary table is the target shape, not a
      source to extract from. Over-extraction is a real failure mode: it turns
      a readable one-line verdict into a link the reader has to follow.
   d. Extraction never leaves the project: the doc moves to `rejected/`, not to
      `_archived/`. `_archived/` is for superseded *documents*; `rejected/` is
      for evaluated-and-not-adopted *approaches*, which stay valid as findings.

5. **Recording**: consolidate writes nothing to `history/`. Its trace is left in
   place instead — rows that archive a file log to `_archived/_log.md` as usual,
   supersede notes, cross-references, and `rejected/` extractions are
   self-documenting inside the docs, and index changes land through
   `reorg readme`. The run summary goes to the user's output only.

## reorg readme

Fully regenerates `docs/devlog/<project>/README.md`'s machine-owned region.

1. Read all investigation docs. (The AUTO-GENERATED region — the `Entries`
   table and the `Remaining / Next` summary — is built entirely from
   investigation docs, so `history/` is not read here.)
2. Rebuild the `<!-- AUTO-GENERATED -->` … `<!-- /AUTO-GENERATED -->` region:
   the `Entries` table (one row per `NN_*.md`, with its title/summary) and the
   `Remaining / Next` summary (`[Critical]` + `[High]` items across investigation
   docs, each tagged with its source file).
3. Never touch anything outside the AUTO-GENERATED markers — the title, Scope,
   Out of scope, and all prose are user-owned.
