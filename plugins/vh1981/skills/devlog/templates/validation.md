# Validation Templates

Used by the `devlog` skill's `run` and `compare` commands. Two templates: a Run
Manifest and a Comparison Report.

## Run Manifest Template

For `docs/devlog/<project>/runs/<condition-name>/manifest.md`.

````markdown
# Run: <condition-name>

- **Project**: <project>
- **Condition**: <condition-name>   # same as the folder name; self-describing, immutable
- **Date(s)**: <start> ~ <end>
- **Target**: <machine / environment>
- **Repeated from**: <prior condition name if this is a re-run, else "(new)">

## Setup (machine-readable)

```yaml
# Free-form: list whatever defines this run's conditions. Keys are
# experiment-specific — there is NO fixed schema. Keep it parseable so a
# later comparison can check condition equality.
condition: <name>
baseline: <what this is compared against, if any>
# ... experiment-specific parameters ...
```

## Hypothesis

<1-3 lines: what this run is expected to show, and why it is being run now>

## Artifacts (paths relative to this directory)

- `metrics.md` — computed KPIs
- <raw data files: CSV, logs, etc.>
````

## Comparison Report Template

For `docs/devlog/<project>/comparisons/<title>.md`.

````markdown
# <Title> — <condition-a> vs <condition-b> [vs ...]

- **Project**: <project>
- **First written**: <yyyy-mm-dd>
- **Last updated**: <yyyy-mm-dd>
- **Conditions included**: <canonical run-folder names>

## Results

| Metric | <cond-a> | <cond-b> | ... | Δ |
|--------|----------|----------|-----|---|

## Interpretation (chronological)

### <yyyy-mm-dd> — <cond-a> vs <cond-b>
<interpretation>

### <yyyy-mm-dd> — +<cond-c> added
*(state explicitly if this supersedes a prior interpretation)*

## Current conclusion

<always the conclusion under the most recent data; the Interpretation section above is the audit trail of what was thought, when>
````
