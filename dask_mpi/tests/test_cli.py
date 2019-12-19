from __future__ import print_function, division, absolute_import

import os

from time import sleep

import pytest

pytest.importorskip("mpi4py")

import requests

from distributed import Client
from distributed.comm.addressing import get_address_host_port
from distributed.metrics import time
from distributed.utils import tmpfile
from distributed.utils_test import popen
from distributed.utils_test import loop  # noqa: F401


FNULL = open(os.devnull, "w")  # hide output of subprocess


@pytest.mark.parametrize("nanny", ["--nanny", "--no-nanny"])
def test_basic(loop, nanny, mpirun):
    with tmpfile(extension="json") as fn:

        cmd = mpirun + ["-np", "4", "dask-mpi", "--scheduler-file", fn, nanny]

        with popen(cmd):
            with Client(scheduler_file=fn) as c:
                start = time()
                while len(c.scheduler_info()["workers"]) != 3:
                    assert time() < start + 10
                    sleep(0.2)

                assert c.submit(lambda x: x + 1, 10, workers=1).result() == 11


def test_no_scheduler(loop, mpirun):
    with tmpfile(extension="json") as fn:

        cmd = mpirun + ["-np", "2", "dask-mpi", "--scheduler-file", fn]

        with popen(cmd, stdin=FNULL):
            with Client(scheduler_file=fn) as c:

                start = time()
                while len(c.scheduler_info()["workers"]) != 1:
                    assert time() < start + 10
                    sleep(0.2)

                assert c.submit(lambda x: x + 1, 10).result() == 11

                cmd = mpirun + [
                    "-np",
                    "1",
                    "dask-mpi",
                    "--scheduler-file",
                    fn,
                    "--no-scheduler",
                ]

                with popen(cmd):
                    start = time()
                    while len(c.scheduler_info()["workers"]) != 2:
                        assert time() < start + 10
                        sleep(0.2)


@pytest.mark.skip(reason="Should we explicilty expose --worker-port?")
@pytest.mark.parametrize("nanny", ["--nanny", "--no-nanny"])
def test_non_default_ports(loop, nanny, mpirun):
    with tmpfile(extension="json") as fn:

        cmd = mpirun + [
            "-np",
            "2",
            "dask-mpi",
            "--scheduler-file",
            fn,
            nanny,
            "--scheduler-port",
            "56723",
            "--worker-port",
            "58464",
            "--nanny-port",
            "50164",
        ]

        with popen(cmd):
            with Client(scheduler_file=fn) as c:

                start = time()
                while len(c.scheduler_info()["workers"]) != 1:
                    assert time() < start + 10
                    sleep(0.2)

                sched_info = c.scheduler_info()
                sched_host, sched_port = get_address_host_port(sched_info["address"])
                assert sched_port == 56723
                for worker_addr, worker_info in sched_info["workers"].items():
                    worker_host, worker_port = get_address_host_port(worker_addr)
                    assert worker_port == 58464
                    if nanny == "--nanny":
                        _, nanny_port = get_address_host_port(worker_info["nanny"])
                        assert nanny_port == 50164

                assert c.submit(lambda x: x + 1, 10).result() == 11


def check_port_okay(port):
    start = time()
    while True:
        try:
            response = requests.get("http://localhost:%d/status/" % port)
            assert response.ok
            break
        except Exception:
            sleep(0.1)
            assert time() < start + 20


def test_dashboard(loop, mpirun):
    with tmpfile(extension="json") as fn:

        cmd = mpirun + [
            "-np",
            "2",
            "dask-mpi",
            "--scheduler-file",
            fn,
            "--dashboard-address",
            ":59583",
        ]

        with popen(cmd, stdin=FNULL):
            check_port_okay(59583)

        with pytest.raises(Exception):
            requests.get("http://localhost:59583/status/")


@pytest.mark.skip(reason="Should we expose this option?")
def test_bokeh_worker(loop, mpirun):
    with tmpfile(extension="json") as fn:

        cmd = mpirun + [
            "-np",
            "2",
            "dask-mpi",
            "--scheduler-file",
            fn,
            "--bokeh-worker-port",
            "59584",
        ]

        with popen(cmd, stdin=FNULL):
            check_port_okay(59584)
