from __future__ import absolute_import, division, print_function

import os
import subprocess
import sys

import pytest

pytest.importorskip("mpi4py")


def test_basic(mpirun):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "core_basic.py"
    )

    p = subprocess.Popen(mpirun + ["-np", "4", sys.executable, script_file])

    p.communicate()
    print("mpirun ended")
    assert p.returncode == 0


def test_context(mpirun):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "core_context.py"
    )

    p = subprocess.Popen(mpirun + ["-np", "4", sys.executable, script_file])

    p.communicate()
    print("mpirun ended")
    assert p.returncode == 0
