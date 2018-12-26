from __future__ import print_function, division, absolute_import
import sys
import dask
import atexit

from distributed import Client
from mpi4py import MPI
from tornado import gen
from tornado.ioloop import IOLoop

from dask_mpi.common import get_host_from_interface, create_scheduler, run_scheduler, create_and_run_worker

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
loop = IOLoop()


def initialize(interface=None, nthreads=1, local_directory='', memory_limit='auto', nanny=False,
               bokeh=True, bokeh_port=8787, bokeh_prefix=None, bokeh_worker_port=8789):
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
    host = get_host_from_interface(interface)

    if rank == 0:
        scheduler = create_scheduler(loop, host=host, bokeh=bokeh, bokeh_port=bokeh_port, bokeh_prefix=bokeh_prefix)
        addr = scheduler.address
    else:
        addr = None

    scheduler_address = comm.bcast(addr, root=0)
    dask.config.set(scheduler_address=scheduler_address)
    comm.Barrier()

    if rank == 0:
        run_scheduler(scheduler)
        sys.exit()
    elif rank == 1:
        return
    else:
        create_and_run_worker(loop, host=host, rank=rank, nanny=nanny, nthreads=nthreads,
                              local_directory=local_directory, memory_limit=memory_limit,
                              bokeh=bokeh, bokeh_port=bokeh_worker_port)
        sys.exit()


def send_close_signal():
    @gen.coroutine
    def stop(dask_scheduler):
        yield dask_scheduler.close()
        yield gen.sleep(0.1)
        local_loop = dask_scheduler.loop
        local_loop.add_callback(local_loop.stop)

    with Client() as c:
        c.run_on_scheduler(stop, wait=False)


if rank == 1:
    atexit.register(send_close_signal)
