"""Engagement plan loading and validation.

An engagement plan is the authorization document for a security testing run.
It declares who authorized the work, when authorization expires, the SSH
parameters to use, and the explicit list of target hosts. Targets not listed
here are refused at orchestration time.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


RISK_LEVELS = ("passive", "low", "medium", "high", "intrusive")
RISK_RANK = {level: idx for idx, level in enumerate(RISK_LEVELS)}

# Conservative hostname/IP pattern. Refuses shell metacharacters that could
# leak into the ssh command line.
_HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\.\-_:]{0,253}$")
_USER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_\-]{0,31}$")


class EngagementError(ValueError):
    """Raised when an engagement plan is malformed or unauthorized."""


@dataclass(frozen=True)
class SSHDefaults:
    user: str
    port: int = 22
    identity_file: str | None = None
    known_hosts_file: str | None = None
    strict_host_key_checking: bool = True
    connect_timeout: int = 10
    extra_options: tuple[str, ...] = ()


@dataclass(frozen=True)
class Target:
    host: str
    user: str
    port: int
    identity_file: str | None
    tags: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        return f"{self.user}@{self.host}:{self.port}"


@dataclass(frozen=True)
class Limits:
    max_parallel: int = 4
    per_host_timeout: int = 600
    per_command_timeout: int = 60


@dataclass(frozen=True)
class Engagement:
    id: str
    name: str
    authorized_by: str
    authorization_date: dt.date
    scope_expires: dt.date
    ssh: SSHDefaults
    targets: tuple[Target, ...]
    modules: tuple[str, ...]
    max_risk: str = "low"
    limits: Limits = field(default_factory=Limits)
    notes: str | None = None
    source_path: Path | None = None

    def assert_in_scope(self, host: str) -> None:
        """Raise if host is not on the authorized target list."""
        if not any(t.host == host for t in self.targets):
            raise EngagementError(
                f"Host {host!r} is not in engagement scope. "
                f"Authorized hosts: {[t.host for t in self.targets]}"
            )

    def assert_active(self, today: dt.date | None = None) -> None:
        today = today or dt.date.today()
        if today > self.scope_expires:
            raise EngagementError(
                f"Engagement {self.id} expired on {self.scope_expires.isoformat()}; "
                f"refusing to run on {today.isoformat()}."
            )
        if today < self.authorization_date:
            raise EngagementError(
                f"Engagement {self.id} is not yet active "
                f"(authorized {self.authorization_date.isoformat()})."
            )

    def assert_module_risk_allowed(self, module_id: str, risk: str) -> None:
        if risk not in RISK_RANK:
            raise EngagementError(
                f"Module {module_id!r} declares unknown risk {risk!r}; "
                f"valid: {RISK_LEVELS}"
            )
        if RISK_RANK[risk] > RISK_RANK[self.max_risk]:
            raise EngagementError(
                f"Module {module_id!r} has risk {risk!r} which exceeds "
                f"engagement max_risk {self.max_risk!r}."
            )


def _require(mapping: dict, key: str, where: str) -> object:
    if key not in mapping:
        raise EngagementError(f"{where}: missing required field {key!r}")
    return mapping[key]


def _parse_date(value: object, where: str) -> dt.date:
    if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError as exc:
            raise EngagementError(f"{where}: invalid date {value!r}") from exc
    raise EngagementError(f"{where}: expected ISO date, got {type(value).__name__}")


def _validate_host(host: str) -> str:
    if not isinstance(host, str) or not _HOST_RE.match(host):
        raise EngagementError(f"invalid host: {host!r}")
    return host


def _validate_user(user: str) -> str:
    if not isinstance(user, str) or not _USER_RE.match(user):
        raise EngagementError(f"invalid SSH user: {user!r}")
    return user


def load_engagement(path: str | Path) -> Engagement:
    """Load and validate an engagement plan from YAML."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, dict):
        raise EngagementError(f"{path}: engagement file must be a YAML mapping")
    return parse_engagement(raw, source_path=path)


