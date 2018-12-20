import sys

from time import sleep
from distributed import Client
from distributed.metrics import time
from tornado import gen

from dask_mpi.core import initialize

scheduler_file = sys.argv[1]

initialize(scheduler_file=scheduler_file)

with Client(scheduler_file=scheduler_file) as c:

    start = time()
    while len(c.scheduler_info()['workers']) != 2:
        assert time() < start + 10
        sleep(0.2)

    assert c.submit(lambda x: x + 1, 10, workers=1).result() == 11

    async def stop(dask_scheduler):
        await dask_scheduler.close()
        await gen.sleep(0.1)
        loop = dask_scheduler.loop
        loop.add_callback(loop.stop)
    c.run_on_scheduler(stop, wait=False)
