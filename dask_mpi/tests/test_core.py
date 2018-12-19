from __future__ import print_function, division, absolute_import

import os
import sys
import subprocess

import pytest
pytest.importorskip('mpi4py')

from distributed.utils import tmpfile
from distributed.utils_test import loop  # noqa: F401


def test_basic(loop):
    script_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'basic.py')
    with tmpfile(extension='json') as fn:
        with open('test_basic.out', 'w') as fo:
            p = subprocess.Popen(['mpirun', '-np', '4', sys.executable, script_file, fn],
                                 stdout=fo, stderr=subprocess.STDOUT)
            p.communicate()
            assert p.returncode == 0
