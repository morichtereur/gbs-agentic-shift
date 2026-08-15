from src.orgtype import market_type, org_type


def test_advisory_beats_bpo_on_overlapping_names():
    # "Infosys Consulting" must not fall through to the BPO list just because
    # "infosys" appears in it — advisory is checked first for exactly this case.
    assert org_type("Infosys Consulting - Europe") == "advisory"
    assert org_type("Infosys") == "bpo"


def test_bpo_is_in_scope_and_distinct_from_captive():
    assert org_type("Accenture") == "bpo"
    assert org_type("Accenture Operations") == "bpo"
    assert org_type("Genpact") == "bpo"


def test_advisory_matches_bare_ey_without_over_matching():
    assert org_type("EY") == "advisory"
    assert org_type("ey") == "advisory"
    # "ey" as a substring of an ordinary name must not trigger.
    assert org_type("Honeywell") == "captive"
    assert org_type("Seyfarth Logistics") == "captive"


def test_unknown_employer_defaults_to_captive():
    assert org_type("Nestlé") == "captive"
    assert org_type("") == "captive"
    assert org_type(None) == "captive"


def test_market_type_buckets():
    assert market_type("in") == "delivery"
    assert market_type("pl") == "delivery"
    assert market_type("ch") == "retained"
    assert market_type("gb") == "retained"
    assert market_type("es") == "mixed"
    assert market_type("sg") == "mixed"
    assert market_type("zz") == "unclassified"
    assert market_type(None) == "unclassified"


def test_market_type_is_case_and_space_insensitive():
    assert market_type(" IN ") == "delivery"
    assert org_type("  accenture  ") == "bpo"
