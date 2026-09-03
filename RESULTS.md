# Results

**Generated:** 2026-09-03  **Scope:** live Adzuna postings, point-in-time cross-section

Cross-section of **6253** labelled live GBS / finance-operations postings (adzuna/ch, adzuna/de, adzuna/es, adzuna/gb, adzuna/in, adzuna/mx, adzuna/nl, adzuna/pl, adzuna/sg, adzuna/za), pulled from the sources shown. Point-in-time, not a trend.

## Family mix

| family | postings |
|---|---|
| transactional | 2543 (41%) |
| judgment | 3571 (57%) |
| agent_ops | 139 (2%) |

![mix](data/chart_mix.png)

Excludes **147** postings from advisory firms (consultancies selling GBS advice rather than performing GBS work). Third-party BPO delivery is kept in — it is the same work, outsourced — and broken out below.

## By market type

Delivery hubs and high-cost retained markets are different populations. Pooling them makes the headline partly a statement about the country basket, so the split is reported rather than averaged away.

| market type | postings | transactional | judgment | agent_ops |
|---|---|---|---|---|
| delivery (low-cost delivery hubs) | 3131 | 49% | 49% | 1.6% |
| retained (high-cost, HQ / process ownership) | 2267 | 33% | 64% | 2.7% |
| mixed (regional HQ alongside nearshore delivery) | 855 | 30% | 67% | 3.0% |

## By organisation type

| organisation | postings | transactional | judgment | agent_ops |
|---|---|---|---|---|
| captive (in-house GBS) | 5445 | 36% | 62% | 2.1% |
| bpo (third-party delivery) | 808 | 73% | 24% | 3.1% |

## By seniority (title-inferred, crude)

| seniority | transactional | judgment | agent_ops |
|---|---|---|---|
| junior | 195 | 86 | 11 |
| mid/unknown | 1809 | 1498 | 71 |
| senior | 539 | 1987 | 57 |

## Method transparency

- 4179 labelled by the deterministic taxonomy, 2074 by the LLM fallback.
- LLM fallback share among included postings: 33%.
- 1584 postings were labelled `none` and excluded from the family mix.
- 0 fetched postings remain unlabelled and are excluded from this report.
- Agent-ops audit: 4 clear, 4 borderline, 3 likely false positives, 3 duplicate rows.
- Taxonomy gold-set accuracy: 66.7% (n=60).
- Gold-set agent_ops recall: 42.9%; the agent_ops share should be treated as a lower-bound signal until recall improves.
- Confidence split: agent_ops precision is strong, but the transactional-vs-judgment mix is exploratory at 66.7% overall accuracy.
- Sensitivity illustration: correcting the observed 139 agent_ops labels for the measured recall gives approximately 5.2%; this is an upper-bound diagnostic, not a new point estimate.

## Country cut

| source / country | family | postings |
|---|---|---|
| adzuna / ch | judgment | 111 |
| adzuna / ch | transactional | 37 |
| adzuna / ch | agent_ops | 13 |
| adzuna / de | judgment | 548 |
| adzuna / de | transactional | 214 |
| adzuna / de | agent_ops | 31 |
| adzuna / es | judgment | 199 |
| adzuna / es | transactional | 99 |
| adzuna / es | agent_ops | 18 |
| adzuna / gb | judgment | 596 |
| adzuna / gb | transactional | 385 |
| adzuna / gb | agent_ops | 12 |
| adzuna / in | transactional | 779 |
| adzuna / in | judgment | 494 |
| adzuna / in | agent_ops | 23 |
| adzuna / mx | judgment | 281 |
| adzuna / mx | transactional | 173 |
| adzuna / mx | agent_ops | 6 |
| adzuna / nl | judgment | 192 |
| adzuna / nl | transactional | 122 |
| adzuna / nl | agent_ops | 6 |
| adzuna / pl | judgment | 409 |
| adzuna / pl | transactional | 324 |
| adzuna / pl | agent_ops | 22 |
| adzuna / sg | judgment | 376 |
| adzuna / sg | transactional | 155 |
| adzuna / sg | agent_ops | 8 |
| adzuna / za | judgment | 365 |
| adzuna / za | transactional | 255 |

- Gold-set detail: `python -m eval.eval_classify` prints the confusion matrix and per-family metrics.
- Seniority is inferred from title keywords only — treat as directional.
