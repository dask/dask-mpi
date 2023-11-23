from __future__ import absolute_import, division, print_function

import os
import subprocess
import sys

import pytest

pytest.importorskip("mpi4py")


@pytest.mark.parametrize(
    "mpisize,crank,srank,xworkers,retcode",
    [
        (4, 1, 0, True, 0),  # DEFAULTS
        (1, 1, 0, True, 1),  # Set too few processes to start cluster
        (4, 2, 3, True, 0),
        (5, 1, 3, True, 0),
        (3, 2, 2, True, 0),
        (2, 0, 0, False, 0),
        (1, 0, 0, False, 0),
        (1, 0, 0, True, 1),
    ],
)
def test_basic(mpisize, crank, srank, xworkers, retcode, mpirun):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "execute_basic.py"
    )

    script_args = [str(v) for v in (mpisize, crank, srank, xworkers)]
    p = subprocess.Popen(
        mpirun + ["-n", script_args[0], sys.executable, script_file] + script_args
    )

    p.communicate()
    assert p.returncode == retcode


def test_no_exit(mpirun):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "execute_no_exit.py"
    )

    p = subprocess.Popen(mpirun + ["-np", "4", sys.executable, script_file])

    p.communicate()
    assert p.returncode == 0
