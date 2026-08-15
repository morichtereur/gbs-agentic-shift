"""
Generate a single-file HTML dashboard — no server, no build step, open in a
browser and hand to a colleague. Renders the family mix and lets you filter the
underlying postings so a reader can audit any bucket.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
import duckdb

from src import config as C


def run() -> None:
    con = duckdb.connect(str(C.DB_PATH))
    rows = con.execute("""
        SELECT p.source, p.country, p.title, p.company, l.label, l.source, l.hits, l.reason
        FROM labels l JOIN postings p ON p.id = l.id
        WHERE l.label != 'none'
        ORDER BY l.label, p.country
    """).fetchall()
    con.close()

    data = [
        {"source_name": r[0], "country": r[1], "title": r[2], "company": r[3],
         "label": r[4], "source": r[5], "hits": r[6], "reason": r[7]}
        for r in rows
    ]
    payload = json.dumps(data, ensure_ascii=True)
    n = len(data)
    run_date = datetime.now(timezone.utc).date().isoformat()
    source_label = " + ".join(sorted({row["source_name"] for row in data}))

    page = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Point-in-time GBS labour-market research brief.">
<title>GBS / Agentic Shift — Research brief</title>
<style>
  :root {{ --ink:#14213d; --paper:#f5f1e8; --panel:#fffdf8; --line:#d9d5ca; --muted:#667085; --yellow:#f4b942; --teal:#2f8f83; --coral:#d85d45; --slate:#6f7d8c; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink); font:15px/1.5 "Avenir Next", "Helvetica Neue", sans-serif; }}
  .shell {{ max-width:1240px; margin:0 auto; padding:28px 34px 64px; }}
  .masthead {{ display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--ink); padding-bottom:16px; }}
  .mark {{ display:flex; gap:11px; align-items:center; font-size:12px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }}
  .mark-dot {{ width:12px; height:12px; background:var(--yellow); display:block; }}
  .meta {{ color:var(--muted); font-size:12px; }}
  .hero {{ display:grid; grid-template-columns:minmax(0,1.4fr) minmax(280px,.6fr); gap:40px; padding:56px 0 44px; border-bottom:1px solid var(--line); }}
  .eyebrow {{ color:var(--coral); font-size:12px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }}
  h1 {{ max-width:760px; margin:12px 0 18px; font:500 clamp(38px,5vw,68px)/.98 "Iowan Old Style", "Baskerville", Georgia, serif; letter-spacing:-.025em; }}
  .dek {{ max-width:650px; margin:0; color:#475467; font-size:17px; }}
  .hero-note {{ align-self:end; border-left:3px solid var(--yellow); padding:6px 0 6px 18px; color:#475467; font-size:13px; }}
  .hero-note strong {{ display:block; color:var(--ink); font-size:26px; line-height:1.1; }}
  .section-head {{ display:flex; align-items:end; justify-content:space-between; gap:20px; margin:36px 0 16px; }}
  h2 {{ margin:0; font:500 27px/1.1 "Iowan Old Style", "Baskerville", Georgia, serif; }}
  .section-kicker {{ color:var(--muted); font-size:12px; letter-spacing:.08em; text-transform:uppercase; }}
  .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); border-top:1px solid var(--ink); border-bottom:1px solid var(--line); }}
  .kpi {{ min-height:112px; padding:17px 18px 14px 0; border-right:1px solid var(--line); }}
  .kpi:not(:first-child) {{ padding-left:18px; }}
  .kpi:last-child {{ border-right:0; }}
  .kpi-value {{ font:500 34px/1 "Iowan Old Style", Georgia, serif; }}
  .kpi-label {{ margin-top:8px; color:var(--muted); font-size:12px; }}
  .mix {{ display:flex; height:42px; overflow:hidden; background:#e8e4da; }}
  .segment {{ display:flex; align-items:center; justify-content:center; min-width:0; color:#fff; font-size:12px; font-weight:700; transition:width .35s ease; }}
  .segment.transactional {{ background:var(--slate); }} .segment.judgment {{ background:var(--ink); }} .segment.agent_ops {{ background:var(--teal); }}
  .legend {{ display:flex; flex-wrap:wrap; gap:18px; margin-top:12px; color:var(--muted); font-size:12px; }}
  .legend-item {{ display:flex; gap:7px; align-items:center; }} .swatch {{ width:9px; height:9px; display:inline-block; }}
  .swatch.transactional {{ background:var(--slate); }} .swatch.judgment {{ background:var(--ink); }} .swatch.agent_ops {{ background:var(--teal); }}
  .toolbar {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; padding:14px 0; border-top:1px solid var(--ink); border-bottom:1px solid var(--line); }}
  input, select, button {{ font:inherit; }}
  input, select {{ height:40px; border:1px solid #b8b4aa; background:var(--panel); color:var(--ink); padding:0 12px; border-radius:0; }}
  input {{ min-width:260px; flex:1; }}
  button {{ border:1px solid #b8b4aa; background:transparent; color:var(--ink); padding:9px 13px; cursor:pointer; border-radius:0; }}
  button:hover, button:focus-visible {{ border-color:var(--ink); background:#ece7dc; }}
  button.active {{ background:var(--ink); border-color:var(--ink); color:#fff; }}
  button:focus-visible, input:focus-visible, select:focus-visible {{ outline:3px solid rgba(244,185,66,.65); outline-offset:2px; }}
  .toolbar-note {{ color:var(--muted); font-size:12px; margin-left:auto; }}
  .table-wrap {{ overflow-x:auto; background:var(--panel); }}
  table {{ border-collapse:collapse; width:100%; min-width:860px; }}
  td, th {{ text-align:left; padding:14px 13px; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ color:var(--muted); font-size:11px; letter-spacing:.08em; text-transform:uppercase; background:#f0ece3; }}
  td {{ font-size:13px; }} tr:last-child td {{ border-bottom:0; }}
  .title {{ min-width:250px; font-weight:700; }} .company {{ color:var(--muted); }} .country {{ text-transform:uppercase; font-size:11px; letter-spacing:.1em; }}
  .tag {{ display:inline-block; padding:4px 7px; color:#fff; font-size:10px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; }}
  .tag.transactional {{ background:var(--slate); }} .tag.judgment {{ background:var(--ink); }} .tag.agent_ops {{ background:var(--teal); }}
  .why {{ max-width:390px; color:#475467; font-size:12px; }} .source {{ display:block; margin-top:4px; color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:.08em; }}
  .empty {{ padding:45px 20px; color:var(--muted); text-align:center; }}
  .footer {{ display:flex; justify-content:space-between; gap:20px; margin-top:22px; color:var(--muted); font-size:11px; }}
  @media (max-width:760px) {{ .shell {{ padding:18px 18px 42px; }} .masthead {{ align-items:flex-start; gap:12px; }} .hero {{ display:block; padding:38px 0 30px; }} .hero-note {{ margin-top:30px; }} .kpis {{ grid-template-columns:repeat(2,1fr); }} .kpi:nth-child(2) {{ border-right:0; }} .kpi:nth-child(-n+2) {{ border-bottom:1px solid var(--line); }} .kpi:nth-child(3) {{ padding-left:0; }} .toolbar-note {{ width:100%; margin-left:0; }} input {{ min-width:0; width:100%; flex-basis:100%; }} h1 {{ font-size:45px; }} .footer {{ display:block; }} .footer span {{ display:block; margin-top:8px; }} }}
  @media (prefers-reduced-motion:reduce) {{ .segment {{ transition:none; }} }}
</style>
<main class="shell">
  <header class="masthead"><div class="mark"><span class="mark-dot"></span> GBS / agentic shift</div><div class="meta">Research brief · snapshot {run_date}</div></header>
  <section class="hero"><div><div class="eyebrow">Labour-market readout / 01</div><h1>Where the GBS job market is asking for judgment.</h1><p class="dek">A transparent scan of live finance-operations postings, testing whether the pyramid-to-diamond thesis is visible in demand today.</p></div><div class="hero-note"><strong>Point-in-time</strong>Current postings are a cross-section, not a trend line. They show demand, not workforce headcount.</div></section>
  <section><div class="section-head"><h2>The shape of demand</h2><span class="section-kicker">Family mix / n={n}</span></div><div class="kpis" id="kpis"></div><div class="mix" id="mix" role="img" aria-label="Family mix"></div><div class="legend" id="legend"></div></section>
  <section><div class="section-head"><h2>Postings, made inspectable</h2><span class="section-kicker" id="result-count"></span></div><div class="toolbar"><input id="search" type="search" placeholder="Search title, company, or evidence" aria-label="Search postings"><select id="country" aria-label="Filter by country"><option value="all">All countries</option></select><div id="filters"></div><button id="export" type="button">Export visible CSV</button><span class="toolbar-note">Rules leave phrases. Models leave reasons.</span></div><div class="table-wrap"><table><thead><tr><th>Market</th><th>Role</th><th>Family</th><th>Why it landed here</th></tr></thead><tbody id="rows"></tbody></table><div class="empty" id="empty" hidden>No postings match those filters.</div></div></section>
  <footer class="footer"><span>Observed source: {source_label} · market sets in <strong>src/config.py</strong></span><span>Taxonomy is deterministic; Claude handles only the ambiguous residual.</span></footer>
</main>
<script>
const DATA = {payload};
const FAMS = ["transactional","judgment","agent_ops"];
const state = {{ search:"", country:"all", family:"all" }};
function make(tag, text, cls) {{ const el=document.createElement(tag); if(text!==undefined) el.textContent=text; if(cls) el.className=cls; return el; }}
function counts(rows=DATA) {{ const c={{}}; FAMS.forEach(f=>c[f]=0); rows.forEach(d=>c[d.label]++); return c; }}
function drawSummary() {{
  const c=counts(), total=DATA.length||1, k=document.getElementById("kpis"); k.innerHTML="";
  [[total,"relevant postings"],[c.judgment,"judgment family"],[c.agent_ops,"agent_ops family"],[Math.round(100*DATA.filter(d=>d.source==="model").length/total)+"%","Claude fallback"]].forEach(x=>{{ const box=make("div",undefined,"kpi"); box.append(make("div",x[0],"kpi-value"),make("div",x[1],"kpi-label")); k.append(box); }});
  const mix=document.getElementById("mix"); mix.innerHTML="";
  FAMS.forEach(f=>{{ const share=100*c[f]/total; const seg=make("div",share>=8?f+" · "+Math.round(share)+"%":"","segment "+f); seg.style.width=share+"%"; seg.setAttribute("aria-label",f+" "+c[f]); mix.append(seg); }});
  const legend=document.getElementById("legend"); legend.innerHTML=""; FAMS.forEach(f=>{{ const item=make("span",undefined,"legend-item"); item.append(make("i",undefined,"swatch "+f),make("span",f+" · "+c[f])); legend.append(item); }});
}}
function filtered() {{ const q=state.search.toLowerCase(); return DATA.filter(d=>(state.family==="all"||d.label===state.family)&&(state.country==="all"||d.country===state.country)&&(!q||[d.title,d.company,d.source_name,d.hits,d.reason].join(" ").toLowerCase().includes(q))); }}
function drawFilters() {{ const box=document.getElementById("filters"); box.innerHTML=""; ["all",...FAMS].forEach(f=>{{ const b=make("button",f); if(f===state.family) b.className="active"; b.onclick=()=>{{ state.family=f; render(); }}; box.append(b); }}); }}
function drawRows() {{ const rows=filtered(), tb=document.getElementById("rows"), empty=document.getElementById("empty"); tb.innerHTML=""; document.getElementById("result-count").textContent=rows.length+" of "+DATA.length+" shown"; empty.hidden=rows.length>0; rows.forEach(d=>{{ const tr=make("tr"); const why=d.source==="model"?(d.reason||"Model classification"):(d.hits||"Keyword evidence"); const market=make("td"); market.append(make("div",d.source_name+" / "+d.country,"country"),make("div",d.company||"Company not listed","company")); const role=make("td",d.title,"title"); const family=make("td"); family.append(make("span",d.label,"tag "+d.label)); const evidence=make("td"); evidence.append(make("span",why,"why"),make("span",d.source==="model"?"Claude fallback":"Deterministic taxonomy","source")); tr.append(market,role,family,evidence); }}); }}
function exportCsv() {{ const headers=["country","title","company","label","source","hits","reason"]; const body=filtered().map(d=>headers.map(h=>'"'+String(d[h]||"").replaceAll('"','""')+'"').join(",")); const blob=new Blob([[headers.join(","),...body].join("\\n")],{{type:"text/csv"}}); const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download="gbs-agentic-shift-visible.csv"; a.click(); URL.revokeObjectURL(a.href); }}
function render() {{ drawSummary(); drawFilters(); drawRows(); }}
const countries=[...new Set(DATA.map(d=>d.country))].sort(), select=document.getElementById("country"); countries.forEach(c=>select.append(make("option",c))); document.getElementById("search").oninput=e=>{{state.search=e.target.value;drawRows();}}; select.onchange=e=>{{state.country=e.target.value;drawRows();}}; document.getElementById("export").onclick=exportCsv; render();
</script>
"""
    out = C.ROOT / "dashboard.html"
    out.write_text(page.format(n=n, payload=payload, run_date=run_date,
                   source_label=source_label))
    print(f"Wrote dashboard.html ({n} postings).")


if __name__ == "__main__":
    run()
