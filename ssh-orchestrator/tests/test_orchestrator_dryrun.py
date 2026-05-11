from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest
import yaml

from ssh_orchestrator.cli import main
from ssh_orchestrator.engagement import load_engagement
from ssh_orchestrator.modules import resolve_modules
from ssh_orchestrator.orchestrator import execute
from ssh_orchestrator.report import write_run


@pytest.fixture()
def plan_path(tmp_path: Path) -> Path:
    plan = {
        "engagement": {
            "id": "eng-dryrun",
            "name": "Dry run test",
            "authorized_by": "sec@example.com",
            "authorization_date": "2026-05-01",
            "scope_expires": "2026-12-31",
            "max_risk": "low",
        },
        "ssh": {"default_user": "audit"},
        "targets": [
            {"host": "host-a.example.com", "tags": ["a"]},
            {"host": "host-b.example.com", "tags": ["b"]},
        ],
        "modules": ["system_info", "ssh_audit"],
        "limits": {"max_parallel": 2, "per_command_timeout": 30},
    }
    p = tmp_path / "engagement.yaml"
    p.write_text(yaml.safe_dump(plan))
    return p


def test_dry_run_produces_run_artifact(plan_path: Path, tmp_path: Path):
    eng = load_engagement(plan_path)
    modules = resolve_modules(eng.modules)
    run = execute(eng, modules, dry_run=True, today=dt.date(2026, 6, 1))

    assert len(run.hosts) == 2
    assert all(h.detected_platform == "dry-run" for h in run.hosts)
    for host in run.hosts:
        assert host.checks
        for ce in host.checks:
            assert ce.skipped_reason == "dry-run"

    out_dir = tmp_path / "out"
    run_path = write_run(run, out_dir)
    payload = json.loads(run_path.read_text())

    assert payload["run"]["engagement_id"] == "eng-dryrun"
    assert payload["totals"]["hosts"] == 2
    expected_checks = sum(len(m.checks) for m in modules) * 2
    assert payload["totals"]["checks"] == expected_checks
    assert payload["totals"]["skipped"] == expected_checks
    assert payload["artifact_sha256"].startswith("sha256:")

    # No evidence should be on disk for skipped checks.
    evidence = out_dir / "evidence"
    assert not any(evidence.rglob("*.stdout"))


def test_cli_validate_succeeds(plan_path: Path, capsys):
    rc = main(["validate", str(plan_path)])
    captured = capsys.readouterr()
    assert rc == 0
    assert "OK" in captured.out


def test_cli_validate_rejects_unknown_module(tmp_path: Path):
    plan = {
        "engagement": {
            "id": "eng-x",
            "name": "x",
            "authorized_by": "x",
            "authorization_date": "2026-01-01",
            "scope_expires": "2026-12-31",
        },
        "ssh": {"default_user": "audit"},
        "targets": [{"host": "h.example.com"}],
        "modules": ["does_not_exist"],
    }
    p = tmp_path / "eng.yaml"
    p.write_text(yaml.safe_dump(plan))
    rc = main(["validate", str(p)])
    assert rc == 2


def test_cli_run_dryrun_writes_outputs(plan_path: Path, tmp_path: Path, capsys):
    out = tmp_path / "out"
    rc = main(["run", str(plan_path), "-o", str(out), "--dry-run"])
    captured = capsys.readouterr()
    assert rc == 0
    assert (out / "run.json").exists()
    assert "hosts=2" in captured.out


def test_cli_list_modules(capsys):
    rc = main(["list-modules"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "system_info" in captured.out
    assert "ssh_audit" in captured.out


def test_risk_gate_blocks_high_risk_module(tmp_path: Path):
    high_risk_module = {
        "module": {
            "id": "evil",
            "name": "Evil",
            "category": "x",
            "risk": "intrusive",
            "platforms": ["linux"],
            "checks": [{"id": "a", "command": "true"}],
        }
    }
    user_dir = tmp_path / "modules"
    user_dir.mkdir()
    (user_dir / "evil.yaml").write_text(yaml.safe_dump(high_risk_module))

    plan = {
        "engagement": {
            "id": "eng-risk",
            "name": "x",
            "authorized_by": "x",
            "authorization_date": "2026-01-01",
            "scope_expires": "2026-12-31",
            "max_risk": "low",
        },
        "ssh": {"default_user": "audit"},
        "targets": [{"host": "h.example.com"}],
        "modules": ["evil"],
    }
    plan_path = tmp_path / "eng.yaml"
    plan_path.write_text(yaml.safe_dump(plan))
    rc = main(["validate", str(plan_path), "--module-dir", str(user_dir)])
    assert rc == 2
