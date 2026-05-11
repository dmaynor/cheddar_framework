# ssh-orchestrator

A small, opinionated orchestrator for **authorized** remote security testing
over SSH. Runs on macOS or Linux, talks to remote hosts using the system
`ssh` client (no third-party SSH library), and emits self-verifying JSON
evidence artifacts for each run.

## What it does

Given an *engagement plan* (a YAML file declaring who authorized the work,
when authorization expires, which hosts are in scope, and which test
modules to run), `ssh-orchestrator`:

1. Refuses to start if the engagement is expired or not yet active.
2. Refuses any module whose risk tier exceeds the engagement's `max_risk`.
3. Detects the remote OS per host (`uname -s`).
4. Fans checks out across hosts in parallel, with per-command timeouts.
5. Captures stdout/stderr to disk and writes a `run.json` with SHA256
   hashes for every captured stream.

It is **not** an exploitation framework. The built-in modules are read-only
recon and configuration audits.

## Install

```bash
cd ssh-orchestrator
python -m pip install -e .
```

Requires Python 3.10+ and an OpenSSH `ssh` client on `PATH`.

## Usage

```bash
# List the modules shipped with the tool.
ssh-orch list-modules

# Validate an engagement plan without contacting any hosts.
ssh-orch validate examples/example_engagement.yaml

# Plan-only run: prints what would execute, writes an empty-evidence run.json.
ssh-orch run examples/example_engagement.yaml --dry-run -o /tmp/run

# Real run.
ssh-orch run examples/example_engagement.yaml -o ./out -v
```

Output layout:

```
out/
├── run.json
└── evidence/
    └── run-<uuid>/
        └── <host>/
            └── <module>/
                ├── <check>.stdout
                └── <check>.stderr
```

Every check entry in `run.json` carries `stdout_sha256` and `stderr_sha256`
(over the bytes written to disk), and the file as a whole carries
`artifact_sha256` over its own contents (excluding that field). This lets
downstream auditors verify evidence has not been altered.

## Engagement plan

See `examples/example_engagement.yaml`. The required shape:

```yaml
engagement:
  id: <string>
  name: <string>
  authorized_by: <string>           # who signed off
  authorization_date: YYYY-MM-DD
  scope_expires: YYYY-MM-DD          # hard stop
  max_risk: passive|low|medium|high|intrusive   # default: low
  notes: <optional string>

ssh:
  default_user: <username>
  default_port: 22
  identity_file: <optional path>
  known_hosts_file: <optional path>
  strict_host_key_checking: true     # default
  connect_timeout: 10
  extra_options:                     # optional list of -o k=v values
    - "ServerAliveInterval=30"

targets:
  - host: <hostname-or-ip>           # required, must match safe charset
    user: <override>                 # optional
    port: <override>                 # optional
    identity_file: <override>        # optional
    tags: [a, b]                     # optional, free-form

modules:
  - <module-id>                      # ids from `ssh-orch list-modules`

limits:
  max_parallel: 4                    # how many hosts to hit concurrently
  per_host_timeout: 600              # advisory; per-command_timeout dominates
  per_command_timeout: 60            # default per-check timeout
```

Hosts not listed under `targets` are refused at orchestration time, even
if they appear in `known_hosts` or are reachable.

## Modules

A module is a YAML file shipped under
`src/ssh_orchestrator/builtin_modules/` (or any directory passed via
`--module-dir`). Built-in modules:

| id | risk | platforms | what it captures |
|---|---|---|---|
| `system_info` | passive | linux, darwin | uname, uptime, id, clock |
| `user_audit` | passive | linux, darwin | passwd/group, who, last, UID-0 / empty-pw accounts |
| `ssh_audit` | low | linux, darwin | sshd config, authorized_keys, host key perms |
| `listening_services` | low | linux, darwin | ss/netstat/lsof, routes, iptables/nft/pf |
| `sudo_audit` | low | linux, darwin | sudoers, sudo -ln, wheel/admin members |
| `filesystem_hygiene` | low | linux, darwin | world-writable, suid/sgid, no-owner files |
| `package_audit_linux` | passive | linux | dpkg/rpm/apk inventory, pending updates |
| `package_audit_macos` | passive | darwin | sw_vers, pkgutil, brew formulae/casks |

Module shape:

```yaml
module:
  id: <unique id>
  name: <human label>
  category: <free-form bucket>
  risk: passive|low|medium|high|intrusive
  description: <one paragraph>
  platforms: [linux, darwin, any]
  checks:
    - id: <stable id, no slashes>
      command: <shell command run on the remote host via ssh>
      timeout_seconds: <optional override; falls back to engagement default>
      description: <optional>
```

Drop your own modules in a directory and pass `--module-dir <dir>` (the
flag is repeatable). User modules with the same id as a built-in override
the built-in.

## Safety model

- **Authorization first.** Every run requires an engagement with an
  explicit authorizer and an expiry date. The tool refuses to run a plan
  that has expired.
- **Scope is an allowlist.** Only hosts listed under `targets` are
  contacted. Engagements cannot wildcard.
- **Risk gating.** Each module declares a risk tier. The engagement
  declares `max_risk`. Modules above the cap are refused.
- **Strict host keys by default.** `StrictHostKeyChecking=yes` is the
  default; set `strict_host_key_checking: false` only when intentional.
- **No password prompts.** `BatchMode=yes` is forced; runs that need a
  password fail fast rather than hang.
- **No shell interpolation of plan data.** Hostnames/users are validated
  against a safe charset. Commands come from module YAML, never from the
  CLI or target.
- **Self-describing evidence.** stdout/stderr are written to disk with
  SHA256 hashes recorded in `run.json`.

This tool is for engagements you are authorized to perform. Do not point
it at infrastructure you do not own or have written permission to test.

## Exit codes

| code | meaning |
|---|---|
| 0 | run completed; no failed/unreachable hosts |
| 2 | usage error (bad CLI args, malformed engagement, unknown module) |
| 3 | authorization error (expired, out-of-scope, risk over cap) |
| 4 | run completed but at least one check failed or host was unreachable |

## Development

```bash
python -m pip install -e '.[dev]'
pytest
```
