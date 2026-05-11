from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest
import yaml

from ssh_orchestrator.engagement import (
    EngagementError,
    load_engagement,
    parse_engagement,
)


def _base_plan() -> dict:
    return {
        "engagement": {
            "id": "eng-1",
            "name": "Test",
            "authorized_by": "sec@example.com",
            "authorization_date": "2026-05-01",
            "scope_expires": "2026-05-31",
            "max_risk": "low",
        },
        "ssh": {"default_user": "audit"},
        "targets": [{"host": "host01.example.com"}],
        "modules": ["system_info"],
    }


def test_parse_minimal_plan():
    eng = parse_engagement(_base_plan())
    assert eng.id == "eng-1"
    assert eng.targets[0].host == "host01.example.com"
    assert eng.targets[0].user == "audit"
    assert eng.targets[0].port == 22
    assert eng.max_risk == "low"
    assert eng.modules == ("system_info",)


def test_load_example_plan():
    example = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "example_engagement.yaml"
    )
    eng = load_engagement(example)
    assert eng.id == "eng-2026-q2-baseline"
    assert any(t.host == "db01.example.com" and t.port == 2222 for t in eng.targets)


def test_assert_in_scope_rejects_unknown_host():
    eng = parse_engagement(_base_plan())
    with pytest.raises(EngagementError):
        eng.assert_in_scope("attacker.example.org")


def test_expired_engagement_refused():
    plan = _base_plan()
    plan["engagement"]["scope_expires"] = "2026-05-10"
    eng = parse_engagement(plan)
    eng.assert_active(today=dt.date(2026, 5, 10))  # boundary ok
    with pytest.raises(EngagementError):
        eng.assert_active(today=dt.date(2026, 5, 11))


def test_inactive_before_authorization():
    eng = parse_engagement(_base_plan())
    with pytest.raises(EngagementError):
        eng.assert_active(today=dt.date(2026, 4, 30))


def test_expiry_must_be_after_authorization():
    plan = _base_plan()
    plan["engagement"]["scope_expires"] = "2026-04-30"
    with pytest.raises(EngagementError):
        parse_engagement(plan)


def test_invalid_max_risk():
    plan = _base_plan()
    plan["engagement"]["max_risk"] = "bogus"
    with pytest.raises(EngagementError):
        parse_engagement(plan)


def test_risk_gate():
    eng = parse_engagement(_base_plan())  # max_risk=low
    eng.assert_module_risk_allowed("m", "passive")
    eng.assert_module_risk_allowed("m", "low")
    with pytest.raises(EngagementError):
        eng.assert_module_risk_allowed("m", "high")


def test_invalid_host_rejected():
    plan = _base_plan()
    plan["targets"] = [{"host": "evil; rm -rf /"}]
    with pytest.raises(EngagementError):
        parse_engagement(plan)


def test_invalid_user_rejected():
    plan = _base_plan()
    plan["targets"] = [{"host": "ok.example.com", "user": "; whoami"}]
    with pytest.raises(EngagementError):
        parse_engagement(plan)


def test_duplicate_targets_rejected():
    plan = _base_plan()
    plan["targets"] = [
        {"host": "h.example.com"},
        {"host": "h.example.com"},
    ]
    with pytest.raises(EngagementError):
        parse_engagement(plan)


def test_empty_modules_rejected():
    plan = _base_plan()
    plan["modules"] = []
    with pytest.raises(EngagementError):
        parse_engagement(plan)


def test_load_engagement_round_trip(tmp_path: Path):
    plan_path = tmp_path / "eng.yaml"
    plan_path.write_text(yaml.safe_dump(_base_plan()))
    eng = load_engagement(plan_path)
    assert eng.source_path == plan_path
