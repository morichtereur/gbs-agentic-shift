# Results

**Generated:** 2026-09-02  **Scope:** live Adzuna postings, point-in-time cross-section

Cross-section of **4173** labelled live GBS / finance-operations postings (adzuna/ch, adzuna/de, adzuna/es, adzuna/gb, adzuna/in, adzuna/mx, adzuna/nl, adzuna/pl, adzuna/sg, adzuna/za), pulled from the sources shown. Point-in-time, not a trend.

## Family mix

| family | postings |
|---|---|
| transactional | 1681 (40%) |
| judgment | 2391 (57%) |
| agent_ops | 101 (2%) |

![mix](data/chart_mix.png)

Excludes **81** postings from advisory firms (consultancies selling GBS advice rather than performing GBS work). Third-party BPO delivery is kept in — it is the same work, outsourced — and broken out below.

## By market type

Delivery hubs and high-cost retained markets are different populations. Pooling them makes the headline partly a statement about the country basket, so the split is reported rather than averaged away.

| market type | postings | transactional | judgment | agent_ops |
|---|---|---|---|---|
| delivery (low-cost delivery hubs) | 2124 | 50% | 48% | 2.1% |
| retained (high-cost, HQ / process ownership) | 1475 | 32% | 66% | 2.7% |
| mixed (regional HQ alongside nearshore delivery) | 574 | 25% | 72% | 2.8% |

## By organisation type

| organisation | postings | transactional | judgment | agent_ops |
|---|---|---|---|---|
| captive (in-house GBS) | 3462 | 33% | 65% | 2.2% |
| bpo (third-party delivery) | 711 | 76% | 20% | 3.5% |

## By seniority (title-inferred, crude)

| seniority | transactional | judgment | agent_ops |
|---|---|---|---|
| junior | 100 | 63 | 8 |
| mid/unknown | 1195 | 1056 | 51 |
| senior | 386 | 1272 | 42 |

## Method transparency

- 4173 labelled by the deterministic taxonomy, 0 by the LLM fallback.
- LLM fallback share among included postings: 0%.
- 3709 postings were labelled `none` and excluded from the family mix.
- 0 fetched postings remain unlabelled and are excluded from this report.
- Agent-ops audit: 4 clear, 4 borderline, 3 likely false positives, 3 duplicate rows.
- Taxonomy gold-set accuracy: 66.7% (n=60).
- Gold-set agent_ops recall: 42.9%; the agent_ops share should be treated as a lower-bound signal until recall improves.
- Confidence split: agent_ops precision is strong, but the transactional-vs-judgment mix is exploratory at 66.7% overall accuracy.
- Sensitivity illustration: correcting the observed 101 agent_ops labels for the measured recall gives approximately 5.6%; this is an upper-bound diagnostic, not a new point estimate.

## Country cut

| source / country | family | postings |
|---|---|---|
| adzuna / ch | judgment | 71 |
| adzuna / ch | transactional | 12 |
| adzuna / ch | agent_ops | 10 |
| adzuna / de | judgment | 375 |
| adzuna / de | transactional | 141 |
| adzuna / de | agent_ops | 19 |
| adzuna / es | judgment | 129 |
| adzuna / es | transactional | 55 |
| adzuna / es | agent_ops | 12 |
| adzuna / gb | judgment | 415 |
| adzuna / gb | transactional | 247 |
| adzuna / gb | agent_ops | 6 |
| adzuna / in | transactional | 646 |
| adzuna / in | judgment | 284 |
| adzuna / in | agent_ops | 20 |
| adzuna / mx | judgment | 168 |
| adzuna / mx | transactional | 84 |
| adzuna / mx | agent_ops | 6 |
| adzuna / nl | judgment | 107 |
| adzuna / nl | transactional | 67 |
| adzuna / nl | agent_ops | 5 |
| adzuna / pl | judgment | 297 |
| adzuna / pl | transactional | 190 |
| adzuna / pl | agent_ops | 19 |
| adzuna / sg | judgment | 284 |
| adzuna / sg | transactional | 90 |
| adzuna / sg | agent_ops | 4 |
| adzuna / za | judgment | 261 |
| adzuna / za | transactional | 149 |

- Gold-set detail: `python -m eval.eval_classify` prints the confusion matrix and per-family metrics.
- Seniority is inferred from title keywords only — treat as directional.
