from __future__ import print_function, division, absolute_import
from functools import partial

from distributed import Scheduler, Nanny, Worker
from distributed.comm.addressing import uri_from_host_port
from distributed.utils import get_ip_interface
from tornado import gen


def get_host_from_interface(interface=None):
    if interface:
        host = get_ip_interface(interface)
    else:
        host = None
    return host


def create_scheduler(loop, scheduler_file=None, host=None, bokeh=True, bokeh_port=8787, bokeh_prefix=None,
                     scheduler_port=None):
    try:
        from distributed.bokeh.scheduler import BokehScheduler
    except ImportError:
        BokehScheduler = None

    if bokeh and BokehScheduler:
        services = {('bokeh', bokeh_port): partial(BokehScheduler, prefix=bokeh_prefix)}
    else:
        services = {}

    scheduler = Scheduler(loop=loop, services=services, scheduler_file=scheduler_file)
    addr = uri_from_host_port(host, scheduler_port, 8786)
    scheduler.start(addr)
    return scheduler


def run_scheduler(scheduler):
    scheduler_loop = scheduler.loop
    try:
        scheduler_loop.start()
    finally:
        scheduler_loop.close()
    scheduler.stop()


def create_and_run_worker(loop, host=None, rank=0, scheduler_file=None, nanny=False,
                          local_directory='', nthreads=0, memory_limit='auto',
                          bokeh=True, bokeh_port=8789, bokeh_prefix=None,
                          worker_port=None, nanny_port=None):
    try:
        from distributed.bokeh.worker import BokehWorker
    except ImportError:
        BokehWorker = None

    if bokeh and BokehWorker:
        services = {('bokeh', bokeh_port): partial(BokehWorker, prefix=bokeh_prefix)}
    else:
        services = {}

    if nanny:
        port = nanny_port
        kwargs = {'worker_port': worker_port}
        W = Nanny
    else:
        port = worker_port
        kwargs = {}
        W = Worker

    W = Nanny if nanny else Worker
    worker = W(scheduler_file=scheduler_file,
               loop=loop,
               name='mpi-rank-%d' % rank,
               ncores=nthreads,
               local_dir=local_directory,
               services=services,
               memory_limit=memory_limit,
               **kwargs)

    addr = uri_from_host_port(host, port, 0)

    @gen.coroutine
    def run_until_closed():
        yield worker._start(addr)
        while worker.status != 'closed':
            yield gen.sleep(0.2)

    worker_loop = worker.loop
    try:
        worker_loop.run_sync(run_until_closed)
    finally:
        @gen.coroutine
        def close():
            yield worker._close(timeout=2)

        worker_loop.run_sync(close)
        worker_loop.close()
