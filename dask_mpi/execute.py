import asyncio
import threading

import dask
from distributed import Nanny, Scheduler
from distributed.utils import import_term

from .exceptions import WorldTooSmallException
from .initialize import send_close_signal


def execute(
    func,
    *args,
    client_rank=1,
    scheduler_rank=0,
    interface=None,
    nthreads=1,
    local_directory="",
    memory_limit="auto",
    nanny=False,
    dashboard=True,
    dashboard_address=":8787",
    protocol=None,
    exclusive_workers=True,
    worker_class="distributed.Worker",
    worker_options=None,
    comm=None,
    **kwargs,
):
    """
    Execute a function on a given MPI rank with a Dask cluster launched using mpi4py

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
    func : callable
        A function containing Dask client code to execute with a Dask cluster
    args : list
        Arguments to func
    client_rank : int
        The MPI rank on which to run func
    scheduler_rank : int
        The MPI rank on which to run the Dask scheduler
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
        Start workers in nanny process for management (deprecated, use worker_class instead)
    dashboard : bool
        Enable Bokeh visual diagnostics
    dashboard_address : str
        Bokeh port for visual diagnostics
    protocol : str
        Protocol like 'inproc' or 'tcp'
    exclusive_workers : bool
        Whether to only run Dask workers on their own MPI ranks
    worker_class : str
        Class to use when creating workers
    worker_options : dict
        Options to pass to workers
    comm: mpi4py.MPI.Intracomm
        Optional MPI communicator to use instead of COMM_WORLD
    """
    if comm is None:
        from mpi4py import MPI

        comm = MPI.COMM_WORLD

    world_size = comm.Get_size()
    min_world_size = 1 + max(client_rank, scheduler_rank, exclusive_workers)
    if world_size < min_world_size:
        raise WorldTooSmallException(
            f"Not enough MPI ranks to start cluster with exclusive_workers={exclusive_workers} and "
            f"scheduler_rank={scheduler_rank}, found {world_size} MPI ranks but needs {min_world_size}."
        )

    rank = comm.Get_rank()

    if not worker_options:
        worker_options = {}

    async def run_client():
        def wrapped_func(*args, **kwargs):
            func(*args, **kwargs)
            send_close_signal()

        threading.Thread(target=wrapped_func, args=args, kwargs=kwargs).start()

    async def run_worker(with_client=False):
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
            if with_client:
                asyncio.get_event_loop().create_task(run_client())

            await worker.finished()

    async def run_scheduler(with_worker=False, with_client=False):
        async with Scheduler(
            interface=interface,
            protocol=protocol,
            dashboard=dashboard,
            dashboard_address=dashboard_address,
        ) as scheduler:
            dask.config.set(scheduler_address=scheduler.address)
            comm.bcast(scheduler.address, root=scheduler_rank)
            comm.Barrier()

            if with_worker:
                asyncio.get_event_loop().create_task(
                    run_worker(with_client=with_client)
                )

            elif with_client:
                asyncio.get_event_loop().create_task(run_client())

            await scheduler.finished()

    launch_scheduler = rank == scheduler_rank
    launch_client = rank == client_rank

    if launch_scheduler:
        run_coro = run_scheduler(
            with_worker=not exclusive_workers,
            with_client=launch_client,
        )

    else:
        scheduler_address = comm.bcast(None, root=scheduler_rank)
        dask.config.set(scheduler_address=scheduler_address)
        comm.Barrier()

        if launch_client and exclusive_workers:
            run_coro = run_client()
        else:
            run_coro = run_worker(with_client=launch_client)

    asyncio.get_event_loop().run_until_complete(run_coro)
