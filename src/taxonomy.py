"""
Deterministic skill taxonomy for GBS job postings.

This is the auditable first pass. Every label a posting receives can be traced
to the exact phrases that produced it — no model judgement, no black box. The
LLM fallback in classify.py only runs on the residual this can't decide.

Three families, mapped to McKinsey's pyramid->diamond thesis:
  - transactional : rule-based processing work (the shrinking base of the pyramid)
  - judgment      : analytical / advisory / planning work (the widening middle)
  - agent_ops     : managing the "agent force" — the new layer that didn't exist

A posting is scored by counting distinct family hits. The label is the family
with the most hits; ties and zero-hit postings are flagged ambiguous and handed
to the model fallback. Every hit is kept so a reader can see WHY.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# ---------------------------------------------------------------------------
# Keyword families. Phrases are matched on word boundaries, case-insensitive.
# Multi-word phrases are matched as phrases. Keep these visible and editable —
# the taxonomy IS the method, so it lives in code, not in a model prompt.
# ---------------------------------------------------------------------------

FAMILIES: Dict[str, List[str]] = {
    "transactional": [
        "data entry", "invoice processing", "process invoices", "accounts payable clerk",
        "accounts receivable clerk", "ap clerk", "ar clerk", "cash application",
        "manual reconciliation", "posting entries", "keying", "ticket handling",
        "high volume processing", "transaction processing", "back office processing",
        "rpa maintenance", "bot maintenance", "process transactions", "master data maintenance",
        "document handling", "scanning", "sla adherence", "queue management",
        "accounts payable", "accounts receivable", "general ledger", "bookkeeping",
        "invoice", "payment processing", "journal entries", "journal posting",
        "account reconciliation", "month-end close", "month end close", "financial close",
        "closing activities", "r2r processing", "record to report processing",
        "operations support", "accountant", "financial accountant", "bookkeeper",
        "buchhalter", "buchhaltung", "finanzbuchhalter", "finanzbuchhaltung",
        "debitorenbuchhaltung", "sachbearbeiter", "customer service",
        "process associate", "ops associate", "operations associate", "operations assistant",
        "finance operations assistant", "finance & operations", "record to report ops",
        "order to cash operations", "r2r analyst", "procure-to-pay specialist",
        "billing supervisor", "billing", "arrears recovery", "accounting shared services",
        "working student", "werkstudent", "associate",
        "księgowość", "faktury", "należności", "zobowiązania", "uzgodnienia",
        "księgowy", "księgowa", "raportowanie finansowe", "zamknięcie miesiąca",
    ],
    "judgment": [
        "fp&a", "financial planning and analysis", "forecasting", "scenario planning",
        "business partnering", "business partner", "strategic sourcing", "category management",
        "decision support", "advisory", "analytics", "data analysis", "insight",
        "commentary", "variance analysis", "modelling", "modeling", "stakeholder management",
        "continuous improvement", "process design", "process reengineering", "transformation",
        "root cause", "next best action", "recommendation", "planning and forecasting",
        "management reporting", "controllership", "risk assessment",
        "controlling", "financial analyst", "business controller", "business control",
        "reporting analyst", "financial reporting", "process optimization",
        "finance transformation", "business intelligence", "performance management",
        "data & analytics", "commercial finance", "p2p transformation", "o2c transformation",
        "finance manager", "accounting manager", "business analyst", "project controller",
        "controller", "tax manager", "contract manager", "process manager",
        "sap consultant", "business consultant", "rechnungswesen",
        "process owner", "global process owner", "business process", "solution consultant",
        "project manager", "enterprise architect", "tax advisor", "financial analyst",
        "steering manager", "business excellence", "controls & compliance", "einkäufer",
        "projektmanager", "director of finance", "head of finance", "finance lead",
        "team lead finance", "teamleiter finance", "shared services lead", "director",
        "project", "consultant",
        "controlling finansowy", "analiza danych", "raportowanie", "planowanie finansowe",
        "transformacja finansów", "optymalizacja procesów", "doradztwo finansowe",
    ],
    "agent_ops": [
        "agent orchestration", "orchestrate agents", "agentic", "ai agent", "ai agents",
        "prompt engineering", "prompt design", "llm", "large language model", "genai",
        "generative ai", "copilot", "ai ops", "aiops", "mlops", "manage digital workforce",
        "digital workforce", "digital labour", "digital labor", "human in the loop",
        "ai governance", "model monitoring", "automation design", "intelligent automation",
        "ai orchestration", "supervise agents", "ai-enabled", "conversational ai",
        "process automation", "workflow automation", "automation engineer", "automation strategy",
        "automation platform", "rpa", "rpa automation", "ai automation",
        "sap ai", "autonomous finance", "smart automation",
        "ki-agent", "ki-agenten", "ki-first", "ai-native finance", "applied ai",
        "design and deploy ai agents", "develop ai agents", "agent creation",
        "automatyzacja", "automatyzacji", "automatyzacja procesów", "automatyzacji procesów",
        "robotyzacja", "robotyzacji", "sztuczna inteligencja",
        "uczenie maszynowe", "agenci ai", "orkiestracja agentów",
    ],
}

# Pre-compile one regex per phrase, longest-first so "ai agents" wins over "ai".
_COMPILED: Dict[str, List[tuple[str, re.Pattern]]] = {}
for _fam, _phrases in FAMILIES.items():
    _ordered = sorted(set(_phrases), key=len, reverse=True)
    _COMPILED[_fam] = [
        (p, re.compile(r"(?<!\w)" + re.escape(p) + r"(?!\w)", re.IGNORECASE))
        for p in _ordered
    ]


@dataclass
class TaxonomyResult:
    label: str                                  # transactional | judgment | agent_ops | ambiguous
    scores: Dict[str, int] = field(default_factory=dict)
    hits: Dict[str, List[str]] = field(default_factory=dict)   # family -> matched phrases
    ambiguous: bool = False                      # True => send to model fallback

    def to_row(self) -> dict:
        return {
            "label": self.label,
            "score_transactional": self.scores.get("transactional", 0),
            "score_judgment": self.scores.get("judgment", 0),
            "score_agent_ops": self.scores.get("agent_ops", 0),
            "ambiguous": self.ambiguous,
            "hits": "; ".join(
                f"{fam}:{','.join(ph)}" for fam, ph in self.hits.items() if ph
            ),
        }


def classify_text(text: str) -> TaxonomyResult:
    """Score one posting (title + description concatenated) by family."""
    text = text or ""
    scores: Dict[str, int] = {}
    hits: Dict[str, List[str]] = {}

    for fam, patterns in _COMPILED.items():
        matched = [phrase for phrase, rx in patterns if rx.search(text)]
        hits[fam] = matched
        scores[fam] = len(matched)

    # Employer/product AI language must not turn a sales, customer-success, or
    # payments role into agent operations. Keep the rule visible and conservative.
    role_text = text[:180]
    if re.search(r"(?i)\b(account executive|head of sales|sales manager|customer success manager|operations manager\s*[—-]?\s*payments)\b", role_text):
        scores["agent_ops"] = 0
        hits["agent_ops"] = []

    top = max(scores.values())
    if top == 0:
        return TaxonomyResult("ambiguous", scores, hits, ambiguous=True)

    leaders = [fam for fam, s in scores.items() if s == top]
    if len(leaders) > 1:
        # Tie: agent_ops is the discriminating signal for the thesis, so a
        # posting that ties agent_ops against anything is NOT ambiguous —
        # its agent-ops content is the point. Only non-agent-ops ties are.
        if "agent_ops" in leaders:
            return TaxonomyResult("agent_ops", scores, hits, ambiguous=False)
        return TaxonomyResult("ambiguous", scores, hits, ambiguous=True)

    return TaxonomyResult(leaders[0], scores, hits, ambiguous=False)


if __name__ == "__main__":
    samples = [
        "Accounts Payable Clerk — high volume invoice processing, manual reconciliation, SLA adherence.",
        "Finance Business Partner — FP&A, forecasting, scenario planning and decision support for the CFO.",
        "GBS Automation Lead — orchestrate AI agents, prompt engineering, manage the digital workforce.",
        "Office coordinator for the Krakow site.",
    ]
    for s in samples:
        r = classify_text(s)
        print(f"{r.label:14} {r.scores}  <- {s[:55]}")
