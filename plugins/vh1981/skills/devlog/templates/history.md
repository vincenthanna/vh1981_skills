# History Entry Template

Used by the `devlog` skill for files in `docs/devlog/<project>/history/NN_<topic-slug>.md`.
Copy the block below. Keep the history entry short — analysis tables and code
citations belong in the investigation doc, not here.

```markdown
# <Descriptive Title>

- **Branch**: <branch-name or JIRA tag>
- **Period**: <today> ~ <today>

## Summary
<1-3 line summary of the work>

## Changes
<List of modified files, what changed, and why>
<!-- Optional: a table (file | change | why) when several files changed.
     Free-form prose is fine for config / discussion / decision changes. -->

## Decisions
<Key decisions made and their rationale>

## Issues & Blockers
<Problems encountered, unresolved items>

## Next Steps
<Remaining work items>
```
