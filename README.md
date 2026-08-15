# gbs-agentic-shift

**A transparent labour-market readout for the GBS pyramid-to-diamond thesis.**

![Python](https://img.shields.io/badge/Python-3.11%2B-14213d?style=flat-square)
![Method](https://img.shields.io/badge/headline-deterministic%20taxonomy-f4b942?style=flat-square)
![Data](https://img.shields.io/badge/data-Adzuna%20Search%20API-2f8f83?style=flat-square)

> What is the current GBS hiring market asking people to do: execute, exercise
> judgement, or manage the agent force?

McKinsey argues that agentic AI turns the GBS talent pyramid into a diamond: a
shrinking transactional base, a widening judgment-based middle, and a new layer
of people who manage the "agent force" ([McKinsey Talks Operations, Aug 2026](https://www.mckinsey.com/capabilities/operations/our-insights/agentic-ai-and-the-future-of-global-business-services)).
That's a claim about what work looks like. The labour market is where that claim
is either visible or not, so this reads it off job postings instead of taking it
on faith.

It pulls live GBS / finance-operations postings, classifies each into
**transactional**, **judgment**, or **agent_ops**, and reports the mix — with the
classifier's own accuracy measured against a hand-labelled set, because a
constructed metric only counts if you can see how wrong it is.

## The consulting readout

This repository is a small, reproducible research brief rather than a
forecasting model. A run gives the reader four things: the observed family mix,
the country cut, the title-inferred seniority cut, and the share of records that
required Claude. Every posting in the dashboard carries either the exact
deterministic phrases that fired or the one-line reason returned by the
fallback.

The decision rule is deliberately conservative: a clear rule majority carries
the headline; the model handles only the residual. That makes the result
inspectable, but it also means taxonomy coverage is a first-class metric, not a
footnote.

## What it does not claim

This is a **point-in-time cross-section, not a trend.** The Adzuna search API
returns current live postings only — it cannot see 2023, so it cannot draw the
pyramid-to-diamond line over time. What it can answer is the honest first
question: *right now, how much of the GBS hiring market is already asking for
agent-ops skills, and how thin is the transactional base?* The trend version
needs a second, historical source and is left as a stated v2, not faked here.

## Method

Two stages, and the split is the point:

1. **Deterministic taxonomy** (`src/taxonomy.py`) carries the headline. Each
   posting is scored by counting distinct phrase hits across three keyword
   families. Every label traces back to the exact phrases that produced it — no
   model in the critical path. The families live in code, editable and visible,
   not hidden in a prompt.
2. **Claude fallback** (`src/classify.py`) decides *only* the residual the
   taxonomy flags as ambiguous (no family hit, or a non-agent-ops tie), and logs
   a one-line reason so its calls are auditable the same way. The share of
   postings that needed the fallback is reported, so you can see how much of the
   answer rests on the model versus the rules.

Accuracy of the taxonomy is measured, not assumed: `eval/eval_classify.py`
scores it against a hand-labelled gold set and prints per-family
precision/recall and a confusion matrix. The shipped `labels.sample.jsonl` is a
clean smoke-test fixture — it scores ~100% and is meant to; replace it with
~60+ of your own hand labels off real postings and expect the honest number to
be lower, especially on judgment-vs-agent_ops overlap.

## Run it

```bash
cp .env.example .env      # add ADZUNA_APP_ID / KEY and ANTHROPIC_API_KEY
make install
make all                  # fetch -> classify -> analyze -> dashboard
make eval                 # taxonomy accuracy vs gold set
make test
```

For a small smoke run, set `GBS_MAX_PAGES=1`; the default is five pages per
search term and country. API keys are read only from the environment and must
never be committed.

`make all` writes `RESULTS.md` (generated from the run, never hand-edited) and a
single-file `dashboard.html` you can open in a browser and hand to a colleague —
filter by family, country, or free-text search, export visible rows as CSV, and
every row shows why it landed there.

## Read the output correctly

- **Family mix:** a distribution of posting classifications, not a measurement
  of employee headcount or organisational design.
- **Fallback share:** how much of the run was not decided by the visible rules;
  a high share is evidence to improve the taxonomy before making a strong claim.
- **Agent-ops share:** a narrow construct for roles involving AI or automation
  orchestration, governance, monitoring, or supervision. It is not a count of
  every job that mentions a digital tool.
- **Seniority:** inferred from title words only. It is directional and should
  not be used as a workforce demographic.

## Repository map

| path | responsibility |
|---|---|
| `src/fetch.py` | keyed Adzuna retrieval and idempotent DuckDB upserts |
| `src/taxonomy.py` | visible phrases, scoring, tie rule, audit hits |
| `src/classify.py` | taxonomy first; Claude fallback for the residual |
| `src/analyze.py` | generated report, chart, country and seniority cuts |
| `src/dashboard.py` | standalone research brief and posting-level audit view |
| `eval/eval_classify.py` | gold-set metrics and confusion matrix |
| `tests/` | deterministic behaviour checks with no API calls |

## Stack

`Python` · `DuckDB` · `Claude API` · `matplotlib` · `pytest`. Data via the
Adzuna API — a keyed, legal job-search endpoint, no scraping.

## Limitations, stated plainly

- **Cross-section, not trend** (above). The headline is a snapshot.
- **CH coverage is thin.** Adzuna is strong on DE/UK; much of the Swiss
  mid-market isn't in it. Defaults to `de,gb` for that reason.
- **Seniority is title-inferred** — a crude keyword split, directional only.
- **The taxonomy is a construct.** Its accuracy is reported, not claimed; read
  the eval before trusting the mix.
- **Postings are demand, not headcount.** They show what employers are asking
  for, which leads the actual workforce and overstates the frontier.
- **Search and duplicate bias.** Adzuna results are shaped by query coverage,
  geography, reposting, and employer behaviour; idempotent IDs remove exact
  duplicates but not all market bias.
- **Fallback quality is a separate risk.** Claude reasons are logged for
  auditability, but the fallback itself needs a labelled evaluation set before
  it should be treated as ground truth.
