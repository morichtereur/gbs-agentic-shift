from src.taxonomy import classify_text


def test_transactional():
    r = classify_text("Invoice processing clerk, manual reconciliation, data entry.")
    assert r.label == "transactional"
    assert not r.ambiguous


def test_judgment():
    r = classify_text("FP&A analyst: forecasting, scenario planning, decision support.")
    assert r.label == "judgment"


def test_agent_ops():
    r = classify_text("Orchestrate AI agents, prompt engineering, manage digital workforce.")
    assert r.label == "agent_ops"


def test_agent_ops_wins_ties():
    # A posting mixing judgment and agent-ops signal equally is agent_ops,
    # because the agent-ops content is the thesis-relevant signal.
    r = classify_text("Forecasting and scenario planning while you orchestrate AI agents and design intelligent automation.")
    assert r.label == "agent_ops"
    assert not r.ambiguous


def test_non_agent_tie_is_ambiguous():
    r = classify_text("Invoice processing with forecasting.")
    assert r.label == "ambiguous"
    assert r.ambiguous
    assert r.scores["transactional"] == r.scores["judgment"]


def test_hits_are_auditable():
    r = classify_text("Invoice processing clerk with manual reconciliation.")
    row = r.to_row()
    assert "transactional:manual reconciliation,invoice processing" in row["hits"]
    assert row["score_transactional"] == 2
    assert row["score_judgment"] == 0
    assert row["score_agent_ops"] == 0


def test_unrelated_is_ambiguous():
    r = classify_text("Front desk receptionist for the Zurich office.")
    assert r.ambiguous
    assert all(score == 0 for score in r.scores.values())


def test_word_boundary_no_false_ai_match():
    # "email" must not trigger the "ai" family via substring.
    r = classify_text("Coordinate email correspondence and calendar invites.")
    assert r.scores["agent_ops"] == 0
