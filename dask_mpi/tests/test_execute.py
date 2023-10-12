from __future__ import absolute_import, division, print_function

import os
import subprocess
import sys

import pytest

pytest.importorskip("mpi4py")


@pytest.mark.parametrize(
    "mpisize,execute_args,retcode",
    [
        (4, [], 0),
        (1, [], 1),  # Set too few processes to start cluster
        (4, ["-c", "2", "-s", "3"], 0),
        (5, ["-s", "3"], 0),
        (3, ["-c", "2", "-s", "2"], 0),
        (2, ["-c", "0", "-s", "0", "-x", "False"], 0),
        (1, ["-c", "0", "-s", "0", "-x", "False"], 0),
        (1, ["-c", "0", "-s", "0", "-x", "True"], 1),
    ],
)
def test_basic(mpisize, execute_args, retcode, mpirun):
    script_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "execute_basic.py"
    )

    execute_args += ["-m", str(mpisize)]
    p = subprocess.Popen(
        mpirun + ["-n", str(mpisize), sys.executable, script_file] + execute_args
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
