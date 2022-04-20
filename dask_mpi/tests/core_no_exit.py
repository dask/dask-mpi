from distributed import Client
from mpi4py.MPI import COMM_WORLD as world

from dask_mpi import finalize, initialize

# Split our MPI world into two pieces, one consisting just of
# the old rank 3 process and the other with everything else
new_comm_assignment = 1 if world.rank == 3 else 0
comm = world.Split(new_comm_assignment)

if world.rank != 3:
    # run tests with rest of comm
    is_client = initialize(comm=comm, exit=False)

    if is_client:
        with Client() as c:
            c.submit(lambda x: x + 1, 10).result() == 11
            c.submit(lambda x: x + 1, 20).result() == 21
        finalize()

# check that our original comm is intact
world.Barrier()
x = 100 if world.rank == 0 else 200
x = world.bcast(x)
assert x == 100
