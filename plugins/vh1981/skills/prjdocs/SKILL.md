---
name: prjdocs
description: Investigate and document project topics with structured analysis reports. Supports create, list, select, and update commands. Reports are stored as markdown files in docs/projects/<project>/. Use this skill when the user wants to deeply analyze a codebase topic, create technical investigation reports, document architecture decisions, evaluate risks, compare cross-repo implementations, or produce structured findings with tables and diagrams. Trigger phrases include "prjdocs", "investigate", "analyze this", "deep dive", "evaluate", "document findings", "create project doc", "update project doc", "list project docs". Do NOT use for git commits (use /commit), PR descriptions (use /pr), session work logs (use /worklog), or code changes (use /develop).
---

# Project Docs Context

- **Current branch**: !`git branch --show-current`
- **Today**: !`date +%Y-%m-%d`
- **Existing projects**: Check `docs/projects/` directory when needed (may not exist yet)

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

If the argument does not match any command above, treat it as `create <argument>` (assume user wants to create a new project doc with that name).

---

## Command: Create

### Steps

1. Sanitize `<project>`: lowercase, hyphens for spaces, alphanumeric and hyphens only.
2. Create directory: `docs/projects/<project>/` (create `docs/` and `docs/projects/` if they don't exist).
3. Analyze the current conversation context to understand the project topic:
   - What has been discussed and investigated in this session
   - Current git branch and recent commits (`git log --oneline -10`)
   - Recent diff (`git diff --stat HEAD~5..HEAD 2>/dev/null || git diff --stat`)
4. Determine a topic slug from the primary investigation theme (e.g., `cloud-mode-architecture`, `source-id-guard-analysis`).
5. Create `01_<topic-slug>.md` using this template:

```markdown
# <Descriptive Title>

- **Branch**: <branch-name>
- **Period**: <today> ~ <today>

## Summary
<1-3 line summary of the investigation/analysis>

## Scope
- **Files examined**: <count>
- **Repos**: <list of repo paths if cross-repo>
- **Depth**: <quick | medium | deep>

## Findings

### <Finding 1 Title>
<Analysis content — tables, code references (file:line), data flows>

### <Finding 2 Title>
<Analysis content>

## Data Flow
<If applicable — trace how data moves through the system>

## Risk Assessment
<If applicable — risk table with severity, probability, analysis>

| Risk | Severity | Probability | Analysis |
|------|----------|-------------|----------|

## 진행 상태

### 완료
<What has been done — code changes, analysis completed, decisions made>

### 미완료 / 다음 단계
<What remains — prioritized with [Critical], [High], [Medium], [Low] tags>

## Conclusion
<Design intent / problems found / recommendations with priority>

## References
- `<file:line>` — <description>
```

6. Output confirmation: "Created project doc `<project>` with `01_<topic-slug>.md`. This is now the active project for this session."
7. **Set active project**: remember `<project>` as the active project for subsequent `/prjdocs update` calls in this session.

---

## Command: List

### Steps

1. Scan `docs/projects/*/` for subdirectories.
2. For each project directory, count the `.md` files inside.
3. Output a table:

```
Projects:
  <project-1>  (3 entries)
  <project-2>  (1 entry)
```

4. If no directories exist, output: "No project docs found. Use `/prjdocs create <project>` to start one."

---

## Command: Select

### Steps

1. Check if `docs/projects/<project>/` exists.
2. If NOT found: scan `docs/projects/*/` and output available projects — "Project `<project>` not found. Available: <list>. Use `/prjdocs create <project>` to start one."
3. If found:
   - Read all `.md` files in the directory to understand existing context.
   - **Set active project**: remember `<project>` as the active project for this session.
   - Output: "Selected project `<project>` as active. Use `/prjdocs update` to add new entries."

---

## Command: Update

### Steps

1. **Check active project**: if no project has been set via `create` or `select` in this session, output error — "No active project. Use `/prjdocs create <project>` or `/prjdocs select <project>` first."

2. **Read existing entries**: read ALL `.md` files in `docs/projects/<project>/` sorted by filename.

3. **Gather context — 3 mandatory steps**:

   **Step A: Code changes** — Search for code modifications related to the topic:
   - `git diff --stat` and `git diff --name-status HEAD` for uncommitted changes
   - `git log --oneline -20` for recent commits related to the topic
   - Grep/glob for topic keywords in modified files
   - Summarize what was changed, added, or removed in source code

   **Step B: Related documents** — Collect ALL existing markdown/html docs related to the topic:
   - Scan `docs/` directory recursively for related `.md` and `.html` files
   - Scan `docs/history/` (worklogs) for related entries
   - Read and extract relevant content from each document found
   - Note any discrepancies between docs and actual code state

   **Step C: Progress tracking** — Separate completed work from future work:
   - **Completed**: What has been implemented, tested, analyzed, or decided
   - **Next steps**: What remains to be done, prioritized with `[Critical]`, `[High]`, `[Medium]`, `[Low]` tags
   - **Planned/Directional**: Designs or approaches that have been evaluated and deemed correct but not yet implemented

   If user provided specific instructions in the update command, follow those in addition to the 3 steps above.

4. **Investigate**: Perform thorough analysis based on gathered context:
   - **Read source files**: Read the full content of relevant files (use parallel agents for large scopes)
   - **Cross-repo comparison**: If applicable, compare implementations across repos
   - **Trace data flows**: Follow function call chains and data transformations
   - **Build location maps**: Create tables showing where things happen (file:line → behavior)
   - **Calculate metrics**: Memory usage, FPS, CPU%, latency — when applicable
   - **Assess risks**: Severity/probability matrix when applicable

5. **Determine topic**: Identify what distinct topic(s) the current work covers.

6. **CRITICAL — One topic per file**: Each `.md` file must cover exactly ONE topic. Never merge multiple distinct topics into a single file.
   - If the current work spans multiple topics, create separate files for each.
   - Topic examples: architecture overview, specific subsystem analysis, performance optimization, risk assessment.

7. **If topic already has a file** (same theme as existing entry):
   - Update that `.md` file using Edit tool.
   - Update the `Period` end date to today.
   - Append new findings to relevant sections.
   - Update `진행 상태` (completed items, next steps).
   - Be conservative: only remove content that is fully obsolete.

8. **If topic is new** (no existing file for this theme):
   - Determine the next sequence number (e.g., if last file is `03_xxx.md`, create `04_<new-topic>.md`).
   - Create new file using the same template as Create.
   - Do NOT modify existing files unless correcting outdated information.

9. Output summary of what was investigated, key findings, and what was updated or created.

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
- **Never delete existing project doc files** — only edit or append.
- **Be conservative with edits** — preserve historical accuracy. Only remove content that is fully obsolete.
- **Topic slugs**: lowercase, hyphens, descriptive (e.g., `appsrc-scaling-analysis`, not `update-3`).
- **Period field**: always update end date to today when editing.
- **Read before writing**: Always read relevant source code before producing findings. Never guess.
- **진행 상태 section is mandatory**: Every file must have `진행 상태` with `완료` and `미완료 / 다음 단계` subsections. Use priority tags: `[Critical]`, `[High]`, `[Medium]`, `[Low]`.
- **3 mandatory gather steps**: When updating, always perform Step A (code changes), Step B (related docs), Step C (progress tracking) before writing.
- **Active project is session-scoped**: it does not persist across Claude Code sessions. Users must `select` or `create` at the start of each session.
- **This skill is read-only for source code**: It investigates and documents but does NOT modify application source code. If code changes are needed, recommend them in the Conclusion section.
