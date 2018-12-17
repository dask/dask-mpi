from functools import partial

from distributed import Scheduler, Nanny, Worker
from distributed.bokeh.worker import BokehWorker
from distributed.cli.utils import uri_from_host_port
from distributed.utils import get_ip_interface
from tornado import gen


def get_host_from_interface(interface=None):
    if interface:
        host = get_ip_interface(interface)
    else:
        host = None
    return host


def start_scheduler(host, loop, scheduler_file, bokeh_port, bokeh_prefix):
    try:
        from distributed.bokeh.scheduler import BokehScheduler
    except ImportError:
        services = {}
    else:
        services = {('bokeh', bokeh_port): partial(BokehScheduler, prefix=bokeh_prefix)}
    scheduler = Scheduler(scheduler_file=scheduler_file,
                          loop=loop,
                          services=services)
    addr = uri_from_host_port(host, None, 8786)
    scheduler.start(addr)
    try:
        loop.start()
        loop.close()
    finally:
        scheduler.stop()


def start_worker(host, loop, name, scheduler_file, nanny, local_directory,
                 nthreads, memory_limit, bokeh_worker_port):
    W = Nanny if nanny else Worker
    worker = W(scheduler_file=scheduler_file,
               loop=loop,
               name=name,
               ncores=nthreads,
               local_dir=local_directory,
               services={('bokeh', bokeh_worker_port): BokehWorker},
               memory_limit=memory_limit)
    addr = uri_from_host_port(host, None, 0)

    @gen.coroutine
    def run():
        yield worker._start(addr)
        while worker.status != 'closed':
            yield gen.sleep(0.2)

    try:
        loop.run_sync(run)
        loop.close()
    finally:
        pass

    @gen.coroutine
    def close():
        yield worker._close(timeout=2)

    loop.run_sync(close)
