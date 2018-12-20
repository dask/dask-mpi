from __future__ import print_function, division, absolute_import

import os
import sys
import subprocess

import pytest
pytest.importorskip('mpi4py')

from distributed.utils import tmpfile


def test_basic():
    script_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'core_basic.py')
    with tmpfile(extension='json') as fn:
        p = subprocess.Popen(['mpirun', '-np', '4', sys.executable, script_file, fn],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (stdout, _) = p.communicate()
        assert p.returncode == 0
