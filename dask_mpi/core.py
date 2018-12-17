import sys

from mpi4py import MPI
from tornado.ioloop import IOLoop

from dask_mpi.common import get_host_from_interface, start_scheduler, start_worker

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
loop = IOLoop()


def initialize(scheduler_file='scheduler.json', interface=None, nthreads=0, local_directory='',
               memory_limit='auto', scheduler=True, nanny=True, bokeh_port=8787, bokeh_prefix=None,
               bokeh_worker_port=8789):
    host = get_host_from_interface(interface)

    if rank == 0 and scheduler:
        import logging
        logger = logging.getLogger('distributed.scheduler')
        logger.info(f'[{rank}] scheduler started...')
        start_scheduler(loop, host=host, scheduler_file=scheduler_file,
                        bokeh_port=bokeh_port, bokeh_prefix=bokeh_prefix)
        logger.info(f'[{rank}] scheduler stopped.')
        sys.exit()

    elif rank == 1:
        pass

    else:
        import logging
        logger = logging.getLogger('distributed.worker')
        name = rank-1 if scheduler else None
        logger.info(f'[{rank}] worker started...')
        start_worker(loop, host=host, name=name, scheduler_file=scheduler_file, nanny=nanny,
                     local_directory=local_directory, nthreads=nthreads, memory_limit=memory_limit,
                     bokeh_worker_port=bokeh_worker_port)
        logger.info(f'[{rank}] worker stopped.')
        sys.exit()
