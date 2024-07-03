import asyncio
import atexit
import sys

import dask
from distributed import Nanny, Scheduler
from distributed.utils import import_term

from .exceptions import WorldTooSmallException
from .execute import send_close_signal


def initialize(
    interface=None,
    nthreads=1,
    local_directory=None,
    memory_limit="auto",
    nanny=False,
    dashboard=True,
    dashboard_address=":8787",
    protocol=None,
    worker_class="distributed.Worker",
    worker_options=None,
    comm=None,
    exit=True,
):
    """
    Initialize a Dask cluster using mpi4py

    Using mpi4py, MPI rank 0 launches the Scheduler, MPI rank 1 passes through to the
    client script, and all other MPI ranks launch workers.  All MPI ranks other than
    MPI rank 1 block while their event loops run.

    In normal operation these ranks exit once rank 1 ends. If exit=False is set they
    instead return an bool indicating whether they are the client and should execute
    more client code, or a worker/scheduler who should not.  In this case the user is
    responsible for the client calling send_close_signal when work is complete, and
    checking the returned value to choose further actions.

    Parameters
    ----------
    interface : str
        Network interface like 'eth0' or 'ib0'
    nthreads : int
        Number of threads per worker
    local_directory : str or None
        Directory to place worker files
    memory_limit : int, float, or 'auto'
        Number of bytes before spilling data to disk.  This can be an
        integer (nbytes), float (fraction of total memory), or 'auto'.
    nanny : bool
        Start workers in nanny process for management (deprecated, use worker_class instead)
    dashboard : bool
        Enable Bokeh visual diagnostics
    dashboard_address : str
        Bokeh port for visual diagnostics
    protocol : str
        Protocol like 'inproc' or 'tcp'
    worker_class : str
        Class to use when creating workers
    worker_options : dict
        Options to pass to workers
    comm: mpi4py.MPI.Intracomm
        Optional MPI communicator to use instead of COMM_WORLD
    exit: bool
        Whether to call sys.exit on the workers and schedulers when the event
        loop completes.

    Returns
    -------
    is_client: bool
        Only returned if exit=False. Inidcates whether this rank should continue
        to run client code (True), or if it acts as a scheduler or worker (False).
    """
    if comm is None:
        from mpi4py import MPI

        comm = MPI.COMM_WORLD

    world_size = comm.Get_size()
    if world_size < 3:
        raise WorldTooSmallException(
            f"Not enough MPI ranks to start cluster, found {world_size}, "
            "needs at least 3, one each for the scheduler, client and a worker."
        )

    rank = comm.Get_rank()

    if not worker_options:
        worker_options = {}

    if rank == 0:

        async def run_scheduler():
            async with Scheduler(
                interface=interface,
                protocol=protocol,
                dashboard=dashboard,
                dashboard_address=dashboard_address,
            ) as scheduler:
                comm.bcast(scheduler.address, root=0)
                comm.Barrier()
                await scheduler.finished()

        asyncio.get_event_loop().run_until_complete(run_scheduler())
        if exit:
            sys.exit()
        else:
            return False

    else:
        scheduler_address = comm.bcast(None, root=0)
        dask.config.set(scheduler_address=scheduler_address)
        comm.Barrier()

    if rank == 1:
        if exit:
            atexit.register(send_close_signal)
        return True
    else:

        async def run_worker():
            WorkerType = import_term(worker_class)
            if nanny:
                WorkerType = Nanny
                raise DeprecationWarning(
                    "Option nanny=True is deprectaed, use worker_class='distributed.Nanny' instead"
                )
            opts = {
                "interface": interface,
                "protocol": protocol,
                "nthreads": nthreads,
                "memory_limit": memory_limit,
                "local_directory": local_directory,
                "name": rank,
                **worker_options,
            }
            async with WorkerType(**opts) as worker:
                await worker.finished()

        asyncio.get_event_loop().run_until_complete(run_worker())
        if exit:
            sys.exit()
        else:
            return False