def parse_engagement(raw: dict, *, source_path: Path | None = None) -> Engagement:
    """Validate a parsed engagement mapping and return an Engagement."""
    eng = _require(raw, "engagement", "root")
    if not isinstance(eng, dict):
        raise EngagementError("engagement: must be a mapping")

    eng_id = str(_require(eng, "id", "engagement"))
    name = str(_require(eng, "name", "engagement"))
    authorized_by = str(_require(eng, "authorized_by", "engagement"))
    authorization_date = _parse_date(
        _require(eng, "authorization_date", "engagement"),
        "engagement.authorization_date",
    )
    scope_expires = _parse_date(
        _require(eng, "scope_expires", "engagement"),
        "engagement.scope_expires",
    )
    if scope_expires < authorization_date:
        raise EngagementError(
            "engagement.scope_expires must be on or after authorization_date"
        )

    max_risk = str(eng.get("max_risk", "low"))
    if max_risk not in RISK_RANK:
        raise EngagementError(
            f"engagement.max_risk: must be one of {RISK_LEVELS}, got {max_risk!r}"
        )
    notes = eng.get("notes")
    if notes is not None and not isinstance(notes, str):
        raise EngagementError("engagement.notes: must be a string")

    ssh_raw = raw.get("ssh") or {}
    if not isinstance(ssh_raw, dict):
        raise EngagementError("ssh: must be a mapping")
    default_user = _validate_user(str(_require(ssh_raw, "default_user", "ssh")))
    default_port = int(ssh_raw.get("default_port", 22))
    if not (1 <= default_port <= 65535):
        raise EngagementError("ssh.default_port: must be 1..65535")
    identity_file = ssh_raw.get("identity_file")
    if identity_file is not None and not isinstance(identity_file, str):
        raise EngagementError("ssh.identity_file: must be a string path")
    known_hosts_file = ssh_raw.get("known_hosts_file")
    if known_hosts_file is not None and not isinstance(known_hosts_file, str):
        raise EngagementError("ssh.known_hosts_file: must be a string path")
    strict_host_key_checking = bool(ssh_raw.get("strict_host_key_checking", True))
    connect_timeout = int(ssh_raw.get("connect_timeout", 10))
    if connect_timeout <= 0:
        raise EngagementError("ssh.connect_timeout: must be a positive integer")
    extra_options_raw = ssh_raw.get("extra_options", []) or []
    if not isinstance(extra_options_raw, list) or not all(
        isinstance(o, str) for o in extra_options_raw
    ):
        raise EngagementError("ssh.extra_options: must be a list of strings")
    extra_options = tuple(extra_options_raw)

    ssh = SSHDefaults(
        user=default_user,
        port=default_port,
        identity_file=identity_file,
        known_hosts_file=known_hosts_file,
        strict_host_key_checking=strict_host_key_checking,
        connect_timeout=connect_timeout,
        extra_options=extra_options,
    )

    targets_raw = _require(raw, "targets", "root")
    if not isinstance(targets_raw, list) or not targets_raw:
        raise EngagementError("targets: must be a non-empty list")
    seen_hosts: set[str] = set()
    targets: list[Target] = []
    for idx, t in enumerate(targets_raw):
        where = f"targets[{idx}]"
        if not isinstance(t, dict):
            raise EngagementError(f"{where}: must be a mapping")
        host = _validate_host(str(_require(t, "host", where)))
        if host in seen_hosts:
            raise EngagementError(f"{where}: duplicate host {host!r}")
        seen_hosts.add(host)
        user = _validate_user(str(t.get("user", default_user)))
        port = int(t.get("port", default_port))
        if not (1 <= port <= 65535):
            raise EngagementError(f"{where}.port: must be 1..65535")
        ident = t.get("identity_file", identity_file)
        if ident is not None and not isinstance(ident, str):
            raise EngagementError(f"{where}.identity_file: must be a string path")
        tags_raw = t.get("tags", []) or []
        if not isinstance(tags_raw, list) or not all(
            isinstance(tag, str) for tag in tags_raw
        ):
            raise EngagementError(f"{where}.tags: must be a list of strings")
        targets.append(
            Target(
                host=host,
                user=user,
                port=port,
                identity_file=ident,
                tags=tuple(tags_raw),
            )
        )

    modules_raw = _require(raw, "modules", "root")
    if not isinstance(modules_raw, list) or not modules_raw:
        raise EngagementError("modules: must be a non-empty list of module ids")
    if not all(isinstance(m, str) and m for m in modules_raw):
        raise EngagementError("modules: must be a list of non-empty strings")
    modules = tuple(modules_raw)

    limits_raw = raw.get("limits") or {}
    if not isinstance(limits_raw, dict):
        raise EngagementError("limits: must be a mapping")
    max_parallel = int(limits_raw.get("max_parallel", 4))
    per_host_timeout = int(limits_raw.get("per_host_timeout", 600))
    per_command_timeout = int(limits_raw.get("per_command_timeout", 60))
    if max_parallel <= 0:
        raise EngagementError("limits.max_parallel: must be positive")
    if per_host_timeout <= 0:
        raise EngagementError("limits.per_host_timeout: must be positive")
    if per_command_timeout <= 0:
        raise EngagementError("limits.per_command_timeout: must be positive")

    return Engagement(
        id=eng_id,
        name=name,
        authorized_by=authorized_by,
        authorization_date=authorization_date,
        scope_expires=scope_expires,
        ssh=ssh,
        targets=tuple(targets),
        modules=modules,
        max_risk=max_risk,
        limits=Limits(
            max_parallel=max_parallel,
            per_host_timeout=per_host_timeout,
            per_command_timeout=per_command_timeout,
        ),
        notes=notes,
        source_path=source_path,
    )
