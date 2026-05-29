# Command: Validation (run / compare) — detailed procedures

Read this file when the user invokes `/devlog run ...` or `/devlog compare ...`.
For validation/ablation campaigns where each measurement adds a *condition* to
an existing project — not a new investigation topic.

Both commands require an active project (resolve per `## Active Project`).

## run <condition-name>

Registers one measurement run. **`run` only writes the manifest — it does not
execute anything.** The user runs the actual experiment; this command captures
its setup and results as devlog artifacts.

1. `<condition-name>` is the canonical, durable name of this measurement —
   self-describing and immutable (e.g. `dynamic-fps-baseline`, not `dataA` or a
   bare date). If it re-runs an existing condition, suffix `-take2`; never
   overwrite the original folder.
2. Create `docs/devlog/<project>/runs/<condition-name>/`.
3. Write `runs/<condition-name>/manifest.md` — read `templates/validation.md`
   (Run Manifest Template) and follow it. The Setup YAML is free-form: capture
   whatever defines this run's conditions; there is no fixed schema.
4. Raw artifacts (CSV, logs, etc.) go in the same directory; the user supplies
   them. Large raw files should be gitignored.
5. Write `runs/<condition-name>/metrics.md` with the measured KPIs.
6. Do NOT touch comparison reports here — that is `compare`'s job.

## compare <condition-a> <condition-b> ...

Produces or grows a side-by-side comparison across registered runs.

1. Resolve the condition list. Arguments are condition directory names under
   `runs/` (tokens without `/`). If none are given, use all conditions under
   `runs/`.
2. For each condition, read its `manifest.md` + `metrics.md`.
3. If `comparisons/<title>.md` already exists, **grow it, do not rewrite**: use
   Edit to add a column or append a Δ row. A conclusion gets a dated suffix when
   newer data supersedes it — never silently replace it:
   > **Conclusion (2026-04-29)**: … (data at the time)
   > **Conclusion (2026-05-06, supersedes above)**: … (updated with cond-c)
   If the existing table's structure genuinely no longer fits, create it fresh
   and say so in the output.
4. If new, create `comparisons/<title>.md` — read `templates/validation.md`
   (Comparison Report Template) and follow it.
5. Cite conditions by their canonical run-folder name, never by ad-hoc letters
   (A, B, C) — so the report can be re-run months later against the same runs.

## Supersede chains

When a run or comparison supersedes an earlier doc's conclusion, add to the
earlier doc's frontmatter: `- **Superseded by**: <repo-relative path>`. Do not
delete the old doc — it stays as the historical record.

## Layout

- `docs/devlog/<project>/runs/<condition-name>/` — manifest + metrics + raw artifacts
- `docs/devlog/<project>/comparisons/<title>.md` — comparison reports

Use these instead of ad-hoc date-stamped directories.
