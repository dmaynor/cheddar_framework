from __future__ import annotations

import pytest

from ssh_orchestrator import ssh_runner
from ssh_orchestrator.engagement import SSHDefaults, Target
from ssh_orchestrator.ssh_runner import build_ssh_argv


@pytest.fixture(autouse=True)
def stub_ssh_binary(monkeypatch):
    """The sandbox may lack /usr/bin/ssh. argv-shape tests don't need a
    real binary — give them a stable fake path."""
    monkeypatch.setattr(ssh_runner, "_ssh_binary", lambda: "/usr/bin/ssh")


def _target(**overrides) -> Target:
    base = dict(
        host="host01.example.com",
        user="audit",
        port=22,
        identity_file=None,
        tags=(),
    )
    base.update(overrides)
    return Target(**base)


def _defaults(**overrides) -> SSHDefaults:
    base = dict(
        user="audit",
        port=22,
        identity_file=None,
        known_hosts_file=None,
        strict_host_key_checking=True,
        connect_timeout=10,
        extra_options=(),
    )
    base.update(overrides)
    return SSHDefaults(**base)


def test_argv_basic_shape():
    argv = build_ssh_argv(_target(), "uname -a", defaults=_defaults())
    assert argv[0].endswith("ssh")
    # Final two args: host, command (passed as a single string).
    assert argv[-2] == "host01.example.com"
    assert argv[-1] == "uname -a"
    # Mandatory hardening options.
    assert "BatchMode=yes" in argv
    assert "StrictHostKeyChecking=yes" in argv


def test_argv_uses_target_overrides():
    argv = build_ssh_argv(
        _target(user="root", port=2222, identity_file="/k/id_ed25519"),
        "id",
        defaults=_defaults(),
    )
    assert "-l" in argv and argv[argv.index("-l") + 1] == "root"
    assert "-p" in argv and argv[argv.index("-p") + 1] == "2222"
    assert "-i" in argv and argv[argv.index("-i") + 1] == "/k/id_ed25519"
    assert "IdentitiesOnly=yes" in argv


def test_argv_known_hosts_and_extra_opts():
    argv = build_ssh_argv(
        _target(),
        "true",
        defaults=_defaults(
            known_hosts_file="/etc/ssh/known_hosts.audit",
            extra_options=("ServerAliveInterval=30",),
        ),
    )
    assert "UserKnownHostsFile=/etc/ssh/known_hosts.audit" in argv
    assert "ServerAliveInterval=30" in argv


def test_argv_relaxed_host_keys():
    argv = build_ssh_argv(
        _target(),
        "true",
        defaults=_defaults(strict_host_key_checking=False),
    )
    assert "StrictHostKeyChecking=no" in argv


def test_command_is_single_argument():
    """Multi-token commands must arrive as a single argv element so the
    remote shell — not the local one — interprets them."""
    cmd = "echo 'hi there' | tr a-z A-Z"
    argv = build_ssh_argv(_target(), cmd, defaults=_defaults())
    assert argv[-1] == cmd
