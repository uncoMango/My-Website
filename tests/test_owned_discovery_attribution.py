import pytest
import stripe

import app as app_module
from blueprints import payments


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def test_youtube_bridge_sets_bounded_first_party_attribution(client):
    response = client.get(
        "/campaign/003?utm_source=youtube&utm_medium=organic_video"
        "&utm_campaign=campaign_003&utm_term=related_video"
        "&utm_content=rrwpXfaXu2E"
    )
    cookies = "\n".join(response.headers.getlist("Set-Cookie"))
    assert "rf_source=youtube" in cookies
    assert "rf_medium=organic_video" in cookies
    assert "rf_campaign=campaign_003" in cookies
    assert "rf_bridge=related_video" in cookies
    assert "rf_content=rrwpXfaXu2E" in cookies
    assert "rf_youtube_bridge_visit" in response.get_data(as_text=True)


def test_unknown_utm_source_does_not_become_durable_attribution(client):
    response = client.get("/campaign/001?utm_source=untrusted")
    cookies = "\n".join(response.headers.getlist("Set-Cookie"))
    assert "rf_source=" not in cookies


def test_ranch_verification_traffic_is_marked_without_deleting_history(client):
    first = client.get("/campaign/001?rf_verify=1")
    assert "rf_verification=1" in "\n".join(first.headers.getlist("Set-Cookie"))
    assert "'traffic_type': 'ranch_verification'" in first.get_data(as_text=True)

    later = client.get("/campaign/002")
    assert "'traffic_type': 'ranch_verification'" in later.get_data(as_text=True)


def test_normal_audience_traffic_is_not_marked_as_verification(client):
    response = client.get("/campaign/001")
    assert "'traffic_type': 'ranch_verification'" not in response.get_data(as_text=True)


def test_youtube_attribution_reaches_stripe_metadata(client, monkeypatch):
    captured = {}

    class FakeSession:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs)
            return type("Session", (), {"url": "https://checkout.example/session"})()

    monkeypatch.setattr(stripe.checkout, "Session", FakeSession)
    monkeypatch.setattr(payments, "STRIPE_SECRET_KEY", "sk_test")
    monkeypatch.setattr(payments, "STRIPE_ENABLED", True)
    client.set_cookie("rf_source", "youtube")
    client.set_cookie("rf_medium", "organic_video")
    client.set_cookie("rf_campaign", "campaign_002")
    client.set_cookie("rf_bridge", "related_video")
    client.set_cookie("rf_content", "_nnPJXOwV3I")

    response = client.post("/stripe/create-session/rotten_fencepost_field_guide")

    assert response.status_code in {302, 303}
    assert captured["metadata"] == {
        "product_id": "rotten_fencepost_field_guide",
        "attribution_source": "youtube",
        "attribution_medium": "organic_video",
        "attribution_campaign": "campaign_002",
        "attribution_bridge": "related_video",
        "attribution_content": "_nnPJXOwV3I",
    }
