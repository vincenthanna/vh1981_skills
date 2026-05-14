# Investigation Doc Template

Used by the `devlog` skill for files in `docs/devlog/<project>/NN_<topic-slug>.md`.
Copy the block below. Optional sections are marked — **omit the whole section
(header included) when it does not apply**; do not leave an empty "N/A" section.

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

## Data Flow *(optional — omit this section entirely if N/A)*
<Trace how data moves through the system>

## Risk Assessment *(optional — omit this section entirely if N/A)*
<Risk table with severity, probability, analysis>

| Risk | Severity | Probability | Analysis |
|------|----------|-------------|----------|

## Progress

### Done
<What has been done — code changes, analysis completed, decisions made>

### Remaining / Next
<What remains — prioritized with [Critical], [High], [Medium], [Low] tags>

## Conclusion
<Design intent / problems found / recommendations with priority>

## References
- `<file:line>` — <description>
```
