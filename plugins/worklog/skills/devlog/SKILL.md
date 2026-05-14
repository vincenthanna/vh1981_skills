---
name: devlog
description: Unified project documentation and work logging skill. Manages investigation reports and session work history as markdown files in docs/devlog/<project>/. Supports create, list, select, and update commands. Use this skill when the user wants to deeply analyze a codebase topic, create technical investigation reports, log work progress, document architecture decisions, or produce structured findings. Trigger phrases include "devlog", "investigate", "analyze this", "deep dive", "log my work", "save work history", "create devlog", "update devlog", "list devlogs", "select devlog". Do NOT use for git commits (use /commit), PR descriptions (use /pr), or CLAUDE.md updates (use /review-claudemd).
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
| *(no args)* | **Update** |

If the argument does not match any command above, treat it as `create <argument>` (assume user wants to create a new project with that name).

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
7. **Set active project**: write `<project>` to `docs/devlog/.active` (single line, no trailing newline). All subsequent `update` calls read this file first.
8. Output confirmation: "Created devlog `<project>` with `01_<topic-slug>.md` and `history/01_<topic-slug>.md`." End the output with the active-project marker line: `[devlog/active: <project>]`.

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
   - Read all `.md` files in the directory and `history/` to understand existing context.
   - **Set active project**: write `<project>` to `docs/devlog/.active` (single line, no trailing newline).
   - Output: "Selected devlog `<project>` as active. Use `/devlog update` to add new entries." End the output with the marker line: `[devlog/active: <project>]`.

---

## Command: Update

The update command performs TWO tasks in sequence: (A) update investigation docs, then (B) update work history.

### Steps

1. **Check active project**: read `docs/devlog/.active`. If the file is missing or empty, output the error — "No active project. Use `/devlog create <project>` or `/devlog select <project>` first."

2. **Read existing entries**: read ALL `.md` files in `docs/devlog/<project>/` and `docs/devlog/<project>/history/` sorted by filename.

3. **Gather context — 3 mandatory steps**:

   **Step A: Code changes** — Search for code modifications related to the topic:
   - `git diff --stat` and `git diff --name-status HEAD` for uncommitted changes
   - `git log --oneline -20` for recent commits related to the topic
   - Grep/glob for topic keywords in modified files
   - Summarize what was changed, added, or removed in source code

   **Step B: Related documents** — Collect ALL existing markdown/html docs related to the topic:
   - Scan `docs/` directory recursively for related `.md` and `.html` files
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

   c. **One topic per file**: Each `.md` file must cover exactly ONE topic. Never merge multiple distinct topics into a single file. If the current work spans multiple topics, create separate files for each.

   d. **If topic already has a file** (same theme as existing entry):
      - Update that `.md` file using Edit tool.
      - Update the `Period` end date to today.
      - Append new findings to relevant sections.
      - Update `Progress` (completed items, next steps).
      - Be conservative: only remove content that is fully obsolete.

   e. **If topic is new** (no existing file for this theme):
      - Determine the next sequence number (e.g., if last file is `03_xxx.md`, create `04_<new-topic>.md`).
      - Create new file — read `templates/investigation.md` (in this skill's directory) and follow it.
      - Do NOT modify existing files unless correcting outdated information.

5. **Part 2 — Work History** (`docs/devlog/<project>/history/`):

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
      - Determine the next sequence number.
      - Create new file — read `templates/history.md` (in this skill's directory) and follow it.
      - Do NOT modify existing history files unless correcting outdated Next Steps.

6. Output summary of what was investigated, key findings, and what was updated or created (in both docs and history). End the output with the marker line: `[devlog/active: <project>]`.

---

## Investigation doc vs History entry — what goes where

- **Investigation doc** = *durable knowledge* about the system: how it works, what was found, why decisions were made. Re-readable months later as a reference. No chronological narration of the work session.
- **History entry** = *what happened this session*: commands run, commits made, problems hit — in chronological order. A disposable timeline.
- **Never duplicate**: if a fact lives in the investigation doc, the history entry only references it ("see `02_xxx.md` Finding 2"), and vice versa. Give the two files different titles — the same title is a signal of duplication.

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

---

## Output Quality Rules

- **Tables over prose**: Use markdown tables for comparisons, location maps, risk assessments, and metrics.
- **Code references**: Always include `file:line` references so the reader can navigate to source.
- **Data flow notation**: Use `A → B → C` with annotations for describing pipelines and call chains.
- **Quantitative over qualitative**: Prefer "32MB per view" over "significant memory usage".
- **Conclusions must be actionable**: End with prioritized recommendations, not just observations.
- **Korean or English**: Match the language the user has been using in the session.

---

## Rules

- **One topic per file**: NEVER merge multiple distinct topics into a single file. If analysis covers architecture + scaling + optimization, create 3 separate files. When in doubt, split.
- **Never delete existing files** — only edit or append.
- **Be conservative with edits** — preserve historical accuracy. Only remove content that is fully obsolete.
- **Topic slugs**: lowercase, hyphens, descriptive (e.g., `appsrc-scaling-analysis`, not `update-3`). For multi-phase work, slug the outcome/decision, not the journey. Project names follow the same rule — prefer the work's nature (`rtmp-stall-investigation`) over a bare JIRA ticket ID (`pii-2176`); a `<ticket>-<topic>` combination is fine.
- **Period field**: the first-to-last date this doc was *edited* — not the calendar span of the underlying work. Always update the end date to today when editing, using the resolved `Today` from the context header (never a remembered or guessed date). If the work's calendar span matters, record it separately in the body.
- **Read before writing**: Always read relevant source code before producing findings. Never guess.
- **Progress section is mandatory**: Every investigation doc must have a `Progress` section with `Done` and `Remaining / Next` subsections. Use priority tags: `[Critical]`, `[High]`, `[Medium]`, `[Low]`.
- **3 mandatory gather steps**: When updating, always perform Step A (code changes), Step B (related docs), Step C (progress tracking) before writing.
- **Active project**: tracked via the `docs/devlog/.active` file (written by `create`/`select`, read by `update`). Every `create`/`select`/`update` output ends with the marker line `[devlog/active: <project>]` so the active project stays visible in context. A stale `.active` from a prior session should be re-confirmed with the user before use.
- **This skill is read-only for source code**: It investigates and documents but does NOT modify application source code. If code changes are needed, recommend them in the Conclusion section.
