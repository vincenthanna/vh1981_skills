---
name: devlog
description: Unified project documentation and work logging skill. Manages investigation reports and session work history as markdown files in docs/devlog/<project>/. Supports create, list, select, update, and upload commands. Use this skill when the user wants to deeply analyze a codebase topic, create technical investigation reports, log work progress, document architecture decisions, produce structured findings, or publish a devlog project to an external knowledge-base repo. Trigger phrases include "devlog", "investigate", "analyze this", "deep dive", "log my work", "save work history", "create devlog", "update devlog", "list devlogs", "select devlog", "upload devlog", "publish to knowledge base", "sync to knowledge base", "run validation condition", "register a run", "compare conditions", "validation campaign", "ablation run". Do NOT use for git commits (use /commit), PR descriptions (use /pr), or CLAUDE.md updates (use /review-claudemd).
---

# Devlog Context

- **Current branch**: !`git branch --show-current`
- **Today**: !`date +%Y-%m-%d`
- **Existing projects**: Check `docs/devlog/` directory when needed (may not exist yet)

---

## Command Routing

Parse the arguments to determine which command to run:

| Input | Command |
|-------|---------|
| `create <project>` | **Create** |
| `list` | **List** |
| `select <project>` | **Select** |
| `update` | **Update** |
| `update <instructions>` | **Update** with specific instructions |
| `reorg <action> [args]` | **Reorg** (rename / archive / cleanup / readme) |
| `rename <old> <new>` | **Reorg** — alias for `reorg rename` |
| `run <condition-name>` | **Validation** — register a measurement run |
| `compare <condition> ...` | **Validation** — build/grow a comparison report |
| `upload [<project>] [--to <path>]` | **Upload** — publish to an external knowledge-base repo |
| *(no args)* | **Update** |

If the first token is not one of the reserved commands above (`create`, `list`, `select`, `update`, `reorg`, `rename`, `run`, `compare`, `upload`), treat the whole argument as `create <argument>` (assume the user wants a new project with that name).

### Chained invocation guard

When `create` / `select` / `update` are invoked in immediate succession within the same response, do NOT re-execute work the prior command already did:

- **`select` right after `create`** → no-op. The active project is already set; do NOT re-read all `.md` files. Just confirm.
- **`update` right after `create`** → only append genuinely new information produced since creation. Do NOT re-run the full gather — the creation context is still fresh.

---

## Granularity decision (before `create`)

Before creating a new project, decide the right granularity:

- Same JIRA/PR, same component, continuation of prior work → prefer `update` on the existing project (add a new `NN_<topic>.md` if the topic genuinely differs).
- New problem domain, or a deliberate pivot / abandonment of a prior approach → `create` a new project.
- When unsure, prefer `update` with a new file over `create` — splitting one effort across projects fragments its history.

---

## Active Project

The active project is tracked in `docs/devlog/.active` (one line, no trailing newline). `create` and `select` write it; `update` reads it. Every `create` / `select` / `update` output ends with the marker line `[devlog/active: <project>]`.

### Resolving the active project

When a command needs the active project and no name was given explicitly, resolve in this priority order — lower number first; if one level yields 2+ tied candidates, stop and ask the user:

1. **Explicit `select` / `create`** in the current message — authoritative.
2. **`docs/devlog/.active`** — if it points to an existing project directory.
3. **Recent file activity** — a `docs/devlog/<X>/` file Read or Edited earlier in this session.
4. **Conversation topic match** — a project whose `README` / `01_*.md` keywords match the recent conversation.
5. None of the above → error: "No active project. Use `/devlog create <project>` or `/devlog select <project>` first."

- Levels 1–2 proceed silently, then show `[devlog/active: <project>]`.
- Levels 3–4 are inferences: proceed even with a single candidate, but the marker MUST flag it — `[devlog/active: <project> — inferred from file activity]`. With 2+ candidates at level 3–4, stop and ask.
- **Stale `.active`**: if it points to a missing directory, or its mtime predates this session, treat it as a candidate to re-confirm with the user — not an authoritative answer.

### Session re-entry

