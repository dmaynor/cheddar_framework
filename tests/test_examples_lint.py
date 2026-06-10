"""Integration test: the full strict lint pipeline must pass on the
canonical examples.

This is the same command CI runs (.github/workflows/ci.yml). Keeping it in
the test suite means `pytest` alone reproduces CI locally, and any future
hashing or schema change that breaks the examples fails here with the lint
runner's own diagnostics.
"""

import subprocess
import sys

from conftest import REPO_ROOT


def test_examples_pass_strict_lint():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "lint" / "run_all.py"), "--examples", "--strict"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"strict lint failed (exit {result.returncode})\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
