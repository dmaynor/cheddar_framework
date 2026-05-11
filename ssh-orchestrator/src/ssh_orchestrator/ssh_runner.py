"""SSH execution layer.

Wraps the system `ssh` binary via subprocess so the tool inherits the
operator's existing keys, agent, and known_hosts. No third-party SSH library
is required; this matters because the tool may be run from constrained jump
hosts.

Design choices:
- The remote command is passed as a single argument to ssh; ssh will hand it
  to the remote login shell. We never interpolate target-supplied data into
  the command string.
- StrictHostKeyChecking defaults to "yes" (refuses unknown hosts) unless the
  engagement explicitly opts out.
- BatchMode=yes prevents prompting; runs that need a password fail fast.
- Per-command timeouts are enforced locally with subprocess timeout.
"""

from __future__ import annotations

import datetime as dt
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .engagement import SSHDefaults, Target


class SSHRunnerError(RuntimeError):
    """Raised when the local ssh client is misconfigured."""


@dataclass(frozen=True)
class CommandResult:
    target_label: str
    host: str
    command: str
    started_at: dt.datetime
    finished_at: dt.datetime
    duration_seconds: float
    exit_code: int
    timed_out: bool
    stdout: bytes
    stderr: bytes
    ssh_argv: tuple[str, ...]

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


def _ssh_binary() -> str:
    binary = shutil.which("ssh")
    if not binary:
        raise SSHRunnerError(
            "`ssh` binary not found on PATH. Install OpenSSH client."
        )
    return binary


def build_ssh_argv(
    target: Target,
    command: str,
    *,
    defaults: SSHDefaults,
) -> list[str]:
    """Build the argv to invoke ssh for a single command.

    The remote command is passed as a single argument; ssh handles quoting.
    """
    argv: list[str] = [_ssh_binary()]
    argv += ["-p", str(target.port)]
    argv += ["-l", target.user]
    argv += ["-o", "BatchMode=yes"]
    argv += ["-o", f"ConnectTimeout={defaults.connect_timeout}"]
    argv += [
        "-o",
        f"StrictHostKeyChecking={'yes' if defaults.strict_host_key_checking else 'no'}",
    ]
    if defaults.known_hosts_file:
        argv += ["-o", f"UserKnownHostsFile={defaults.known_hosts_file}"]
    if target.identity_file:
        argv += ["-i", target.identity_file]
        argv += ["-o", "IdentitiesOnly=yes"]
    for opt in defaults.extra_options:
        argv += ["-o", opt]
    argv += [target.host, command]
    return argv


def run_command(
    target: Target,
    command: str,
    *,
    defaults: SSHDefaults,
    timeout_seconds: int,
) -> CommandResult:
    """Execute a single remote command. Never raises on remote failure."""
    argv = build_ssh_argv(target, command, defaults=defaults)
    started = dt.datetime.now(dt.timezone.utc)
    timed_out = False
    stdout = b""
    stderr = b""
    exit_code = -1
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or b""
        stderr = (exc.stderr or b"") + (
            f"\n[ssh-orchestrator] timed out after {timeout_seconds}s\n".encode()
        )
        exit_code = 124  # convention used by GNU `timeout`
    finished = dt.datetime.now(dt.timezone.utc)
    return CommandResult(
        target_label=target.label,
        host=target.host,
        command=command,
        started_at=started,
        finished_at=finished,
        duration_seconds=(finished - started).total_seconds(),
        exit_code=exit_code,
        timed_out=timed_out,
        stdout=stdout,
        stderr=stderr,
        ssh_argv=tuple(argv),
    )


def detect_platform(
    target: Target,
    *,
    defaults: SSHDefaults,
    timeout_seconds: int = 15,
) -> str:
    """Probe the remote host for `uname -s`. Returns 'linux', 'darwin', or 'unknown'."""
    result = run_command(
        target,
        "uname -s",
        defaults=defaults,
        timeout_seconds=timeout_seconds,
    )
    if not result.succeeded:
        return "unknown"
    out = result.stdout.decode("utf-8", errors="replace").strip().lower()
    if out == "linux":
        return "linux"
    if out == "darwin":
        return "darwin"
    return "unknown"


def write_evidence(
    base_dir: Path,
    relative_dir: str,
    name: str,
    result: CommandResult,
) -> tuple[Path, Path]:
    """Write stdout/stderr to disk. Returns (stdout_path, stderr_path)."""
    out_dir = base_dir / relative_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = out_dir / f"{name}.stdout"
    stderr_path = out_dir / f"{name}.stderr"
    stdout_path.write_bytes(result.stdout)
    stderr_path.write_bytes(result.stderr)
    return stdout_path, stderr_path
