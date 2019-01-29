from __future__ import print_function, division, absolute_import

import os
import sys
import subprocess

import pytest

pytest.importorskip("mpi4py")

try:
    ALLOW_RUN_AS_ROOT = bool(os.environ.get("ALLOW_RUN_AS_ROOT"))
except:
    ALLOW_RUN_AS_ROOT = False


def test_basic(ALLOW_RUN_AS_ROOT):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "core_basic.py"
    )

    if ALLOW_RUN_AS_ROOT:
        p = subprocess.Popen(
            ["mpirun", "-np", "4", "--allow-run-as-root", sys.executable, script_file]
        )
    else:
        p = subprocess.Popen(["mpirun", "-np", "4", sys.executable, script_file])
    p.communicate()
    assert p.returncode == 0
