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

Detailed procedures live in `commands/*.md` in this skill's directory (`update`, `upload`, `reorg`, `validation`) — read the relevant file when routing lands on that command. Doc-writing rules (what goes where, templates, split triggers, output quality) live in `reference/writing.md` — read it once per session before writing or editing devlog docs.

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

`docs/devlog/.active` (one line, no trailing newline) records the last project explicitly `select`ed or `create`d in this repo. It is a **cross-session resume hint, not authoritative state**: multiple Claude sessions may run concurrently in one repo and overwrite it at any time, so this session's own devlog record (level 2 below) always outranks the file — weaker inference (level 4) does not. `create` and `select` write it, and `reorg rename` fixes it when it names the renamed project; for resolution, commands consult it only where these rules explicitly say so (level 3, and the level-2 compaction check / missing-directory handling below).

**Marker line (stated once here — command procedures do not repeat it)**: every command output that resolves an active project ends with the marker line `[devlog/active: <project>]`.

### Resolving the active project

When a command needs the active project and no name was given explicitly, resolve in this priority order — lower number first; if one level yields 2+ tied candidates, stop and ask the user:

1. **Explicit `select` / `create`** in the current message — authoritative.
2. **This session's own record** — in order: (i) the project this session most recently `select`ed or `create`d; (ii) failing that, the project a prior devlog command this session resolved — its `[devlog/active: <project>]` marker line in this conversation is the evidence; (iii) failing that, the project(s) whose `docs/devlog/<X>/` files this session Read or Edited via tool calls — grep hits alone do not count, nor do files read only as context-gathering during an update's related-document sweep; 2+ distinct projects are tied candidates. When this level resolves from evidence visible in context, do not consult `.active` — another session may have rewritten it, and this session's record wins.
   - **Compaction demotion**: if the record survives only in a compacted-context summary (the actual command, marker line, or file reads are no longer visible in context), treat the session as resumed and cross-check `.active` once — if it matches, proceed silently; if it names a different existing project, stop and ask the user once. This mitigates summary distortion; it does not fully solve it.
   - **Missing directory**: level 2 resolves only if `docs/devlog/<X>/` still exists. If it is gone, do NOT recreate it — another session likely renamed or archived it. Check `.active` and `git log --oneline -- docs/devlog/<X>` for the successor, report what you found, and ask before proceeding.
3. **`docs/devlog/.active`** — fresh-session resume only: the session has no record of its own and the file points to an existing project directory.
4. **Conversation topic match** — a project whose `README` / `01_*.md` keywords match the recent conversation.
5. None of the above → error: "No active project. Use `/devlog create <project>` or `/devlog select <project>` first."

- Level 1 proceeds silently, then shows the marker.
- Level 2 proceeds without confirmation (marker only) — except the compaction and missing-directory cases above.
- Levels 3–4 are resumptions/inferences: proceed with a single candidate, flagging the marker — `[devlog/active: <project> — resumed from .active]` / `[devlog/active: <project> — inferred from topic]`. With 2+ candidates, stop and ask. Exception — external writes: when `upload` resolved its project via level 3–4, confirm the project name with the user once before copying.
- **Broken `.active`**: if the file is absent, skip level 3 silently. If it names a missing project directory, ignore it (fall through to level 4) and add one line before the marker: "`.active` names missing project `<x>`; ignored." Never treat a recent mtime as evidence of freshness or ownership — concurrent sessions write the file at arbitrary times; resolution never runs `stat`. Staleness surfaces through the recap, not the filesystem.

### History is not context

Never read `history/` to understand the project, gather context, resume state, build the README, or answer a question — investigation docs are the source of truth for project content. Read a history entry ONLY when (a) the user explicitly asks to look at the history / a past session, or (b) `update` Part 2 appends to the single latest entry — a write-target read of that one file, not context gathering. Older or other history entries are read only on explicit request.

### Session re-entry — previous-state recap

A session is **resumed** for a project when its active status was first established this session via level 3 or 4 (not by `select` / `create`), or via the level-2 compaction demotion above.

**Previous-state recap** = the short orientation printed when re-entering a project so work can continue. Trigger it on a `select`, and on the first `update` of a resumed session. Produce it at most once per resumed session — a `select` satisfies it, so a first `update` immediately after does not repeat it.

