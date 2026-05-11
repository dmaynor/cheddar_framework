"""Report writer.

Emits a single run.json artifact summarizing the run, plus per-check
stdout/stderr files under evidence/. Every captured stream gets a SHA256 so
the result file is self-verifying.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import __version__
from .orchestrator import HostExecution, Run, evidence_subdir


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def write_run(run: Run, output_dir: Path) -> Path:
    """Write evidence files and run.json. Returns path to run.json."""
    output_dir = Path(output_dir)
    evidence_root = output_dir / "evidence"
    evidence_root.mkdir(parents=True, exist_ok=True)

    summary = {
        "schema_version": "1.0",
        "tool": "ssh-orchestrator",
        "tool_version": __version__,
        "run": {
            "id": run.id,
            "engagement_id": run.engagement.id,
            "engagement_name": run.engagement.name,
            "engagement_source": (
                str(run.engagement.source_path)
                if run.engagement.source_path
                else None
            ),
            "authorized_by": run.engagement.authorized_by,
            "authorization_date": run.engagement.authorization_date.isoformat(),
            "scope_expires": run.engagement.scope_expires.isoformat(),
            "started_at": run.started_at.isoformat(),
            "finished_at": (
                run.finished_at.isoformat() if run.finished_at else None
            ),
            "orchestrator": {
                "host": run.orchestrator_host,
                "user": run.orchestrator_user,
                "platform": run.orchestrator_platform,
            },
        },
        "hosts": [_host_summary(run, h, evidence_root) for h in run.hosts],
    }

    summary["totals"] = _compute_totals(summary["hosts"])

    run_path = output_dir / "run.json"
    payload = json.dumps(summary, indent=2, sort_keys=True).encode("utf-8")
    summary["artifact_sha256"] = _sha256(payload)
    final = json.dumps(summary, indent=2, sort_keys=True).encode("utf-8")
    run_path.write_bytes(final)
    return run_path


def _host_summary(run: Run, host_exec: HostExecution, evidence_root: Path) -> dict:
    checks_out = []
    for ce in host_exec.checks:
        rel_dir = evidence_subdir(run, host_exec, ce.module)
        if ce.skipped_reason is None:
            stdout_path = evidence_root / rel_dir / f"{ce.check_id}.stdout"
            stderr_path = evidence_root / rel_dir / f"{ce.check_id}.stderr"
            stdout_path.parent.mkdir(parents=True, exist_ok=True)
            stdout_path.write_bytes(ce.result.stdout)
            stderr_path.write_bytes(ce.result.stderr)
            stdout_rel = str(stdout_path.relative_to(evidence_root.parent))
            stderr_rel = str(stderr_path.relative_to(evidence_root.parent))
        else:
            stdout_rel = None
            stderr_rel = None

        checks_out.append(
            {
                "module": ce.module.id,
                "check": ce.check_id,
                "risk": ce.risk,
                "command": ce.command,
                "skipped_reason": ce.skipped_reason,
                "started_at": ce.result.started_at.isoformat(),
                "finished_at": ce.result.finished_at.isoformat(),
                "duration_seconds": round(ce.result.duration_seconds, 4),
                "exit_code": ce.result.exit_code,
                "timed_out": ce.result.timed_out,
                "stdout_sha256": _sha256(ce.result.stdout),
                "stderr_sha256": _sha256(ce.result.stderr),
                "stdout_bytes": len(ce.result.stdout),
                "stderr_bytes": len(ce.result.stderr),
                "stdout_path": stdout_rel,
                "stderr_path": stderr_rel,
            }
        )

    return {
        "host": host_exec.target.host,
        "label": host_exec.target.label,
        "tags": list(host_exec.target.tags),
        "detected_platform": host_exec.detected_platform,
        "error": host_exec.error,
        "checks": checks_out,
    }


def _compute_totals(hosts: list[dict]) -> dict:
    total_checks = 0
    skipped = 0
    failed = 0
    timed_out = 0
    for h in hosts:
        for c in h["checks"]:
            total_checks += 1
            if c["skipped_reason"]:
                skipped += 1
                continue
            if c["timed_out"]:
                timed_out += 1
            if c["exit_code"] != 0:
                failed += 1
    return {
        "hosts": len(hosts),
        "checks": total_checks,
        "skipped": skipped,
        "failed_exit": failed,
        "timed_out": timed_out,
    }
