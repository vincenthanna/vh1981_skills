# Doc-writing rules — reference

Read this file once per session before writing or editing devlog docs — at
`create`, and before `update` Parts 1–3. SKILL.md carries routing and
active-project rules; `commands/*.md` carry per-command procedures; this file
carries the rules for doc content and structure.

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

## Templates

At the step that creates a NEW file, **read the relevant template from this skill's directory first**:

- **Investigation doc** → `templates/investigation.md` — for `docs/devlog/<project>/NN_<topic>.md`
- **History entry** → `templates/history.md` — for `docs/devlog/<project>/history/NN_<topic>.md`

**Language**: render section *headers* in the session's language, but keep field *keys* (`Branch`, `Period`, `Summary`) in English for grep-ability across mixed-language devlogs.

## One topic per file — split triggers

Each `.md` covers one topic. **Hard triggers** (act — create a new file): the user explicitly asks to split, OR non-prose artifacts (measurement data, logs) are getting mixed into prose analysis. **Soft signals** (only *consider* splitting, not automatic): a section dwarfs the rest of the file, the same finding is being augmented across multiple updates, or a finding starts growing its own Risk/Data-Flow subsections. **Create exception**: the first file `01_<slug>.md` may stay a multi-finding overview. When a split actually happens, say so in the output (one line). Entry points: new project → `Granularity decision` (SKILL.md); one file growing too big → these split triggers; many related files → the subtopic-folder trigger below.

## Subtopic folders

Keep docs flat in the project root until investigation docs grow past roughly 5–6 AND at least 3 of them share a common topic-slug prefix (e.g. `clustering-eval`, `clustering-params`, `clustering-fps` → prefix `clustering`). Only then *consider* grouping those into a `<prefix>/` subtopic folder, and only if it clearly improves navigation. No preemptive foldering. When a folder is created or files are moved, say so in the output (one line).

Do not create template-outside root files (`PII-XXXX-pr-summary.md`, raw prompt dumps, etc.) — absorb that content into an investigation doc or follow the `NN_<topic>.md` naming.

## Cross-references

When a devlog doc references another devlog doc, use a single path form:

- Always a repo-relative full path: `docs/devlog/<project>/NN_<slug>.md` (history and subtopic paths likewise, e.g. `docs/devlog/<project>/history/NN_<slug>.md`).
- References outside devlog (memory files, repo source) — a repo-relative or absolute path plus a one-line note.
- Never put a ticket ID or commit SHA in a path component — it breaks on rename/squash.

This single form is what makes `reorg rename` and `reorg cleanup` reliable. **Premise**: file moves and renames go through `reorg` — it auto-substitutes cross-references and shows the match list for approval. Avoid manual `mv` of devlog files.

## Writing rules

- **Topic slugs**: lowercase, hyphens, descriptive (e.g., `appsrc-scaling-analysis`, not `update-3`). For multi-phase work, slug the outcome/decision, not the journey. Project names follow the same rule — prefer the work's nature (`rtmp-stall-investigation`) over a bare JIRA ticket ID (`pii-2176`); a `<ticket>-<topic>` combination is fine.
- **Period field**: the first-to-last date this doc was *edited* — not the calendar span of the underlying work. Always update the end date to today when editing, using the resolved `Today` from the context header (never a remembered or guessed date). If the work's calendar span matters, record it separately in the body.
- **Read before writing**: Always read relevant source code before producing findings. Never guess.
- **Progress section is mandatory**: Every investigation doc must have a `Progress` section with `Done` and `Remaining / Next` subsections. Use priority tags: `[Critical]`, `[High]`, `[Medium]`, `[Low]`.
- **Be conservative with edits** — preserve historical accuracy. Only remove content that is fully obsolete.

## Investigation depth levels

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

## Output quality rules

- **Tables over prose**: Use markdown tables for comparisons, location maps, risk assessments, and metrics.
- **Code references**: Always include `file:line` references so the reader can navigate to source.
- **Data flow notation**: Use `A → B → C` with annotations for describing pipelines and call chains.
- **Quantitative over qualitative**: Prefer "32MB per view" over "significant memory usage".
- **Conclusions must be actionable**: End with prioritized recommendations, not just observations.
- **Language consistency**: one project, one language — follow the first doc's language (usually the session's). Section header *text* and prose go in the project language; field *keys* (`Branch`, `Period`, `Summary`), priority tags (`[Critical]` …), and code / `file:line` references stay in English. Do not force-migrate existing files to a different language.
