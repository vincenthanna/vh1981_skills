# Command: Update — detailed procedure

Read this file when routing lands on **Update** (`/devlog update`, or `/devlog`
with no args). SKILL.md carries the routing, active-project resolution, and the
recap rules; this file has the steps. Update performs three parts in sequence:
(1) investigation docs, (2) work history, (3) README maintenance.

Before writing or editing any doc, read `reference/writing.md` (in this skill's
directory) once per session — it carries the doc-writing rules.

## Scoped read — what update reads

This section is the ONLY definition of what `update` reads. `update` does NOT
read every `.md` file. It reads: the project `README.md` (if any) and the
investigation docs whose slug matches the current topic. The active project is
resolved per SKILL.md `## Active Project` — `.active` itself is consulted only
where those rules say so. A
full read happens only on the first `select` of a project in a session, or when
the user explicitly asks for full context — and a "full read" still means all
*investigation* docs (plus `README.md`), never the `history/` folder ("History
is not context", SKILL.md). The gather-intensity table below decides *how hard*
to gather; this decides *what* to read.

## Next sequence number (used by Parts 1 and 2)

When creating a new `NN_` file: list the target directory's `.md` files, take
the highest `NN_` prefix and add 1. If two files already share an `NN_`, report
the collision. Never guess from memory.

## Steps

1. **Read existing entries (scoped)**: per "Scoped read" above. If this is the
   first `update` of a resumed session (SKILL.md `## Active Project`), the
   previous-state recap applies first.

2. **Gather context — intensity-scaled**:

   Pick the gather intensity from observable signals (no subjective "little has changed"):

   | Intensity | When | Scope |
   |-----------|------|-------|
   | **Light** | `git diff --stat` shows 0 changed files AND a prior `/devlog` call already ran in this same response | Step C only |
   | **Normal** | 1–5 commits since the latest investigation doc's `Period` end date | Step A full + Step B (keyword-scoped) + Step C |
   | **Full** | 6+ such commits, OR this is the first `update` of a resumed session (SKILL.md `## Active Project`), OR uncertain | Step A + Step B + Step C, all full |

   **Step A: Code changes** — Search for code modifications related to the topic:
   - `git diff --stat` and `git diff --name-status HEAD` for uncommitted changes
   - `git log --oneline -20` for recent commits related to the topic
   - Grep/glob for topic keywords in modified files
   - Summarize what was changed, added, or removed in source code

   **Step B: Related documents** — Collect existing markdown/html docs related to the topic:
   - Scope by topic keywords, NOT a blind recursive walk. Use `grep -rl <keyword> docs/` to find candidates, then read only those.
   - Read and extract relevant content from each document found
   - Note any discrepancies between docs and actual code state

   **Step C: Progress tracking** — Separate completed work from future work:
   - **Completed**: What has been implemented, tested, analyzed, or decided
   - **Next steps**: What remains to be done, prioritized with `[Critical]`, `[High]`, `[Medium]`, `[Low]` tags
   - **Planned/Directional**: Designs or approaches that have been evaluated and deemed correct but not yet implemented

   If user provided specific instructions in the update command, follow those in addition to the 3 steps above.

3. **Part 1 — Investigation Docs** (`docs/devlog/<project>/`):

   a. Perform thorough analysis based on gathered context:
      - **Read source files**: Read the full content of relevant files (use parallel agents for large scopes)
      - **Cross-repo comparison**: If applicable, compare implementations across repos
      - **Trace data flows**: Follow function call chains and data transformations
      - **Build location maps**: Create tables showing where things happen (file:line → behavior)
      - **Calculate metrics**: Memory usage, FPS, CPU%, latency — when applicable
      - **Assess risks**: Severity/probability matrix when applicable

   b. Determine what distinct topic(s) the current work covers.

   c. **One topic per file**: each `.md` covers one topic. Apply the
      split-trigger rules in `reference/writing.md` — hard triggers create a new
      file, soft signals only suggest considering it; `01_<slug>.md` may stay a
      multi-finding overview.

   d. **If topic already has a file** (same theme as existing entry):
      - Update that `.md` file using Edit tool.
      - Update the `Period` end date to today.
      - Append new findings to relevant sections.
      - Update `Progress` (completed items, next steps).
      - Be conservative: only remove content that is fully obsolete.

   e. **If topic is new** (no existing file for this theme):
      - Determine the next sequence number (rule above).
      - Create new file — read `templates/investigation.md` (in this skill's directory) and follow it.
      - Do NOT modify existing files unless correcting outdated information.

4. **Part 2 — Work History** (`docs/devlog/<project>/history/`):

   This is the ONLY place `update` touches `history/`. It reads just the single
   latest entry as the append target ("History is not context", SKILL.md) — to
   decide topic continuity and append — never the full history, and never for
   context gathering.

   a. Analyze current session context:
      - Recent git activity: `git log --oneline -10`, `git diff --stat`
      - Work done in the current conversation session
      - Decisions made, problems encountered

   b. Determine topic continuity: compare the last history entry's topic with the current work.

   c. **If same topic** (work continues the same theme):
      - Update the last `.md` file in `history/` using Edit tool.
      - Update the `Period` end date to today.
      - Append new information to relevant sections (Changes, Decisions, Issues, Next Steps).
      - Remove completed items from Next Steps.
      - Be conservative: only remove content that is fully obsolete.

   d. **If different topic** (work shifted to a new theme):
      - Determine the next sequence number (rule above).
      - Create new file — read `templates/history.md` (in this skill's directory) and follow it.
      - Do NOT modify existing history files unless correcting outdated Next Steps.

5. **Part 3 — README maintenance** (`docs/devlog/<project>/README.md`, only if it exists):
   - Always update the `Period` end date.
   - If Part 2 created a NEW history file in this run, append its one-line row to the README `Entries` table inside the `<!-- AUTO-GENERATED -->` region.
   - Do NOT rescan or fully regenerate the README here — that is `reorg readme`. Only the `<!-- AUTO-GENERATED -->` region is ever touched; everything else is user-owned.

6. Output summary of what was investigated, key findings, and what was updated
   or created (in docs, history, and README).
