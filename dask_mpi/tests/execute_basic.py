import sys
from time import sleep

from distributed import Client
from distributed.metrics import time

from dask_mpi import execute


def client_func(m, c, s, x):
    xranks = {c, s} if x else set()
    worker_ranks = set(i for i in range(m) if i not in xranks)

    with Client() as c:
        start = time()
        while len(c.scheduler_info()["workers"]) != len(worker_ranks):
            assert time() < start + 10
            sleep(0.2)

        actual_worker_ranks = set(
            v["name"] for k, v in c.scheduler_info()["workers"].items()
        )
        assert actual_worker_ranks == worker_ranks

        for i in actual_worker_ranks:
            assert c.submit(lambda x: x + 1, 10, workers=i).result() == 11


if __name__ == "__main__":
    vmap = {"True": True, "False": False, "None": None}
    int_or_bool = lambda s: vmap[s] if s in vmap else int(s)
    args = [int_or_bool(i) for i in sys.argv[1:]]

    execute(
        client_function=client_func,
        client_args=args,
        client_rank=args[1],
        scheduler_rank=args[2],
        exclusive_workers=args[3],
    )
