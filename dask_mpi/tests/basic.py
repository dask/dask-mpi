import sys

from time import sleep
from distributed import Client
from distributed.metrics import time
from dask_mpi.core import initialize, rank

scheduler_file = sys.argv[1]
nanny = bool(int(sys.argv[2]))

initialize(scheduler_file=scheduler_file, nanny=nanny)

print(f'[{rank}] scheduler_file = {scheduler_file}')
print(f'[{rank}] nanny = {nanny}')

with Client(scheduler_file=scheduler_file) as c:
    start = time()
    while len(c.scheduler_info()['workers']) != 2:
        assert time() < start + 10
        sleep(0.2)

    print(f'[{rank}] workers all running')

    assert c.submit(lambda x: x + 1, 10, workers=1).result() == 11
    print(f'[{rank}] client submission response received')

    workers = list(c.scheduler_info()['workers'])
    c.run_on_scheduler(lambda dask_scheduler=None:
                       dask_scheduler.retire_workers(workers, close_workers=True))
    c.sync(c.scheduler.close())
