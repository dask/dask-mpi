from __future__ import print_function, division, absolute_import

import os
import sys
import subprocess
from time import sleep

import pytest
pytest.importorskip('mpi4py')

import requests

from distributed import Client
from distributed.utils import tmpfile
from distributed.metrics import time
from distributed.utils_test import popen
#from distributed.utils_test import loop  # noqa: F401


@pytest.mark.parametrize('nanny', ['0', '1'])
def test_basic(nanny):
    script_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'basic.py')
    with tmpfile(extension='json') as fn:
        with open('test_basic.out', 'w') as fo:
            p = subprocess.Popen(['mpirun', '-np', '4', sys.executable, script_file, fn, nanny],
                                 stdout=fo, stderr=subprocess.STDOUT)
            p.communicate()
            assert p.returncode == 0


def test_no_scheduler(loop):
    with tmpfile() as fn:
        with popen(['mpirun', '--np', '2', 'dask-mpi', '--scheduler-file', fn],
                   stdin=subprocess.DEVNULL):
            with Client(scheduler_file=fn) as c:

                start = time()
                while len(c.scheduler_info()['workers']) != 1:
                    assert time() < start + 10
                    sleep(0.2)

                assert c.submit(lambda x: x + 1, 10).result() == 11
                with popen(['mpirun', '--np', '1', 'dask-mpi',
                            '--scheduler-file', fn, '--no-scheduler']):

                    start = time()
                    while len(c.scheduler_info()['workers']) != 2:
                        assert time() < start + 10
                        sleep(0.2)


def test_bokeh(loop):
    with tmpfile() as fn:
        with popen(['mpirun', '--np', '2', 'dask-mpi', '--scheduler-file', fn,
                    '--bokeh-port', '59583', '--bokeh-worker-port', '59584'],
                   stdin=subprocess.DEVNULL):

            for port in [59853, 59584]:
                start = time()
                while True:
                    try:
                        response = requests.get('http://localhost:%d/status/' % port)
                        assert response.ok
                        break
                    except Exception:
                        sleep(0.1)
                        assert time() < start + 20

    with pytest.raises(Exception):
        requests.get('http://localhost:59583/status/')
