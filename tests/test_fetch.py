from src.fetch import _normalise, _stable_id


def test_adzuna_id_remains_stable_during_migration():
    row = _normalise(
        "adzuna",
        "de",
        "finance operations",
        {
            "id": 123,
            "title": "Finance Analyst",
            "company": {"display_name": "Example"},
            "description": "Forecasting",
            "redirect_url": "https://example.test/job/123",
        },
    )
    assert row[0] == "123"
    assert row[1] == "adzuna"
    assert row[2] == "123"


def test_jooble_id_is_namespaced_and_uses_link():
    row = _normalise(
        "jooble",
        "pt",
        "shared services finance",
        {
            "title": "Accounts Payable Specialist",
            "company": "Example",
            "snippet": "Invoice processing",
            "location": "Lisbon",
            "link": "https://example.test/job/456",
        },
    )
    assert row[0].startswith("jooble_")
    assert row[1:4] == ["jooble", "https://example.test/job/456", "pt"]
    assert row[5] == "Accounts Payable Specialist"


def test_source_ids_do_not_collide():
    assert _stable_id("adzuna", "1", "", "", "") != _stable_id(
        "jooble", "1", "", "", ""
    )


def test_jooble_snippet_is_used_as_description():
    row = _normalise(
        "jooble", "cz", "finance operations",
        {"title": "Finance Operations", "snippet": "Process invoices.",
         "company": "Example", "location": "Prague", "link": "https://example.test"},
    )
    assert row[7] == "Process invoices."
    assert row[11] == "Prague"
