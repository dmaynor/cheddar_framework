"""Module loader for security test definitions.

A "module" is a YAML file describing a related set of read-only or
configuration-audit checks to run against a target. Each check declares its
shell command. Commands run on the remote host through `sh -c` quoted on the
local side. Modules also declare a risk level which is checked against the
engagement's max_risk before execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .engagement import RISK_LEVELS


BUILTIN_DIR = Path(__file__).resolve().parent / "builtin_modules"

PLATFORMS = ("linux", "darwin", "any")


class ModuleError(ValueError):
    """Raised when a module file is malformed."""


@dataclass(frozen=True)
class Check:
    id: str
    command: str
    description: str = ""
    timeout_seconds: int | None = None


@dataclass(frozen=True)
class Module:
    id: str
    name: str
    category: str
    risk: str
    description: str
    platforms: tuple[str, ...]
    checks: tuple[Check, ...]
    source_path: Path | None = None

    def applies_to(self, platform: str) -> bool:
        return "any" in self.platforms or platform in self.platforms


def load_module(path: str | Path) -> Module:
    """Load and validate a single module YAML file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, dict):
        raise ModuleError(f"{path}: module file must be a YAML mapping")
    return parse_module(raw, source_path=path)


def parse_module(raw: dict, *, source_path: Path | None = None) -> Module:
    if "module" not in raw or not isinstance(raw["module"], dict):
        raise ModuleError("module: top-level 'module' mapping is required")
    m = raw["module"]
    for required in ("id", "name", "category", "risk", "checks"):
        if required not in m:
            raise ModuleError(f"module: missing required field {required!r}")

    risk = str(m["risk"])
    if risk not in RISK_LEVELS:
        raise ModuleError(f"module.risk: must be one of {RISK_LEVELS}, got {risk!r}")

    platforms_raw = m.get("platforms", ["linux", "darwin"]) or []
    if not isinstance(platforms_raw, list) or not platforms_raw:
        raise ModuleError("module.platforms: must be a non-empty list")
    for p in platforms_raw:
        if p not in PLATFORMS:
            raise ModuleError(
                f"module.platforms: unknown platform {p!r}; valid: {PLATFORMS}"
            )

    checks_raw = m["checks"]
    if not isinstance(checks_raw, list) or not checks_raw:
        raise ModuleError("module.checks: must be a non-empty list")
    seen_ids: set[str] = set()
    checks: list[Check] = []
    for idx, c in enumerate(checks_raw):
        where = f"module.checks[{idx}]"
        if not isinstance(c, dict):
            raise ModuleError(f"{where}: must be a mapping")
        if "id" not in c or "command" not in c:
            raise ModuleError(f"{where}: 'id' and 'command' are required")
        check_id = str(c["id"])
        if not check_id or "/" in check_id or check_id.startswith("."):
            raise ModuleError(f"{where}.id: invalid check id {check_id!r}")
        if check_id in seen_ids:
            raise ModuleError(f"{where}.id: duplicate check id {check_id!r}")
        seen_ids.add(check_id)
        command = str(c["command"]).strip()
        if not command:
            raise ModuleError(f"{where}.command: must be a non-empty string")
        if "\x00" in command:
            raise ModuleError(f"{where}.command: contains NUL byte")
        timeout = c.get("timeout_seconds")
        if timeout is not None:
            timeout = int(timeout)
            if timeout <= 0:
                raise ModuleError(f"{where}.timeout_seconds: must be positive")
        description = str(c.get("description", ""))
        checks.append(
            Check(
                id=check_id,
                command=command,
                description=description,
                timeout_seconds=timeout,
            )
        )

    return Module(
        id=str(m["id"]),
        name=str(m["name"]),
        category=str(m["category"]),
        risk=risk,
        description=str(m.get("description", "")),
        platforms=tuple(platforms_raw),
        checks=tuple(checks),
        source_path=source_path,
    )


def discover_modules(extra_dirs: list[Path] | None = None) -> dict[str, Module]:
    """Load all built-in modules plus any in extra search dirs.

    Returns a mapping from module id to Module. Later directories override
    earlier ones (built-ins first, then user-supplied).
    """
    modules: dict[str, Module] = {}
    search_dirs: list[Path] = [BUILTIN_DIR]
    if extra_dirs:
        search_dirs.extend(Path(d) for d in extra_dirs)
    for directory in search_dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.yaml")):
            module = load_module(path)
            modules[module.id] = module
    return modules


def resolve_modules(
    requested_ids: list[str] | tuple[str, ...],
    extra_dirs: list[Path] | None = None,
) -> list[Module]:
    """Look up the requested module ids; raise if any are missing."""
    catalog = discover_modules(extra_dirs)
    missing = [mid for mid in requested_ids if mid not in catalog]
    if missing:
        available = sorted(catalog)
        raise ModuleError(
            f"unknown modules: {missing}. Available: {available}"
        )
    return [catalog[mid] for mid in requested_ids]
