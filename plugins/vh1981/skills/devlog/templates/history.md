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
- <YYYY-MM-DD>: <modified file / what changed / why>
<!-- Every bullet in Changes, Decisions, Issues & Blockers starts with its date
     (reference/writing.md "Date every entry you add"). -->
<!-- Optional: a table (file | change | why) when several files changed.
     Free-form prose is fine for config / discussion / decision changes. -->

## Decisions
- <YYYY-MM-DD>: <decision and its rationale>

## Issues & Blockers
- <YYYY-MM-DD>: <problem or unresolved item>

## Next Steps
<Remaining work items>
```
