# Results

**Generated:** 2026-08-15  **Scope:** live Adzuna postings, point-in-time cross-section

Cross-section of **1445** live GBS / finance-operations postings (de, gb, nl, pl, in, za), pulled from Adzuna. Point-in-time, not a trend.

## Family mix

| family | postings |
|---|---|
| transactional | 670 (46%) |
| judgment | 761 (53%) |
| agent_ops | 14 (1%) |

![mix](data/chart_mix.png)

## By seniority (title-inferred, crude)

| seniority | transactional | judgment | agent_ops |
|---|---|---|---|
| junior | 43 | 25 | 1 |
| mid/unknown | 504 | 341 | 6 |
| senior | 123 | 395 | 7 |

## Method transparency

- 1083 labelled by the deterministic taxonomy, 362 by the Claude fallback.
- Claude fallback share among included postings: 25%.
- 165 postings were labelled `none` and excluded from the family mix.

## Country cut

| country | family | postings |
|---|---|---|
| de | judgment | 157 |
| de | transactional | 76 |
| de | agent_ops | 9 |
| gb | transactional | 143 |
| gb | judgment | 127 |
| gb | agent_ops | 1 |
| in | transactional | 198 |
| in | judgment | 76 |
| in | agent_ops | 1 |
| nl | judgment | 93 |
| nl | transactional | 63 |
| nl | agent_ops | 1 |
| pl | judgment | 167 |
| pl | transactional | 110 |
| pl | agent_ops | 1 |
| za | judgment | 141 |
| za | transactional | 80 |
| za | agent_ops | 1 |

- Taxonomy accuracy against the hand-labelled gold set: run `python -m eval.eval_classify`.
- Seniority is inferred from title keywords only — treat as directional.
