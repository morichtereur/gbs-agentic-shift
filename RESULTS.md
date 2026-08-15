# Results

**Generated:** 2026-08-15  **Scope:** live Adzuna postings, point-in-time cross-section

Cross-section of **1445** live GBS / finance-operations postings (adzuna/de, adzuna/gb, adzuna/in, adzuna/nl, adzuna/pl, adzuna/za), pulled from the sources shown. Point-in-time, not a trend.

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
- Agent-ops audit: 4 clear, 4 borderline, 3 likely false positives, 3 duplicate rows.
- Taxonomy gold-set accuracy: 66.7% (n=60).
- Gold-set agent_ops recall: 42.9%; the agent_ops share should be treated as a lower-bound signal until recall improves.

## Country cut

| source / country | family | postings |
|---|---|---|
| adzuna / de | judgment | 157 |
| adzuna / de | transactional | 76 |
| adzuna / de | agent_ops | 9 |
| adzuna / gb | transactional | 143 |
| adzuna / gb | judgment | 127 |
| adzuna / gb | agent_ops | 1 |
| adzuna / in | transactional | 198 |
| adzuna / in | judgment | 76 |
| adzuna / in | agent_ops | 1 |
| adzuna / nl | judgment | 93 |
| adzuna / nl | transactional | 63 |
| adzuna / nl | agent_ops | 1 |
| adzuna / pl | judgment | 167 |
| adzuna / pl | transactional | 110 |
| adzuna / pl | agent_ops | 1 |
| adzuna / za | judgment | 141 |
| adzuna / za | transactional | 80 |
| adzuna / za | agent_ops | 1 |

- Gold-set detail: `python -m eval.eval_classify` prints the confusion matrix and per-family metrics.
- Seniority is inferred from title keywords only — treat as directional.
