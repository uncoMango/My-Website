# tests/conftest.py
# =========================================================
# Hurricane Readiness work order (2026-08-21): the Stripe fulfillment
# idempotency tracker (blueprints/payments.py's STRIPE_FULFILLED_SESSIONS_FILE)
# is a new, real file on disk. Without isolating it, any test that
# exercises /stripe/success or /stripe/webhook would write real
# idempotency state into the actual repository file -- this autouse
# fixture gives every test its own disposable copy instead, with no
# changes required to any existing test file.
# =========================================================

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from blueprints import payments as payments_module  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate_stripe_fulfillment_tracking(tmp_path, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_FULFILLED_SESSIONS_FILE", tmp_path / "stripe_fulfilled_sessions.json")
