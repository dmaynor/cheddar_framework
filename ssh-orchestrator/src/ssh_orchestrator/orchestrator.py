"""Orchestration: fan check execution out across targets.

The orchestrator is the entry point used by the CLI. It:
1. Validates the engagement is active and authorizes the modules.
2. Detects the remote platform per host.
3. Filters modules/checks down to those supported on each host's platform.
4. Runs checks in parallel up to limits.max_parallel.
5. Emits a structured Run object suitable for the report writer.
"""

from __future__ import annotations

import datetime as dt
import getpass
import platform as platform_mod
import socket
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .engagement import Engagement, Target
from .modules import Module
from .ssh_runner import CommandResult, detect_platform, run_command


@dataclass(frozen=True)
class CheckExecution:
    target: Target
    module: Module
    check_id: str
    command: str
    result: CommandResult
    risk: str
    skipped_reason: str | None = None


@dataclass
class HostExecution:
    target: Target
    detected_platform: str = "unknown"
    checks: list[CheckExecution] = field(default_factory=list)
    error: str | None = None


@dataclass
class Run:
    id: str
    engagement: Engagement
    started_at: dt.datetime
    finished_at: dt.datetime | None
    orchestrator_host: str
    orchestrator_user: str
    orchestrator_platform: str
    hosts: list[HostExecution] = field(default_factory=list)


ProgressCallback = Callable[[str], None]


def _noop(_msg: str) -> None:
    return None


def _execute_host(
    target: Target,
    modules: list[Module],
    engagement: Engagement,
    *,
    dry_run: bool,
    progress: ProgressCallback,
) -> HostExecution:
    host_exec = HostExecution(target=target)
    if dry_run:
        host_exec.detected_platform = "dry-run"
    else:
        progress(f"[{target.label}] detecting platform")
        host_exec.detected_platform = detect_platform(
            target, defaults=engagement.ssh
        )
        if host_exec.detected_platform == "unknown":
            host_exec.error = "platform detection failed (ssh unreachable?)"
            progress(f"[{target.label}] {host_exec.error}")
            return host_exec

    for module in modules:
        applies = (
            host_exec.detected_platform == "dry-run"
            or module.applies_to(host_exec.detected_platform)
        )
        for check in module.checks:
            cmd_timeout = (
                check.timeout_seconds
                if check.timeout_seconds is not None
                else engagement.limits.per_command_timeout
            )

            if not applies:
                skip = (
                    f"module {module.id} not applicable on "
                    f"{host_exec.detected_platform}"
                )
                progress(f"[{target.label}] skip {module.id}/{check.id}: {skip}")
                host_exec.checks.append(
                    CheckExecution(
                        target=target,
                        module=module,
                        check_id=check.id,
                        command=check.command,
                        result=_blank_result(target, check.command),
                        risk=module.risk,
                        skipped_reason=skip,
                    )
                )
                continue

            if dry_run:
                progress(
                    f"[{target.label}] DRY-RUN {module.id}/{check.id}: "
                    f"{check.command}"
                )
                host_exec.checks.append(
                    CheckExecution(
                        target=target,
                        module=module,
                        check_id=check.id,
                        command=check.command,
                        result=_blank_result(target, check.command),
                        risk=module.risk,
                        skipped_reason="dry-run",
                    )
                )
                continue

            progress(f"[{target.label}] run {module.id}/{check.id}")
            result = run_command(
                target,
                check.command,
                defaults=engagement.ssh,
                timeout_seconds=cmd_timeout,
            )
            host_exec.checks.append(
                CheckExecution(
                    target=target,
                    module=module,
                    check_id=check.id,
                    command=check.command,
                    result=result,
                    risk=module.risk,
                )
            )
    return host_exec


def _blank_result(target: Target, command: str) -> CommandResult:
    now = dt.datetime.now(dt.timezone.utc)
    return CommandResult(
        target_label=target.label,
        host=target.host,
        command=command,
        started_at=now,
        finished_at=now,
        duration_seconds=0.0,
        exit_code=0,
        timed_out=False,
        stdout=b"",
        stderr=b"",
        ssh_argv=(),
    )


def execute(
    engagement: Engagement,
    modules: list[Module],
    *,
    dry_run: bool = False,
    progress: ProgressCallback | None = None,
    today: dt.date | None = None,
) -> Run:
    """Run the engagement and return a populated Run."""
    progress = progress or _noop
    engagement.assert_active(today=today)
    for module in modules:
        engagement.assert_module_risk_allowed(module.id, module.risk)

    run = Run(
        id=f"run-{uuid.uuid4()}",
        engagement=engagement,
        started_at=dt.datetime.now(dt.timezone.utc),
        finished_at=None,
        orchestrator_host=socket.gethostname(),
        orchestrator_user=getpass.getuser(),
        orchestrator_platform=platform_mod.system().lower(),
    )

    workers = max(1, min(engagement.limits.max_parallel, len(engagement.targets)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _execute_host,
                target,
                modules,
                engagement,
                dry_run=dry_run,
                progress=progress,
            ): target
            for target in engagement.targets
        }
        for future in as_completed(futures):
            host_exec = future.result()
            run.hosts.append(host_exec)

    run.hosts.sort(key=lambda h: h.target.host)
    run.finished_at = dt.datetime.now(dt.timezone.utc)
    return run


def evidence_subdir(run: Run, host_exec: HostExecution, module: Module) -> str:
    return f"{run.id}/{host_exec.target.host}/{module.id}"
