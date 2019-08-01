import asyncio
import atexit
import sys

import dask
from dask.distributed import Client, Scheduler, Worker, Nanny

from tornado import gen
from tornado.ioloop import IOLoop


def initialize(
    interface=None,
    nthreads=1,
    local_directory="",
    memory_limit="auto",
    nanny=False,
    dashboard=True,
    dashboard_address=":8787",
    protocol=None,
):
    """
    Initialize a Dask cluster using mpi4py

    Using mpi4py, MPI rank 0 launches the Scheduler, MPI rank 1 passes through to the
    client script, and all other MPI ranks launch workers.  All MPI ranks other than
    MPI rank 1 block while their event loops run and exit once shut down.

    Parameters
    ----------
    interface : str
        Network interface like 'eth0' or 'ib0'
    nthreads : int
        Number of threads per worker
    local_directory : str
        Directory to place worker files
    memory_limit : int, float, or 'auto'
        Number of bytes before spilling data to disk.  This can be an
        integer (nbytes), float (fraction of total memory), or 'auto'.
    nanny : bool
        Start workers in nanny process for management
    bokeh : bool
        Enable Bokeh visual diagnostics
    bokeh_port : int
        Bokeh port for visual diagnostics
    bokeh_prefix : str
        Prefix for the bokeh app
    bokeh_worker_port : int
        Worker's Bokeh port for visual diagnostics
    """
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    loop = IOLoop.current()

    if rank == 0:

        async def run_scheduler():
            async with Scheduler(
                interface=interface,
                protocol=protocol,
                dashboard_address=dashboard_address,
            ) as scheduler:
                comm.bcast(scheduler.address, root=0)
                comm.Barrier()
                await scheduler.finished()

        asyncio.get_event_loop().run_until_complete(run_scheduler())
        sys.exit()

    else:
        scheduler_address = comm.bcast(None, root=0)
        dask.config.set(scheduler_address=scheduler_address)
        comm.Barrier()

    if rank == 1:
        atexit.register(send_close_signal)
    else:

        async def run_worker():
            WorkerType = Nanny if nanny else Worker
            async with WorkerType(
                interface=interface,
                protocol=protocol,
                nthreads=nthreads,
                memory_limit=memory_limit,
                local_dir=local_directory,
                name=rank,
            ) as worker:
                await worker.finished()

        asyncio.get_event_loop().run_until_complete(run_worker())
        sys.exit()


def send_close_signal():
    async def stop(dask_scheduler):
        await dask_scheduler.close()
        await gen.sleep(0.1)
        local_loop = dask_scheduler.loop
        local_loop.add_callback(local_loop.stop)

    with Client() as c:
        c.run_on_scheduler(stop, wait=False)
