from argparse import ArgumentParser
from time import sleep

from distributed import Client
from distributed.metrics import time

from dask_mpi import execute


def client_func(m=4, c=1, s=0, x=True):
    xranks = {c, s} if x else set()
    worker_ranks = set(i for i in range(m) if i not in xranks)

    with Client() as c:
        start = time()
        while len(c.scheduler_info()["workers"]) != len(worker_ranks):
            assert time() < start + 10
            sleep(0.2)

        actual_worker_ranks = set(v["name"] for k,v in c.scheduler_info()["workers"].items())
        assert actual_worker_ranks == worker_ranks

        for i in actual_worker_ranks:
            assert c.submit(lambda x: x + 1, 10, workers=i).result() == 11


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", type=int, default=None)
    parser.add_argument("-c", type=int, default=None)
    parser.add_argument("-s", type=int, default=None)
    parser.add_argument("-x", type=lambda v: v.lower() != "false", default=None)
    kwargs = vars(parser.parse_args())

    execute_kwargs = {k:v for k,v in kwargs.items() if v is not None}
    if "c" in execute_kwargs:
        execute_kwargs["client_rank"] = execute_kwargs["c"]
    if "s" in execute_kwargs:
        execute_kwargs["scheduler_rank"] = execute_kwargs["s"]
    if "x" in execute_kwargs:
        execute_kwargs["exclusive_workers"] = execute_kwargs["x"]

    execute(client_func, **execute_kwargs)
