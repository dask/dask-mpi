from time import sleep
from distributed import Client
from distributed.metrics import time

from dask_mpi.core import initialize

initialize()

with Client() as c:

    start = time()
    while len(c.scheduler_info()['workers']) != 2:
        assert time() < start + 10
        sleep(0.2)

    assert c.submit(lambda x: x + 1, 10, workers='mpi-rank-2').result() == 11
