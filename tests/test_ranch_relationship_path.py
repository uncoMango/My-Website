"""The Ranch's continuing relationship uses existing public infrastructure."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


@pytest.mark.parametrize("path", ["/", "/campaign/001", "/campaign/002", "/campaign/003"])
def test_public_journey_offers_the_existing_youtube_relationship(path, client):
    html = client.get(path).get_data(as_text=True)
    assert "Keep Riding with the Ranch" in html
    assert "https://www.youtube.com/@keaupuniokeakua?sub_confirmation=1" in html
    assert "rf_relationship_follow" in html


def test_sitewide_footer_no_longer_promises_an_inactive_email_relationship(client):
    html = client.get("/").get_data(as_text=True)
    assert 'action="/subscribe"' not in html
    assert "No paid membership or email list required" in html


def test_campaign_preserves_free_value_and_paid_deepening(client):
    html = client.get("/campaign/001").get_data(as_text=True)
    assert "Go Deeper" in html
    assert "/product/prod_find_the_cause_not_the_symptoms" in html
