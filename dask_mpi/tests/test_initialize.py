from __future__ import absolute_import, division, print_function

import os
import subprocess
import sys

import pytest

pytest.importorskip("mpi4py")


def test_basic(mpirun):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "initialize_basic.py"
    )

    p = subprocess.Popen(mpirun + ["-np", "4", sys.executable, script_file])

    p.communicate()
    assert p.returncode == 0


def test_small_world(mpirun):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "initialize_basic.py"
    )

    # Set too few processes to start cluster
    p = subprocess.Popen(mpirun + ["-np", "1", sys.executable, script_file])

    p.communicate()
    assert p.returncode != 0


def test_no_exit(mpirun):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "initialize_no_exit.py"
    )

    p = subprocess.Popen(mpirun + ["-np", "4", sys.executable, script_file])

    p.communicate()
    assert p.returncode == 0
