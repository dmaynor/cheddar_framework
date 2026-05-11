from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ssh_orchestrator.modules import (
    BUILTIN_DIR,
    ModuleError,
    discover_modules,
    load_module,
    parse_module,
    resolve_modules,
)


def test_builtins_load():
    catalog = discover_modules()
    # All shipped modules should parse.
    expected = {
        "system_info",
        "user_audit",
        "ssh_audit",
        "listening_services",
        "sudo_audit",
        "filesystem_hygiene",
        "package_audit_linux",
        "package_audit_macos",
    }
    assert expected.issubset(set(catalog))
    for module in catalog.values():
        assert module.checks
        assert module.risk in {"passive", "low", "medium", "high", "intrusive"}


def test_builtin_module_files_round_trip():
    for path in BUILTIN_DIR.glob("*.yaml"):
        module = load_module(path)
        assert module.id
        # Each check id is unique within the module.
        ids = [c.id for c in module.checks]
        assert len(ids) == len(set(ids)), f"dup ids in {path}"


def test_resolve_unknown_module_fails():
    with pytest.raises(ModuleError):
        resolve_modules(["nope_does_not_exist"])


def test_user_dir_overrides_builtin(tmp_path: Path):
    override = {
        "module": {
            "id": "system_info",
            "name": "Override",
            "category": "recon",
            "risk": "passive",
            "platforms": ["linux"],
            "checks": [{"id": "x", "command": "true"}],
        }
    }
    (tmp_path / "system_info.yaml").write_text(yaml.safe_dump(override))
    catalog = discover_modules([tmp_path])
    assert catalog["system_info"].name == "Override"


def test_invalid_risk_rejected():
    raw = {
        "module": {
            "id": "x",
            "name": "x",
            "category": "x",
            "risk": "yolo",
            "checks": [{"id": "a", "command": "true"}],
        }
    }
    with pytest.raises(ModuleError):
        parse_module(raw)


def test_duplicate_check_ids_rejected():
    raw = {
        "module": {
            "id": "x",
            "name": "x",
            "category": "x",
            "risk": "passive",
            "checks": [
                {"id": "a", "command": "true"},
                {"id": "a", "command": "false"},
            ],
        }
    }
    with pytest.raises(ModuleError):
        parse_module(raw)


def test_empty_command_rejected():
    raw = {
        "module": {
            "id": "x",
            "name": "x",
            "category": "x",
            "risk": "passive",
            "checks": [{"id": "a", "command": "   "}],
        }
    }
    with pytest.raises(ModuleError):
        parse_module(raw)


def test_applies_to_platform():
    raw = {
        "module": {
            "id": "x",
            "name": "x",
            "category": "x",
            "risk": "passive",
            "platforms": ["linux"],
            "checks": [{"id": "a", "command": "true"}],
        }
    }
    m = parse_module(raw)
    assert m.applies_to("linux")
    assert not m.applies_to("darwin")
