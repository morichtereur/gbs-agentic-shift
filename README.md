# gbs-agentic-shift

**Testing the GBS pyramid-to-diamond thesis against the live hiring market.**

[![Tests](https://github.com/morichtereur/gbs-agentic-shift/actions/workflows/test.yml/badge.svg)](https://github.com/morichtereur/gbs-agentic-shift/actions/workflows/test.yml)

McKinsey argues that agentic AI turns the GBS talent pyramid into a diamond: a
shrinking transactional base, a widening judgment-based middle, and a new layer
of people managing the "agent force"
([McKinsey Talks Operations, Aug 2026](https://www.mckinsey.com/capabilities/operations/our-insights/agentic-ai-and-the-future-of-global-business-services)).
That is a claim about what work looks like. The labour market is where it is
either visible or not — so this reads it off job postings instead of taking it
on faith.

## Key finding

**The diamond is not visible yet.** Across 2,110 live GBS / finance-operations
postings in ten markets:

| family | postings | share |
|---|---|---|
| transactional | 921 | 44% |
| judgment | 1,157 | 55% |
| agent_ops | **32** | **2%** |

The transactional base is not thin, and the agent-ops layer barely exists.
Correcting the observed count for the classifier's own measured recall of 42.9%
lifts agent-ops to roughly 4% — still marginal. A point-in-time cross-section
cannot show a trend, so this does not disprove the thesis; it establishes that
as of this snapshot, hiring demand has not moved there.

![Family mix](data/chart_mix.png)

### The base did not shrink. It changed employer.

Splitting the same postings by who is hiring is the sharpest cut in the data:

| organisation | postings | transactional | judgment |
|---|---|---|---|
| captive (in-house GBS) | 1,869 | 38% | 60% |
| **third-party BPO** | 241 | **84%** | 15% |

An in-house GBS function looks diamond-shaped on its own. It looks that way in
part because the transactional layer sits at a provider rather than on the
captive payroll — Accenture, Genpact, Capgemini and peers hire 84% transactional
against the captive 38%. Outsourcing and automation produce the same shape in a
captive-only readout, and only the provider cut tells them apart. This is a
hiring-side observation, not a measurement of work volume, but it is the reason
a captive-only sample would overstate the shift.

### The headline depends on the country basket

| market type | postings | transactional | judgment | agent_ops |
|---|---|---|---|---|
| delivery — low-cost hubs (in, pl, mx, za) | 946 | 50% | 49% | 0.5% |
| retained — HQ / process ownership (ch, nl, de, gb) | 753 | 40% | 59% | 1.7% |
| mixed — regional HQ plus nearshore (es, sg) | 411 | 36% | 60% | 3.4% |

India runs 72% transactional; Switzerland runs 81% judgment. The pooled figure
is therefore partly a statement about which countries were sampled. It is
reported as a split for that reason, and any single number over the whole basket
should be read as basket-dependent. Both populations belong in the study — the
thesis is about the interaction between where transactional work sits and where
judgment and process ownership sit — but they should not be averaged into one
claim.

Advisory firms (EY, Deloitte, KPMG, PwC, McKinsey and peers) match the same
search terms while selling advice about GBS rather than performing it. The 49
such postings are excluded from every figure above; the classification lives in
`src/orgtype.py` and is a visible list, not a model.

### How much of that you can lean on

The classifier's accuracy is measured against a 60-posting hand-labelled gold
set, not assumed:

| metric | value | what it means |
|---|---|---|
| Overall accuracy | 66.7% | the transactional/judgment split is **exploratory** |
| `agent_ops` precision | 100% | detected agent-ops roles are **credible** |
| `agent_ops` recall | 42.9% | the low agent-ops share is a **lower bound** |
| LLM fallback share | 30% | how much was not decided by visible rules |

**Confidence is asymmetric, and that shapes what may be said.** The defensible
headline is that agent-ops demand is small — precision is perfect, so the roles
found are real, and even a generous recall correction leaves it marginal. The
transactional-vs-judgment ratio should not be headlined at 66.7% accuracy.

A 30% fallback share is high by this project's own standard: the more the model
decides, the less the visible rules explain. Reducing it is the main open work.

Full generated readout: [`RESULTS.md`](RESULTS.md) · interactive
`dashboard.html` (committed, opens offline, every row shows why it landed
there) · manual review of every agent-ops hit in
[`eval/agent_ops_audit.jsonl`](eval/agent_ops_audit.jsonl), which records 3
likely false positives and 3 duplicates alongside the 4 clear ones.

## Method

Two stages, and the split is the point.

**1. Deterministic taxonomy** (`src/taxonomy.py`) carries the headline. Each
posting is scored by counting distinct phrase hits across three keyword
families. Every label traces back to the exact phrases that produced it — no
model in the critical path. The families live in code, editable and visible,
not hidden in a prompt.

**2. LLM fallback** (`src/classify.py`) decides *only* the residual the
taxonomy flags as ambiguous — no family hit, or a non-agent-ops tie — and logs
a one-line reason, so its calls are auditable the same way. The share of
postings that needed it is reported rather than buried.

Accuracy is then measured against the gold set by `eval/eval_classify.py`,
which prints per-family precision/recall and a confusion matrix.

The shipped `labels.sample.jsonl` is a clean smoke-test fixture — it scores
~100% and is meant to. The real number comes from `labels.jsonl`, 60 hand
labels off real postings, and it is lower.

## Run it

```bash
cp .env.example .env      # Adzuna, Jooble and Anthropic keys
make install
make all                  # fetch → classify → analyze → dashboard
make eval                 # taxonomy accuracy vs the gold set
make test
```

`make all` writes `RESULTS.md` and a single-file `dashboard.html` — filter by
family, country or free text, export visible rows as CSV. Both are generated;
never hand-edit them.

Useful switches: `GBS_MAX_PAGES=1` for a smoke run (default is five pages per
term and country), `ADZUNA_COUNTRIES` / `JOOBLE_COUNTRIES` to narrow the
comparison, `GBS_RECLASSIFY=1` when the taxonomy changed and an existing DuckDB
run needs relabelling. After editing phrases, `make refresh-taxonomy` updates
every clear label without spending an LLM call. API keys are read from the
environment only.

## Building a gold set

The metrics above are only as good as the labels behind them, so the
annotation workflow is part of the repo rather than a one-off.

```bash
.venv/bin/python -m eval.build_gold_template          # balanced sample
.venv/bin/python -m eval.build_country_gold_template  # 10 per market
```

Fill each empty `gold` value with exactly one of `transactional`, `judgment`,
`agent_ops` (country worksheets also allow `none`). Copy the completed file to
`eval/labels.jsonl` and run `make eval`, or `make eval-country` for per-market
accuracy and agent-ops recall. The template uses existing labels only to
balance the sample — it does not copy them into the gold set, which would
grade the classifier against itself.

The country set is a diagnostic at `n=10` per market, useful for finding
language and recall failures. It is far too small to rank countries. The latest
run reaches 100% agent-ops recall in the DE, IN, NL and PL slices at 60%
overall country accuracy — a debugging signal, not a market estimate.

## Data and coverage

Live postings via keyed Adzuna and Jooble search APIs — no scraping. The
committed snapshot is **Adzuna-only** across `ch`, `de`, `es`, `gb`, `in`,
`mx`, `nl`, `pl`, `sg`, `za`.

Jooble is implemented but its freshly issued key returns `403 Forbidden`. The
adapter **fails closed**: an unavailable source is reported as unavailable and
contributes no zero-valued rows, so an outage cannot be mistaken for weak
demand. The planned 12-market design splits sources deliberately — Adzuna for
`PL`, `IN`, `MX`, `NL`, `DE`, `CH`, `ES`, `SG`; Jooble for `PT`, `RO`, `HU`,
`CZ` — and keeps provenance visible, because the two aggregators may carry
overlapping supply.

## What this is not

- **A trend.** The APIs return current live postings only; they cannot see
  2023. The pyramid-to-diamond line over time needs a historical source and is
  a stated v2, not faked here.
- **Headcount.** Postings are demand. They lead the actual workforce and
  overstate the frontier.
- **An organisational measurement.** The family mix is a distribution of
  posting classifications, nothing more.
- **A country ranking.** Coverage varies by source and market, and the
  taxonomy is strongest in English and German. Polish finance and automation
  phrases are included, but a low PL count may still be a language artifact.
- **A seniority profile.** Inferred from title words only — directional.
- **A validated fallback.** The LLM's reasons are logged for auditability, but
  the fallback itself has no labelled evaluation set yet.

Search coverage, reposting and employer behaviour shape Adzuna results;
idempotent IDs remove exact duplicates but not that bias. A future pooled
Adzuna + Jooble headline needs URL/title/company deduplication and a
source-overlap report first.

## Repository map

| path | responsibility |
|---|---|
| `src/fetch.py` | source-aware Adzuna/Jooble retrieval, idempotent DuckDB upserts |
| `src/taxonomy.py` | visible phrases, scoring, tie rule, audit hits |
| `src/orgtype.py` | captive / BPO / advisory and delivery / retained market lists |
| `src/classify.py` | taxonomy first, LLM fallback for the residual |
| `src/analyze.py` | generated report, chart, country and seniority cuts |
| `src/dashboard.py` | standalone research brief and posting-level audit view |
| `eval/eval_classify.py` | gold-set metrics and confusion matrix |
| `eval/agent_ops_audit.jsonl` | manual review of every current agent-ops row |
| `tests/` | deterministic checks, no API calls |

## Stack

`Python` · `DuckDB` · `LLM API` · `matplotlib` · `pytest`

---

Built by [Moritz Richter](https://www.linkedin.com/in/moritz-richter-28297119a/) · Finance & Strategy Consultant · Zürich
