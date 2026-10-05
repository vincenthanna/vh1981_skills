---
name: worklog
description: DEPRECATED legacy skill, superseded by vh1981:devlog. Manages session work logs in docs/history/<subject>/ for repos that still use that old layout. Use ONLY when the user explicitly types /worklog or names the "worklog" skill, or asks to keep working in an existing docs/history/<subject>/ tree. For any new investigation, deep dive, analysis report or work log, use vh1981:devlog instead.
---

> **Deprecated.** 새 작업은 `vh1981:devlog` 를 쓴다. 이 스킬은 `docs/history/<subject>/` 를 이미 쓰는 repo의 기존 문서를 이어 쓸 때만 쓴다. 문서 작성 규칙은 devlog와 같이 `doc-style.md` 와 `output-principles.md` 를 따른다.

# Worklog Context

- **Current branch**: !`git branch --show-current`
- **Today**: !`date +%Y-%m-%d`
- **Existing worklogs**: Check `docs/history/` directory when needed (may not exist yet)

---

## Command Routing

Parse the arguments to determine which command to run:

| Input | Command |
|-------|---------|
| `create <subject>` | **Create** |
| `list` | **List** |
| `select <subject>` | **Select** |
| `update` | **Update** |
| *(no args)* | **Update** |

If the argument does not match any command above, treat it as `create <argument>` (assume user wants to create a new worklog with that subject name).

---

## Command: Create

### Steps

1. Sanitize `<subject>`: lowercase, hyphens for spaces, alphanumeric and hyphens only.
2. Create directory: `docs/history/<subject>/`
3. Analyze the current conversation context:
   - Current git branch and recent commits (`git log --oneline -10`)
   - Recent diff (`git diff --stat HEAD~5..HEAD 2>/dev/null || git diff --stat`)
   - What was discussed and worked on in this session
4. Determine a topic slug from the primary work theme (e.g., `int8-model-support`, `ci-failure-analysis`).
5. Create `01_<topic-slug>.md` using this template:

```markdown
# <Descriptive Title>

- **Branch**: <branch-name or JIRA tag>
- **Period**: <today> ~ <today>

## Summary
<1-3 line summary of the work>

## Changes
<List of modified files, what changed, and why>

## Decisions
<Key decisions made and their rationale>

## Issues & Blockers
<Problems encountered, unresolved items>

## Next Steps
<Remaining work items>
```

6. Output confirmation: "Created worklog `<subject>` with `01_<topic-slug>.md`. This is now the active worklog for this session."
7. **Set active worklog**: remember `<subject>` as the active worklog for subsequent `/worklog update` calls in this session.

---

## Command: List

### Steps

1. Scan `docs/history/*/` for subdirectories.
2. For each subject directory, count the `.md` files inside.
3. Output a table:

```
Worklogs:
  <subject-1>  (3 entries)
  <subject-2>  (1 entry)
```

4. If no directories exist, output: "No worklogs found. Use `/worklog create <subject>` to start one."

---

## Command: Select

### Steps

1. Check if `docs/history/<subject>/` exists.
2. If NOT found: output error — "Worklog `<subject>` not found. Use `/worklog list` to see available worklogs."
3. If found:
   - Read all `.md` files in the directory to understand existing context.
   - **Set active worklog**: remember `<subject>` as the active worklog for this session.
   - Output: "Selected worklog `<subject>` as active. Use `/worklog update` to add new entries."

---

## Command: Update

### Steps

1. **Check active worklog**: if no worklog has been set via `create` or `select` in this session, output error — "No active worklog. Use `/worklog create <subject>` or `/worklog select <subject>` first."

2. **Read existing entries**: read ALL `.md` files in `docs/history/<subject>/` sorted by filename.

3. **Analyze current context**:
   - Recent git activity: `git log --oneline -10`, `git diff --stat`
   - Work done in the current conversation session
   - Decisions made, problems encountered

4. **Determine topic continuity**: compare the last entry's topic with the current work.

5. **If same topic** (work continues the same theme):
   - Update the last `.md` file using Edit tool.
   - Update the `Period` end date to today.
   - Append new information to relevant sections (Changes, Decisions, Issues, Next Steps).
   - Remove completed items from Next Steps.
   - Be conservative: only remove content that is fully obsolete.

6. **If different topic** (work shifted to a new theme):
   - Determine the next sequence number (e.g., if last file is `02_xxx.md`, create `03_<new-topic>.md`).
   - Create new file using the same template as Create.
   - Do NOT modify existing files unless correcting outdated Next Steps.

7. Output summary of what was updated or created.

---

## Rules

- **Never delete existing worklog files** — only edit or append.
- **Be conservative with edits** — preserve historical accuracy. Only remove content that is completely obsolete.
- **Topic slugs**: lowercase, hyphens, descriptive (e.g., `rebase-conflict-resolution`, not `update-3`).
- **Period field**: always update end date to today when editing.
- **Korean or English**: match the language the user has been using in the session.
- **No status tracking**: no metadata files, no status fields. Simple numbered markdown files only.
- **Active worklog is session-scoped**: it does not persist across Claude Code sessions. Users must `select` or `create` at the start of each session.
