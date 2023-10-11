from __future__ import absolute_import, division, print_function

import json
import os
import subprocess
import tempfile
from time import sleep

import pytest
import requests
from dask.utils import tmpfile
from distributed import Client
from distributed.comm.addressing import get_address_host_port
from distributed.metrics import time
from distributed.utils import import_term
from distributed.utils_test import cleanup, loop, loop_in_thread, popen  # noqa: F401

pytest.importorskip("mpi4py")

FNULL = open(os.devnull, "w")  # hide output of subprocess


@pytest.mark.parametrize(
    "worker_class",
    ["distributed.Worker", "distributed.Nanny", "dask_cuda.CUDAWorker"],
)
def test_basic(loop, worker_class, mpirun):
    try:
        import_term(worker_class)
    except (ImportError, AttributeError):
        pytest.skip(
            "Cannot import {}, perhaps it is not installed".format(worker_class)
        )
    with tmpfile(extension="json") as fn:
        cmd = mpirun + [
            "-np",
            "4",
            "dask-mpi",
            "--scheduler-file",
            fn,
            "--worker-class",
            worker_class,
        ]

        with popen(cmd):
            with Client(scheduler_file=fn) as c:
                start = time()
                while len(c.scheduler_info()["workers"]) < 3:
                    assert time() < start + 10
                    sleep(0.2)

                assert c.submit(lambda x: x + 1, 10).result() == 11


def test_inclusive_workers(loop, mpirun):
    with tmpfile(extension="json") as fn:
        cmd = mpirun + [
            "-np",
            "4",
            "dask-mpi",
            "--scheduler-file",
            fn,
            "--inclusive-workers",
        ]

        with popen(cmd):
            with Client(scheduler_file=fn) as client:
                start = time()
                while len(client.scheduler_info()["workers"]) < 4:
                    assert time() < start + 10
                    sleep(0.1)

                assert client.submit(lambda x: x + 1, 10).result() == 11


def test_small_world(mpirun):
    with tmpfile(extension="json") as fn:
        # Set too few processes to start cluster
        p = subprocess.Popen(
            mpirun
            + [
                "-np",
                "1",
                "dask-mpi",
                "--scheduler-file",
                fn,
            ]
        )

        p.communicate()
        assert p.returncode != 0


def test_inclusive_small_world(mpirun):
    with tmpfile(extension="json") as fn:
        cmd = mpirun + [
            "-np",
            "1",
            "dask-mpi",
            "--scheduler-file",
            fn,
            "--inclusive-workers",
        ]

        with popen(cmd):
            with Client(scheduler_file=fn) as client:
                start = time()
                while len(client.scheduler_info()["workers"]) < 1:
                    assert time() < start + 10
                    sleep(0.1)

                assert client.submit(lambda x: x + 1, 10).result() == 11


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


def test_scheduler_rank(loop, mpirun):
    with tmpfile(extension="json") as fn:
        cmd = mpirun + [
            "-np",
            "2",
            "dask-mpi",
            "--scheduler-file",
            fn,
            "--exclusive-workers",
            "--scheduler-rank",
            "1",
        ]

        with popen(cmd, stdin=FNULL):
            with Client(scheduler_file=fn) as client:
                start = time()
                while len(client.scheduler_info()["workers"]) < 1:
                    assert time() < start + 10
                    sleep(0.2)

                worker_infos = client.scheduler_info()["workers"]
                assert len(worker_infos) == 1

                worker_info = next(iter(worker_infos.values()))
                assert worker_info["name"].rsplit("-")[-1] == "0"

                assert client.submit(lambda x: x + 1, 10).result() == 11


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
        ]

        with popen(cmd):
            with Client(scheduler_file=fn) as c:
                sched_info = c.scheduler_info()
                _, sched_port = get_address_host_port(sched_info["address"])
                assert sched_port == 56723


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


def tmpfile_static(extension="", dir=None):
    """
    utility function for test_stale_sched test
    """

    extension = "." + extension.lstrip(".")
    handle, filename = tempfile.mkstemp(extension, dir=dir)
    return handle, filename


@pytest.mark.parametrize("nanny", ["--nanny", "--no-nanny"])
def test_stale_sched(loop, nanny, mpirun):
    """
    the purpose of this unit test is to simulate the situation in which
    an old scheduler file has been left behind from a non-clean dask exit.
    in this situation the scheduler should wake up and overwrite the stale
    file before the workers start.
    """

    fhandle, fn = tmpfile_static(extension="json")

    stale_json = {
        "type": "Scheduler",
        "id": "Scheduler-edb63f9c-9e83-4021-8563-44bcffc451cc",
        "address": "tcp://10.128.0.32:45373",
        "services": {"dashboard": 8787},
        "workers": {},
    }

    with open(fn, "w") as f:
        json.dump(stale_json, f)

    cmd = mpirun + [
        "-np",
        "4",
        "dask-mpi",
        "--scheduler-file",
        fn,
        "--dashboard-address",
        "0",
        nanny,
    ]

    p = subprocess.Popen(cmd)

    sleep(5)

    p.kill()

    with open(fn) as f:
        new_json = json.load(f)

    os.close(fhandle)
    os.remove(fn)

    assert new_json != stale_json
