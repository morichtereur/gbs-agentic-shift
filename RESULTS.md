# Results

**Generated:** 2026-08-15  **Scope:** live Adzuna postings, point-in-time cross-section

Cross-section of **493** live GBS / finance-operations postings (de, gb), pulled from Adzuna. Point-in-time, not a trend.

## Family mix

| family | postings |
|---|---|
| transactional | 194 (39%) |
| judgment | 285 (58%) |
| agent_ops | 14 (3%) |

![mix](data/chart_mix.png)

## By seniority (title-inferred, crude)

| seniority | transactional | judgment | agent_ops |
|---|---|---|---|
| junior | 10 | 5 | 1 |
| mid/unknown | 152 | 126 | 7 |
| senior | 32 | 154 | 6 |

## Method transparency

- 107 labelled by the deterministic taxonomy, 386 by the Claude fallback.
- Claude fallback share among included postings: 78%.
- 74 postings were labelled `none` and excluded from the family mix.

## Country cut

| country | family | postings |
|---|---|---|
| de | judgment | 153 |
| de | transactional | 61 |
| de | agent_ops | 13 |
| gb | transactional | 133 |
| gb | judgment | 132 |
| gb | agent_ops | 1 |

- Taxonomy accuracy against the hand-labelled gold set: run `python -m eval.eval_classify`.
- Seniority is inferred from title keywords only — treat as directional.
