# Template: rejected approach

Used by `reorg consolidate` when extracting off-mainstream detail out of an
investigation doc into `docs/devlog/<project>/rejected/NN_<slug>.md`.

Header text goes in the project language; field keys stay English
(`reference/writing.md`). Fill every field — a record with no verdict and no
revisit condition is worse than no record, because the reader cannot act on it.

```markdown
# <approach name> — <one-line verdict>

- **Branch**: <branch>
- **Verdict**: 폐기 | 보류 | 부분 채택 | 대체됨 (superseded by <what>)
- **Period**: <first> ~ <last>
- **Extracted from**: docs/devlog/<project>/NN_<slug>.md (<date>)

## 채택하지 않은 이유

<2~4 sentences, specific enough that a reader can tell whether the idea they
are about to try is this same idea. "효과 없음" alone does not qualify.>

## 시도한 내용

<The detail moved out of the mainstream doc, verbatim. Implementation notes,
code blocks, parameters. Do not re-summarize or improve it — this is a record
of what was actually done.>

## 측정 결과

<The tables and numbers that produced the verdict.>

## 판정이 뒤집힐 조건

<What would make this worth revisiting — a parameter range not swept, a
dataset not tried, a dependency that has since changed. "없음" is a valid and
useful answer: it closes the door explicitly.>
```

## Sizing

Match the extracted content. If the source block was 12 lines, the result is a
short doc — do not pad it to look like an investigation doc.
