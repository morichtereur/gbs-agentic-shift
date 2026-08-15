# Results

**Generated:** 2026-08-15  **Scope:** live Adzuna postings, point-in-time cross-section

Cross-section of **513** live GBS / finance-operations postings (de, gb), pulled from Adzuna. Point-in-time, not a trend.

## Family mix

| family | postings |
|---|---|
| transactional | 219 (43%) |
| judgment | 284 (55%) |
| agent_ops | 10 (2%) |

![mix](data/chart_mix.png)

## By seniority (title-inferred, crude)

| seniority | transactional | judgment | agent_ops |
|---|---|---|---|
| junior | 13 | 3 | 1 |
| mid/unknown | 164 | 131 | 5 |
| senior | 42 | 150 | 4 |

## Method transparency

- 398 labelled by the deterministic taxonomy, 115 by the Claude fallback.
- Claude fallback share among included postings: 22%.
- 54 postings were labelled `none` and excluded from the family mix.

## Country cut

| country | family | postings |
|---|---|---|
| de | judgment | 157 |
| de | transactional | 76 |
| de | agent_ops | 9 |
| gb | transactional | 143 |
| gb | judgment | 127 |
| gb | agent_ops | 1 |

- Taxonomy accuracy against the hand-labelled gold set: run `python -m eval.eval_classify`.
- Seniority is inferred from title keywords only — treat as directional.
