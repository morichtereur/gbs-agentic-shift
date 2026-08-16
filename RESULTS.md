# Results

**Generated:** 2026-08-15  **Scope:** live Adzuna postings, point-in-time cross-section

Cross-section of **2110** labelled live GBS / finance-operations postings (adzuna/ch, adzuna/de, adzuna/es, adzuna/gb, adzuna/in, adzuna/mx, adzuna/nl, adzuna/pl, adzuna/sg, adzuna/za), pulled from the sources shown. Point-in-time, not a trend.

## Family mix

| family | postings |
|---|---|
| transactional | 921 (44%) |
| judgment | 1157 (55%) |
| agent_ops | 32 (2%) |

![mix](data/chart_mix.png)

Excludes **49** postings from advisory firms (consultancies selling GBS advice rather than performing GBS work). Third-party BPO delivery is kept in — it is the same work, outsourced — and broken out below.

## By market type

Delivery hubs and high-cost retained markets are different populations. Pooling them makes the headline partly a statement about the country basket, so the split is reported rather than averaged away.

| market type | postings | transactional | judgment | agent_ops |
|---|---|---|---|---|
| delivery (low-cost delivery hubs) | 946 | 50% | 49% | 0.5% |
| retained (high-cost, HQ / process ownership) | 753 | 40% | 59% | 1.7% |
| mixed (regional HQ alongside nearshore delivery) | 411 | 36% | 60% | 3.4% |

## By organisation type

| organisation | postings | transactional | judgment | agent_ops |
|---|---|---|---|---|
| captive (in-house GBS) | 1869 | 38% | 60% | 1.6% |
| bpo (third-party delivery) | 241 | 84% | 15% | 0.8% |

## By seniority (title-inferred, crude)

| seniority | transactional | judgment | agent_ops |
|---|---|---|---|
| junior | 70 | 34 | 1 |
| mid/unknown | 657 | 498 | 13 |
| senior | 194 | 625 | 18 |

## Method transparency

- 1471 labelled by the deterministic taxonomy, 639 by the LLM fallback.
- LLM fallback share among included postings: 30%.
- 289 postings were labelled `none` and excluded from the family mix.
- 0 fetched postings remain unlabelled and are excluded from this report.
- Agent-ops audit: 4 clear, 4 borderline, 3 likely false positives, 3 duplicate rows.
- Taxonomy gold-set accuracy: 66.7% (n=60).
- Gold-set agent_ops recall: 42.9%; the agent_ops share should be treated as a lower-bound signal until recall improves.
- Confidence split: agent_ops precision is strong, but the transactional-vs-judgment mix is exploratory at 66.7% overall accuracy.
- Sensitivity illustration: correcting the observed 32 agent_ops labels for the measured recall gives approximately 3.5%; this is an upper-bound diagnostic, not a new point estimate.

## Country cut

| source / country | family | postings |
|---|---|---|
| adzuna / ch | judgment | 70 |
| adzuna / ch | transactional | 17 |
| adzuna / ch | agent_ops | 1 |
| adzuna / de | judgment | 154 |
| adzuna / de | transactional | 76 |
| adzuna / de | agent_ops | 10 |
| adzuna / es | judgment | 112 |
| adzuna / es | transactional | 76 |
| adzuna / es | agent_ops | 8 |
| adzuna / gb | transactional | 143 |
| adzuna / gb | judgment | 127 |
| adzuna / gb | agent_ops | 1 |
| adzuna / in | transactional | 197 |
| adzuna / in | judgment | 74 |
| adzuna / in | agent_ops | 1 |
| adzuna / mx | judgment | 107 |
| adzuna / mx | transactional | 84 |
| adzuna / mx | agent_ops | 2 |
| adzuna / nl | judgment | 90 |
| adzuna / nl | transactional | 63 |
| adzuna / nl | agent_ops | 1 |
| adzuna / pl | judgment | 148 |
| adzuna / pl | transactional | 112 |
| adzuna / pl | agent_ops | 1 |
| adzuna / sg | judgment | 136 |
| adzuna / sg | transactional | 73 |
| adzuna / sg | agent_ops | 6 |
| adzuna / za | judgment | 139 |
| adzuna / za | transactional | 80 |
| adzuna / za | agent_ops | 1 |

- Gold-set detail: `python -m eval.eval_classify` prints the confusion matrix and per-family metrics.
- Seniority is inferred from title keywords only — treat as directional.
