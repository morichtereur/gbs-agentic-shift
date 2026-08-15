# gbs-agentic-shift

**A transparent labour-market readout for the GBS pyramid-to-diamond thesis.**

![Python](https://img.shields.io/badge/Python-3.11%2B-14213d?style=flat-square)
![Method](https://img.shields.io/badge/headline-deterministic%20taxonomy-f4b942?style=flat-square)
![Data](https://img.shields.io/badge/data-Adzuna%20(snapshot)%20%7C%20Jooble%20pending-2f8f83?style=flat-square)

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

This is a **point-in-time cross-section, not a trend.** The search APIs return
current live postings only — they cannot see 2023, so they cannot draw the
pyramid-to-diamond line over time. The committed snapshot is Adzuna-only;
Jooble is an implemented but currently unavailable second source. What the
project can answer is the honest first question: *right now, how much of the
GBS hiring market is already asking for agent-ops skills, and how thin is the
transactional base?* The trend version needs a historical source and is left
as a stated v2, not faked here.

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
cp .env.example .env      # add Adzuna, Jooble and Anthropic keys
make install
make all                  # fetch -> classify -> analyze -> dashboard
make eval                 # taxonomy accuracy vs gold set
make test
```

For a small smoke run, set `GBS_MAX_PAGES=1`; the default is five pages per
search term and country. Override `ADZUNA_COUNTRIES` or `JOOBLE_COUNTRIES` when
you want a narrower comparison. API keys are read only from the environment and
must never be committed.

Set `GBS_RECLASSIFY=1` when the taxonomy changes and an existing DuckDB run
needs to be classified again. The default `0` keeps normal runs idempotent.

After editing deterministic phrases, use `make refresh-taxonomy` to update all
clear labels without making Claude calls. Existing model labels are preserved
only where the revised taxonomy remains ambiguous.

`make all` writes `RESULTS.md` (generated from the run, never hand-edited) and a
single-file `dashboard.html` you can open in a browser and hand to a colleague —
filter by family, country, or free-text search, export visible rows as CSV, and
every row shows why it landed there.

To create a balanced annotation worksheet from a completed local run:

```bash
.venv/bin/python -m eval.build_gold_template
```

Read each posting and fill its empty `gold` value with exactly one of
`transactional`, `judgment`, or `agent_ops`. Copy the completed worksheet to
`eval/labels.jsonl`, then run `make eval`. The template uses existing labels
only to balance the sample; it does not copy them into the gold set.

For country-level validation, generate a separate stratified worksheet:

```bash
.venv/bin/python -m eval.build_country_gold_template
```

It selects 10 relevant postings per observed market (`de`, `gb`, `in`, `nl`,
`pl`, `za`). Label these independently with `transactional`, `judgment`,
`agent_ops`, or `none`; do not reuse the model labels. This is the required
check before interpreting country-level agent_ops differences, especially for
Polish-language postings.

Evaluate the completed worksheet with `make eval-country`; it reports accuracy
and `agent_ops` recall separately for each market.

The current country review is a small diagnostic set (`n=10` per market), not
a prevalence estimate. It is useful for finding language and recall failures,
but it is too small to support ranking countries or making a country-level
agent_ops claim on its own.

The repository includes a committed generated snapshot in `RESULTS.md`,
`dashboard.html`, and `data/chart_mix.png`, so a reviewer can see an actual
finding before configuring API keys. These are dated point-in-time outputs, not
historical data; rerunning the pipeline replaces them with a newer snapshot.
The current committed snapshot is the complete Adzuna-only run across
`ch`, `de`, `es`, `gb`, `in`, `mx`, `nl`, `pl`, `sg`, and `za`. Jooble
integration is implemented, but its freshly requested key currently returns
`403 Forbidden`, so no Jooble rows are silently treated as zero demand.

The committed 60-posting gold set currently scores the taxonomy at **66.7%
accuracy**; `agent_ops` precision is **100%**, but recall is only **42.9%**.
That recall is reported because a low observed `agent_ops` share is otherwise
easy to mistake for proof that the market has no agent-ops demand.

The practical sensitivity check is still small: `33` observed agent_ops labels
out of `2,159` relevant postings is about `1.5%`. If the measured `42.9%`
recall missed a similar share of true positives, the implied share would be
roughly `3.6%`, or about `4%`. That is an upper-bound illustration, not a new
estimate, but even that correction leaves agent_ops marginal in this snapshot.

The latest diagnostic run reaches `100%` agent_ops recall in the DE, IN, NL,
and PL slices, but the overall country-set accuracy is only `60%`. This is a
debugging signal for taxonomy work, not a country ranking or a market estimate.
The **planned** 12-market design is source-specific: Adzuna targets `PL`, `IN`,
`MX`, `NL`, `DE`, `CH`, `ES`, and `SG`; Jooble targets `PT`, `RO`, `HU`, and
`CZ`. Those planned markets are distinct from the committed Adzuna snapshot
above. The report keeps source provenance visible because Jooble and Adzuna are
aggregators with potentially overlapping supply.

The Jooble adapter fails closed: an API `403` or unavailable Jooble market is
reported as unavailable and contributes no zero-valued jobs to the findings.
This keeps a source outage from being mistaken for weak hiring demand.

## Read the output correctly

- **Family mix:** a distribution of posting classifications, not a measurement
  of employee headcount or organisational design.
- **Confidence is asymmetric:** the `agent_ops` precision is strong in the
  current 60-case gold set, so detected agent-ops roles are credible; recall is
  only `42.9%`, so a low agent-ops share is a lower bound. The
  transactional-vs-judgment split is exploratory because overall accuracy is
  only `66.7%`.
- **Do not headline the family split.** The `transactional`/`judgment`
  distribution is exploratory at current accuracy; the defensible headline is
  that detected agent_ops demand is small, with recall reported and sensitivity
  shown rather than hidden.
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
| `src/fetch.py` | source-aware Adzuna/Jooble retrieval and idempotent DuckDB upserts |
| `src/taxonomy.py` | visible phrases, scoring, tie rule, audit hits |
| `src/classify.py` | taxonomy first; Claude fallback for the residual |
| `src/analyze.py` | generated report, chart, country and seniority cuts |
| `src/dashboard.py` | standalone research brief and posting-level audit view |
| `eval/eval_classify.py` | gold-set metrics and confusion matrix |
| `eval/agent_ops_audit.jsonl` | manual review of every current agent_ops row |
| `tests/` | deterministic behaviour checks with no API calls |

## Stack

`Python` · `DuckDB` · `Claude API` · `matplotlib` · `pytest`. Data via keyed
Adzuna and Jooble search APIs — no scraping.

## Limitations, stated plainly

- **Cross-section, not trend** (above). The headline is a snapshot.
- **Coverage varies by source and market.** The twelve markets are split
  deliberately across Adzuna and Jooble; an unavailable source is not counted
  as zero demand.
- **Language bias.** The taxonomy is strongest in English and German. Polish
  finance and automation phrases are now included, but PL recall still needs
  a larger Polish gold set before country-level agent_ops comparisons are
  treated as robust. A low PL count may be a language artifact, not a market
  finding.
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
- **Cross-source overlap.** Adzuna and Jooble are aggregators, not independent
  censuses. A future combined headline needs URL/title/company deduplication and
  a source-overlap report before pooled counts should be interpreted.
