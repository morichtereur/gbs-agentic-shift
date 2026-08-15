# Results

**Generated:** 2026-08-15  **Scope:** live Adzuna postings, point-in-time cross-section

Cross-section of **1858** labelled live GBS / finance-operations postings (adzuna/ch, adzuna/de, adzuna/es, adzuna/gb, adzuna/in, adzuna/mx, adzuna/nl, adzuna/pl, adzuna/sg, adzuna/za), pulled from the sources shown. Point-in-time, not a trend.

## Family mix

| family | postings |
|---|---|
| transactional | 793 (43%) |
| judgment | 1035 (56%) |
| agent_ops | 30 (2%) |

![mix](data/chart_mix.png)

## By seniority (title-inferred, crude)

| seniority | transactional | judgment | agent_ops |
|---|---|---|---|
| junior | 56 | 33 | 1 |
| mid/unknown | 572 | 450 | 13 |
| senior | 165 | 552 | 16 |

## Method transparency

- 1504 labelled by the deterministic taxonomy, 354 by the Claude fallback.
- Claude fallback share among included postings: 19%.
- 165 postings were labelled `none` and excluded from the family mix.
- 425 fetched postings remain unlabelled and are excluded from this report.
- Agent-ops audit: 4 clear, 4 borderline, 3 likely false positives, 3 duplicate rows.
- Taxonomy gold-set accuracy: 66.7% (n=60).
- Gold-set agent_ops recall: 42.9%; the agent_ops share should be treated as a lower-bound signal until recall improves.

## Country cut

| source / country | family | postings |
|---|---|---|
| adzuna / ch | judgment | 47 |
| adzuna / ch | transactional | 8 |
| adzuna / ch | agent_ops | 1 |
| adzuna / de | judgment | 156 |
| adzuna / de | transactional | 76 |
| adzuna / de | agent_ops | 10 |
| adzuna / es | judgment | 68 |
| adzuna / es | transactional | 36 |
| adzuna / es | agent_ops | 7 |
| adzuna / gb | transactional | 143 |
| adzuna / gb | judgment | 127 |
| adzuna / gb | agent_ops | 1 |
| adzuna / in | transactional | 198 |
| adzuna / in | judgment | 76 |
| adzuna / in | agent_ops | 1 |
| adzuna / mx | judgment | 62 |
| adzuna / mx | transactional | 40 |
| adzuna / mx | agent_ops | 2 |
| adzuna / nl | judgment | 93 |
| adzuna / nl | transactional | 63 |
| adzuna / nl | agent_ops | 1 |
| adzuna / pl | judgment | 164 |
| adzuna / pl | transactional | 112 |
| adzuna / pl | agent_ops | 2 |
| adzuna / sg | judgment | 101 |
| adzuna / sg | transactional | 37 |
| adzuna / sg | agent_ops | 4 |
| adzuna / za | judgment | 141 |
| adzuna / za | transactional | 80 |
| adzuna / za | agent_ops | 1 |

- Gold-set detail: `python -m eval.eval_classify` prints the confusion matrix and per-family metrics.
- Seniority is inferred from title keywords only — treat as directional.