To build it (cheapest source first — do NOT read every doc):

1. Read `README.md` (if present). Its `Entries` index and AUTO-GENERATED `Remaining / Next (summary)` are the primary source of open items — trust them instead of re-reading the docs they summarize.
2. Read the latest investigation doc in full. Never read `history/`.
3. Only if the README is missing, or its AUTO-GENERATED region is absent or stale (README `Period` end date older than the newest investigation doc's), collect open items by grep instead of full reads:
   ```
   grep -rn -E "\[(Critical|High)\]" docs/devlog/<project>/ --include="*.md" --exclude-dir=history --exclude-dir=_archived
   ```
   Priority tags stay English in every project language, so this is reliable. Read in full only the docs the grep shows still carrying open `[Critical]` / `[High]` items.
4. Print 1–3 lines: **current state** (what is done / verified) · **open items** (the `[Critical]` / `[High]` entries, each tagged with its source file) · a **suggested next step** or two.

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
5. Read `reference/writing.md` (in this skill's directory) if not already read this session — it carries the doc-writing rules and template pointers.
6. Create investigation doc `01_<topic-slug>.md` in `docs/devlog/<project>/` — read `templates/investigation.md` (in this skill's directory) and follow it.
7. Create work history `history/01_<topic-slug>.md` — read `templates/history.md` (in this skill's directory) and follow it.
8. Create `docs/devlog/<project>/README.md` — read `templates/readme.md` (in this skill's directory) and follow it.
9. **Set active project**: write `<project>` to `docs/devlog/.active` (single line, no trailing newline) — the cross-session resume hint. Subsequent commands resolve the active project per `## Active Project`.
10. Output confirmation: "Created devlog `<project>` with `README.md`, `01_<topic-slug>.md`, and `history/01_<topic-slug>.md`."

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
   - **Set active project**: write `<project>` to `docs/devlog/.active` (single line, no trailing newline).
   - Build and print the **previous-state recap** (see `## Active Project`) — this is what orients the user to continue, not a bare confirmation.
   - Print `Selected devlog <project> as active — /devlog update to continue.`, then the marker line as the final line.

---

## Command: Update

Performs three parts in sequence: update investigation docs, update work history, refresh the README's AUTO-GENERATED region.

1. Resolve the active project per `## Active Project` (error if level 5 is reached).
2. **Read `commands/update.md` (in this skill's directory) and follow it** — it defines the scoped read, the gather-intensity scaling, and the three parts. Do not run the procedure from memory. If the file is already in context from an earlier call this session, do not re-read it.

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

Publishes a devlog project to an external knowledge-base repo — a bulk copy of `docs/devlog/<project>/` into the target; no git commit. Syntax: `upload [<project>] [--to <path>]` (positional `upload <project> <path>` also accepted); `--to` saves the target to `docs/devlog/.upload-target` as the new default.

**Read `commands/upload.md` (in this skill's directory) for target resolution and the copy procedure.**

---

## Project layout

A devlog project directory holds these path types:

- `docs/devlog/<project>/NN_<topic>.md` — investigation docs (top level)
- `docs/devlog/<project>/history/NN_<topic>.md` — history entries
- `docs/devlog/<project>/<subtopic>/NN_<topic>.md` — investigation docs grouped under a subtopic folder (trigger in `reference/writing.md`)
- `docs/devlog/<project>/_archived/` — superseded docs, kept for the record
- `docs/devlog/<project>/README.md` — project index (see `Command: Create`)

The full path/artifact-type reference table lives in `reference/layout.md` (read it only when reorganizing). Validation-campaign paths (`runs/`, `comparisons/`) are defined by the validation command, not here.

---

## Rules

- **Archive over delete**: never `rm` a devlog file. Edit or append in place; to remove an obsolete doc, use `reorg archive` — it moves the doc to `_archived/` with a logged reason.
- **This skill is read-only for source code**: it investigates and documents but does NOT modify application source code. If code changes are needed, recommend them in the Conclusion section.
- **Doc-writing rules** (investigation-vs-history routing, templates, one-topic-per-file split triggers, subtopic folders, cross-references, slugs, `Period`, `Progress`, depth levels, output quality) live in `reference/writing.md` — read it once per session before writing or editing devlog docs.
