"""Guards on the committed dashboard artifact.

The dashboard is a single generated HTML file, so its JavaScript never runs
in CI. These check the shape of what shipped rather than its behaviour —
enough to catch the failure that actually happened: `drawRows` built each
row and dropped it, because the built `<tr>` was never appended to the
table body. Counts rendered correctly the whole time, so the bug looked
like styling rather than logic.

Not a substitute for opening the file. A generator change that is not
regenerated into dashboard.html still passes here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

DASHBOARD = Path(__file__).parent.parent / "dashboard.html"


@pytest.fixture(scope="module")
def html() -> str:
    if not DASHBOARD.exists():
        pytest.skip("dashboard.html not generated yet — run `make dashboard`")
    return DASHBOARD.read_text(encoding="utf-8")


def _draw_rows_body(html: str) -> str:
    match = re.search(r"function drawRows\(\)\s*\{(.*?)\n", html, re.DOTALL)
    assert match, "drawRows() not found in the generated dashboard"
    return match.group(1)


def test_rows_are_appended_to_the_table(html: str) -> None:
    body = _draw_rows_body(html)
    assert "tb.append(tr)" in body or "tb.appendChild(tr)" in body, (
        "drawRows() builds each <tr> but never appends it — the table renders "
        "empty while the result count still reports the filtered total"
    )


def test_table_body_target_exists(html: str) -> None:
    assert 'id="rows"' in html, "drawRows() writes into #rows; the element must exist"


def test_data_payload_is_present(html: str) -> None:
    assert re.search(r"const DATA\s*=\s*\[", html), "no DATA array embedded in the dashboard"