On the FIRST `update` after a `select` (resuming prior-session work), read the latest investigation doc's `Remaining / Next` (and `README.md` if present), and print a 1–3 line "previous state" summary before gathering. Do NOT read `history/` for this — investigation docs are the source of resume state. Once per resumed session only.

### Scoped read (single source of truth)

This section is the ONLY definition of what `update` reads. `update` does NOT read every `.md` file. It reads: `docs/devlog/.active`, the project `README.md` (if any), and the investigation docs whose slug matches the current topic. A full read happens only on the first `select` of a project in a session, or when the user explicitly asks for full context — and a "full read" still means all *investigation* docs (plus `README.md`), never the `history/` folder. (The gather-intensity table in `Command: Update` decides *how hard* to gather; this decides *what* to read.)

**History is not context.** Never read `history/` to understand the project, gather context, resume state, build the README, or answer a question — investigation docs are the source of truth for project content. Read a history entry ONLY when (a) the user explicitly asks to look at the history / a past session, or (b) `update` Part 2 appends to the single latest entry — a write-target read of that one file, not context gathering. Older or other history entries are read only on explicit request.

---

## Command: Create

### Steps

1. Sanitize `<project>`: lowercase, hyphens for spaces, alphanumeric and hyphens only.
2. Create directories: `docs/devlog/<project>/` and `docs/devlog/<project>/history/` (create parent dirs if they don't exist). Immediately after, run `git check-ignore docs/devlog/<project>`. If it is ignored, tell the user these devlog files are local-only (not committed) so they set expectations correctly. The skill does not commit anything.
3. Analyze the current conversation context:
   - What has been discussed and investigated in this session
   - Current git branch and recent commits (`git log --oneline -10`)
   - Recent diff (`git diff --stat HEAD~5..HEAD 2>/dev/null || git diff --stat`)
4. Determine a topic slug from the primary work/investigation theme (e.g., `cloud-mode-architecture`, `int8-model-support`).
5. Create investigation doc `01_<topic-slug>.md` in `docs/devlog/<project>/` — read `templates/investigation.md` (in this skill's directory) and follow it.
6. Create work history `history/01_<topic-slug>.md` — read `templates/history.md` (in this skill's directory) and follow it.
7. Create `docs/devlog/<project>/README.md` — read `templates/readme.md` (in this skill's directory) and follow it.
8. **Set active project**: write `<project>` to `docs/devlog/.active` (single line, no trailing newline). All subsequent `update` calls read this file first.
9. Output confirmation: "Created devlog `<project>` with `README.md`, `01_<topic-slug>.md`, and `history/01_<topic-slug>.md`." End the output with the active-project marker line: `[devlog/active: <project>]`.

---

## Command: List

### Steps

1. Scan `docs/devlog/` for project subdirectories using `ls` (Glob cannot list directories). Example: `ls docs/devlog/`.
2. For each project directory, count `.md` files in root (docs) using `docs/devlog/<project>/*.md` glob and in `history/` using `docs/devlog/<project>/history/*.md` glob separately.
3. Output a table:

```
Projects:
  <project-1>  (2 docs, 3 history entries)
  <project-2>  (1 doc, 1 history entry)
```

4. If no directories exist, output: "No devlogs found. Use `/devlog create <project>` to start one."

---

## Command: Select

### Steps

1. Check if `docs/devlog/<project>/` exists.
2. If NOT found: scan `docs/devlog/*/` and output available projects — "Project `<project>` not found. Available: <list>. Use `/devlog create <project>` to start one."
3. If found:
   - Read the investigation docs and `README.md` to understand existing context. Do NOT read `history/` — it is the work-log timeline, not project content; read it only if the user explicitly asks to review past sessions.
   - **Set active project**: write `<project>` to `docs/devlog/.active` (single line, no trailing newline).
   - Output: "Selected devlog `<project>` as active. Use `/devlog update` to add new entries." End the output with the marker line: `[devlog/active: <project>]`.

---

## Command: Update

The update command performs TWO tasks in sequence: (A) update investigation docs, then (B) update work history.

### Steps

1. **Check active project**: resolve it per the `## Active Project` section (priority order; error if level 5 is reached).

2. **Read existing entries (scoped)**: read only what `## Active Project` → "Scoped read" specifies — not every file. On the first `select` of this project in the session, do the full read instead.

3. **Gather context — intensity-scaled**:

   Pick the gather intensity from observable signals (no subjective "little has changed"):

   | Intensity | When | Scope |
   |-----------|------|-------|
   | **Light** | `git diff --stat` shows 0 changed files AND a prior `/devlog` call already ran in this same response | Step C only |
   | **Normal** | 1–5 commits since the latest investigation doc's `Period` end date | Step A full + Step B (keyword-scoped) + Step C |
   | **Full** | 6+ such commits, OR `.active` is older than this session, OR uncertain | Step A + Step B + Step C, all full |

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

4. **Part 1 — Investigation Docs** (`docs/devlog/<project>/`):

   a. Perform thorough analysis based on gathered context:
      - **Read source files**: Read the full content of relevant files (use parallel agents for large scopes)
      - **Cross-repo comparison**: If applicable, compare implementations across repos
      - **Trace data flows**: Follow function call chains and data transformations
      - **Build location maps**: Create tables showing where things happen (file:line → behavior)
      - **Calculate metrics**: Memory usage, FPS, CPU%, latency — when applicable
      - **Assess risks**: Severity/probability matrix when applicable

   b. Determine what distinct topic(s) the current work covers.

   c. **One topic per file**: each `.md` covers one topic. Apply the split-triggers rule in `Rules` — hard triggers create a new file, soft signals only suggest considering it; `01_<slug>.md` may stay a multi-finding overview.

   d. **If topic already has a file** (same theme as existing entry):
      - Update that `.md` file using Edit tool.
      - Update the `Period` end date to today.
      - Append new findings to relevant sections.
      - Update `Progress` (completed items, next steps).
      - Be conservative: only remove content that is fully obsolete.

   e. **If topic is new** (no existing file for this theme):
      - Determine the next sequence number: actually list the directory's `.md` files, take the highest `NN_` prefix and add 1. If two files already share an `NN_`, report the collision. Never guess from memory.
      - Create new file — read `templates/investigation.md` (in this skill's directory) and follow it.
      - Do NOT modify existing files unless correcting outdated information.

5. **Part 2 — Work History** (`docs/devlog/<project>/history/`):

   This is the ONLY place `update` touches `history/`. It reads just the single latest entry as the append target (per the "History is not context" rule) — to decide topic continuity and append — never the full history, and never for context gathering.

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
      - Determine the next sequence number the same way: list `history/`, take the highest `NN_` + 1, report any duplicate `NN_`. Never guess.
      - Create new file — read `templates/history.md` (in this skill's directory) and follow it.
      - Do NOT modify existing history files unless correcting outdated Next Steps.

6. **Part 3 — README maintenance** (`docs/devlog/<project>/README.md`, only if it exists):
   - Always update the `Period` end date.
   - If Part 2 created a NEW history file in this run, append its one-line row to the README `Entries` table inside the `<!-- AUTO-GENERATED -->` region.
   - Do NOT rescan or fully regenerate the README here — that is `reorg readme`. Only the `<!-- AUTO-GENERATED -->` region is ever touched; everything else is user-owned.

7. Output summary of what was investigated, key findings, and what was updated or created (in docs, history, and README). End the output with the marker line: `[devlog/active: <project>]`.

---

## Command: Reorg

Reorganization actions, grouped under one command. Routing: `reorg <action> [args]`, plus `rename` as a top-level alias for `reorg rename`. If `reorg` is called with no action, list the available actions.

| Action | Purpose |
|--------|---------|
| `reorg rename <old> <new>` | rename a project, fix all cross-references |
| `reorg archive <path>` | isolate an obsolete doc/subtopic into `_archived/` |
| `reorg cleanup` | propose hygiene fixes (duplicate `NN_`, broken refs, empty files) — proposal only, never auto-executes |
| `reorg readme` | fully regenerate the README's `<!-- AUTO-GENERATED -->` region |
| `reorg move` | reserved — not yet implemented; tell the user it is unavailable |

**Read `commands/reorg.md` (in this skill's directory) for the step-by-step procedure of the requested action.** Never `rm` a file directly — removal goes through `reorg archive`. Every reorg action is meta/housekeeping work: record it as one line in history, not as a new investigation doc.

---

## Command: Validation (run / compare)

For validation/ablation campaigns — each measurement adds a *condition* to the active project rather than a new investigation topic.

| Command | Purpose |
|---------|---------|
| `run <condition-name>` | register one measurement run — writes a manifest under `runs/<condition-name>/`. **`run` writes the manifest only; it does NOT execute the experiment.** |
| `compare <condition> ...` | build or grow a side-by-side comparison under `comparisons/` — grows existing reports (adds columns/rows, dated supersede notes), never silently rewrites |

**Read `commands/validation.md` (in this skill's directory) for the step-by-step procedure.** Run artifacts live in `docs/devlog/<project>/runs/<condition-name>/` and comparison reports in `docs/devlog/<project>/comparisons/` — not in ad-hoc date-stamped directories.

---

## Command: Upload

Publish a devlog project to an external knowledge-base repo so the docs are visible alongside other projects.

### Syntax

| Form | Meaning |
|------|---------|
| `upload` | upload the active project to the saved target |
| `upload <project>` | upload `<project>` to the saved target |
| `upload --to <path>` | upload the active project to `<path>`, and save `<path>` as the new default |
| `upload <project> --to <path>` | upload `<project>` to `<path>`, and save it as the new default |
| `upload <project> <path>` | positional form — same as `upload <project> --to <path>` |

`<path>` is the absolute or `~`-expanded path of a knowledge-base repo (e.g. `~/workspace/ds_knowledge_base`). Expand `~` before use.

### Target-path resolution

Resolve in this priority order, error out if all fail:

1. Explicit `--to <path>` (or trailing positional) in the current command — and save it to `docs/devlog/.upload-target` for future calls.
2. `docs/devlog/.upload-target` (single line, repo absolute path) — written by a prior `upload` call.
3. Error: "No upload target. Use `/devlog upload <project> --to <path>` first."

### Steps

1. Parse `<project>` and `<path>`. If `<project>` was not given, resolve the active project per the `## Active Project` rules.
2. Resolve the target path as described above. If level 1 supplied a new path, write it (single line, no trailing newline) to `docs/devlog/.upload-target`.
3. Validate target:
   - Target directory exists. If not, ask the user before creating it — do not silently `mkdir` an external repo.
   - If `<target>/projects/` exists, use `<target>/projects/<project>/` as the destination root (knowledge-base convention).
   - Otherwise, default to `<target>/<project>/` and warn the user in the output that the target lacks a `projects/` directory.
4. `mkdir -p <dest>` if it doesn't exist.
5. Copy `docs/devlog/<project>/` recursively into `<dest>`, overwriting same-named files. Files that exist only in the destination are left untouched (no delete sync). The copy includes everything under the project directory — investigation docs, `history/`, `runs/`, `comparisons/`, `_archived/`, `README.md`.
   - Use `cp -a docs/devlog/<project>/. <dest>/` (the trailing `/.` copies contents into `<dest>` directly).
   - Do NOT copy `docs/devlog/.active` or `docs/devlog/.upload-target` — those are not inside the project directory anyway, but verify with `ls -A docs/devlog/<project>/` before the copy.
6. Count copied files (`find <dest> -type f -newer ...` is overkill — just count source files: `find docs/devlog/<project>/ -type f | wc -l`).
7. Output a one-line summary in the form:
   ```
   Uploaded <project> → <dest>  (N files)
   ```
   If step 2 wrote a new `.upload-target`, add a second line: `Saved target to docs/devlog/.upload-target`. If the destination layout was non-standard (no `projects/`), add a warning line. End with the marker `[devlog/active: <project>]`.

### Notes

- `upload` does NOT git-commit anything in the target repo. The user runs `cd <target> && git add . && git commit` themselves.
- `upload` is read-only against the source devlog — it only writes to the destination and to `docs/devlog/.upload-target`.
- This is a bulk copy, not a merge. Hand-edits in the destination that diverge from the source will be overwritten.
- `.upload-target` lives at `docs/devlog/.upload-target` (one path per repo, shared across all projects in this repo). To change the target, pass `--to <new-path>` and it will be overwritten.

---

## Project layout

A devlog project directory holds these path types:

- `docs/devlog/<project>/NN_<topic>.md` — investigation docs (top level)
- `docs/devlog/<project>/history/NN_<topic>.md` — history entries
- `docs/devlog/<project>/<subtopic>/NN_<topic>.md` — investigation docs grouped under a subtopic folder (see trigger below)
- `docs/devlog/<project>/_archived/` — superseded docs, kept for the record
- `docs/devlog/<project>/README.md` — project index (see `Command: Create`)

Do not create template-outside root files (`PII-XXXX-pr-summary.md`, raw prompt dumps, etc.) — absorb that content into an investigation doc or follow the `NN_<topic>.md` naming.

**Subtopic folder trigger**: keep docs flat in the project root until investigation docs grow past roughly 5–6 AND at least 3 of them share a common topic-slug prefix (e.g. `clustering-eval`, `clustering-params`, `clustering-fps` → prefix `clustering`). Only then *consider* grouping those into a `<prefix>/` subtopic folder, and only if it clearly improves navigation. No preemptive foldering. When a folder is created or files are moved, say so in the output (one line).

The full path/artifact-type reference table lives in `reference/layout.md` (read it only when reorganizing). Validation-campaign paths (`runs/`, `comparisons/`) are defined by the validation command, not here.

---

## Cross-references

When a devlog doc references another devlog doc, use a single path form:

- Always a repo-relative full path: `docs/devlog/<project>/NN_<slug>.md` (history and subtopic paths likewise, e.g. `docs/devlog/<project>/history/NN_<slug>.md`).
- References outside devlog (memory files, repo source) — a repo-relative or absolute path plus a one-line note.
- Never put a ticket ID or commit SHA in a path component — it breaks on rename/squash.

This single form is what makes `reorg rename` and `reorg cleanup` reliable. **Premise**: file moves and renames go through `reorg` — it auto-substitutes cross-references and shows the match list for approval. Avoid manual `mv` of devlog files.

---

## Investigation doc vs History entry — what goes where

- **Investigation doc** = *durable knowledge* about the system: how it works, what was found, why decisions were made. Re-readable months later as a reference. No chronological narration of the work session.
- **History entry** = *what happened this session*: commands run, commits made, problems hit — in chronological order. A disposable timeline.
- **Never duplicate**: if a fact lives in the investigation doc, the history entry only references it ("see `02_xxx.md` Finding 2"), and vice versa. Give the two files different titles — the same title is a signal of duplication.

| Output of the work | Goes to |
|--------------------|---------|
| Code analysis / tracing result (with `file:line` refs) | Investigation doc |
| Performance / measurement data (tables, metrics) | Investigation doc |
| Architecture decision + its rationale | Investigation doc — `Conclusion` |
| List of changed files + why each changed | History entry — `Changes` |
| Commands / tests / builds run, problems hit | History entry |
| Future work items | Both — but History keeps only a short pointer to the investigation doc's `Remaining / Next` |
| Ambiguous / both seem to apply | Default to History as the primary record; the investigation doc references it ("see `history/NN`") |

Do not print classification labels to the user — this table is an internal routing rule.

**Meta / housekeeping work** — devlog's own tidying (rename, README refresh, cross-ref fixes, `NN_` renumbering, splitting/merging docs) does NOT get a new investigation doc. Record it as one line in the history `Changes` section, and if relevant one line in an investigation doc's `Done`. If investigation or implementation work is mixed in, record that normally too — the meta exemption applies only to pure tidying.

---

## Templates

Two template files back the investigation docs and history entries. At the step that creates a NEW file, **read the relevant template from this skill's directory first**:

- **Investigation doc** → `templates/investigation.md` — for `docs/devlog/<project>/NN_<topic>.md`
- **History entry** → `templates/history.md` — for `docs/devlog/<project>/history/NN_<topic>.md`

**Language**: render section *headers* in the session's language, but keep field *keys* (`Branch`, `Period`, `Summary`) in English for grep-ability across mixed-language devlogs.

---

## Investigation Depth Levels

The depth of investigation should match the complexity of the topic and user's request:

### Quick
- Grep/glob for relevant files
- Read key files only (not exhaustive)
- Summary-level findings
- No diagrams

### Medium (default)
- Thorough file search across relevant directories
- Read all related files
- Detailed findings with tables and code references
- Data flow traces
- Risk assessment if applicable

### Deep
- Exhaustive search across entire repo (and cross-repo if applicable)
- Read every related file completely
- Detailed calculations (memory, performance, scaling)
- Cross-reference with documentation and git history
- Mermaid diagrams
- Comprehensive risk matrix

### Output length
Match output length to investigation depth — but there is **no hard line-count cap**. If a doc runs long relative to its depth: move measurement data and logs into a `data/` directory, split off any genuinely separate topic (see split triggers), and otherwise compress. Never truncate to hit a number — relocate instead.

---

## Output Quality Rules

- **Tables over prose**: Use markdown tables for comparisons, location maps, risk assessments, and metrics.
- **Code references**: Always include `file:line` references so the reader can navigate to source.
- **Data flow notation**: Use `A → B → C` with annotations for describing pipelines and call chains.
- **Quantitative over qualitative**: Prefer "32MB per view" over "significant memory usage".
- **Conclusions must be actionable**: End with prioritized recommendations, not just observations.
- **Language consistency**: one project, one language — follow the first doc's language (usually the session's). Section header *text* and prose go in the project language; field *keys* (`Branch`, `Period`, `Summary`), priority tags (`[Critical]` …), and code / `file:line` references stay in English. Do not force-migrate existing files to a different language.

---

## Rules

- **One topic per file; split triggers**: each `.md` covers one topic. **Hard triggers** (act — create a new file): the user explicitly asks to split, OR non-prose artifacts (measurement data, logs) are getting mixed into prose analysis. **Soft signals** (only *consider* splitting, not automatic): a section dwarfs the rest of the file, the same finding is being augmented across multiple updates, or a finding starts growing its own Risk/Data-Flow subsections. **Create exception**: the first file `01_<slug>.md` may stay a multi-finding overview. When a split actually happens, say so in the output (one line). Entry points: new project → `Granularity decision`; one file growing too big → these split triggers; many related files → the subtopic-folder trigger in `Project layout`.
- **Archive over delete**: never `rm` a devlog file. Edit or append in place; to remove an obsolete doc, use `reorg archive` — it moves the doc to `_archived/` with a logged reason.
- **Be conservative with edits** — preserve historical accuracy. Only remove content that is fully obsolete.
- **Topic slugs**: lowercase, hyphens, descriptive (e.g., `appsrc-scaling-analysis`, not `update-3`). For multi-phase work, slug the outcome/decision, not the journey. Project names follow the same rule — prefer the work's nature (`rtmp-stall-investigation`) over a bare JIRA ticket ID (`pii-2176`); a `<ticket>-<topic>` combination is fine.
- **Period field**: the first-to-last date this doc was *edited* — not the calendar span of the underlying work. Always update the end date to today when editing, using the resolved `Today` from the context header (never a remembered or guessed date). If the work's calendar span matters, record it separately in the body.
- **Read before writing**: Always read relevant source code before producing findings. Never guess.
- **Progress section is mandatory**: Every investigation doc must have a `Progress` section with `Done` and `Remaining / Next` subsections. Use priority tags: `[Critical]`, `[High]`, `[Medium]`, `[Low]`.
- **Gather is intensity-scaled**: `update` picks Light / Normal / Full from observable signals (see the gather-intensity table in `Command: Update`). Step A/B/C are scaled to that intensity, not always run in full.
- **Active project**: see the `## Active Project` section — tracked via `docs/devlog/.active`, resolved by the priority order there, and surfaced in every command output via the `[devlog/active: …]` marker.
- **This skill is read-only for source code**: It investigates and documents but does NOT modify application source code. If code changes are needed, recommend them in the Conclusion section.
