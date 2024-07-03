from time import sleep, time

from distributed import Client
from mpi4py.MPI import COMM_WORLD as world

from dask_mpi import execute

# Split our MPI world into two pieces, one consisting just of
# the old rank 3 process and the other with everything else
new_comm_assignment = 1 if world.rank == 3 else 0
comm = world.Split(new_comm_assignment)

if world.rank != 3:

    def client_code():
        with Client() as c:
            start = time()
            while len(c.scheduler_info()["workers"]) != 1:
                assert time() < start + 10
                sleep(0.2)

            c.submit(lambda x: x + 1, 10).result() == 11
            c.submit(lambda x: x + 1, 20).result() == 21

    execute(client_code, comm=comm)

# check that our original comm is intact
world.Barrier()
x = 100 if world.rank == 0 else 200
x = world.bcast(x)
assert x == 100
